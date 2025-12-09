"""
Kanban board API endpoints
"""

from flask import Blueprint, request, jsonify
from services.kanban_service import KanbanService
from services.auth_service import AuthService

kanban_bp = Blueprint("kanban", __name__, url_prefix="/api/kanban")


@kanban_bp.route("", methods=["GET"])
def get_all_items():
    """Get all Kanban items grouped by status"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        items = KanbanService.get_all_items()
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kanban_bp.route("", methods=["POST"])
def create_item():
    """Create a new Kanban item"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        item = KanbanService.create_item(data)
        return jsonify({"item": item, "message": "Item created"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kanban_bp.route("/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Get a single Kanban item"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        item = KanbanService.get_item_by_id(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"item": item})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kanban_bp.route("/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """Update a Kanban item"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        item = KanbanService.update_item(item_id, data)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        return jsonify({"item": item, "message": "Item updated"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kanban_bp.route("/<int:item_id>/status", methods=["PUT"])
def update_item_status(item_id):
    """Quick status update for moving items between columns"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        if not data or "status" not in data:
            return jsonify({"error": "Status is required"}), 400

        item = KanbanService.update_status(item_id, data["status"])
        if not item:
            return jsonify({"error": "Item not found"}), 404

        return jsonify({"item": item, "message": "Status updated"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@kanban_bp.route("/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete a Kanban item"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        success = KanbanService.delete_item(item_id)
        if not success:
            return jsonify({"error": "Item not found"}), 404

        return jsonify({"message": "Item deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
