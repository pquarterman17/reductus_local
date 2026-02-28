"""
Tests for Phase 4: Template Management.

Tests template discovery, loading, saving, and cloning.
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_template_manager_import():
    """Test that the template manager module can be imported."""
    from reductus.template_manager import TemplateManager, get_template_manager
    assert TemplateManager is not None
    assert get_template_manager is not None


def test_template_manager_initialization():
    """Test template manager initialization."""
    from reductus.template_manager import TemplateManager

    manager = TemplateManager()
    assert manager is not None
    assert manager._user_template_dir is not None
    assert manager._built_in_dir is not None


def test_list_templates():
    """Test listing templates."""
    from reductus.template_manager import get_template_manager

    manager = get_template_manager()
    templates = manager.list_templates()

    assert isinstance(templates, dict)
    assert 'built-in' in templates or 'custom' in templates


def test_extract_template_metadata():
    """Test extracting metadata from a template file."""
    from reductus.template_manager import TemplateManager
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        template_def = {
            "name": "Test Template",
            "description": "A test template",
            "instrument": "test.instrument",
            "version": "1.0",
            "modules": [],
            "wires": []
        }
        json.dump(template_def, f)
        f.flush()
        temp_path = f.name

    try:
        metadata = TemplateManager._extract_metadata(Path(temp_path))
        assert metadata['name'] == "Test Template"
        assert metadata['description'] == "A test template"
        assert metadata['instrument'] == "test.instrument"
    finally:
        os.unlink(temp_path)


def test_save_template():
    """Test saving a template."""
    from reductus.template_manager import TemplateManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = TemplateManager()
        manager._user_template_dir = Path(tmpdir)

        template_def = {
            "name": "My Test Template",
            "description": "A custom template",
            "instrument": "test.refl",
            "modules": [],
            "wires": []
        }

        success = manager.save_template(template_def, name="my_test_template")
        assert success

        # Verify file was created
        saved_file = Path(tmpdir) / "my_test_template.json"
        assert saved_file.exists()

        # Verify content
        with open(saved_file, 'r') as f:
            saved_template = json.load(f)
        assert saved_template['name'] == "My Test Template"


def test_load_template():
    """Test loading a template."""
    from reductus.template_manager import TemplateManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = TemplateManager()
        manager._user_template_dir = Path(tmpdir)

        # Save a template
        template_def = {
            "name": "Load Test Template",
            "description": "Test loading",
            "modules": [],
            "wires": []
        }
        manager.save_template(template_def, name="load_test")

        # Load it back
        loaded = manager.load_template("load_test", source="custom")
        assert loaded is not None
        assert loaded['name'] == "Load Test Template"


def test_clone_template():
    """Test cloning a template."""
    from reductus.template_manager import TemplateManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = TemplateManager()
        manager._user_template_dir = Path(tmpdir)

        # Create a source template in built-in dir
        manager._built_in_dir = Path(tmpdir) / "built-in"
        manager._built_in_dir.mkdir(exist_ok=True)

        source_template = {
            "name": "Source Template",
            "description": "Original template",
            "modules": [],
            "wires": []
        }

        source_file = manager._built_in_dir / "source_template.json"
        with open(source_file, 'w') as f:
            json.dump(source_template, f)

        # Clone it
        success = manager.clone_template("source_template", "cloned_template")
        assert success

        # Verify cloned template exists and has correct name
        cloned = manager.load_template("cloned_template", source="custom")
        assert cloned is not None
        assert cloned['name'] == "cloned_template"


def test_delete_template():
    """Test deleting a template."""
    from reductus.template_manager import TemplateManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = TemplateManager()
        manager._user_template_dir = Path(tmpdir)

        # Save a template
        template_def = {
            "name": "Delete Me",
            "modules": [],
            "wires": []
        }
        manager.save_template(template_def, name="delete_test")

        # Verify it exists
        saved_file = Path(tmpdir) / "delete_test.json"
        assert saved_file.exists()

        # Delete it
        success = manager.delete_template("delete_test")
        assert success
        assert not saved_file.exists()


def test_template_api_endpoints():
    """Test that template API endpoints are properly defined."""
    from reductus.web_gui.template_api import register_template_api
    import inspect

    # Verify the function exists and has correct signature
    sig = inspect.signature(register_template_api)
    params = list(sig.parameters.keys())
    assert 'app' in params


def test_list_custom_templates():
    """Test listing only custom templates."""
    from reductus.template_manager import TemplateManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = TemplateManager()
        manager._user_template_dir = Path(tmpdir)

        # Save some templates
        for i in range(3):
            template_def = {
                "name": f"Custom Template {i}",
                "modules": [],
                "wires": []
            }
            manager.save_template(template_def, name=f"custom_{i}")

        # List custom templates
        custom = manager._list_custom_templates()
        assert len(custom) == 3

        # Verify metadata
        assert all('source' in t for t in custom)
        assert all(t['source'] == 'custom' for t in custom)


def test_find_template_by_name():
    """Test finding templates by display name."""
    from reductus.template_manager import TemplateManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = TemplateManager()
        manager._user_template_dir = Path(tmpdir)

        # Save a template with display name
        template_def = {
            "name": "My Display Name",
            "modules": [],
            "wires": []
        }
        manager.save_template(template_def, name="filename")

        # Find by display name
        path = manager._find_template_file("My Display Name", source="custom")
        assert path is not None
        assert path.name == "filename.json"


if __name__ == '__main__':
    # Run tests manually
    test_functions = [
        test_template_manager_import,
        test_template_manager_initialization,
        test_list_templates,
        test_extract_template_metadata,
        test_save_template,
        test_load_template,
        test_clone_template,
        test_delete_template,
        test_template_api_endpoints,
        test_list_custom_templates,
        test_find_template_by_name,
    ]

    for test_func in test_functions:
        try:
            test_func()
            print(f"PASS: {test_func.__name__}")
        except Exception as e:
            print(f"FAIL: {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
