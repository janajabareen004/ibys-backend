from services.supabase_client import supabase
from services.errors import ServiceError


class ManagerService:
    """Read-only Supabase access for the project_managers profile table.

    Exposes just enough to resolve a project manager's display name
    (manager_name), phone, and email by id, following the same conventions as
    TenantService: returns exactly the data the route should jsonify, and raises
    ServiceError(message, status) on failure. The project_managers table has no
    email column; email is resolved server-side from Supabase Auth (source of
    truth) via the privileged admin client and merged into the response.
    """

    TABLE = "project_managers"

    def _get_auth_email(self, manager_id):
        """Best-effort lookup of the manager's real email from Supabase Auth.

        Uses supabase.auth.admin.get_user_by_id on the shared privileged
        (sb_secret_ key) client — server-side only, never exposed to the
        frontend. Returns "" if the Auth user can't be found or the lookup
        fails for any reason, so this never fails the manager profile request.
        """
        try:
            result = supabase.auth.admin.get_user_by_id(manager_id)
        except Exception as e:
            print(f"[manager] auth email lookup failed for {manager_id}: {e}")
            return ""
        user = getattr(result, "user", None)
        return getattr(user, "email", None) or ""

    def get_by_id(self, manager_id):
        """Return a single manager profile (user_id, manager_name, phone, email).

        email is looked up from Supabase Auth best-effort: a failed/missing Auth
        email never fails this call as long as the project_managers row exists.
        """
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
        profile = response.data[0]
        profile["email"] = self._get_auth_email(manager_id)
        return profile
