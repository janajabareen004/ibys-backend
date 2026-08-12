-- Phase 1: Project Manager Tasks feature.
-- Creates the public.tasks table. Tasks belong to a project (ON DELETE CASCADE);
-- manager ownership is derived via projects.project_manager_id in the API layer,
-- consistent with the existing requests/meetings/progress manager scoping.

CREATE TABLE IF NOT EXISTS public.tasks (
    task_id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id       bigint NOT NULL REFERENCES public.projects(project_id) ON DELETE CASCADE,
    title            text NOT NULL,
    description      text,
    assigned_to      text,
    stage            text,
    due_date         date,
    priority         text NOT NULL DEFAULT 'medium',
    status           text NOT NULL DEFAULT 'pending',
    progress_percent integer NOT NULL DEFAULT 0,
    created_at       timestamptz NOT NULL DEFAULT now(),
    updated_at       timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT tasks_progress_percent_range
        CHECK (progress_percent >= 0 AND progress_percent <= 100)
);

-- Speeds up the common "tasks for a project" lookup used by the manager API.
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON public.tasks(project_id);
