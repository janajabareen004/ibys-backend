from services.supabase_client import supabase
from services.errors import ServiceError


class TenantService:
    """Read-only Supabase access for the tenants profile table.

    Exposes just enough to resolve a tenant's display name (full_name), phone,
    email, and created_at by id, following the same conventions as the other
    feature services: returns exactly the data the route should jsonify, and
    raises ServiceError(message, status) on failure. The tenants table has no
    email/created_at columns; both are resolved server-side from Supabase Auth
    (source of truth) via the privileged admin client and merged into the
    response, mirroring ManagerService's email lookup.
    """

    TABLE = "tenants"

    def _get_auth_profile(self, tenant_id):
        """Best-effort lookup of {email, created_at} from Supabase Auth.

        Uses supabase.auth.admin.get_user_by_id on the shared privileged
        (sb_secret_ key) client — server-side only, never exposed to the
        frontend. Returns {"email": "", "created_at": ""} if the Auth user
        can't be found or the lookup fails for any reason, so this never
        fails the tenant profile request.
        """
        try:
            result = supabase.auth.admin.get_user_by_id(tenant_id)
        except Exception as e:
            print(f"[tenant] auth lookup failed for {tenant_id}: {e}")
            return {"email": "", "created_at": ""}
        user = getattr(result, "user", None)
        email = getattr(user, "email", None) or ""
        created_at = getattr(user, "created_at", None)
        created_at_str = created_at.isoformat() if created_at else ""
        return {"email": email, "created_at": created_at_str}

    def get_by_id(self, tenant_id):
        """Return a single tenant profile row (user_id, full_name, phone, email, created_at).

        email/created_at are looked up from Supabase Auth best-effort: a
        failed/missing Auth lookup never fails this call as long as the
        tenants row exists.
        """
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("user_id", tenant_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Tenant not found.", 404)
        profile = response.data[0]
        profile.update(self._get_auth_profile(tenant_id))
        return profile
