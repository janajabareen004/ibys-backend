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
