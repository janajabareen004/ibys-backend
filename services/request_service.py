from services.supabase_client import supabase
from services.errors import ServiceError
from models.request import Request


class RequestService:
    """Business logic and Supabase access for the requests resource.

    Every method returns exactly the data the route should jsonify on success,
    and raises ServiceError(message, status) on failure, following the same
    conventions as ProjectService, ProgressService, and CommentService.
    """

    TABLE = "requests"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, request_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("request_id", request_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Request not found.", 404)
        return response.data[0]

    def get_for_tenant(self, tenant_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("tenant_id", tenant_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def create(self, current_user_id, data):
        error = Request.validate_create(data)
        if error:
            raise ServiceError(error, 400)

        # request_id is auto-generated, and tenant_id (owner) comes only from the
        # authenticated token. strip_protected removes both from any client body
        # before we inject the trusted tenant_id.
        Request.strip_protected(data)
        data["tenant_id"] = current_user_id

        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. foreign key violation for an invalid tenant_id
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, request_id, data, current_user_id, current_role):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        # Fetch first (404 if missing), then enforce ownership for TENANT only.
        existing = self.get_by_id(request_id)
        if current_role == "TENANT" and existing.get("tenant_id") != current_user_id:
            raise ServiceError("Forbidden: you do not own this request.", 403)

        # request_id and tenant_id must never be updated from the body.
        Request.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("request_id", request_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Request not found.", 404)
        return response.data[0]

    def delete(self, request_id, current_user_id, current_role):
        # Fetch first (404 if missing), then enforce ownership for TENANT only.
        existing = self.get_by_id(request_id)
        if current_role == "TENANT" and existing.get("tenant_id") != current_user_id:
            raise ServiceError("Forbidden: you do not own this request.", 403)

        try:
            response = (
                supabase.table(self.TABLE)
                .delete()
                .eq("request_id", request_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Request not found.", 404)
        return {"message": "Request deleted successfully."}
