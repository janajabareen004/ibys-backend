from services.supabase_client import supabase
from services.errors import ServiceError
from models.comment import Comment


class CommentService:
    """Business logic and Supabase access for the comments resource.

    Every method returns exactly the data the route should jsonify on success,
    and raises ServiceError(message, status) on failure, following the same
    conventions as ProjectService and ProgressService.
    """

    TABLE = "comments"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, comment_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("comment_id", comment_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Comment not found.", 404)
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

    def create(self, project_id, current_user_id, data):
        error = Comment.validate_create(data)
        if error:
            raise ServiceError(error, 400)

        # project_id comes only from the URL, and the author (user_id) comes only
        # from the authenticated token. strip_protected removes both (plus the PK)
        # from any client-supplied body before we inject the trusted values.
        Comment.strip_protected(data)
        data["project_id"] = project_id
        data["user_id"] = current_user_id

        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. foreign key violation for an invalid project_id or user_id
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, comment_id, data, current_user_id):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        # Author-only: fetch first, 404 if missing, then 403 if not the author.
        existing = self.get_by_id(comment_id)
        if existing.get("user_id") != current_user_id:
            raise ServiceError("Forbidden: you are not the author of this comment.", 403)

        # comment_id, project_id, and user_id must never be updated from the body.
        Comment.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("comment_id", comment_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("Comment not found.", 404)
        return response.data[0]

    def delete(self, comment_id, current_user_id):
        # Author-only: fetch first, 404 if missing, then 403 if not the author.
        existing = self.get_by_id(comment_id)
        if existing.get("user_id") != current_user_id:
            raise ServiceError("Forbidden: you are not the author of this comment.", 403)

        try:
            response = (
                supabase.table(self.TABLE)
                .delete()
                .eq("comment_id", comment_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("Comment not found.", 404)
        return {"message": "Comment deleted successfully."}
