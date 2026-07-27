class Apartment:
    """Plain data model for a row in the public.apartments table."""

    # apartment_number is the only NOT NULL column without a default that the
    # client must supply. floor, size, status, and tenant_id are nullable, and
    # project_id comes from the URL.
    REQUIRED_FIELDS = ["apartment_number"]

    # apartment_id (PK, auto-generated) and project_id (FK, from the URL) must
    # never be set or changed via the body.
    PROTECTED_FIELDS = ["apartment_id", "project_id"]

    def __init__(
        self,
        apartment_id=None,
        apartment_number=None,
        floor=None,
        size=None,
        status=None,
        tenant_id=None,
        project_id=None,
    ):
        self.apartment_id = apartment_id
        self.apartment_number = apartment_number
        self.floor = floor
        self.size = size
        self.status = status
        self.tenant_id = tenant_id
        self.project_id = project_id

    @classmethod
    def from_dict(cls, data):
        """Build an Apartment from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            apartment_id=data.get("apartment_id"),
            apartment_number=data.get("apartment_number"),
            floor=data.get("floor"),
            size=data.get("size"),
            status=data.get("status"),
            tenant_id=data.get("tenant_id"),
            project_id=data.get("project_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "apartment_id": self.apartment_id,
            "apartment_number": self.apartment_number,
            "floor": self.floor,
            "size": self.size,
            "status": self.status,
            "tenant_id": self.tenant_id,
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
