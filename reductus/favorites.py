"""
File browser favorites/bookmarks management.

Enables users to pin frequently-accessed directories for quick navigation.

Storage: ~/.local/share/reductus/favorites.json (Windows: %APPDATA%/reductus/...)
"""

import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class FavoritesManager:
    """Manages pinned/favorite directories for quick access."""

    def __init__(self):
        """Initialize favorites manager."""
        self._favorites_file = self._get_favorites_file()

    @staticmethod
    def _get_favorites_file() -> Path:
        """Get path to favorites.json file."""
        from reductus.userdata import get_user_data_dir

        favorites_file = get_user_data_dir() / "favorites.json"
        return favorites_file

    def _load_favorites(self) -> Dict[str, List[Dict]]:
        """Load favorites from file."""
        if not self._favorites_file.exists():
            return {"directories": []}

        try:
            with open(self._favorites_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load favorites: {e}")
            return {"directories": []}

    def _save_favorites(self, data: Dict) -> bool:
        """Save favorites to file."""
        try:
            self._favorites_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._favorites_file, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except OSError as e:
            logger.error(f"Failed to save favorites: {e}")
            return False

    def list_favorites(self) -> List[Dict]:
        """
        List all pinned directories.

        Returns:
            List of favorites: [{"path": str, "name": str, "icon": str}, ...]
        """
        data = self._load_favorites()
        return data.get("directories", [])

    def add_favorite(self, path: str, name: Optional[str] = None) -> bool:
        """
        Pin a directory as a favorite.

        Args:
            path: Absolute path to directory
            name: Display name (auto-generated from path if not provided)

        Returns:
            True if successful
        """
        # Normalize path
        path = os.path.abspath(path).replace("\\", "/")

        if not os.path.isdir(path):
            logger.warning(f"Not a directory: {path}")
            return False

        # Generate name if not provided
        if not name:
            name = os.path.basename(path.rstrip("/\\")) or path

        # Check if already exists
        data = self._load_favorites()
        for fav in data.get("directories", []):
            if fav["path"] == path:
                logger.info(f"Favorite already exists: {path}")
                return True  # Already pinned, consider it success

        # Add new favorite
        favorite = {
            "path": path,
            "name": name,
            "icon": "folder"  # Default icon
        }
        data.setdefault("directories", []).append(favorite)

        logger.info(f"Added favorite: {name} -> {path}")
        return self._save_favorites(data)

    def remove_favorite(self, path: str) -> bool:
        """
        Unpin a favorite directory.

        Args:
            path: Absolute path to directory

        Returns:
            True if successful
        """
        path = os.path.abspath(path).replace("\\", "/")

        data = self._load_favorites()
        original_count = len(data.get("directories", []))

        data["directories"] = [
            fav for fav in data.get("directories", [])
            if fav["path"] != path
        ]

        if len(data["directories"]) < original_count:
            logger.info(f"Removed favorite: {path}")
            return self._save_favorites(data)

        logger.warning(f"Favorite not found: {path}")
        return False

    def reorder_favorites(self, order: List[int]) -> bool:
        """
        Reorder favorites by index.

        Args:
            order: List of indices in new order

        Returns:
            True if successful
        """
        data = self._load_favorites()
        directories = data.get("directories", [])

        if len(order) != len(directories):
            logger.warning("Invalid order length")
            return False

        try:
            data["directories"] = [directories[i] for i in order]
            return self._save_favorites(data)
        except (IndexError, TypeError) as e:
            logger.error(f"Failed to reorder: {e}")
            return False


class ExportHistoryManager:
    """Tracks export/save locations for quick access."""

    def __init__(self):
        """Initialize export history manager."""
        self._history_file = self._get_history_file()

    @staticmethod
    def _get_history_file() -> Path:
        """Get path to export_history.json file."""
        from reductus.userdata import get_user_data_dir

        history_file = get_user_data_dir() / "export_history.json"
        return history_file

    def _load_history(self) -> Dict[str, List[Dict]]:
        """Load export history from file."""
        if not self._history_file.exists():
            return {"locations": [], "default_location": None}

        try:
            with open(self._history_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load export history: {e}")
            return {"locations": [], "default_location": None}

    def _save_history(self, data: Dict) -> bool:
        """Save export history to file."""
        try:
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._history_file, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except OSError as e:
            logger.error(f"Failed to save export history: {e}")
            return False

    def get_recent_exports(self, limit: int = 10) -> List[Dict]:
        """
        Get recent export locations.

        Args:
            limit: Maximum number to return

        Returns:
            List of locations: [{"path": str, "timestamp": float}, ...]
        """
        data = self._load_history()
        locations = data.get("locations", [])
        return sorted(locations, key=lambda x: x.get("timestamp", 0), reverse=True)[:limit]

    def add_export_location(self, path: str) -> bool:
        """
        Record an export location.

        Args:
            path: Directory where data was exported

        Returns:
            True if successful
        """
        import time

        path = os.path.abspath(path).replace("\\", "/")

        if not os.path.isdir(path):
            logger.warning(f"Not a directory: {path}")
            return False

        data = self._load_history()
        locations = data.get("locations", [])

        # Remove if already exists (to move it to top)
        locations = [loc for loc in locations if loc["path"] != path]

        # Add at beginning with timestamp
        locations.insert(0, {
            "path": path,
            "timestamp": time.time()
        })

        # Keep only last 50 locations
        data["locations"] = locations[:50]

        logger.info(f"Recorded export location: {path}")
        return self._save_history(data)

    def get_default_export_location(self) -> Optional[str]:
        """
        Get default export location (last used or configured).

        Returns:
            Path or None if not set
        """
        data = self._load_history()
        return data.get("default_location")

    def set_default_export_location(self, path: str) -> bool:
        """
        Set default export location.

        Args:
            path: Directory to use as default

        Returns:
            True if successful
        """
        path = os.path.abspath(path).replace("\\", "/")

        if not os.path.isdir(path):
            logger.warning(f"Not a directory: {path}")
            return False

        data = self._load_history()
        data["default_location"] = path

        logger.info(f"Set default export location: {path}")
        return self._save_history(data)


# Global instances
_favorites_manager = None
_export_history_manager = None


def get_favorites_manager() -> FavoritesManager:
    """Get or create global favorites manager."""
    global _favorites_manager
    if _favorites_manager is None:
        _favorites_manager = FavoritesManager()
    return _favorites_manager


def get_export_history_manager() -> ExportHistoryManager:
    """Get or create global export history manager."""
    global _export_history_manager
    if _export_history_manager is None:
        _export_history_manager = ExportHistoryManager()
    return _export_history_manager
