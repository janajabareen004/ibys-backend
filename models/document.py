class Document:
    """Plain data model for a row in the public.documents table."""

    # file_name is the only NOT NULL column without a default that the client
    # must supply. upload_date defaults to CURRENT_DATE, and project_id comes
    # from the URL.
    REQUIRED_FIELDS = ["file_name"]

    # document_id (PK, auto-generated) and project_id (FK, from the URL) must
    # never be set or changed via the body.
    PROTECTED_FIELDS = ["document_id", "project_id"]

    def __init__(
        self,
        document_id=None,
        file_name=None,
        upload_date=None,
        project_id=None,
    ):
        self.document_id = document_id
        self.file_name = file_name
        self.upload_date = upload_date
        self.project_id = project_id

    @classmethod
    def from_dict(cls, data):
        """Build a Document from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            document_id=data.get("document_id"),
            file_name=data.get("file_name"),
            upload_date=data.get("upload_date"),
            project_id=data.get("project_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "document_id": self.document_id,
            "file_name": self.file_name,
            "upload_date": self.upload_date,
            "project_id": self.project_id,
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
