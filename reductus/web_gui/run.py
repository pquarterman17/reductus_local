import os
import argparse
import threading
import requests
import sys


def main():
    """
    Main CLI entry point supporting multiple subcommands.
    Default subcommand is 'gui' (web server).
    """
    parser = argparse.ArgumentParser(
        description='Reductus: data reduction for neutron scattering'
    )
    subparsers = parser.add_subparsers(dest='subcommand', help='subcommand to run')

    # GUI subcommand (default)
    gui_parser = subparsers.add_parser(
        'gui',
        help='start web GUI server (default if no subcommand specified)'
    )
    gui_parser.add_argument('-d', '--debug', action='store_true', help='autoload modules on change')
    gui_parser.add_argument('-x', '--headless', action='store_true', help='do not automatically load client in browser')
    gui_parser.add_argument('--external', action='store_true', help='listen on all interfaces, including external (local connections only if not set)')
    gui_parser.add_argument('-p', '--port', default=8002, type=int, help='port on which to start the server')
    gui_parser.add_argument('-c', '--config-file', type=str, help='path to JSON configuration to load')
    gui_parser.add_argument('-i', '--instruments', nargs='+', help='instruments to load (overrides config)')
    gui_parser.add_argument('--cache-engine', type=str, default='memory', choices=['memory', 'diskcache', 'redis'], help='select cache engine (default is "memory", overrides config)')
    gui_parser.add_argument('--data-dir', dest='data_dirs', action='append', metavar='PATH',
                            help='register a local directory as a named data source (repeatable)')

    # Batch subcommand
    batch_parser = subparsers.add_parser(
        'batch',
        help='run batch reduction without server'
    )
    batch_parser.add_argument('--template', required=True, help='path to template JSON file')
    batch_parser.add_argument('--files', help='glob pattern for data files (e.g., "D:\\Data\\*.nxs")')
    batch_parser.add_argument('--data-dir', help='directory to search for data files')
    batch_parser.add_argument('--glob-pattern', default='**/*', help='glob pattern for files in data_dir (default: "**/*")')
    batch_parser.add_argument('-i', '--instruments', nargs='+', help='instruments to load (overrides config)')
    batch_parser.add_argument('--output', required=True, help='directory to write output files')
    batch_parser.add_argument('--format', default='column', help='export format (default: "column")')
    batch_parser.add_argument('--node', type=int, help='node index to extract results from (default: last node)')
    batch_parser.add_argument('--terminal', default='output', help='output terminal name (default: "output")')

    # Parse arguments
    # If no arguments and no subcommand, default to 'gui' for backward compatibility
    if len(sys.argv) == 1:
        args = parser.parse_args(['gui'])
    else:
        args = parser.parse_args()

    # Default to gui if no subcommand specified
    if args.subcommand is None:
        args.subcommand = 'gui'

    if args.subcommand == 'gui':
        _run_gui(args)
    elif args.subcommand == 'batch':
        _run_batch(args)
    else:
        parser.print_help()


def _run_gui(args):
    """Run the web GUI server."""
    if args.config_file is not None:
        import json
        config = json.loads(open(args.config_file, 'rt').read())
    else:
        from reductus.dataflow.configure import load_config
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

    # Strip "local" from data sources if running external
    if args.external:
        config["data_sources"] = [
            d for d in config.get("data_sources", [])
            if d["name"] != "local"
        ]

    from reductus.web_gui.server_flask import create_app
    app = create_app(config)
    if not args.headless:
        thread = threading.Thread(target=_open_browser_when_server_ready, args=(args.port,))
        thread.start()
    host = '0.0.0.0' if args.external else None
    app.run(port=args.port, host=host, debug=args.debug)


def _run_batch(args):
    """Run batch reduction without server."""
    from reductus import reduce

    print(f"Loading template from {args.template}...")
    template = reduce.load_template(args.template)

    print("Running template...")
    result = template.run(
        files=args.files.split() if args.files else None,
        data_dir=args.data_dir,
        glob_pattern=args.glob_pattern,
        node=args.node,
        terminal=args.terminal,
        instruments=args.instruments,
    )

    print(f"Saving results to {args.output}...")
    result.save(args.output, fmt=args.format)
    print("Done!")

def _open_browser_when_server_ready(port, retry_interval=0.2, max_retries=50):
    # Wait for the server to start
    retry_count = 0
    while retry_count < max_retries:
        try:
            requests.get("http://localhost:%d" % (port), timeout=retry_interval)
            break
        except requests.exceptions.ConnectionError:
            retry_count += 1
    import webbrowser
    webbrowser.open("http://localhost:%d" % (port))

if __name__ == '__main__':
    main()
