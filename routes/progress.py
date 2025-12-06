"""
Progress logging API endpoints
"""

from flask import Blueprint, request, jsonify
from database.db import get_db
from services.progress_service import ProgressService
from services.task_service import TaskService

progress_bp = Blueprint("progress", __name__, url_prefix="/api/progress")


@progress_bp.route("/week", methods=["GET"])
def get_week_progress():
    """Get progress for a specific week"""
    try:
        date_str = request.args.get("date")  # YYYY-MM-DD format
        progress = ProgressService.get_week_progress(date_str)
        return jsonify(progress)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@progress_bp.route("", methods=["POST"])
def log_progress():
    """Log a progress entry"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get("task_id"):
            return jsonify({"error": "Task ID is required"}), 400
        if not data.get("date"):
            return jsonify({"error": "Date is required"}), 400

        # Check if task exists
        task = TaskService.get_task_by_id(data["task_id"])
        if task is None:
            return jsonify({"error": "Task not found"}), 404

        # Validate metric value based on task type
        if task["metric_type"] != "BOOLEAN":
            if data.get("value") is None:
                return jsonify({"error": "Value is required for this metric type"}), 400

            # Validate value ranges
            value = float(data["value"])
            if task["metric_type"] == "PROGRESS" and (value < 0 or value > 100):
                return jsonify({"error": "Progress must be between 0 and 100"}), 400
            if task["metric_type"] == "INTENSITY" and (value < 1 or value > 10):
                return jsonify({"error": "Intensity must be between 1 and 10"}), 400
            if value < 0:
                return jsonify({"error": "Value cannot be negative"}), 400

        log = ProgressService.log_progress(data)
        return jsonify({"log": log, "message": "Progress logged successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@progress_bp.route("/<int:log_id>", methods=["PUT"])
def update_progress(log_id):
    """Update a progress entry"""
    try:
        data = request.get_json()
        log = ProgressService.update_progress(log_id, data)
        if log is None:
            return jsonify({"error": "Progress log not found"}), 404
        return jsonify({"log": log, "message": "Progress updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@progress_bp.route("/stats/<int:task_id>", methods=["GET"])
def get_task_stats(task_id):
    """Get statistics for a specific task"""
    try:
        # Check if task exists
        task = TaskService.get_task_by_id(task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404

        stats = ProgressService.get_task_stats(task_id)
        return jsonify({"stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
