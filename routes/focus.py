"""
Focus/Pomodoro timer API endpoints
"""

from flask import Blueprint, request, jsonify
from services.focus_service import FocusService
from services.auth_service import AuthService

focus_bp = Blueprint("focus", __name__, url_prefix="/api/focus")


@focus_bp.route("/start", methods=["POST"])
def start_session():
    """Start a new focus session"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json() or {}
        session = FocusService.start_session(data)
        return jsonify({"session": session, "message": "Session started"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@focus_bp.route("/complete/<int:session_id>", methods=["POST"])
def complete_session(session_id):
    """Mark a session as completed"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json() or {}
        session = FocusService.complete_session(session_id, data.get("notes"))
        if not session:
            return jsonify({"error": "Session not found"}), 404
        return jsonify({"session": session, "message": "Session completed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@focus_bp.route("/today", methods=["GET"])
def get_today_sessions():
    """Get all sessions from today"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        sessions = FocusService.get_today_sessions()
        return jsonify({"sessions": sessions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@focus_bp.route("/stats", methods=["GET"])
def get_stats():
    """Get focus statistics"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        stats = FocusService.get_stats()
        return jsonify({"stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@focus_bp.route("/<int:session_id>", methods=["DELETE"])
def delete_session(session_id):
    """Delete a focus session"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        FocusService.delete_session(session_id)
        return jsonify({"message": "Session deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@focus_bp.route("/clear-today", methods=["DELETE"])
def clear_today_sessions():
    """Clear all of today's focus sessions"""
    if not AuthService.is_authenticated():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        FocusService.clear_today_sessions()
        return jsonify({"message": "Today's sessions cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
