from datetime import datetime, timezone

from services.supabase_client import supabase
from services.errors import ServiceError
from models.team_member import TeamMember


class TeamService:
    """Business logic and Supabase access for the team_members resource.

    Mirrors the conventions of TaskService/ProgressService: every method returns
    exactly what the route should jsonify on success and raises
    ServiceError(message, status) on failure. Manager ownership scoping (by
    projects.project_manager_id) is applied in the frontend API layer, matching
    the existing tasks/meetings/progress manager APIs.
    """

    TABLE = "team_members"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, member_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("member_id", member_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Team member not found.", 404)
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

    def _normalize(self, data):
        """Coerce validated fields into their stored representation."""
        if isinstance(data.get("availability"), str):
            data["availability"] = data["availability"].strip().lower()
        for key in ("role", "email", "phone"):
            if data.get(key) == "":
                data[key] = None
        return data

    def create(self, project_id, data):
        error = TeamMember.validate_create(data)
        if error:
            raise ServiceError(error, 400)

        availability_error = TeamMember.validate_availability(data.get("availability"))
        if availability_error:
            raise ServiceError(availability_error, 400)

        # project_id comes only from the URL, never the body.
        TeamMember.strip_protected(data)
        self._normalize(data)
        data["project_id"] = project_id

        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. foreign key violation for an invalid project_id
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, member_id, data):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        # member_id, project_id and timestamps must never be updated from the body.
        TeamMember.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        if "availability" in data:
            availability_error = TeamMember.validate_availability(data.get("availability"))
            if availability_error:
                raise ServiceError(availability_error, 400)

        self._normalize(data)

        # Keep updated_at fresh (PostgREST stores the literal value, so send a
        # real ISO timestamp rather than a SQL expression).
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("member_id", member_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Team member not found.", 404)
        return response.data[0]

    def delete(self, member_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .delete()
                .eq("member_id", member_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Team member not found.", 404)
        return {"message": "Team member deleted successfully."}
