from services.supabase_client import supabase
from services.errors import ServiceError


class TenantService:
    """Read-only Supabase access for the tenants profile table.

    Exposes just enough to resolve a tenant's display name (full_name) by id,
    following the same conventions as the other feature services: returns exactly
    the data the route should jsonify, and raises ServiceError(message, status)
    on failure.
    """

    TABLE = "tenants"

    def get_by_id(self, tenant_id):
        """Return a single tenant profile row (user_id, full_name, phone)."""
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
        return response.data[0]
