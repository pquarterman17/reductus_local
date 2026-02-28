"""
Tests for Phase 5: File Browser & Export UX.

Tests favorites management, export history, and browser improvements.
"""

import sys
import os
import json
import tempfile
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_favorites_manager_import():
    """Test that favorites module can be imported."""
    from reductus.favorites import FavoritesManager, get_favorites_manager
    assert FavoritesManager is not None
    assert get_favorites_manager is not None


def test_export_history_manager_import():
    """Test that export history can be imported."""
    from reductus.favorites import ExportHistoryManager, get_export_history_manager
    assert ExportHistoryManager is not None
    assert get_export_history_manager is not None


def test_list_favorites():
    """Test listing favorite directories."""
    from reductus.favorites import FavoritesManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = FavoritesManager()
        manager._favorites_file = Path(tmpdir) / "favorites.json"

        # Initially empty
        favorites = manager.list_favorites()
        assert isinstance(favorites, list)
        assert len(favorites) == 0


def test_add_favorite():
    """Test adding a favorite directory."""
    from reductus.favorites import FavoritesManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test directory
        test_dir = os.path.join(tmpdir, "my_data")
        os.makedirs(test_dir)

        manager = FavoritesManager()
        manager._favorites_file = Path(tmpdir) / "favorites.json"

        # Add favorite
        success = manager.add_favorite(test_dir, name="My Data")
        assert success

        # List and verify
        favorites = manager.list_favorites()
        assert len(favorites) == 1
        assert favorites[0]["name"] == "My Data"
        assert "my_data" in favorites[0]["path"]


def test_remove_favorite():
    """Test removing a favorite directory."""
    from reductus.favorites import FavoritesManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "my_data")
        os.makedirs(test_dir)

        manager = FavoritesManager()
        manager._favorites_file = Path(tmpdir) / "favorites.json"

        # Add then remove
        manager.add_favorite(test_dir, name="My Data")
        success = manager.remove_favorite(test_dir)
        assert success

        # Verify removed
        favorites = manager.list_favorites()
        assert len(favorites) == 0


def test_reorder_favorites():
    """Test reordering favorite directories."""
    from reductus.favorites import FavoritesManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = FavoritesManager()
        manager._favorites_file = Path(tmpdir) / "favorites.json"

        # Add multiple favorites
        for i in range(3):
            test_dir = os.path.join(tmpdir, f"dir_{i}")
            os.makedirs(test_dir)
            manager.add_favorite(test_dir, name=f"Dir {i}")

        # Reorder: reverse the list
        success = manager.reorder_favorites([2, 1, 0])
        assert success

        # Verify reordered
        favorites = manager.list_favorites()
        assert favorites[0]["name"] == "Dir 2"
        assert favorites[2]["name"] == "Dir 0"


def test_export_history():
    """Test tracking export locations."""
    from reductus.favorites import ExportHistoryManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ExportHistoryManager()
        manager._history_file = Path(tmpdir) / "history.json"

        # Create test directories
        for i in range(3):
            export_dir = os.path.join(tmpdir, f"export_{i}")
            os.makedirs(export_dir)

            # Record export with slight delay to ensure different timestamps
            success = manager.add_export_location(export_dir)
            assert success
            time.sleep(0.01)

        # Get recent (should be in reverse order: most recent first)
        recent = manager.get_recent_exports(limit=10)
        assert len(recent) == 3
        assert "export_2" in recent[0]["path"]
        assert "export_0" in recent[2]["path"]


def test_default_export_location():
    """Test setting default export location."""
    from reductus.favorites import ExportHistoryManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ExportHistoryManager()
        manager._history_file = Path(tmpdir) / "history.json"

        # Create test directory
        export_dir = os.path.join(tmpdir, "default_export")
        os.makedirs(export_dir)

        # Set default
        success = manager.set_default_export_location(export_dir)
        assert success

        # Get default
        default = manager.get_default_export_location()
        assert default is not None
        assert "default_export" in default


def test_browser_api_endpoints():
    """Test that browser API endpoints are properly defined."""
    from reductus.web_gui.browser_api import register_browser_api
    import inspect

    sig = inspect.signature(register_browser_api)
    params = list(sig.parameters.keys())
    assert 'app' in params


def test_favorite_persistence():
    """Test that favorites persist across manager instances."""
    from reductus.favorites import FavoritesManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        favorites_file = Path(tmpdir) / "favorites.json"

        # First manager: add favorite
        manager1 = FavoritesManager()
        manager1._favorites_file = favorites_file

        test_dir = os.path.join(tmpdir, "my_data")
        os.makedirs(test_dir)
        manager1.add_favorite(test_dir, name="Test")

        # Second manager: should load the favorite
        manager2 = FavoritesManager()
        manager2._favorites_file = favorites_file

        favorites = manager2.list_favorites()
        assert len(favorites) == 1
        assert favorites[0]["name"] == "Test"


def test_export_history_limit():
    """Test that export history respects limit."""
    from reductus.favorites import ExportHistoryManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ExportHistoryManager()
        manager._history_file = Path(tmpdir) / "history.json"

        # Add 20 locations
        for i in range(20):
            export_dir = os.path.join(tmpdir, f"export_{i}")
            os.makedirs(export_dir, exist_ok=True)
            manager.add_export_location(export_dir)
            time.sleep(0.001)

        # Should keep only 50, but verify the recent call limits properly
        recent = manager.get_recent_exports(limit=5)
        assert len(recent) == 5


def test_favorites_with_special_chars():
    """Test favorites with special characters in paths."""
    from reductus.favorites import FavoritesManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = FavoritesManager()
        manager._favorites_file = Path(tmpdir) / "favorites.json"

        # Create directory with special name
        test_dir = os.path.join(tmpdir, "my data 2024")
        os.makedirs(test_dir)

        # Add favorite
        success = manager.add_favorite(test_dir, name="My Data 2024")
        assert success

        # Load and verify name preserved
        favorites = manager.list_favorites()
        assert favorites[0]["name"] == "My Data 2024"


if __name__ == '__main__':
    # Run tests manually
    test_functions = [
        test_favorites_manager_import,
        test_export_history_manager_import,
        test_list_favorites,
        test_add_favorite,
        test_remove_favorite,
        test_reorder_favorites,
        test_export_history,
        test_default_export_location,
        test_browser_api_endpoints,
        test_favorite_persistence,
        test_export_history_limit,
        test_favorites_with_special_chars,
    ]

    for test_func in test_functions:
        try:
            test_func()
            print(f"PASS: {test_func.__name__}")
        except Exception as e:
            print(f"FAIL: {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
