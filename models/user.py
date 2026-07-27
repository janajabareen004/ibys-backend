class User:
    """Plain data model for a row in the public.users table."""

    # Allowed role enum values.
    VALID_ROLES = ["TENANT", "MANAGER", "BUILDING_COMPANY"]

    # Maps each role to its dedicated table and the required "name" column.
    ROLE_CONFIG = {
        "TENANT": {"table": "tenants", "name_field": "full_name"},
        "MANAGER": {"table": "project_managers", "name_field": "manager_name"},
        "BUILDING_COMPANY": {"table": "building_companies", "name_field": "company_name"},
    }

    def __init__(self, user_id=None, role=None):
        self.user_id = user_id
        self.role = role

    @classmethod
    def from_dict(cls, data):
        """Build a User from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            user_id=data.get("user_id"),
            role=data.get("role"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "user_id": self.user_id,
            "role": self.role,
        }

    @classmethod
    def role_config(cls, role):
        """Return the {table, name_field} config for a role, or None."""
        return cls.ROLE_CONFIG.get(role)

    @classmethod
    def is_valid_role(cls, role):
        return role in cls.VALID_ROLES
