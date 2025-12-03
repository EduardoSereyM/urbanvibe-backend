-- 004_add_google_place_id.sql

-- Agrega columna google_place_id a la tabla venues
ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS google_place_id VARCHAR(255);

-- Opcional: Agregar índice único si se desea evitar duplicados de lugares de Google
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_venues_google_place_id ON public.venues(google_place_id);
