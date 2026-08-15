from flask import Blueprint, request, jsonify, g
from services.progress_service import ProgressService
from services.activity_service import ActivityService
from services.manager_notification_service import ManagerNotificationService
from services.project_service import ProjectService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/progress... and /api/projects/<project_id>/progress
progress_bp = Blueprint("progress", __name__)

progress_service = ProgressService()
activity_service = ActivityService()
manager_notification_service = ManagerNotificationService()
project_service = ProjectService()


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
    """Update a progress record. The id comes only from the URL.

    A BUILDING_COMPANY caller may only update a progress record belonging to
    a project it owns (project.building_company_id must match the
    authenticated user); this is checked here since the progress_id alone
    cannot be trusted. MANAGER behavior is unchanged — no ownership check is
    performed for that role.
    """
    if g.current_role == "BUILDING_COMPANY":
        try:
            existing = progress_service.get_by_id(progress_id)
            project = project_service.get_by_id(existing.get("project_id"))
        except ServiceError as e:
            return jsonify({"error": e.message}), e.status
        if str(project.get("building_company_id")) != str(g.current_user_id):
            return jsonify({"error": "Forbidden: you do not own this project."}), 403

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

    # Notify the project's Building Company when a MANAGER updates progress.
    # Best-effort (record() never raises) so a notification failure can never
    # undo the already-successful progress update above. The recipient is
    # resolved server-side from the project's own building_company_id — never
    # trusted from the request. A BUILDING_COMPANY updating its own project's
    # progress through this same route does not notify itself.
    if g.current_role == "MANAGER":
        company_id = manager_notification_service.resolve_project_building_company_id(
            updated.get("project_id")
        )
        if company_id:
            manager_notification_service.record(
                company_id,
                updated.get("project_id"),
                "construction",
                f"Stage updated: {stage_name}",
                message,
            )
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
