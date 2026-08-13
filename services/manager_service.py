from services.supabase_client import supabase
from services.errors import ServiceError


class ManagerService:
    """Read-only Supabase access for the project_managers profile table.

    Exposes just enough to resolve a project manager's display name
    (manager_name) and phone by id, following the same conventions as
    TenantService: returns exactly the data the route should jsonify, and raises
    ServiceError(message, status) on failure. Email is never returned (it lives
    only in Supabase Auth and is intentionally not exposed here).
    """

    TABLE = "project_managers"

    def get_by_id(self, manager_id):
        """Return a single manager profile (user_id, manager_name, phone)."""
        try:
            response = (
                supabase.table(self.TABLE)
                .select("user_id, manager_name, phone")
                .eq("user_id", manager_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Manager not found.", 404)
        return response.data[0]
