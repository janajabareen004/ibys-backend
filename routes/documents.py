from flask import Blueprint, request, jsonify, g
from services.document_service import DocumentService
from services.activity_service import ActivityService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span both
# /api/documents... and /api/projects/<project_id>/documents
documents_bp = Blueprint("documents", __name__)

document_service = DocumentService()
activity_service = ActivityService()


@documents_bp.route("/api/documents", methods=["GET"])
def get_all_documents():
    """List all documents (across all projects)."""
    try:
        return jsonify(document_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@documents_bp.route("/api/documents/<document_id>", methods=["GET"])
def get_document(document_id):
    """Get a single document by document_id."""
    try:
        return jsonify(document_service.get_by_id(document_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@documents_bp.route("/api/projects/<project_id>/documents", methods=["GET"])
def get_project_documents(project_id):
    """List all documents for a single project."""
    try:
        return jsonify(document_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@documents_bp.route("/api/projects/<project_id>/documents", methods=["POST"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def create_document(project_id):
    """Create a document under a project. project_id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        created = document_service.create(project_id, data)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    actor = activity_service.resolve_actor(g.current_user_id, g.current_role)
    label = created.get("file_name") or "a document"
    activity_service.record_event(project_id, actor, "document_added", f"added {label}")
    return jsonify(created), 201


@documents_bp.route("/api/documents/<document_id>", methods=["PUT"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def update_document(document_id):
    """Update a document. The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(document_service.update(document_id, data)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@documents_bp.route("/api/documents/<document_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def delete_document(document_id):
    """Delete a document by document_id."""
    try:
        return jsonify(document_service.delete(document_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
