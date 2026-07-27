from flask import Blueprint, request, jsonify
from services.apartment_service import ApartmentService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# This Blueprint uses full explicit paths because its routes span
# /api/apartments..., /api/projects/<project_id>/apartments, and
# /api/tenants/<tenant_id>/apartments
apartments_bp = Blueprint("apartments", __name__)

apartment_service = ApartmentService()


@apartments_bp.route("/api/apartments", methods=["GET"])
def get_all_apartments():
    """List all apartments (across all projects)."""
    try:
        return jsonify(apartment_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@apartments_bp.route("/api/apartments/<apartment_id>", methods=["GET"])
def get_apartment(apartment_id):
    """Get a single apartment by apartment_id."""
    try:
        return jsonify(apartment_service.get_by_id(apartment_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@apartments_bp.route("/api/projects/<project_id>/apartments", methods=["GET"])
def get_project_apartments(project_id):
    """List all apartments for a single project."""
    try:
        return jsonify(apartment_service.get_for_project(project_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@apartments_bp.route("/api/tenants/<tenant_id>/apartments", methods=["GET"])
def get_tenant_apartments(tenant_id):
    """List all apartments owned by a single tenant."""
    try:
        return jsonify(apartment_service.get_for_tenant(tenant_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@apartments_bp.route("/api/projects/<project_id>/apartments", methods=["POST"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def create_apartment(project_id):
    """Create an apartment under a project. project_id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(apartment_service.create(project_id, data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@apartments_bp.route("/api/apartments/<apartment_id>", methods=["PUT"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def update_apartment(apartment_id):
    """Update an apartment. The id comes only from the URL."""
    data = request.get_json(silent=True)
    try:
        return jsonify(apartment_service.update(apartment_id, data)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@apartments_bp.route("/api/apartments/<apartment_id>", methods=["DELETE"])
@require_auth
@require_roles("MANAGER", "BUILDING_COMPANY")
def delete_apartment(apartment_id):
    """Delete an apartment by apartment_id."""
    try:
        return jsonify(apartment_service.delete(apartment_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
