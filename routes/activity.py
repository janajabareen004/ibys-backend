from flask import Blueprint, jsonify
from services.activity_service import ActivityService
from services.errors import ServiceError
from services.auth_guard import require_auth

# This Blueprint uses full explicit paths because its routes span both
# /api/activity and /api/projects/<project_id>/activity.
# The Activity Log is server-generated and READ-ONLY: no create/update/delete
# endpoints are exposed to the frontend.
activity_bp = Blueprint("activity", __name__)

activity_service = ActivityService()


@activity_bp.route("/api/activity", methods=["GET"])
@require_auth
def get_all_activity():
    """List all activity events, newest first. Manager scoping is applied client-side."""
    try:
        return jsonify(activity_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@activity_bp.route("/api/projects/<project_id>/activity", methods=["GET"])
@require_auth
def get_project_activity(project_id):
    """List activity events for a single project, newest first."""
    try:
        return jsonify(activity_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
