-- Add a nullable 0-100 completion percentage to construction progress rows.
-- Nullable so existing rows keep working; frontend falls back to the
-- status-derived percentage when progress_percent IS NULL.

ALTER TABLE public.progress
    ADD COLUMN IF NOT EXISTS progress_percent integer;

ALTER TABLE public.progress
    DROP CONSTRAINT IF EXISTS progress_percent_range;

ALTER TABLE public.progress
    ADD CONSTRAINT progress_percent_range
    CHECK (progress_percent IS NULL OR (progress_percent >= 0 AND progress_percent <= 100));
