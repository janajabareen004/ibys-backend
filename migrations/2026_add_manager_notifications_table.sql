-- Project Manager Notifications.
-- Targeted, per-recipient attention items (distinct from activity_events, which
-- is a project-wide historical audit feed with no recipient/read state). Rows
-- are server-generated after a primary mutation succeeds and are always scoped
-- to a single recipient (the owning project manager's user id).
--
-- Scope for the initial implementation: exactly one notification is created when
-- a NEW tenant request is submitted, addressed to the manager who owns the
-- request's project (projects.project_manager_id, resolved via the tenant's
-- apartment). `type` uses the frontend ManagedNotification category vocabulary
-- (project, task, meeting, construction, system, request).
--
-- This table is independent of the existing tenant-facing `notifications` table,
-- which is left completely untouched.

CREATE TABLE IF NOT EXISTS public.manager_notifications (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recipient_id uuid NOT NULL,
    project_id   bigint REFERENCES public.projects(project_id) ON DELETE CASCADE,
    type         text NOT NULL,
    title        text NOT NULL,
    message      text,
    is_read      boolean NOT NULL DEFAULT false,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_manager_notifications_recipient_id ON public.manager_notifications(recipient_id);
CREATE INDEX IF NOT EXISTS idx_manager_notifications_created_at ON public.manager_notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_manager_notifications_project_id ON public.manager_notifications(project_id);
