"""
Frozen-app entry point for the standalone Reductus desktop build.

PyInstaller bundles this module as the executable's entry point. It mirrors the
`reductus desktop` subcommand (see reductus/web_gui/run.py::_run_desktop) but
with fixed defaults, so double-clicking the .exe launches the native window with
no arguments.
"""
import multiprocessing
import sys


def main():
    # Required so a frozen build doesn't re-spawn the whole app if any
    # dependency uses multiprocessing under the hood.
    multiprocessing.freeze_support()

    from reductus.dataflow.configure import load_config
    from reductus.desktop import run_desktop

    # Default configuration (fallback to built-in defaults if no named config).
    config = load_config(name="config", fallback=True)

    print("Starting Reductus desktop app on port 8002...")
    print("Close the window to exit.")
    run_desktop(config, port=8002, debug=False)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        # Keep the console open on error when launched with a console so the
        # user can read the traceback (only relevant for console=True builds).
        if sys.stdout and sys.stdout.isatty():
            input("Press Enter to exit...")
        sys.exit(1)
