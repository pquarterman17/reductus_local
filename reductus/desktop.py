"""
Desktop application wrapper using pywebview.

This module wraps the Flask web UI in a native desktop window,
providing a native application experience without Electron.

Features:
- Native file dialogs (open folder, save file)
- Drag-and-drop support
- File associations

Usage:
    from reductus.desktop import run_desktop
    run_desktop(config, port=8002)
"""

import os
import sys
import threading
import time
import logging
import json

logger = logging.getLogger(__name__)

# Global reference to the webview window (set after window creation)
_webview_window = None


def set_webview_window(window):
    """Set the global webview window reference for file dialogs."""
    global _webview_window
    _webview_window = window


def run_desktop(config, port=8002, debug=False):
    """
    Run the Reductus web UI in a native desktop window using pywebview.

    Args:
        config: Configuration dict (same as Flask app expects)
        port: Port to run Flask server on (default: 8002)
        debug: Enable debug mode for Flask

    Returns:
        None (blocks until window is closed)

    Raises:
        ImportError: If pywebview is not installed
    """
    try:
        import webview
    except ImportError:
        print("Error: pywebview is required for desktop mode.")
        print("Install it with: pip install reductus[desktop]")
        sys.exit(1)

    # Create and start Flask app in a background thread
    from reductus.web_gui.server_flask import create_app

    app = create_app(config)

    # Register desktop API endpoints
    _register_desktop_api(app)

    server_thread = threading.Thread(
        target=lambda: app.run(
            port=port,
            host='127.0.0.1',
            debug=debug,
            use_reloader=False,  # Disable reloader in webview
        ),
        daemon=True,
    )
    server_thread.start()

    # Give the server a moment to start
    time.sleep(1)

    # Create and show webview window
    url = f"http://127.0.0.1:{port}"

    try:
        window = webview.create_window(
            title='Reductus',
            url=url,
            width=1200,
            height=800,
        )

        # Store window reference for file dialogs
        set_webview_window(window)

        # Enable drag-and-drop
        window.expose(open_folder_dialog, save_file_dialog)

        webview.start()
    except Exception as e:
        logger.error(f"Failed to start webview: {e}")
        raise


def _register_desktop_api(app):
    """
    Register desktop-specific API endpoints with the Flask app.

    These endpoints bridge the web UI and native file dialogs.

    Args:
        app: Flask application instance
    """
    @app.route('/api/desktop/open-folder', methods=['POST'])
    def api_open_folder():
        """Open folder dialog endpoint."""
        result = open_folder_dialog(title="Select Data Folder")
        return result

    @app.route('/api/desktop/save-file', methods=['POST'])
    def api_save_file():
        """Save file dialog endpoint."""
        data = {}
        try:
            data = json.loads(__import__('flask').request.data or '{}')
        except Exception:
            pass

        title = data.get('title', 'Save File')
        file_types = data.get('file_types')
        default_name = data.get('default_name', 'output.dat')

        result = save_file_dialog(title=title, file_types=file_types, default_name=default_name)
        return result


def open_folder_dialog(title="Select Folder"):
    """
    Show native 'Open Folder' dialog.

    Args:
        title: Dialog title

    Returns:
        dict: {"path": str} or {"error": str} if cancelled/failed
    """
    if _webview_window is None:
        return {"error": "Webview window not initialized"}

    try:
        result = _webview_window.create_file_dialog(
            dialog_type='folder',
            title=title,
            allow_multiple=False,
        )
        if result:
            return {"path": result[0]}
        else:
            return {"cancelled": True}
    except Exception as e:
        logger.error(f"File dialog error: {e}")
        return {"error": str(e)}


def save_file_dialog(title="Save File", file_types=None, default_name="output.dat"):
    """
    Show native 'Save File' dialog.

    Args:
        title: Dialog title
        file_types: List of tuples: [("Data Files", "*.dat"), ("All Files", "*.*")]
        default_name: Default filename

    Returns:
        dict: {"path": str} or {"error": str} if cancelled/failed
    """
    if _webview_window is None:
        return {"error": "Webview window not initialized"}

    if file_types is None:
        file_types = [("Data Files", "*.dat"), ("All Files", "*.*")]

    try:
        result = _webview_window.create_file_dialog(
            dialog_type='save',
            title=title,
            file_types=file_types,
            save_filename=default_name,
        )
        if result:
            return {"path": result}
        else:
            return {"cancelled": True}
    except Exception as e:
        logger.error(f"File dialog error: {e}")
        return {"error": str(e)}


def run_desktop_cli(args):
    """
    CLI entry point for desktop mode.

    Args:
        args: Parsed arguments from argparse
    """
    from reductus.dataflow.configure import load_config

    # Load configuration
    if args.config_file is not None:
        config = json.loads(open(args.config_file, 'rt').read())
    else:
        config = load_config(name="config", fallback=True)

    # CLI overrides (highest priority)
    if args.instruments is not None:
        config["instruments"] = args.instruments
    if args.cache_engine is not None:
        config.setdefault("cache", {})
        config["cache"]["engine"] = args.cache_engine

    # Inject --data-dir entries
    if args.data_dirs:
        existing_names = {s["name"] for s in config.get("data_sources", [])}
        for raw_path in args.data_dirs:
            path = os.path.abspath(raw_path)
            name = os.path.basename(path.rstrip("/\\")) or raw_path
            if name not in existing_names:
                config.setdefault("data_sources", []).append({
                    "name": name,
                    "url": "file:///",
                    "start_path": path.replace("\\", "/"),
                })
                existing_names.add(name)

    # Run desktop app
    print(f"Starting Reductus desktop app on port {args.port}...")
    print("Close the window to exit.")
    run_desktop(config, port=args.port, debug=args.debug)
