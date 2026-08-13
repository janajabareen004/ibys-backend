from services.supabase_client import supabase
from services.errors import ServiceError


class NotificationService:
    """Business logic and Supabase access for the notifications resource.

    Read-only for now: it lists the notifications that belong to a single
    tenant, newest first. Every method returns exactly the data the route should
    jsonify on success, and raises ServiceError(message, status) on failure,
    following the same conventions as RequestService and CommentService.
    """

    TABLE = "notifications"

    def get_for_tenant(self, tenant_id):
        """Return this tenant's notifications, ordered by created_at DESC."""
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("tenant_id", tenant_id)
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def create_for_tenant(self, tenant_id, type, title, message):
        """Insert one tenant notification (is_read defaults to false).

        Best-effort: it must NEVER raise, so a notification failure can never
        break the primary business operation that triggered it (e.g. a manager
        approving/rejecting a request). Skips silently when there is no
        recipient, type, or title so we never write a malformed/unaddressed row.
        """
        if not tenant_id or not type or not title:
            return None
        try:
            supabase.table(self.TABLE).insert(
                {
                    "tenant_id": tenant_id,
                    "type": type,
                    "title": title,
                    "message": message,
                    "is_read": False,
                }
            ).execute()
        except Exception as e:
            # Log server-side and let the primary operation remain successful.
            print(f"[notification] create_for_tenant failed ({type}): {e}")
        return None
