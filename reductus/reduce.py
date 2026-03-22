"""
Python scripting API for running reductions without a web server.

This module provides direct access to the Reductus data reduction engine,
allowing batch processing, automation, and notebook-style workflows.

Example usage:

    from reductus import reduce

    # Load a template and run a reduction
    template = reduce.load_template("my_template.json")
    result = template.run(files=["D:/data/*.nxs"])
    result.save("output/")

    # Or use the convenience function
    result = reduce.run("my_template.json", files=["data/*.nxs"])
"""

import json
import os
import sys
import glob as glob_module
import logging
from pathlib import Path

from reductus.logging_config import get_reduce_logger

logger = get_reduce_logger()

# Lazy initialization
_initialized = False


def _ensure_initialized(instruments=None):
    """
    Lazy initialize the API on first call.
    Loads configuration and registers instruments.
    """
    global _initialized
    if _initialized:
        logger.debug("Already initialized, skipping")
        return

    logger.info("Initializing Reductus reduction API")
    try:
        from reductus.dataflow.configure import load_config, apply_config

        config = load_config(name="config", fallback=True)
        loaded_instruments = config.get("instruments", [])
        logger.debug(f"Loaded configuration with instruments: {loaded_instruments}")

        if instruments:
            logger.info(f"Overriding instruments: {instruments}")
            config["instruments"] = instruments

        apply_config(user_config=config)
        _initialized = True
        logger.info("Reductus API initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize Reductus: {e}", exc_info=True)
        raise


def _path_to_fileinfo(path):
    """
    Convert a filesystem path or glob pattern to a list of fileinfo dicts.

    Returns a list of {"source": "local", "path": str, "mtime": int} dicts,
    one per file that matches the pattern.
    """
    logger.debug(f"Converting path to fileinfo: {path}")

    # Normalize path and handle globs
    expanded_path = os.path.expanduser(path)

    # Try glob expansion
    matches = glob_module.glob(expanded_path, recursive=True)

    if not matches:
        # No glob matches; treat as literal path
        if os.path.exists(expanded_path):
            matches = [expanded_path]
            logger.debug(f"Path exists as literal: {expanded_path}")
        else:
            # Path doesn't exist, but return it anyway (will fail at load time)
            matches = [expanded_path]
            logger.warning(f"Path not found: {expanded_path}")
    else:
        logger.debug(f"Glob pattern matched {len(matches)} files")

    fileinfos = []
    for filepath in matches:
        abs_path = os.path.abspath(filepath)
        try:
            mtime = int(os.path.getmtime(abs_path))
        except (OSError, FileNotFoundError):
            mtime = 0
            logger.warning(f"Could not stat file: {abs_path}")

        fileinfos.append({
            "source": "local",
            "path": abs_path.replace("\\", "/"),  # Always use forward slashes
            "mtime": mtime,
        })

    logger.info(f"Converted {len(fileinfos)} files from pattern: {path}")
    return fileinfos


def _find_loader_nodes(template_def):
    """
    Find all loader node indices in a template.

    Loader nodes are those whose action accepts a 'filelist' parameter.

    Returns a list of node indices for loader nodes.
    """
    import inspect
    from reductus.dataflow.core import lookup_module

    loaders = []

    for node_idx, node_info in enumerate(template_def.get("modules", [])):
        module_id = node_info.get("module")
        if not module_id:
            continue

        try:
            module = lookup_module(module_id)
        except KeyError:
            continue

        # Check if the module's action accepts 'filelist' parameter
        try:
            sig = inspect.signature(module.action)
            if 'filelist' in sig.parameters:
                loaders.append(node_idx)
        except (TypeError, ValueError):
            # Can't inspect action (e.g., it's a lambda or built-in)
            pass

    return loaders


