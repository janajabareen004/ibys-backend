class ManagerNotification:
    """Plain data model for a row in the public.manager_notifications table.

    Manager notifications are server-generated, per-recipient attention items and
    are read (and marked read) only by their owning manager. `type` uses the
    frontend ManagedNotification category vocabulary so both sides agree.
    """

    # The category vocabulary the Notifications UI knows how to render. Used only
    # as a soft guard; unknown types still map to "system" on the frontend.
    KNOWN_TYPES = {
        "project",
        "task",
        "meeting",
        "construction",
        "system",
        "request",
    }

    def __init__(
        self,
        id=None,
        recipient_id=None,
        project_id=None,
        type=None,
        title=None,
        message=None,
        is_read=None,
        created_at=None,
    ):
        self.id = id
        self.recipient_id = recipient_id
        self.project_id = project_id
        self.type = type
        self.title = title
        self.message = message
        self.is_read = is_read
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data):
        data = data or {}
        return cls(
            id=data.get("id"),
            recipient_id=data.get("recipient_id"),
            project_id=data.get("project_id"),
            type=data.get("type"),
            title=data.get("title"),
            message=data.get("message"),
            is_read=data.get("is_read"),
            created_at=data.get("created_at"),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "recipient_id": self.recipient_id,
            "project_id": self.project_id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at,
        }
