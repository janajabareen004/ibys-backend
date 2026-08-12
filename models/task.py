from datetime import date


class Task:
    """Plain data model for a row in the public.tasks table."""

    # Fields that must be present (and non-empty) when creating a task.
    REQUIRED_FIELDS = ["title"]

    # task_id (PK) and project_id (FK) must never be changed via the body;
    # project_id is taken only from the URL. created_at/updated_at are server-managed.
    PROTECTED_FIELDS = ["task_id", "project_id", "created_at", "updated_at"]

    # Basic allow-lists. Values are validated case-insensitively and stored
    # lowercase. These cover the frontend's canonical values plus the table
    # defaults; unknown values are rejected safely.
    ALLOWED_STATUSES = {
        "pending",
        "not_started",
        "in_progress",
        "waiting",
        "completed",
        "blocked",
    }
    ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}

    @staticmethod
    def validate_create(data):
        """Return an error message if the create body is invalid, otherwise None."""
        if not isinstance(data, dict) or not data:
            return "Request body must be a non-empty JSON object."
        missing = [
            f
            for f in Task.REQUIRED_FIELDS
            if not (isinstance(data.get(f), str) and data.get(f).strip())
        ]
        if missing:
            return f"Missing required field(s): {', '.join(missing)}."
        return None

    @staticmethod
    def validate_due_date(value):
        """Validate an optional due_date (YYYY-MM-DD). Returns an error or None."""
        if value is None or value == "":
            return None
        try:
            date.fromisoformat(value)
        except (ValueError, TypeError):
            return f"Invalid date format: '{value}'. Expected YYYY-MM-DD."
        return None

    @staticmethod
    def validate_progress_percent(value):
        """Validate an optional progress_percent (integer 0-100).

        Returns an error message, or None when the value is absent/None or valid.
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

    @staticmethod
    def validate_status(value):
        """Validate an optional status against the allow-list. Returns error or None."""
        if value is None:
            return None
        if not isinstance(value, str) or value.strip().lower() not in Task.ALLOWED_STATUSES:
            return f"Invalid status. Allowed: {', '.join(sorted(Task.ALLOWED_STATUSES))}."
        return None

    @staticmethod
    def validate_priority(value):
        """Validate an optional priority against the allow-list. Returns error or None."""
        if value is None:
            return None
        if not isinstance(value, str) or value.strip().lower() not in Task.ALLOWED_PRIORITIES:
            return f"Invalid priority. Allowed: {', '.join(sorted(Task.ALLOWED_PRIORITIES))}."
        return None

    @classmethod
    def strip_protected(cls, data):
        """Remove protected fields (PK, FK, timestamps) from a payload."""
        for field in cls.PROTECTED_FIELDS:
            data.pop(field, None)
        return data
