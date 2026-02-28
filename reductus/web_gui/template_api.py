"""
API endpoints for template management.

Provides REST endpoints for:
- Listing templates
- Loading templates
- Saving templates
- Deleting templates
- Cloning templates
"""

import json
from flask import request, jsonify
from reductus.template_manager import get_template_manager


def register_template_api(app):
    """
    Register template management endpoints with Flask app.

    Args:
        app: Flask application instance
    """
    manager = get_template_manager()

    @app.route('/api/templates/list', methods=['GET'])
    def api_list_templates():
        """List available templates."""
        category = request.args.get('category', 'all')
        try:
            templates = manager.list_templates(category=category)
            return jsonify(templates)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/templates/load', methods=['GET', 'POST'])
    def api_load_template():
        """Load a template by name."""
        if request.method == 'POST':
            data = request.json or {}
            name = data.get('name')
            source = data.get('source', 'all')
        else:
            name = request.args.get('name')
            source = request.args.get('source', 'all')

        if not name:
            return jsonify({"error": "Template name required"}), 400

        try:
            template = manager.load_template(name, source=source)
            if template:
                return jsonify({"template": template})
            else:
                return jsonify({"error": "Template not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/templates/save', methods=['POST'])
    def api_save_template():
        """Save a template."""
        data = request.json or {}
        template_def = data.get('template')
        name = data.get('name')

        if not template_def:
            return jsonify({"error": "Template definition required"}), 400

        try:
            success = manager.save_template(template_def, name=name)
            if success:
                return jsonify({"success": True, "message": "Template saved"})
            else:
                return jsonify({"error": "Failed to save template"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/templates/delete', methods=['POST'])
    def api_delete_template():
        """Delete a template."""
        data = request.json or {}
        name = data.get('name')

        if not name:
            return jsonify({"error": "Template name required"}), 400

        try:
            success = manager.delete_template(name)
            if success:
                return jsonify({"success": True, "message": "Template deleted"})
            else:
                return jsonify({"error": "Template not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/templates/clone', methods=['POST'])
    def api_clone_template():
        """Clone a template."""
        data = request.json or {}
        source_name = data.get('source_name')
        target_name = data.get('target_name')

        if not source_name or not target_name:
            return jsonify({"error": "Source and target names required"}), 400

        try:
            success = manager.clone_template(source_name, target_name)
            if success:
                return jsonify({"success": True, "message": "Template cloned"})
            else:
                return jsonify({"error": "Failed to clone template"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
