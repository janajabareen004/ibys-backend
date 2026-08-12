class ActivityEvent:
    """Plain data model for a row in the public.activity_events table.

    Activity events are server-generated and read-only from the frontend. The
    `type` uses the frontend ActivityEvent vocabulary so both sides agree.
    """

    # The canonical set the frontend UI knows how to render. record_event uses
    # this only as a soft guard; unknown types are still stored (the UI simply
    # falls back to the raw type label), but callers should stick to these.
    KNOWN_TYPES = {
        "task_created",
        "task_updated",
        "task_deleted",
        "task_completed",
        "meeting_scheduled",
        "meeting_updated",
        "stage_updated",
        "photo_uploaded",
        "document_added",
        "request_received",
        "request_replied",
        "request_approved",
        "request_rejected",
        "note_added",
    }

    def __init__(self, event_id=None, project_id=None, actor=None, type=None, message=None, created_at=None):
        self.event_id = event_id
        self.project_id = project_id
        self.actor = actor
        self.type = type
        self.message = message
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data):
        data = data or {}
        return cls(
            event_id=data.get("event_id"),
            project_id=data.get("project_id"),
            actor=data.get("actor"),
            type=data.get("type"),
            message=data.get("message"),
            created_at=data.get("created_at"),
        )

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "project_id": self.project_id,
            "actor": self.actor,
            "type": self.type,
            "message": self.message,
            "created_at": self.created_at,
        }
