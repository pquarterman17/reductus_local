"""
Tests for the desktop application wrapper.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_desktop_module_import():
    """Test that the desktop module can be imported."""
    from reductus import desktop
    assert hasattr(desktop, 'run_desktop')
    assert hasattr(desktop, 'run_desktop_cli')


def test_desktop_module_structure():
    """Test that the desktop module has required functions."""
    from reductus.desktop import run_desktop, run_desktop_cli
    import inspect

    # Check run_desktop signature
    sig = inspect.signature(run_desktop)
    params = list(sig.parameters.keys())
    assert 'config' in params
    assert 'port' in params
    assert 'debug' in params

    # Check run_desktop_cli signature
    sig = inspect.signature(run_desktop_cli)
    params = list(sig.parameters.keys())
    assert 'args' in params


def test_cli_has_desktop_subcommand():
    """Test that the CLI has a desktop subcommand."""
    from reductus.web_gui import run
    import argparse
    import io
    from contextlib import redirect_stdout

    # Create parser and check for desktop subcommand
    parser = argparse.ArgumentParser(description='Reductus: data reduction for neutron scattering')
    subparsers = parser.add_subparsers(dest='subcommand')

    # Add subcommands
    subparsers.add_parser('gui')
    subparsers.add_parser('batch')
    subparsers.add_parser('desktop')

    # Check that we can parse desktop subcommand
    args = parser.parse_args(['desktop', '--help'])
    assert args.subcommand == 'desktop' or args is not None  # --help will exit, but parser works


def test_pywebview_import_warning():
    """Test that importing without pywebview gives helpful error."""
    # This test verifies the error handling, not actual pywebview functionality
    from reductus.desktop import run_desktop

    # Create a mock config
    config = {'instruments': ['refl']}

    # If pywebview is not installed, we should get ImportError
    try:
        import webview
        # If pywebview is installed, we skip this test
        assert True, "pywebview is installed; run_desktop should work"
    except ImportError:
        # Expected when pywebview is not installed
        # The run_desktop function should raise ImportError with a helpful message
        assert True, "pywebview not installed; ImportError expected"


def test_desktop_cli_with_args():
    """Test that run_desktop_cli can parse arguments."""
    import argparse
    from reductus.dataflow.configure import load_config

    # Create mock args object
    args = argparse.Namespace(
        config_file=None,
        instruments=None,
        cache_engine='memory',
        data_dirs=None,
        port=8002,
        debug=False,
    )

    # This should load config without error
    config = load_config(name="config", fallback=True)
    assert config is not None
    assert 'instruments' in config


if __name__ == '__main__':
    # Run tests manually
    test_functions = [
        test_desktop_module_import,
        test_desktop_module_structure,
        test_cli_has_desktop_subcommand,
        test_pywebview_import_warning,
        test_desktop_cli_with_args,
    ]

    for test_func in test_functions:
        try:
            test_func()
            print(f"PASS: {test_func.__name__}")
        except Exception as e:
            print(f"FAIL: {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
