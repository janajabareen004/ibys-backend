from services.supabase_client import supabase
from services.errors import ServiceError
from models.apartment import Apartment


class ApartmentService:
    """Business logic and Supabase access for the apartments resource.

    Every method returns exactly the data the route should jsonify on success,
    and raises ServiceError(message, status) on failure, following the same
    conventions as the other feature services.
    """

    TABLE = "apartments"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, apartment_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("apartment_id", apartment_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Apartment not found.", 404)
        return response.data[0]

    def get_for_project(self, project_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("project_id", project_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

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

    def create(self, project_id, data):
        error = Apartment.validate_create(data)
        if error:
            raise ServiceError(error, 400)

        # project_id must come only from the URL, never the body.
        Apartment.strip_protected(data)
        data["project_id"] = project_id

        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. foreign key violation for an invalid project_id or tenant_id,
            # or a wrong type for floor/size
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, apartment_id, data):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        # apartment_id and project_id must never be updated from the body.
        Apartment.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("apartment_id", apartment_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Apartment not found.", 404)
        return response.data[0]

    def delete(self, apartment_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .delete()
                .eq("apartment_id", apartment_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Apartment not found.", 404)
        return {"message": "Apartment deleted successfully."}
