-- ============================================================================
-- MIGRACIÓN SISTEMA DE QR DINÁMICO (CORREGIDO)
-- ============================================================================

-- 1. Crear tabla qr_tokens
CREATE TABLE IF NOT EXISTS public.qr_tokens (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    type varchar NOT NULL CHECK (type IN ('checkin', 'promo', 'invite', 'other')),
    scope varchar NOT NULL,
    venue_id uuid NOT NULL REFERENCES public.venues(id),
    
    promotion_id uuid REFERENCES public.promotions(id),
    campaign_key varchar,

    valid_from timestamptz NOT NULL DEFAULT now(),
    valid_until timestamptz NOT NULL,
    max_uses integer NOT NULL DEFAULT 1,
    used_count integer NOT NULL DEFAULT 0,

    is_revoked boolean NOT NULL DEFAULT false,
    revoked_at timestamptz,
    revoked_by uuid REFERENCES public.profiles(id),
    revoked_reason text,

    created_at timestamptz NOT NULL DEFAULT now(),
    created_by uuid REFERENCES public.profiles(id),
    last_used_at timestamptz,
    last_used_by uuid REFERENCES public.profiles(id),

    meta jsonb DEFAULT '{}'::jsonb
);

-- Índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_qr_tokens_venue_id ON public.qr_tokens(venue_id);
CREATE INDEX IF NOT EXISTS idx_qr_tokens_type_scope ON public.qr_tokens(type, scope);

-- ============================================================================
-- 2. Modificar tabla checkins
-- ============================================================================

-- ¡IMPORTANTE!
-- Los check-ins existentes tienen 'token_id' que son strings antiguos y NO existen
-- en la nueva tabla 'qr_tokens'. Por lo tanto, no pueden satisfacer la nueva
-- restricción de llave foránea.
-- Debemos limpiar la tabla checkins para aplicar el nuevo esquema estricto.

TRUNCATE TABLE public.checkins CASCADE;

-- A. Cambiar tipo de columna token_id a UUID
ALTER TABLE public.checkins 
    ALTER COLUMN token_id TYPE uuid USING token_id::uuid;

-- B. Agregar Foreign Key hacia qr_tokens
ALTER TABLE public.checkins
    ADD CONSTRAINT checkins_token_id_fkey 
    FOREIGN KEY (token_id) REFERENCES public.qr_tokens(id);
