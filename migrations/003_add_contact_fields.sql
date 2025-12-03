-- 003_add_contact_fields.sql

-- Agrega columnas de contacto y country_code a la tabla venues
ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS contact_email VARCHAR(255),
ADD COLUMN IF NOT EXISTS website TEXT,
ADD COLUMN IF NOT EXISTS country_code VARCHAR(10);
