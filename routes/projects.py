from flask import Blueprint, request, jsonify
from services.project_service import ProjectService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# All routes here are prefixed with /api/projects
projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")

project_service = ProjectService()


@projects_bp.route("", methods=["GET"])
def get_projects():
    """List all projects."""
    try:
        return jsonify(project_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@projects_bp.route("/<project_id>", methods=["GET"])
def get_project(project_id):
    """Get a single project by project_id."""
    try:
        return jsonify(project_service.get_by_id(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@projects_bp.route("", methods=["POST"])
@require_auth
@require_roles("MANAGER")
def create_project():
    """Create a new project."""
    data = request.get_json(silent=True)
    try:
        return jsonify(project_service.create(data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@projects_bp.route("/<project_id>", methods=["PUT"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def update_project(project_id):
    """Update an existing project. The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(project_service.update(project_id, data)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@projects_bp.route("/<project_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER")
def delete_project(project_id):
    """Delete a project by project_id."""
    try:
        return jsonify(project_service.delete(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
