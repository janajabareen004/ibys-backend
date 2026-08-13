from flask import Blueprint, request, jsonify, g
from services.manager_notification_service import ManagerNotificationService
from services.errors import ServiceError
from services.auth_guard import require_auth, require_roles

# All routes here are prefixed with /api/manager/notifications
manager_notifications_bp = Blueprint(
    "manager_notifications", __name__, url_prefix="/api/manager/notifications"
)

manager_notification_service = ManagerNotificationService()


@manager_notifications_bp.route("", methods=["GET"])
@require_auth
@require_roles("MANAGER")
def list_notifications():
    """List the authenticated manager's notifications, newest first.

    Results are always scoped to the caller's own id (from the validated token),
    so a manager only ever sees notifications addressed to them.
    """
    try:
        return jsonify(
            manager_notification_service.get_for_recipient(g.current_user_id)
        ), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@manager_notifications_bp.route("/<notification_id>/read", methods=["PATCH"])
@require_auth
@require_roles("MANAGER")
def mark_read(notification_id):
    """Set is_read for one of the caller's own notifications.

    Accepts an optional JSON body {"read": true|false} to support the page's
    toggle behavior; defaults to true. Ownership is enforced by the service
    (recipient_id must match the authenticated user), so a manager cannot modify
    another manager's notification.
    """
    body = request.get_json(silent=True) or {}
    read = body.get("read", True)
    try:
        return jsonify(
            manager_notification_service.mark_read(
                notification_id, g.current_user_id, bool(read)
            )
        ), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status


@manager_notifications_bp.route("/read-all", methods=["POST"])
@require_auth
@require_roles("MANAGER")
def mark_all_read():
    """Mark all of the authenticated manager's notifications as read."""
    try:
        return jsonify(
            manager_notification_service.mark_all_read(g.current_user_id)
        ), 200
    except ServiceError as e:
        return jsonify({"error": e.message}), e.status
