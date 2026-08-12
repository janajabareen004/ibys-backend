from flask import Blueprint, request, jsonify, g
from services.progress_service import ProgressService
from services.activity_service import ActivityService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/progress... and /api/projects/<project_id>/progress
progress_bp = Blueprint("progress", __name__)

progress_service = ProgressService()
activity_service = ActivityService()


@progress_bp.route("/api/progress", methods=["GET"])
def get_all_progress():
    """List all progress records (across all projects)."""
    try:
        return jsonify(progress_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@progress_bp.route("/api/progress/<progress_id>", methods=["GET"])
def get_progress(progress_id):
    """Get a single progress record by progress_id."""
    try:
        return jsonify(progress_service.get_by_id(progress_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@progress_bp.route("/api/projects/<project_id>/progress", methods=["GET"])
def get_project_progress(project_id):
    """List all progress records for a single project."""
    try:
        return jsonify(progress_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@progress_bp.route("/api/projects/<project_id>/progress", methods=["POST"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def create_progress(project_id):
    """Create a progress record under a project. project_id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(progress_service.create(project_id, data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@progress_bp.route("/api/progress/<progress_id>", methods=["PUT"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def update_progress(progress_id):
    """Update a progress record. The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        updated = progress_service.update(progress_id, data)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    actor = activity_service.resolve_actor(g.current_user_id, g.current_role)
    stage_name = updated.get("task_name") or "a stage"
    status = updated.get("status")
    message = f"updated {stage_name}" + (f" to {status}" if status else "")
    activity_service.record_event(updated.get("project_id"), actor, "stage_updated", message)
    return jsonify(updated), 200


@progress_bp.route("/api/progress/<progress_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def delete_progress(progress_id):
    """Delete a progress record by progress_id."""
    try:
        return jsonify(progress_service.delete(progress_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
