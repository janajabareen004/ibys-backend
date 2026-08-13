from services.supabase_client import supabase
from services.errors import ServiceError


class ManagerNotificationService:
    """Business logic and Supabase access for the manager_notifications resource.

    Notifications are per-recipient attention items. Reads and mark-read
    operations are ALWAYS scoped to the caller's own user id (recipient_id), so a
    manager can only ever see or modify their own notifications. Recording is
    best-effort: it must NEVER raise, so a notification failure can never break
    the primary business operation that triggered it (e.g. request creation).

    This service is independent of the tenant-facing NotificationService and the
    existing `notifications` table.
    """

    TABLE = "manager_notifications"

    # ---- reads -------------------------------------------------------------

    def get_for_recipient(self, recipient_id):
        """Return this manager's notifications, newest first."""
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("recipient_id", recipient_id)
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    # ---- mutations (ownership enforced in the query) -----------------------

    def mark_read(self, notification_id, recipient_id, read=True):
        """Set is_read for ONE notification the caller owns.

        The recipient_id filter enforces ownership server-side: an update for a
        notification owned by a different manager matches zero rows and raises
        404, so one manager can never modify another manager's notification.
        """
        try:
            response = (
                supabase.table(self.TABLE)
                .update({"is_read": bool(read)})
                .eq("id", notification_id)
                .eq("recipient_id", recipient_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Notification not found.", 404)
        return response.data[0]

    def mark_all_read(self, recipient_id):
        """Mark all of the caller's unread notifications as read."""
        try:
            response = (
                supabase.table(self.TABLE)
                .update({"is_read": True})
                .eq("recipient_id", recipient_id)
                .eq("is_read", False)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        return {
            "message": "All notifications marked as read.",
            "updated": len(response.data or []),
        }

    # ---- recipient resolution + best-effort recording ----------------------

    def resolve_project_manager_id(self, project_id):
        """Return the owning manager's user id for a project, or None.

        Never raises. Does not fabricate a recipient: returns None when the
        project is unknown or has no assigned manager.
        """
        if project_id is None:
            return None
        try:
            res = (
                supabase.table("projects")
                .select("project_manager_id")
                .eq("project_id", project_id)
                .execute()
            )
            for row in res.data or []:
                if row.get("project_manager_id"):
                    return row["project_manager_id"]
        except Exception:
            pass
        return None

    def record(self, recipient_id, project_id, type, title, message):
        """Insert one manager notification. Best-effort: never raises.

        Skips silently when there is no recipient, type, or title, so we never
        write an unaddressed or malformed notification.
        """
        if not recipient_id or not type or not title:
            return None
        try:
            supabase.table(self.TABLE).insert(
                {
                    "recipient_id": recipient_id,
                    "project_id": project_id,
                    "type": type,
                    "title": title,
                    "message": message,
                }
            ).execute()
        except Exception as e:
            # Log server-side and let the primary operation remain successful.
            print(f"[manager_notification] record failed ({type}): {e}")
        return None
