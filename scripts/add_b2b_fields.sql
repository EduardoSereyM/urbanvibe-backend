-- ============================================================================
-- AGREGAR CAMPOS B2B A LA TABLA VENUES
-- ============================================================================

ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS company_tax_id VARCHAR(50),
ADD COLUMN IF NOT EXISTS ownership_proof_url TEXT;

-- Documentación de columnas
COMMENT ON COLUMN public.venues.company_tax_id IS
  'Identificador tributario de la empresa (RUT/DNI/RUC/etc.) usado para verificación del local.';

COMMENT ON COLUMN public.venues.ownership_proof_url IS
  'URL en storage (venues-media) del documento que acredita la propiedad o administración del local.';