class Template:
    """
    A reduction template that can be run with different input files.

    Templates are loaded from JSON files and define the computational
    workflow as a directed acyclic graph of processing modules.
    """

    def __init__(self, template_def):
        """
        Initialize with a template definition dict (from JSON).
        """
        self.template_def = template_def

    @classmethod
    def load(cls, path):
        """
        Load a template from a JSON file.

        Args:
            path: Absolute or relative path to template JSON file

        Returns:
            Template instance
        """
        with open(path, "r") as f:
            template_def = json.load(f)
        return cls(template_def)

    @classmethod
    def from_dict(cls, d):
        """
        Create a template from a dictionary.

        Args:
            d: Template definition dict (same structure as loaded JSON)

        Returns:
            Template instance
        """
        return cls(d)

    def run(self, files=None, data_dir=None, glob_pattern=None,
            node=None, terminal="output", **field_overrides):
        """
        Run the template with specified files.

        Args:
            files: List of file paths or glob patterns to process.
                   If None, uses data_dir + glob_pattern.
            data_dir: Directory to search for files (if files not specified).
            glob_pattern: Glob pattern for files in data_dir (default: "**/*").
            node: Node index to return results from (default: last node).
            terminal: Output terminal name (default: "output").
            **field_overrides: Additional field values to set in the template config.

        Returns:
            ReductionResult instance
        """
        logger.info(f"Running template reduction", extra={
            "template_name": self.template_def.get("name", "Unknown"),
            "has_files": files is not None,
            "has_data_dir": data_dir is not None,
            "node": node,
            "terminal": terminal
        })

        _ensure_initialized()

        from reductus.dataflow.core import Template as CoreTemplate
        from reductus.dataflow.calc import process_template

        try:
            # Build list of fileinfo dicts
            fileinfos = []

            if files is None and data_dir is None:
                # No files specified; loaders will use template defaults if present
                logger.debug("No files specified")
                fileinfos = []
            elif files is not None:
                # Process explicit file list
                logger.debug(f"Processing {len(files)} file patterns")
                for f in files:
                    fileinfos.extend(_path_to_fileinfo(f))
            else:
                # data_dir specified; glob for files
                pattern = glob_pattern or "**/*"
                search_path = os.path.join(data_dir, pattern)
                logger.info(f"Globbing directory: {data_dir}")
                fileinfos.extend(_path_to_fileinfo(search_path))

            logger.info(f"Loaded {len(fileinfos)} files for reduction")

            # Inject file lists into loader nodes
            config = {}
            loaders = _find_loader_nodes(self.template_def)
            logger.debug(f"Found {len(loaders)} loader nodes")

            if loaders and fileinfos:
                # All loaders get the same file list
                for node_idx in loaders:
                    config.setdefault(str(node_idx), {})["filelist"] = fileinfos

            # Apply field overrides
            if field_overrides:
                logger.debug(f"Applying field overrides: {list(field_overrides.keys())}")
                for key, value in field_overrides.items():
                    # key is like "0" for node index or "0:field" for specific field
                    if ":" in key:
                        parts = key.split(":", 1)
                        node_idx, field_name = parts
                        config.setdefault(node_idx, {})[field_name] = value
                    else:
                        if not isinstance(value, dict):
                            raise TypeError(
                                f"Field override for node '{key}' must be a dict, "
                                f"got {type(value).__name__}. Use 'node:field' syntax "
                                f"for individual field overrides."
                            )
                        config.setdefault(key, {}).update(value)

            # Determine target node (default to last)
            num_modules = len(self.template_def.get("modules", []))
            if node is None:
                node = num_modules - 1
            elif node < 0:
                # Handle negative indices like Python lists
                node = num_modules + node

            logger.info(f"Executing through node {node} terminal '{terminal}'")

            # Create a CoreTemplate from the definition
            core_template = CoreTemplate(**self.template_def)

            # Run the template
            logger.debug("Starting template execution")
            bundle = process_template(core_template, config, target=(node, terminal))
            logger.info(f"Template execution complete", extra={
                "datatype": bundle.datatype.id if bundle.datatype else None,
                "output_size": len(str(bundle.values)) if hasattr(bundle, 'values') else 0
            })

            return ReductionResult(bundle, node, terminal)

        except Exception as e:
            logger.error(f"Template execution failed: {e}", exc_info=True)
            raise


