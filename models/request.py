class Request:
    """Plain data model for a row in the public.requests table."""

    # description and status are NOT NULL with no default and must be supplied by
    # the client. request_date defaults to CURRENT_DATE, and tenant_id is nullable.
    REQUIRED_FIELDS = ["description", "status"]

    # request_id (PK) is auto-generated and must never be set or changed via the
    # body. tenant_id is the owner's identity and must come from the authenticated
    # token, never from the client body.
    PROTECTED_FIELDS = ["request_id", "tenant_id"]

    def __init__(
        self,
        request_id=None,
        request_date=None,
        description=None,
        status=None,
        tenant_id=None,
    ):
        self.request_id = request_id
        self.request_date = request_date
        self.description = description
        self.status = status
        self.tenant_id = tenant_id

    @classmethod
    def from_dict(cls, data):
        """Build a Request from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            request_id=data.get("request_id"),
            request_date=data.get("request_date"),
            description=data.get("description"),
            status=data.get("status"),
            tenant_id=data.get("tenant_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "request_id": self.request_id,
            "request_date": self.request_date,
            "description": self.description,
            "status": self.status,
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
