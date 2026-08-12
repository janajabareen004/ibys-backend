class TeamMember:
    """Plain data model for a row in the public.team_members table."""

    # Fields that must be present (and non-empty) when creating a member.
    REQUIRED_FIELDS = ["name"]

    # member_id (PK), project_id (FK) and timestamps must never be changed via
    # the body; project_id is taken only from the URL.
    PROTECTED_FIELDS = ["member_id", "project_id", "created_at", "updated_at"]

    # Availability is validated case-insensitively and stored lowercase.
    ALLOWED_AVAILABILITY = {"available", "busy", "off"}

    @staticmethod
    def validate_create(data):
        """Return an error message if the create body is invalid, otherwise None."""
        if not isinstance(data, dict) or not data:
            return "Request body must be a non-empty JSON object."
        missing = [
            f
            for f in TeamMember.REQUIRED_FIELDS
            if not (isinstance(data.get(f), str) and data.get(f).strip())
        ]
        if missing:
            return f"Missing required field(s): {', '.join(missing)}."
        return None

    @staticmethod
    def validate_availability(value):
        """Validate an optional availability against the allow-list. Returns error or None."""
        if value is None:
            return None
        if not isinstance(value, str) or value.strip().lower() not in TeamMember.ALLOWED_AVAILABILITY:
            return (
                "Invalid availability. Allowed: "
                + ", ".join(sorted(TeamMember.ALLOWED_AVAILABILITY))
                + "."
            )
        return None

    @classmethod
    def strip_protected(cls, data):
        """Remove protected fields (PK, FK, timestamps) from a payload."""
        for field in cls.PROTECTED_FIELDS:
            data.pop(field, None)
        return data
