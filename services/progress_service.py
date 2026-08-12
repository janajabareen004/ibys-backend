from services.supabase_client import supabase
from services.errors import ServiceError
from models.progress import Progress


class ProgressService:
    """Business logic and Supabase access for the progress resource.

    Mirrors the current route behavior (status codes and messages) precisely,
    including the strict single-date validation on update.
    """

    TABLE = "progress"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, progress_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("progress_id", progress_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Progress record not found.", 404)
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
        error = Progress.validate_create(data)
        if error:
            raise ServiceError(error, 400)

        date_error = Progress.validate_date_range(
            data.get("start_date"), data.get("end_date")
        )
        if date_error:
            raise ServiceError(date_error, 400)

        percent_error = Progress.validate_progress_percent(data.get("progress_percent"))
        if percent_error:
            raise ServiceError(percent_error, 400)
        if data.get("progress_percent") is not None:
            data["progress_percent"] = int(data["progress_percent"])

        # project_id must come only from the URL, never the body.
        Progress.strip_protected(data)
        data["project_id"] = project_id

        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. foreign key violation for an invalid project_id
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, progress_id, data):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        # progress_id and project_id must never be updated from the body.
        Progress.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        if "progress_percent" in data:
            percent_error = Progress.validate_progress_percent(data.get("progress_percent"))
            if percent_error:
                raise ServiceError(percent_error, 400)
            if data.get("progress_percent") is not None:
                data["progress_percent"] = int(data["progress_percent"])

        new_start = data.get("start_date")
        new_end = data.get("end_date")

        # Strict date validation: if only one date is supplied, combine it with
        # the stored value before validating the range.
        if new_start is not None or new_end is not None:
            try:
                existing = (
                    supabase.table(self.TABLE)
                    .select("*")
                    .eq("progress_id", progress_id)
                    .execute()
                )
            except Exception as e:
                raise ServiceError(str(e), 500)

            if not existing.data:
                raise ServiceError("Progress record not found.", 404)

            current = existing.data[0]
            start_value = new_start if new_start is not None else current.get("start_date")
            end_value = new_end if new_end is not None else current.get("end_date")

            date_error = Progress.validate_date_range(start_value, end_value)
            if date_error:
                raise ServiceError(date_error, 400)

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("progress_id", progress_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Progress record not found.", 404)
        return response.data[0]

    def delete(self, progress_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .delete()
                .eq("progress_id", progress_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Progress record not found.", 404)
        return {"message": "Progress record deleted successfully."}
