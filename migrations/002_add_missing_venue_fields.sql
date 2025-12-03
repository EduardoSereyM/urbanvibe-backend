-- 002_add_missing_venue_fields.sql

-- Agrega columnas faltantes en la tabla venues que son requeridas por el backend
ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS operational_status VARCHAR(20) DEFAULT 'open',
ADD COLUMN IF NOT EXISTS is_operational BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS region_state VARCHAR(100),
ADD COLUMN IF NOT EXISTS opening_hours JSONB DEFAULT '{}'::jsonb;
