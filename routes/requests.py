from flask import Blueprint, request, jsonify, g
from services.request_service import RequestService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# All routes here are prefixed with /api/requests
requests_bp = Blueprint("requests", __name__, url_prefix="/api/requests")

request_service = RequestService()


@requests_bp.route("", methods=["GET"])
@require_auth
def get_requests():
    """List requests. A TENANT sees only its own; MANAGER/BUILDING_COMPANY see all."""
    try:
        if g.current_role == "TENANT":
            return jsonify(request_service.get_for_tenant(g.current_user_id)), 200
        return jsonify(request_service.get_all()), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@requests_bp.route("/<request_id>", methods=["GET"])
@require_auth
def get_request(request_id):
    """Get a single request. A TENANT may read only its own request."""
    try:
        req = request_service.get_by_id(request_id)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    if g.current_role == "TENANT" and req.get("tenant_id") != g.current_user_id:
        return jsonify({"error": "Forbidden: you do not own this request."}), 403
    return jsonify(req), 200


@requests_bp.route("", methods=["POST"])
@require_auth
@require_roles("TENANT")
def create_request():
    """Create a new request."""
    data = request.get_json(silent=True)
    try:
        return jsonify(request_service.create(g.current_user_id, data)), 201
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@requests_bp.route("/<request_id>", methods=["PUT", "PATCH"])
@require_auth
@require_roles("TENANT", "MANAGER", "BUILDING_COMPANY")
def update_request(request_id):
    """Update an existing request (full PUT or partial PATCH).

    The id comes only from the URL. A MANAGER uses this to change the request
    status (e.g. {"status": "approved"}); the service strips protected fields
    (request_id, tenant_id) and persists the rest, returning the updated row.
    """
    data = request.get_json(silent=True)
    try:
        return jsonify(
            request_service.update(request_id, data, g.current_user_id, g.current_role)
        ), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@requests_bp.route("/<request_id>", methods=["DELETE"])
@require_auth
@require_roles("TENANT", "MANAGER")
def delete_request(request_id):
    """Delete a request by request_id."""
    try:
        return jsonify(
            request_service.delete(request_id, g.current_user_id, g.current_role)
        ), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
