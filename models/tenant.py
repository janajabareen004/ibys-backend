from models.user import User


class Tenant(User):
    """Domain model for a tenant: a User plus the public.tenants profile.

    Inherits user_id and role from User and adds the tenant-specific profile
    fields (full_name, phone). Data model only - no database access.
    """

    def __init__(self, user_id=None, role=None, full_name=None, phone=None):
        super().__init__(user_id=user_id, role=role)
        self.full_name = full_name
        self.phone = phone

    @classmethod
    def from_dict(cls, data):
        """Build a Tenant from a plain dict (e.g. a merged users + tenants row)."""
        data = data or {}
        return cls(
            user_id=data.get("user_id"),
            role=data.get("role"),
            full_name=data.get("full_name"),
            phone=data.get("phone"),
        )

    def to_dict(self):
        """Serialize to a plain dict combining the base User and tenant fields."""
        base = super().to_dict()
        base.update(
            {
                "full_name": self.full_name,
                "phone": self.phone,
            }
        )
        return base
