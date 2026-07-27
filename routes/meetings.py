from flask import Blueprint, request, jsonify
from services.meeting_service import MeetingService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/meetings... and /api/projects/<project_id>/meetings
meetings_bp = Blueprint("meetings", __name__)

meeting_service = MeetingService()


@meetings_bp.route("/api/meetings", methods=["GET"])
def get_all_meetings():
    """List all meetings (across all projects)."""
    try:
        return jsonify(meeting_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@meetings_bp.route("/api/meetings/<meeting_id>", methods=["GET"])
def get_meeting(meeting_id):
    """Get a single meeting by meeting_id."""
    try:
        return jsonify(meeting_service.get_by_id(meeting_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@meetings_bp.route("/api/projects/<project_id>/meetings", methods=["GET"])
def get_project_meetings(project_id):
    """List all meetings for a single project."""
    try:
        return jsonify(meeting_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@meetings_bp.route("/api/projects/<project_id>/meetings", methods=["POST"])
@require_auth
@require_roles("MANAGER")
def create_meeting(project_id):
    """Create a meeting under a project. project_id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(meeting_service.create(project_id, data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@meetings_bp.route("/api/meetings/<meeting_id>", methods=["PUT"])
@require_auth
@require_roles("MANAGER")
def update_meeting(meeting_id):
    """Update a meeting (including approve/reject via status). The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(meeting_service.update(meeting_id, data)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@meetings_bp.route("/api/meetings/<meeting_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER")
def delete_meeting(meeting_id):
    """Delete a meeting by meeting_id."""
    try:
        return jsonify(meeting_service.delete(meeting_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
