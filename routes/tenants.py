from flask import Blueprint, jsonify
from services.tenant_service import TenantService
from services.errors import ServiceError
from services.auth_guard import require_auth

# Uses a full explicit path (like the apartments blueprint) so it can live at
# /api/tenants/<tenant_id> without colliding with the existing
# /api/tenants/<tenant_id>/apartments and /api/tenants/<tenant_id>/ai-chats routes.
tenants_bp = Blueprint("tenants", __name__)

tenant_service = TenantService()


@tenants_bp.route("/api/tenants/<tenant_id>", methods=["GET"])
@require_auth
def get_tenant(tenant_id):
    """Return a single tenant's profile (user_id, full_name, phone).

    Read-only. Requires authentication; used by managers to resolve tenant
    display names for requests scoped to their own projects.
    """
    try:
        return jsonify(tenant_service.get_by_id(tenant_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
