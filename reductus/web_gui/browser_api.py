"""
API endpoints for file browser and export UX improvements.

Provides REST endpoints for:
- Pinned/favorite directories
- Export history and default location
- Browse suggestions based on recent activity
"""

import logging
from flask import request, jsonify
from reductus.favorites import get_favorites_manager, get_export_history_manager
from reductus.logging_config import get_browser_logger

logger = get_browser_logger()


def register_browser_api(app):
    """
    Register file browser and export endpoints with Flask app.

    Args:
        app: Flask application instance
    """
    favorites = get_favorites_manager()
    export_history = get_export_history_manager()

    # ===== Favorites/Bookmarks Endpoints =====

    @app.route('/api/browser/favorites/list', methods=['GET'])
    def api_list_favorites():
        """List pinned directories."""
        logger.info("API request: list favorites")
        try:
            favorites_list = favorites.list_favorites()
            logger.debug(f"Returning {len(favorites_list)} favorites")
            return jsonify({"favorites": favorites_list})
        except Exception as e:
            logger.error(f"API error in list_favorites: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route('/api/browser/favorites/add', methods=['POST'])
    def api_add_favorite():
        """Pin a directory as favorite."""
        data = request.json or {}
        path = data.get('path')
        name = data.get('name')

        logger.info(f"API request: add favorite", extra={"path": path, "name": name})

        if not path:
            logger.warning("API request missing path parameter")
            return jsonify({"error": "Path required"}), 400

        try:
            success = favorites.add_favorite(path, name=name)
            if success:
                favorites_list = favorites.list_favorites()
                logger.debug(f"Favorite added, returning {len(favorites_list)} total favorites")
                return jsonify({
                    "success": True,
                    "message": "Favorite added",
                    "favorites": favorites_list
                })
            else:
                logger.warning(f"Failed to add favorite: {path}")
                return jsonify({"error": "Failed to add favorite"}), 500
        except Exception as e:
            logger.error(f"API error in add_favorite: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route('/api/browser/favorites/remove', methods=['POST'])
    def api_remove_favorite():
        """Unpin a favorite directory."""
        data = request.json or {}
        path = data.get('path')

        if not path:
            return jsonify({"error": "Path required"}), 400

        try:
            success = favorites.remove_favorite(path)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Favorite removed",
                    "favorites": favorites.list_favorites()
                })
            else:
                return jsonify({"error": "Favorite not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/browser/favorites/reorder', methods=['POST'])
    def api_reorder_favorites():
        """Reorder favorites by index."""
        data = request.json or {}
        order = data.get('order')

        if not order or not isinstance(order, list):
            return jsonify({"error": "Order list required"}), 400

        try:
            success = favorites.reorder_favorites(order)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Favorites reordered",
                    "favorites": favorites.list_favorites()
                })
            else:
                return jsonify({"error": "Failed to reorder"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ===== Export History Endpoints =====

    @app.route('/api/export/recent', methods=['GET'])
    def api_get_recent_exports():
        """Get recent export locations."""
        try:
            limit = request.args.get('limit', default=10, type=int)
            recent = export_history.get_recent_exports(limit=limit)
            return jsonify({"locations": recent})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/export/record', methods=['POST'])
    def api_record_export():
        """Record an export location."""
        data = request.json or {}
        path = data.get('path')

        if not path:
            return jsonify({"error": "Path required"}), 400

        try:
            success = export_history.add_export_location(path)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Export location recorded"
                })
            else:
                return jsonify({"error": "Failed to record location"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/export/default', methods=['GET'])
    def api_get_default_export():
        """Get default export location."""
        try:
            location = export_history.get_default_export_location()
            return jsonify({"default_location": location})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/export/default', methods=['POST'])
    def api_set_default_export():
        """Set default export location."""
        data = request.json or {}
        path = data.get('path')

        if not path:
            return jsonify({"error": "Path required"}), 400

        try:
            success = export_history.set_default_export_location(path)
            if success:
                return jsonify({
                    "success": True,
                    "message": "Default location set",
                    "default_location": path
                })
            else:
                return jsonify({"error": "Failed to set default location"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/browser/suggestions', methods=['GET'])
    def api_get_suggestions():
        """Get suggested directories based on recent activity."""
        try:
            # Combine favorites and recent exports
            favorites_list = favorites.list_favorites()
            recent_exports = export_history.get_recent_exports(limit=5)

            suggestions = {
                "favorites": favorites_list,
                "recent_exports": recent_exports,
                "default_export": export_history.get_default_export_location()
            }
            return jsonify(suggestions)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
