from flask import Blueprint, request, jsonify, g
from services.meeting_service import MeetingService
from services.activity_service import ActivityService
from services.project_service import ProjectService
from services.manager_notification_service import ManagerNotificationService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/meetings... and /api/projects/<project_id>/meetings
meetings_bp = Blueprint("meetings", __name__)

meeting_service = MeetingService()
activity_service = ActivityService()
project_service = ProjectService()
manager_notification_service = ManagerNotificationService()


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
@require_roles("MANAGER", "BUILDING_COMPANY")
def create_meeting(project_id):
    """Create a meeting under a project. project_id comes only from the URL.

    A BUILDING_COMPANY caller may only create a meeting for a project it owns
    (project.building_company_id must match the authenticated user); this is
    checked here since the URL project_id alone cannot be trusted. MANAGER
    behavior is unchanged — no ownership check is performed for that role.
    """
    if g.current_role == "BUILDING_COMPANY":
        try:
            project = project_service.get_by_id(project_id)
        except ServiceError as e:
            return jsonify({"error": e.message}), e.status
        if str(project.get("building_company_id")) != str(g.current_user_id):
            return jsonify({"error": "Forbidden: you do not own this project."}), 403

    data = request.get_json(silent=True)
    try:
        created = meeting_service.create(project_id, data)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    actor = activity_service.resolve_actor(g.current_user_id, g.current_role)
    label = created.get("title") or "a meeting"
    activity_service.record_event(project_id, actor, "meeting_scheduled", f"scheduled {label}")

    # Notify the project's assigned manager when a Building Company schedules a
    # meeting on their behalf. Best-effort (record() never raises) so a
    # notification failure can never undo the already-created meeting above.
    # The recipient is resolved server-side from the project's own
    # project_manager_id — the caller's request body is never trusted for
    # notification routing. A MANAGER creating their own meeting does not
    # notify themselves.
    if g.current_role == "BUILDING_COMPANY":
        manager_id = manager_notification_service.resolve_project_manager_id(project_id)
        if manager_id:
            purpose = (created.get("purpose") or "").strip()
            message = (
                f"A new meeting was scheduled: {purpose}"
                if purpose
                else "A new meeting was scheduled for your project."
            )
            manager_notification_service.record(
                manager_id, project_id, "meeting", "New meeting scheduled", message
            )

    return jsonify(created), 201


@meetings_bp.route("/api/meetings/<meeting_id>", methods=["PUT"])
@require_auth
@require_roles("MANAGER")
def update_meeting(meeting_id):
    """Update a meeting (including approve/reject via status). The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        updated = meeting_service.update(meeting_id, data)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    actor = activity_service.resolve_actor(g.current_user_id, g.current_role)
    label = updated.get("title") or "a meeting"
    activity_service.record_event(updated.get("project_id"), actor, "meeting_updated", f"updated {label}")
    return jsonify(updated), 200


@meetings_bp.route("/api/meetings/<meeting_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER")
def delete_meeting(meeting_id):
    """Delete a meeting by meeting_id."""
    try:
        return jsonify(meeting_service.delete(meeting_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
