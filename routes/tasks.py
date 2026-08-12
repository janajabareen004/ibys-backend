from flask import Blueprint, request, jsonify
from services.task_service import TaskService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/tasks... and /api/projects/<project_id>/tasks
tasks_bp = Blueprint("tasks", __name__)

task_service = TaskService()


@tasks_bp.route("/api/tasks", methods=["GET"])
@require_auth
def get_all_tasks():
    """List all tasks (across all projects). Manager scoping is applied client-side."""
    try:
        return jsonify(task_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@tasks_bp.route("/api/tasks/<task_id>", methods=["GET"])
@require_auth
def get_task(task_id):
    """Get a single task by task_id."""
    try:
        return jsonify(task_service.get_by_id(task_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@tasks_bp.route("/api/projects/<project_id>/tasks", methods=["GET"])
@require_auth
def get_project_tasks(project_id):
    """List all tasks for a single project."""
    try:
        return jsonify(task_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@tasks_bp.route("/api/projects/<project_id>/tasks", methods=["POST"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def create_task(project_id):
    """Create a task under a project. project_id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(task_service.create(project_id, data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@tasks_bp.route("/api/tasks/<task_id>", methods=["PUT", "PATCH"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def update_task(task_id):
    """Update a task (full PUT or partial PATCH). The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(task_service.update(task_id, data)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@tasks_bp.route("/api/tasks/<task_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def delete_task(task_id):
    """Delete a task by task_id."""
    try:
        return jsonify(task_service.delete(task_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
