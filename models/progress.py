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
        progress_percent=None,
    ):
        self.progress_id = progress_id
        self.task_name = task_name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.project_id = project_id
        # Nullable 0-100 completion percentage. Null for legacy rows.
        self.progress_percent = progress_percent

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
            progress_percent=data.get("progress_percent"),
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
            "progress_percent": self.progress_percent,
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

    @staticmethod
    def validate_progress_percent(value):
        """Validate an optional progress_percent (integer 0-100).

        Returns an error message, or None when the value is absent/None or valid.
        Accepts int or numeric strings; rejects out-of-range or non-numeric input.
        """
        if value is None:
            return None
        if isinstance(value, bool):
            return "progress_percent must be an integer between 0 and 100."
        try:
            number = int(value)
        except (ValueError, TypeError):
            return "progress_percent must be an integer between 0 and 100."
        if number < 0 or number > 100:
            return "progress_percent must be between 0 and 100."
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