class ReductionResult:
    """
    Results from running a template.

    Provides access to output data and export functionality.
    """

    def __init__(self, bundle, node=None, terminal="output"):
        """
        Initialize with a Bundle from process_template.

        Args:
            bundle: Bundle object from process_template()
            node: Node index this result came from
            terminal: Terminal name this result came from
        """
        self.bundle = bundle
        self.node = node
        self.terminal = terminal

    def get_bundle(self, node=None, terminal="output"):
        """
        Get the underlying Bundle object.

        Returns:
            Bundle instance with datatype and values
        """
        # For now, we only store one bundle; this API is for future
        # multi-node result access
        return self.bundle

    def get_data(self, node=None, terminal="output"):
        """
        Get the raw data values from the result.

        Returns:
            List of processed data objects
        """
        return self.bundle.values

    def save(self, output_dir, fmt="column"):
        """
        Save results to files in the output directory.

        Creates one file per data item using the datatype's export function.

        Args:
            output_dir: Directory to write output files to (created if needed).
            fmt: Export format (default: "column", supported by most datatypes).
        """
        logger.info(f"Saving reduction results", extra={
            "output_dir": output_dir,
            "format": fmt
        })

        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.debug(f"Created output directory: {output_dir}")

            # Get export data from bundle
            logger.debug(f"Exporting data as format: {fmt}")
            try:
                export_data = self.bundle.get_export(export_type=fmt)
                values = export_data.get("values", [])
            except ValueError:
                logger.warning(
                    f"Export type '{fmt}' not available for "
                    f"{self.bundle.datatype.id}; falling back to str()"
                )
                values = self.bundle.values
            logger.info(f"Exporting {len(values)} values")

            # Write each value to a file
            written_files = []
            for i, data in enumerate(values):
                # Construct filename from data attributes if available
                if hasattr(data, "name"):
                    base_name = data.name
                else:
                    base_name = f"output_{i}"

                filename = f"{base_name}.dat"
                filepath = os.path.join(output_dir, filename)

                # Write data
                if isinstance(data, str):
                    with open(filepath, "w") as f:
                        f.write(data)
                else:
                    # Try to serialize as text
                    with open(filepath, "w") as f:
                        f.write(str(data))

                written_files.append(filename)
                logger.debug(f"Wrote output file: {filename}")

            logger.info(f"Successfully saved {len(written_files)} files to {output_dir}")

        except Exception as e:
            logger.error(f"Failed to save results: {e}", exc_info=True)
            raise


# Module-level convenience functions

def load_template(path):
    """
    Load a template from a JSON file.

    Args:
        path: Path to template JSON file

    Returns:
        Template instance
    """
    logger.info(f"Loading template from: {path}")
    try:
        template = Template.load(path)
        logger.info(f"Successfully loaded template: {template.template_def.get('name', 'Unknown')}")
        return template
    except FileNotFoundError as e:
        logger.error(f"Template file not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Failed to load template: {e}", exc_info=True)
        raise


def run(template_or_path, files=None, data_dir=None, glob_pattern=None,
        node=None, terminal="output", instruments=None, **field_overrides):
    """
    Load a template and run it with specified files.

    Convenience function combining load_template() and Template.run().

    Args:
        template_or_path: Path to template JSON or Template instance
        files: List of file paths or glob patterns
        data_dir: Directory to search for files
        glob_pattern: Glob pattern for files in data_dir
        node: Node to return results from
        terminal: Output terminal name
        instruments: List of instruments to load (overrides config)
        **field_overrides: Additional field values to set

    Returns:
        ReductionResult instance
    """
    logger.info("Running reduction via convenience function", extra={
        "template_type": type(template_or_path).__name__,
        "has_files": files is not None,
        "has_data_dir": data_dir is not None,
        "instruments": instruments
    })

    try:
        # Initialize with specified instruments if provided
        if instruments:
            logger.info(f"Initializing with instruments: {instruments}")
            _ensure_initialized(instruments=instruments)
        else:
            _ensure_initialized()

        # Load template if needed
        if isinstance(template_or_path, str):
            logger.debug(f"Loading template from path: {template_or_path}")
            template = Template.load(template_or_path)
        else:
            logger.debug("Using provided Template instance")
            template = template_or_path

        # Run template
        logger.debug("Executing template with convenience function")
        return template.run(
            files=files,
            data_dir=data_dir,
            glob_pattern=glob_pattern,
            node=node,
            terminal=terminal,
            **field_overrides
        )

    except Exception as e:
        logger.error(f"Convenience function failed: {e}", exc_info=True)
        raise
