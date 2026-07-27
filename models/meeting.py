class Meeting:
    """Plain data model for a row in the public.meetings table."""

    # meeting_date and meeting_time are NOT NULL with no default and must be
    # supplied by the client. purpose is nullable, status defaults to 'PENDING',
    # project_id comes from the URL, and project_manager_id is nullable.
    REQUIRED_FIELDS = ["meeting_date", "meeting_time"]

    # meeting_id (PK, auto-generated) and project_id (FK, from the URL) must
    # never be set or changed via the body.
    PROTECTED_FIELDS = ["meeting_id", "project_id"]

    def __init__(
        self,
        meeting_id=None,
        meeting_date=None,
        meeting_time=None,
        purpose=None,
        status=None,
        project_id=None,
        project_manager_id=None,
    ):
        self.meeting_id = meeting_id
        self.meeting_date = meeting_date
        self.meeting_time = meeting_time
        self.purpose = purpose
        self.status = status
        self.project_id = project_id
        self.project_manager_id = project_manager_id

    @classmethod
    def from_dict(cls, data):
        """Build a Meeting from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            meeting_id=data.get("meeting_id"),
            meeting_date=data.get("meeting_date"),
            meeting_time=data.get("meeting_time"),
            purpose=data.get("purpose"),
            status=data.get("status"),
            project_id=data.get("project_id"),
            project_manager_id=data.get("project_manager_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "meeting_id": self.meeting_id,
            "meeting_date": self.meeting_date,
            "meeting_time": self.meeting_time,
            "purpose": self.purpose,
            "status": self.status,
            "project_id": self.project_id,
            "project_manager_id": self.project_manager_id,
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
