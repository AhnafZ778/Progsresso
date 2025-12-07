"""
Task CRUD API endpoints
"""

from flask import Blueprint, request, jsonify
# from database.db import get_db

from services.task_service import TaskService
from services.auth_service import AuthService

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


@tasks_bp.route("", methods=["GET"])
def get_tasks():
    """List all active tasks"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        tasks = TaskService.get_all_tasks()
        return jsonify({"tasks": tasks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Get a single task by ID"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        task = TaskService.get_task_by_id(task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"task": task})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("", methods=["POST"])
def create_task():
    """Create a new task"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("name"):
            return jsonify({"error": "Task name is required"}), 400
        if not data.get("metric_type"):
            return jsonify({"error": "Metric type is required"}), 400
        if not data.get("frequency"):
            return jsonify({"error": "Frequency is required"}), 400

        # Validate metric_type
        valid_metric_types = ["TIME", "INTENSITY", "PROGRESS", "COUNT", "BOOLEAN"]
        if data["metric_type"] not in valid_metric_types:
            return jsonify(
                {"error": f"Invalid metric type. Must be one of: {valid_metric_types}"}
            ), 400

        # Validate frequency
        valid_frequencies = ["DAILY", "WEEKDAYS", "WEEKENDS", "CUSTOM"]
        if data["frequency"] not in valid_frequencies:
            return jsonify(
                {"error": f"Invalid frequency. Must be one of: {valid_frequencies}"}
            ), 400

        # Validate custom_days if frequency is CUSTOM
        if data["frequency"] == "CUSTOM" and not data.get("custom_days"):
            return jsonify(
                {"error": "Custom days are required for CUSTOM frequency"}
            ), 400

        # Validate metric_unit for non-BOOLEAN types
        if data["metric_type"] != "BOOLEAN" and not data.get("metric_unit"):
            return jsonify(
                {"error": "Metric unit is required for non-BOOLEAN metric types"}
            ), 400

        task = TaskService.create_task(data)
        return jsonify({"task": task, "message": "Task created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update an existing task"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()

        # Check if task exists
        existing = TaskService.get_task_by_id(task_id)
        if existing is None:
            return jsonify({"error": "Task not found"}), 404

        # Don't allow changing metric_type (prevents data inconsistency)
        if "metric_type" in data and data["metric_type"] != existing["metric_type"]:
            return jsonify({"error": "Cannot change metric type of existing task"}), 400

        task = TaskService.update_task(task_id, data)
        return jsonify({"task": task, "message": "Task updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete or archive a task"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json() or {}
        permanent = data.get("permanent", False)

        # Check if task exists
        existing = TaskService.get_task_by_id(task_id)
        if existing is None:
            return jsonify({"error": "Task not found"}), 404

        if permanent:
            TaskService.delete_task(task_id)
            message = "Task permanently deleted"
        else:
            TaskService.archive_task(task_id)
            message = "Task archived"

        return jsonify({"message": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
