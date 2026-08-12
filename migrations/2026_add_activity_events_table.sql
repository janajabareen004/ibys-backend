-- Project Manager Activity Log.
-- Server-generated, read-only project activity feed. Events are recorded by the
-- backend after a primary mutation succeeds. Manager ownership is derived via
-- projects.project_manager_id in the API layer, consistent with the existing
-- tasks/team/photos/documents/stages manager scoping. `type` uses the frontend
-- ActivityEvent vocabulary (task_created, task_updated, task_deleted,
-- task_completed, meeting_scheduled, meeting_updated, stage_updated,
-- photo_uploaded, document_added, request_received, request_replied,
-- request_approved, request_rejected, note_added).

CREATE TABLE IF NOT EXISTS public.activity_events (
    event_id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id bigint NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    actor      text,
    type       text NOT NULL,
    message    text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_activity_events_project_id ON public.activity_events(project_id);
CREATE INDEX IF NOT EXISTS idx_activity_events_created_at ON public.activity_events(created_at);
