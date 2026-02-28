"""
Template management for Reductus.

Handles:
- Discovering built-in templates
- Saving/loading user templates
- Template metadata and library organization

Templates are stored as JSON files with optional metadata:
{
    "name": "Template Name",
    "description": "What this template does",
    "instrument": "ncnr.refl",
    "version": "1.0",
    "modules": [...],
    "wires": [...]
}
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages template discovery, loading, and storage."""

    def __init__(self):
        """Initialize template manager."""
        self._user_template_dir = self._get_user_template_dir()
        self._built_in_dir = Path(__file__).parent / "configurations" / "templates"

    @staticmethod
    def _get_user_template_dir() -> Path:
        """Get user template directory, creating if needed."""
        from reductus.userdata import get_user_data_dir

        template_dir = get_user_data_dir() / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        return template_dir

    def list_templates(self, category: str = "all") -> Dict[str, List[Dict]]:
        """
        List available templates by category.

        Args:
            category: "all", "built-in", or "custom"

        Returns:
            Dict with keys "built-in" and "custom", each mapping to list of template metadata dicts
        """
        result = {}

        if category in ("all", "built-in"):
            result["built-in"] = self._list_built_in_templates()

        if category in ("all", "custom"):
            result["custom"] = self._list_custom_templates()

        return result

    def _list_built_in_templates(self) -> List[Dict]:
        """List built-in templates."""
        templates = []

        if not self._built_in_dir.exists():
            return templates

        for template_file in self._built_in_dir.glob("*.json"):
            try:
                metadata = self._extract_metadata(template_file)
                metadata["path"] = str(template_file)
                metadata["source"] = "built-in"
                templates.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")

        return sorted(templates, key=lambda t: t.get("name", ""))

    def _list_custom_templates(self) -> List[Dict]:
        """List user-saved templates."""
        templates = []

        if not self._user_template_dir.exists():
            return templates

        for template_file in self._user_template_dir.glob("*.json"):
            try:
                metadata = self._extract_metadata(template_file)
                metadata["path"] = str(template_file)
                metadata["source"] = "custom"
                templates.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")

        return sorted(templates, key=lambda t: t.get("name", ""))

    @staticmethod
    def _extract_metadata(template_path: Path) -> Dict:
        """Extract metadata from a template file."""
        with open(template_path, "r") as f:
            template_def = json.load(f)

        # Extract relevant fields
        return {
            "name": template_def.get("name", template_path.stem),
            "description": template_def.get("description", ""),
            "instrument": template_def.get("instrument", ""),
            "version": template_def.get("version", "1.0"),
            "filename": template_path.name,
        }

    def load_template(self, name: str, source: str = "all") -> Optional[Dict]:
        """
        Load a template by name.

        Args:
            name: Template name or filename
            source: "all", "built-in", or "custom"

        Returns:
            Template definition dict or None if not found
        """
        # Try as filename first
        template_path = self._find_template_file(name, source)

        if template_path and template_path.exists():
            with open(template_path, "r") as f:
                return json.load(f)

        return None

    def _find_template_file(self, name: str, source: str = "all") -> Optional[Path]:
        """Find template file path by name or filename."""
        # Try exact filename match
        if source in ("all", "built-in") and self._built_in_dir.exists():
            built_in_path = self._built_in_dir / name if name.endswith(".json") else self._built_in_dir / f"{name}.json"
            if built_in_path.exists():
                return built_in_path

        if source in ("all", "custom") and self._user_template_dir.exists():
            custom_path = self._user_template_dir / name if name.endswith(".json") else self._user_template_dir / f"{name}.json"
            if custom_path.exists():
                return custom_path

        # Try matching by template name field
        if source in ("all", "built-in"):
            for template_file in self._built_in_dir.glob("*.json") if self._built_in_dir.exists() else []:
                try:
                    with open(template_file, "r") as f:
                        template_def = json.load(f)
                    if template_def.get("name") == name:
                        return template_file
                except Exception:
                    pass

        if source in ("all", "custom"):
            for template_file in self._user_template_dir.glob("*.json"):
                try:
                    with open(template_file, "r") as f:
                        template_def = json.load(f)
                    if template_def.get("name") == name:
                        return template_file
                except Exception:
                    pass

        return None

    def save_template(self, template_def: Dict, name: Optional[str] = None) -> bool:
        """
        Save a template to the user templates directory.

        Args:
            template_def: Template definition dict
            name: Optional custom filename (without .json). Uses template name if not provided.

        Returns:
            True if successful
        """
        if not self._user_template_dir.exists():
            self._user_template_dir.mkdir(parents=True, exist_ok=True)

        # Determine filename
        if name is None:
            name = template_def.get("name", "template").replace(" ", "_")

        # Add .json extension if needed
        if not name.endswith(".json"):
            name = f"{name}.json"

        # Ensure filename is safe
        name = os.path.basename(name)  # Remove any path components

        template_path = self._user_template_dir / name

        try:
            with open(template_path, "w") as f:
                json.dump(template_def, f, indent=2)
            logger.info(f"Template saved to {template_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False

    def delete_template(self, name: str) -> bool:
        """
        Delete a user template.

        Args:
            name: Template name or filename

        Returns:
            True if successful
        """
        template_path = self._find_template_file(name, source="custom")

        if not template_path:
            logger.warning(f"Template not found: {name}")
            return False

        try:
            template_path.unlink()
            logger.info(f"Template deleted: {template_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False

    def clone_template(self, source_name: str, target_name: str) -> bool:
        """
        Clone a built-in template to user templates.

        Args:
            source_name: Name of template to clone
            target_name: Name for the cloned template

        Returns:
            True if successful
        """
        template_def = self.load_template(source_name, source="built-in")

        if not template_def:
            logger.warning(f"Source template not found: {source_name}")
            return False

        # Update name in cloned template
        template_def["name"] = target_name

        return self.save_template(template_def, name=target_name)


# Global instance
_manager = None


def get_template_manager() -> TemplateManager:
    """Get or create the global template manager instance."""
    global _manager
    if _manager is None:
        _manager = TemplateManager()
    return _manager
