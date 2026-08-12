from flask import Blueprint, request, jsonify, g
from services.team_service import TeamService
from services.activity_service import ActivityService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/team... and /api/projects/<project_id>/team
team_bp = Blueprint("team", __name__)

team_service = TeamService()
activity_service = ActivityService()


@team_bp.route("/api/team", methods=["GET"])
@require_auth
def get_all_team():
    """List all team members. Manager scoping is applied client-side."""
    try:
        return jsonify(team_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@team_bp.route("/api/team/<member_id>", methods=["GET"])
@require_auth
def get_team_member(member_id):
    """Get a single team member by member_id."""
    try:
        return jsonify(team_service.get_by_id(member_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@team_bp.route("/api/projects/<project_id>/team", methods=["GET"])
@require_auth
def get_project_team(project_id):
    """List all team members for a single project."""
    try:
        return jsonify(team_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@team_bp.route("/api/projects/<project_id>/team", methods=["POST"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def create_team_member(project_id):
    """Create a team member under a project. project_id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        created = team_service.create(project_id, data)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    actor = activity_service.resolve_actor(g.current_user_id, g.current_role)
    # No dedicated "member added" type in the frontend enum; use note_added.
    activity_service.record_event(
        project_id, actor, "note_added",
        f"added team member {created.get('name', '')}".strip(),
    )
    return jsonify(created), 201


@team_bp.route("/api/team/<member_id>", methods=["PUT", "PATCH"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def update_team_member(member_id):
    """Update a team member (full PUT or partial PATCH). The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(team_service.update(member_id, data)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@team_bp.route("/api/team/<member_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def delete_team_member(member_id):
    """Delete a team member by member_id."""
    try:
        return jsonify(team_service.delete(member_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
