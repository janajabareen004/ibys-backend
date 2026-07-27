from datetime import date


class Progress:
    """Plain data model for a row in the public.progress table."""

    # Fields that must be present (and non-empty) when creating a progress record.
    REQUIRED_FIELDS = ["task_name", "start_date", "end_date", "status"]

    # progress_id (PK) and project_id (FK) must never be changed via the body.
    PROTECTED_FIELDS = ["progress_id", "project_id"]

    def __init__(
        self,
        progress_id=None,
        task_name=None,
        start_date=None,
        end_date=None,
        status=None,
        project_id=None,
    ):
        self.progress_id = progress_id
        self.task_name = task_name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.project_id = project_id

    @classmethod
    def from_dict(cls, data):
        """Build a Progress from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            progress_id=data.get("progress_id"),
            task_name=data.get("task_name"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            status=data.get("status"),
            project_id=data.get("project_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "progress_id": self.progress_id,
            "task_name": self.task_name,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "project_id": self.project_id,
        }

    @staticmethod
    def parse_date(value):
        """Parse an ISO (YYYY-MM-DD) date string. Returns (date, None) or (None, error)."""
        try:
            return date.fromisoformat(value), None
        except (ValueError, TypeError):
            return None, f"Invalid date format: '{value}'. Expected YYYY-MM-DD."

    @classmethod
    def validate_date_range(cls, start_value, end_value):
        """Validate that start_date is not later than end_date. Returns an error message or None."""
        start, error = cls.parse_date(start_value)
        if error:
            return error
        end, error = cls.parse_date(end_value)
        if error:
            return error
        if start > end:
            return "start_date cannot be later than end_date."
        return None

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
        """Remove protected fields (PK and FK) from an update/create payload."""
        for field in cls.PROTECTED_FIELDS:
            data.pop(field, None)
        return data
