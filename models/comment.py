class Comment:
    """Plain data model for a row in the public.comments table."""

    # content is the only NOT NULL column without a default that the client must
    # supply. comment_date defaults to CURRENT_DATE, project_id comes from the
    # URL, and user_id is nullable/optional.
    REQUIRED_FIELDS = ["content"]

    # comment_id (PK, auto-generated) and project_id (FK, from the URL) must
    # never be set or changed via the body. user_id is the author's identity and
    # must come from the authenticated token, never from the client body.
    PROTECTED_FIELDS = ["comment_id", "project_id", "user_id"]

    def __init__(
        self,
        comment_id=None,
        content=None,
        comment_date=None,
        project_id=None,
        user_id=None,
    ):
        self.comment_id = comment_id
        self.content = content
        self.comment_date = comment_date
        self.project_id = project_id
        self.user_id = user_id

    @classmethod
    def from_dict(cls, data):
        """Build a Comment from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            comment_id=data.get("comment_id"),
            content=data.get("content"),
            comment_date=data.get("comment_date"),
            project_id=data.get("project_id"),
            user_id=data.get("user_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "comment_id": self.comment_id,
            "content": self.content,
            "comment_date": self.comment_date,
            "project_id": self.project_id,
            "user_id": self.user_id,
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
        """Remove protected fields (PK and project FK) from a payload."""
        for field in cls.PROTECTED_FIELDS:
            data.pop(field, None)
        return data
