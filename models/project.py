class Project:
    """Plain data model for a row in the public.projects table."""

    # Fields that must be present (and non-empty) when creating a project.
    REQUIRED_FIELDS = ["project_name", "location", "status"]

    # project_id is the primary key; it must never be set or changed via the body.
    PROTECTED_FIELDS = ["project_id"]

    def __init__(
        self,
        project_id=None,
        project_name=None,
        location=None,
        status=None,
        building_company_id=None,
        project_manager_id=None,
    ):
        self.project_id = project_id
        self.project_name = project_name
        self.location = location
        self.status = status
        self.building_company_id = building_company_id
        self.project_manager_id = project_manager_id

    @classmethod
    def from_dict(cls, data):
        """Build a Project from a plain dict (e.g. a Supabase row)."""
        data = data or {}
        return cls(
            project_id=data.get("project_id"),
            project_name=data.get("project_name"),
            location=data.get("location"),
            status=data.get("status"),
            building_company_id=data.get("building_company_id"),
            project_manager_id=data.get("project_manager_id"),
        )

    def to_dict(self):
        """Serialize back to a plain dict matching the table columns."""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "location": self.location,
            "status": self.status,
            "building_company_id": self.building_company_id,
            "project_manager_id": self.project_manager_id,
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
        """Remove protected fields (e.g. the primary key) from an update payload."""
        for field in cls.PROTECTED_FIELDS:
            data.pop(field, None)
        return data
