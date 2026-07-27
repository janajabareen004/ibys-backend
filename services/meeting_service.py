from services.supabase_client import supabase
from services.errors import ServiceError
from models.meeting import Meeting


class MeetingService:
    """Business logic and Supabase access for the meetings resource.

    Every method returns exactly the data the route should jsonify on success,
    and raises ServiceError(message, status) on failure, following the same
    conventions as the other feature services.
    """

    TABLE = "meetings"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, meeting_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("meeting_id", meeting_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Meeting not found.", 404)
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

    def create(self, project_id, data):
        error = Meeting.validate_create(data)
        if error:
            raise ServiceError(error, 400)

        # project_id must come only from the URL, never the body.
        Meeting.strip_protected(data)
        data["project_id"] = project_id

        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. foreign key violation for an invalid project_id or
            # project_manager_id, or a malformed date/time
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, meeting_id, data):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        # meeting_id and project_id must never be updated from the body.
        Meeting.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("meeting_id", meeting_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Meeting not found.", 404)
        return response.data[0]

    def delete(self, meeting_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .delete()
                .eq("meeting_id", meeting_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Meeting not found.", 404)
        return {"message": "Meeting deleted successfully."}
