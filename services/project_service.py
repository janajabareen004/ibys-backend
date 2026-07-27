from services.supabase_client import supabase
from services.errors import ServiceError
from models.project import Project


class ProjectService:
    """Business logic and Supabase access for the projects resource.

    Every method returns exactly the data the route should jsonify on success,
    and raises ServiceError(message, status) on failure, mirroring the current
    route behavior (status codes and messages) precisely.
    """

    TABLE = "projects"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, project_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("project_id", project_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Project not found.", 404)
        return response.data[0]

    def create(self, data):
        error = Project.validate_create(data)
        if error:
            raise ServiceError(error, 400)
        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. NOT NULL / FK constraint violations from Supabase
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, project_id, data):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        Project.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("project_id", project_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Project not found.", 404)
        return response.data[0]

    def delete(self, project_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .delete()
                .eq("project_id", project_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Project not found.", 404)
        return {"message": "Project deleted successfully."}
