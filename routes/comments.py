from flask import Blueprint, request, jsonify, g
from services.comment_service import CommentService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/comments... and /api/projects/<project_id>/comments
comments_bp = Blueprint("comments", __name__)

comment_service = CommentService()


@comments_bp.route("/api/comments", methods=["GET"])
def get_all_comments():
    """List all comments (across all projects)."""
    try:
        return jsonify(comment_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@comments_bp.route("/api/comments/<comment_id>", methods=["GET"])
def get_comment(comment_id):
    """Get a single comment by comment_id."""
    try:
        return jsonify(comment_service.get_by_id(comment_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@comments_bp.route("/api/projects/<project_id>/comments", methods=["GET"])
def get_project_comments(project_id):
    """List all comments for a single project."""
    try:
        return jsonify(comment_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@comments_bp.route("/api/projects/<project_id>/comments", methods=["POST"])
@require_auth
@require_roles("TENANT", "MANAGER", "BUILDING_COMPANY")
def create_comment(project_id):
    """Create a comment under a project. project_id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(comment_service.create(project_id, g.current_user_id, data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@comments_bp.route("/api/comments/<comment_id>", methods=["PUT"])
@require_auth
@require_roles("TENANT", "MANAGER", "BUILDING_COMPANY")
def update_comment(comment_id):
    """Update a comment. The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(comment_service.update(comment_id, data, g.current_user_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@comments_bp.route("/api/comments/<comment_id>", methods=["DELETE"])
@require_auth
@require_roles("TENANT", "MANAGER", "BUILDING_COMPANY")
def delete_comment(comment_id):
    """Delete a comment by comment_id."""
    try:
        return jsonify(comment_service.delete(comment_id, g.current_user_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
