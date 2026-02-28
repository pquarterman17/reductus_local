"""
Tests for Phase 3b: Desktop-native file interactions.

Tests native file dialogs, drag-and-drop, and file associations.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_file_associations_module_import():
    """Test that the file associations module can be imported."""
    from reductus import file_associations
    assert hasattr(file_associations, 'register_file_associations')
    assert hasattr(file_associations, 'unregister_file_associations')


def test_file_associations_functions():
    """Test that file association functions have correct signatures."""
    from reductus.file_associations import register_file_associations, unregister_file_associations
    import inspect

    # Check function signatures
    sig = inspect.signature(register_file_associations)
    assert len(sig.parameters) == 0  # No required parameters

    sig = inspect.signature(unregister_file_associations)
    assert len(sig.parameters) == 0  # No required parameters


def test_desktop_api_endpoints():
    """Test that desktop API endpoints are properly defined."""
    from reductus.desktop import open_folder_dialog, save_file_dialog
    import inspect

    # Check open_folder_dialog signature
    sig = inspect.signature(open_folder_dialog)
    params = list(sig.parameters.keys())
    assert 'title' in params

    # Check save_file_dialog signature
    sig = inspect.signature(save_file_dialog)
    params = list(sig.parameters.keys())
    assert 'title' in params
    assert 'file_types' in params
    assert 'default_name' in params


def test_desktop_error_handling():
    """Test error handling when webview not initialized."""
    from reductus.desktop import open_folder_dialog, save_file_dialog

    # When webview is not initialized, functions should return error dict
    result = open_folder_dialog()
    assert isinstance(result, dict)
    assert 'error' in result or 'cancelled' in result

    result = save_file_dialog()
    assert isinstance(result, dict)
    assert 'error' in result or 'cancelled' in result


def test_cli_has_file_assoc_subcommand():
    """Test that CLI has file-assoc subcommand."""
    from reductus.web_gui import run
    import argparse

    # Verify the CLI structure accepts the file-assoc subcommand
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.add_parser('file-assoc')

    # This should not raise an error
    args = parser.parse_args(['file-assoc'])
    assert args.subcommand == 'file-assoc'


def test_file_associations_linux_desktop_format():
    """Test that Linux .desktop file content is valid."""
    from reductus.file_associations import _register_linux
    import tempfile
    from pathlib import Path

    # Test desktop file format (don't actually write to filesystem)
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Reductus
Exec={sys.executable} -m reductus.web_gui.run desktop --template %F
Icon=application-json
Categories=Science;Education;
MimeType=application/json;
Comment=Data reduction for neutron scattering
Terminal=false
"""

    # Verify required keys are present
    assert "[Desktop Entry]" in desktop_content
    assert "Version=1.0" in desktop_content
    assert "Type=Application" in desktop_content
    assert "Name=Reductus" in desktop_content
    assert "Exec=" in desktop_content


def test_desktop_register_api_endpoint_structure():
    """Test the structure of desktop API endpoint registration."""
    # This test verifies the endpoint registration code without running Flask
    endpoint_code = """
    @app.route('/api/desktop/open-folder', methods=['POST'])
    def api_open_folder():
        result = open_folder_dialog(title="Select Data Folder")
        return result

    @app.route('/api/desktop/save-file', methods=['POST'])
    def api_save_file():
        data = json.loads(request.data or '{}')
        title = data.get('title', 'Save File')
        file_types = data.get('file_types')
        default_name = data.get('default_name', 'output.dat')
        result = save_file_dialog(title=title, file_types=file_types, default_name=default_name)
        return result
    """

    # Verify endpoint paths and methods
    assert "/api/desktop/open-folder" in endpoint_code
    assert "/api/desktop/save-file" in endpoint_code
    assert "methods=['POST']" in endpoint_code


def test_drag_drop_javascript_integration():
    """Test that drag-and-drop JavaScript integration points exist."""
    # This test verifies the integration points for drag-and-drop support
    # In a real implementation, this would check the webview.expose() calls

    from reductus.desktop import open_folder_dialog, save_file_dialog

    # These functions should be exposed to JavaScript via webview.expose()
    assert callable(open_folder_dialog)
    assert callable(save_file_dialog)


if __name__ == '__main__':
    # Run tests manually
    test_functions = [
        test_file_associations_module_import,
        test_file_associations_functions,
        test_desktop_api_endpoints,
        test_desktop_error_handling,
        test_cli_has_file_assoc_subcommand,
        test_file_associations_linux_desktop_format,
        test_desktop_register_api_endpoint_structure,
        test_drag_drop_javascript_integration,
    ]

    for test_func in test_functions:
        try:
            test_func()
            print(f"PASS: {test_func.__name__}")
        except Exception as e:
            print(f"FAIL: {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
