from datetime import datetime, timezone

from services.supabase_client import supabase
from services.errors import ServiceError
from models.task import Task


class TaskService:
    """Business logic and Supabase access for the tasks resource.

    Mirrors the conventions of ProgressService/RequestService: every method
    returns exactly what the route should jsonify on success and raises
    ServiceError(message, status) on failure. Manager ownership scoping (by
    projects.project_manager_id) is applied in the frontend API layer, matching
    the existing requests/meetings/progress manager APIs.
    """

    TABLE = "tasks"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, task_id):
        try:
            response = (
                supabase.table(self.TABLE).select("*").eq("task_id", task_id).execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Task not found.", 404)
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

    def _validate_optional_fields(self, data):
        """Validate the optional constrained fields shared by create/update."""
        for validator, key in (
            (Task.validate_due_date, "due_date"),
            (Task.validate_progress_percent, "progress_percent"),
            (Task.validate_status, "status"),
            (Task.validate_priority, "priority"),
        ):
            if key in data:
                error = validator(data.get(key))
                if error:
                    raise ServiceError(error, 400)

    def _normalize(self, data):
        """Coerce validated fields into their stored representation."""
        if data.get("progress_percent") is not None and "progress_percent" in data:
            data["progress_percent"] = int(data["progress_percent"])
        if isinstance(data.get("status"), str):
            data["status"] = data["status"].strip().lower()
        if isinstance(data.get("priority"), str):
            data["priority"] = data["priority"].strip().lower()
        # Treat empty-string optionals as NULL for cleaner storage.
        for key in ("description", "assigned_to", "stage", "due_date"):
            if data.get(key) == "":
                data[key] = None
        return data

    def create(self, project_id, data):
        error = Task.validate_create(data)
        if error:
            raise ServiceError(error, 400)

        self._validate_optional_fields(data)

        # project_id comes only from the URL, never the body.
        Task.strip_protected(data)
        self._normalize(data)
        data["project_id"] = project_id

        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. foreign key violation for an invalid project_id
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, task_id, data):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        # task_id, project_id and timestamps must never be updated from the body.
        Task.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        self._validate_optional_fields(data)
        self._normalize(data)

        # Keep updated_at fresh on every write (PostgREST stores the literal
        # value, so send a real ISO timestamp rather than a SQL expression).
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("task_id", task_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Task not found.", 404)
        return response.data[0]

    def delete(self, task_id):
        try:
            response = (
                supabase.table(self.TABLE).delete().eq("task_id", task_id).execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Task not found.", 404)
        return {"message": "Task deleted successfully."}
