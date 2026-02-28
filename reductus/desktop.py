"""
Desktop application wrapper using pywebview.

This module wraps the Flask web UI in a native desktop window,
providing a native application experience without Electron.

Usage:
    from reductus.desktop import run_desktop
    run_desktop(config, port=8002)
"""

import os
import sys
import threading
import time
import logging

logger = logging.getLogger(__name__)


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
        webview.start()
    except Exception as e:
        logger.error(f"Failed to start webview: {e}")
        raise


def run_desktop_cli(args):
    """
    CLI entry point for desktop mode.

    Args:
        args: Parsed arguments from argparse
    """
    from reductus.dataflow.configure import load_config

    # Load configuration
    if args.config_file is not None:
        import json
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
