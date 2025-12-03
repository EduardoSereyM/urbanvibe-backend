-- 005_add_directions_tip.sql

-- Agrega columna directions_tip a la tabla venues
ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS directions_tip TEXT;
