from models.user import User


class BuildingCompany(User):
    """Domain model for a building company: a User plus the public.building_companies profile.

    Inherits user_id and role from User and adds the company-specific profile
    fields (company_name, phone). Data model only - no database access.
    """

    def __init__(self, user_id=None, role=None, company_name=None, phone=None):
        super().__init__(user_id=user_id, role=role)
        self.company_name = company_name
        self.phone = phone

    @classmethod
    def from_dict(cls, data):
        """Build a BuildingCompany from a plain dict (e.g. a merged users + building_companies row)."""
        data = data or {}
        return cls(
            user_id=data.get("user_id"),
            role=data.get("role"),
            company_name=data.get("company_name"),
            phone=data.get("phone"),
        )

    def to_dict(self):
        """Serialize to a plain dict combining the base User and company fields."""
        base = super().to_dict()
        base.update(
            {
                "company_name": self.company_name,
                "phone": self.phone,
            }
        )
        return base
