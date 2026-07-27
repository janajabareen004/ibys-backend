class AIChat:
    """Plain data model for a row in the public.ai_chats table."""

    # question is the only NOT NULL column without a default that the client must
    # supply. answer and tenant_id are nullable, and created_at defaults to now().
    REQUIRED_FIELDS = ["question"]

    # chat_id (PK) is auto-generated and must never be set or changed via the
    # body. tenant_id is the owner's identity and must come from the authenticated
    # token, never from the client body.
    PROTECTED_FIELDS = ["chat_id", "tenant_id"]

    def __init__(
        self,
        chat_id=None,
        question=None,
        answer=None,
        created_at=None,
        tenant_id=None,
    ):
        self.chat_id = chat_id
        self.question = question
        self.answer = answer
        self.created_at = created_at
        self.tenant_id = tenant_id

    @classmethod
    def from_dict(cls, data):
        """Build an AIChat from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            chat_id=data.get("chat_id"),
            question=data.get("question"),
            answer=data.get("answer"),
            created_at=data.get("created_at"),
            tenant_id=data.get("tenant_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "chat_id": self.chat_id,
            "question": self.question,
            "answer": self.answer,
            "created_at": self.created_at,
            "tenant_id": self.tenant_id,
        }

    @classmethod
    def validate_create(cls, data):
        """Return an error message if the create body is invalid, otherwise None."""
        if not isinstance(data, dict) or not data:
            return "Request body must be a non-empty JSON object."
        missing = [f for f in cls.REQUIRED_FIELDS if not data.get(f)]
        if missing:
            return f"Missing required field(s): {', '.join(missing)}."
        return None

    @classmethod
    def strip_protected(cls, data):
        """Remove protected fields (the auto-generated PK) from a payload."""
        for field in cls.PROTECTED_FIELDS:
            data.pop(field, None)
        return data
