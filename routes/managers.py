from flask import Blueprint, jsonify
from services.manager_service import ManagerService
from services.errors import ServiceError
from services.auth_guard import require_auth

# Uses a full explicit path (like the tenants blueprint) so it can live at
# /api/managers/<manager_id> without colliding with other /api routes.
managers_bp = Blueprint("managers", __name__)

manager_service = ManagerService()


@managers_bp.route("/api/managers/<manager_id>", methods=["GET"])
@require_auth
def get_manager(manager_id):
    """Return a single project manager's profile (user_id, manager_name, phone).

    Read-only. Requires authentication; used by a tenant to resolve the display
    name and phone of the manager attached to their own project. Does not expose
    the manager's Supabase Auth email.
    """
    try:
        return jsonify(manager_service.get_by_id(manager_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
