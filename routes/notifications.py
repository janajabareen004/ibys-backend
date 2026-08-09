from flask import Blueprint, jsonify, g
from services.notification_service import NotificationService
from services.errors import ServiceError
from services.auth_guard import require_auth

# All routes here are prefixed with /api/notifications
notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

notification_service = NotificationService()


@notifications_bp.route("", methods=["GET"])
@require_auth
def get_notifications():
    """List the authenticated tenant's notifications, newest first.

    Results are always scoped to the caller's own id (from the validated token),
    so a tenant only ever sees notifications that belong to them.
    """
    try:
        return jsonify(notification_service.get_for_tenant(g.current_user_id)), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
