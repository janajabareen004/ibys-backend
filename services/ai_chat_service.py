from services.supabase_client import supabase
from services.errors import ServiceError
from models.ai_chat import AIChat


class AIChatService:
    """Business logic and Supabase access for the ai_chats resource.

    Every method returns exactly the data the route should jsonify on success,
    and raises ServiceError(message, status) on failure, following the same
    conventions as RequestService and ApartmentService.

    This service only stores and retrieves chat records. It does NOT call any
    external AI service; answer is nullable and can be filled in later via update.
    """

    TABLE = "ai_chats"

    def get_all(self):
        try:
            response = supabase.table(self.TABLE).select("*").execute()
        except Exception as e:
            raise ServiceError(str(e), 500)
        return response.data

    def get_by_id(self, chat_id):
        try:
            response = (
                supabase.table(self.TABLE)
                .select("*")
                .eq("chat_id", chat_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("AI chat not found.", 404)
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
        error = AIChat.validate_create(data)
        if error:
            raise ServiceError(error, 400)

        # chat_id is auto-generated, and tenant_id (owner) comes only from the
        # authenticated token. strip_protected removes both from any client body
        # before we inject the trusted tenant_id.
        AIChat.strip_protected(data)
        data["tenant_id"] = current_user_id

        try:
            response = supabase.table(self.TABLE).insert(data).execute()
        except Exception as e:
            # e.g. foreign key violation for an invalid tenant_id
            raise ServiceError(str(e), 400)
        return response.data[0]

    def update(self, chat_id, data, current_user_id):
        if not isinstance(data, dict) or not data:
            raise ServiceError("Request body must be a non-empty JSON object.", 400)

        # Owner-only: fetch first (404 if missing), then 403 if not the owner.
        existing = self.get_by_id(chat_id)
        if existing.get("tenant_id") != current_user_id:
            raise ServiceError("Forbidden: you do not own this AI chat.", 403)

        # chat_id and tenant_id must never be updated from the body.
        AIChat.strip_protected(data)

        if not data:
            raise ServiceError("No updatable fields provided.", 400)

        try:
            response = (
                supabase.table(self.TABLE)
                .update(data)
                .eq("chat_id", chat_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 400)
        if not response.data:
            raise ServiceError("AI chat not found.", 404)
        return response.data[0]

    def delete(self, chat_id, current_user_id):
        # Owner-only: fetch first (404 if missing), then 403 if not the owner.
        existing = self.get_by_id(chat_id)
        if existing.get("tenant_id") != current_user_id:
            raise ServiceError("Forbidden: you do not own this AI chat.", 403)

        try:
            response = (
                supabase.table(self.TABLE)
                .delete()
                .eq("chat_id", chat_id)
                .execute()
            )
        except Exception as e:
            raise ServiceError(str(e), 500)
        if not response.data:
            raise ServiceError("AI chat not found.", 404)
        return {"message": "AI chat deleted successfully."}
