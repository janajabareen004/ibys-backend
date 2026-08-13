from flask import Blueprint, request, jsonify, g
from services.request_service import RequestService
from services.activity_service import ActivityService
from services.manager_notification_service import ManagerNotificationService
from services.notification_service import NotificationService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# All routes here are prefixed with /api/requests
requests_bp = Blueprint("requests", __name__, url_prefix="/api/requests")

request_service = RequestService()
activity_service = ActivityService()
manager_notification_service = ManagerNotificationService()
notification_service = NotificationService()


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
        created = request_service.create(g.current_user_id, data)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    # Requests have no project_id column; resolve it via the tenant's apartment.
    project_id = activity_service.resolve_request_project_id(created.get("tenant_id"))
    actor = activity_service.resolve_actor(g.current_user_id, g.current_role)
    activity_service.record_event(project_id, actor, "request_received", "submitted a new request")

    # Notify the manager who owns this request's project (best-effort; never
    # fabricates a recipient and never fails the request creation above).
    manager_id = manager_notification_service.resolve_project_manager_id(project_id)
    if manager_id:
        description = (created.get("description") or "").strip()
        snippet = (description[:120] + "\u2026") if len(description) > 120 else description
        message = f"New request: {snippet}" if snippet else "A tenant submitted a new request."
        manager_notification_service.record(
            manager_id, project_id, "request", "New tenant request", message
        )

    return jsonify(created), 201


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
    # Capture the previous status BEFORE the update so we only notify the tenant
    # on a real status transition (prevents duplicate notifications on repeated
    # no-op saves). Best-effort: the authoritative 404 still comes from update().
    prev_status = ""
    try:
        prev_status = str((request_service.get_by_id(request_id) or {}).get("status", "")).strip().lower()
    except ServiceError:
        prev_status = ""
    try:
        updated = request_service.update(request_id, data, g.current_user_id, g.current_role)
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
    # Requests have no project_id column; resolve it via the tenant's apartment.
    project_id = activity_service.resolve_request_project_id(updated.get("tenant_id"))
    actor = activity_service.resolve_actor(g.current_user_id, g.current_role)
    body = data or {}
    status = str(body.get("status", "")).strip().lower()
    if status == "approved":
        activity_service.record_event(project_id, actor, "request_approved", "approved a tenant request")
    elif status == "rejected":
        activity_service.record_event(project_id, actor, "request_rejected", "rejected a tenant request")
    if body.get("reply"):
        activity_service.record_event(project_id, actor, "request_replied", "replied to a tenant request")

    # Notify the request's OWNER (tenant) when the manager transitions the status
    # to a decision. Gated on a real change (status != prev_status) so repeated
    # or no-op saves never duplicate. Best-effort; never fails the update above.
    if status in ("approved", "rejected") and status != prev_status:
        tenant_id = updated.get("tenant_id")
        description = (updated.get("description") or "").strip()
        snippet = (description[:120] + "\u2026") if len(description) > 120 else description
        if status == "approved":
            title = "Request approved"
            message = f"Your request was approved: {snippet}" if snippet else "Your request was approved."
        else:
            title = "Request rejected"
            message = f"Your request was rejected: {snippet}" if snippet else "Your request was rejected."
        notification_service.create_for_tenant(tenant_id, "system", title, message)

    return jsonify(updated), 200


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
