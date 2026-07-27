from models.user import User


class ProjectManager(User):
    """Domain model for a project manager: a User plus the public.project_managers profile.

    Inherits user_id and role from User and adds the manager-specific profile
    fields (manager_name, phone). Data model only - no database access.
    """

    def __init__(self, user_id=None, role=None, manager_name=None, phone=None):
        super().__init__(user_id=user_id, role=role)
        self.manager_name = manager_name
        self.phone = phone

    @classmethod
    def from_dict(cls, data):
        """Build a ProjectManager from a plain dict (e.g. a merged users + project_managers row)."""
        data = data or {}
        return cls(
            user_id=data.get("user_id"),
            role=data.get("role"),
            manager_name=data.get("manager_name"),
            phone=data.get("phone"),
        )

    def to_dict(self):
        """Serialize to a plain dict combining the base User and manager fields."""
        base = super().to_dict()
        base.update(
            {
                "manager_name": self.manager_name,
                "phone": self.phone,
            }
        )
        return base
