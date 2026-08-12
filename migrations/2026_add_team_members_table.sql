-- Project Manager Team feature.
-- Project-scoped team roster. Manager ownership is derived via
-- projects.project_manager_id in the API layer, consistent with the existing
-- tasks/photos/documents/stages manager scoping. Workload is intentionally NOT
-- stored here: it is computed from real tasks in the frontend (Phase 1).

CREATE TABLE IF NOT EXISTS public.team_members (
    member_id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id   bigint NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    name         text NOT NULL,
    role         text,
    email        text,
    phone        text,
    availability text NOT NULL DEFAULT 'available',
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT team_members_availability_check
        CHECK (availability IN ('available', 'busy', 'off'))
);

CREATE INDEX IF NOT EXISTS idx_team_members_project_id ON public.team_members(project_id);
