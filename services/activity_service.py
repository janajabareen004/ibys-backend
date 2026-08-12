from services.supabase_client import supabase
from services.errors import ServiceError
from models.user import User


class ActivityService:
    """Read + server-side recording for the activity_events resource.

    The frontend only ever READS activity (newest first); events are created
    server-side by record_event after a primary mutation succeeds. Recording is
    best-effort: it must NEVER raise, so a logging failure can never break the
    original business operation.
    """

    TABLE = "activity_events"

    # ---- reads -------------------------------------------------------------

    def get_all(self):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_for_project(self, project_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("project_id", project_id)
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    # ---- server-side recording (best-effort, never raises) -----------------

    def resolve_actor(self, user_id, role=None):
        """Best-effort display name for the actor; falls back to the user id.

        Never raises. Does not fabricate a name: if no profile name is found,
        the raw user id is returned so the event still has a stable actor.
        """
        if not user_id:
            return None
        try:
            config = User.role_config(role) if role else None
            if config:
                res = (
                    supabase.table(config["table"])
                    .select(config["name_field"])
                    .eq("user_id", user_id)
                    .execute()
                )
                if res.data and res.data[0].get(config["name_field"]):
                    return res.data[0][config["name_field"]]
        except Exception:
            pass
        return user_id

    def resolve_request_project_id(self, tenant_id):
        """Resolve a request's project via the tenant's apartment.

        Requests have no project_id column; a tenant is linked to a project
        through apartments.tenant_id -> apartments.project_id. Returns the first
        matching project_id, or None. Never raises.
        """
        if not tenant_id:
            return None
        try:
            res = (
                supabase.table("apartments")
                .select("project_id")
                .eq("tenant_id", tenant_id)
                .execute()
            )
            for row in res.data or []:
                if row.get("project_id") is not None:
                    return row["project_id"]
        except Exception:
            pass
        return None

    def record_event(self, project_id, actor, type, message):
        """Insert one activity event. Best-effort: never raises.

        Skips silently when there is no project_id or type (so we never write a
        malformed/unscoped event, and never fabricate a project association).
        """
        if project_id is None or not type:
            return None
        try:
            supabase.table(self.TABLE).insert(
                {
                    "project_id": project_id,
                    "actor": actor,
                    "type": type,
                    "message": message,
                }
            ).execute()
        except Exception as e:
            # Log server-side and let the primary operation remain successful.
            print(f"[activity] record_event failed ({type}): {e}")
        return None
