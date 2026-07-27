class Image:
    """Plain data model for a row in the public.images table."""

    # image_path is the only NOT NULL column without a default that the client
    # must supply. upload_date defaults to CURRENT_DATE, and project_id comes
    # from the URL.
    REQUIRED_FIELDS = ["image_path"]

    # image_id (PK, auto-generated) and project_id (FK, from the URL) must never
    # be set or changed via the body.
    PROTECTED_FIELDS = ["image_id", "project_id"]

    def __init__(
        self,
        image_id=None,
        image_path=None,
        upload_date=None,
        project_id=None,
    ):
        self.image_id = image_id
        self.image_path = image_path
        self.upload_date = upload_date
        self.project_id = project_id

    @classmethod
    def from_dict(cls, data):
        """Build an Image from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            image_id=data.get("image_id"),
            image_path=data.get("image_path"),
            upload_date=data.get("upload_date"),
            project_id=data.get("project_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "image_id": self.image_id,
            "image_path": self.image_path,
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
