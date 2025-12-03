-- 006_full_gamification_schema.sql
-- Based on the Master Blueprint provided by the user.

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ✅ 1. AJUSTES A TABLA venues
ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS menu_media_urls jsonb DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS menu_last_updated_at timestamptz;

ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS referral_code text UNIQUE,
ADD COLUMN IF NOT EXISTS referred_by_user_id uuid,
ADD COLUMN IF NOT EXISTS referred_by_venue_id uuid;

-- FKs for venues referrals (check if they exist first or just add constraint safely)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'venues_referred_by_user_fk') THEN
        ALTER TABLE public.venues
        ADD CONSTRAINT venues_referred_by_user_fk
        FOREIGN KEY (referred_by_user_id)
        REFERENCES public.profiles(id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'venues_referred_by_venue_fk') THEN
        ALTER TABLE public.venues
        ADD CONSTRAINT venues_referred_by_venue_fk
        FOREIGN KEY (referred_by_venue_id)
        REFERENCES public.venues(id);
    END IF;
END $$;

-- Nuevas columnas de características (JSONB)
ALTER TABLE public.venues
  ADD COLUMN IF NOT EXISTS connectivity_features jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS accessibility_features jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS space_features jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS comfort_features jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS audience_features jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS entertainment_features jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS dietary_options jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS access_features jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS security_features jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS mood_tags jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS occasion_tags jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS music_profile jsonb DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS crowd_profile jsonb DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS capacity_estimate smallint,
  ADD COLUMN IF NOT EXISTS seated_capacity smallint,
  ADD COLUMN IF NOT EXISTS standing_allowed boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS noise_level character varying,
  ADD COLUMN IF NOT EXISTS pricing_profile jsonb DEFAULT '{}'::jsonb;

-- Comentarios
COMMENT ON COLUMN public.venues.connectivity_features IS 'JSONB array de slugs sobre conectividad';
COMMENT ON COLUMN public.venues.accessibility_features IS 'JSONB array de slugs de accesibilidad física';
COMMENT ON COLUMN public.venues.space_features IS 'JSONB array de slugs sobre el espacio físico y layout';
COMMENT ON COLUMN public.venues.comfort_features IS 'JSONB array de slugs sobre confort climático/acústico';
COMMENT ON COLUMN public.venues.audience_features IS 'JSONB array de slugs de público/uso familiar/mascotas';
COMMENT ON COLUMN public.venues.entertainment_features IS 'JSONB array de slugs de entretenimiento';
COMMENT ON COLUMN public.venues.dietary_options IS 'JSONB array de slugs de opciones dietarias';
COMMENT ON COLUMN public.venues.access_features IS 'JSONB array de slugs relativos al acceso/transporte';
COMMENT ON COLUMN public.venues.security_features IS 'JSONB array de slugs de seguridad del local';
COMMENT ON COLUMN public.venues.mood_tags IS 'JSONB array de slugs que describen el ambiente/vibe';
COMMENT ON COLUMN public.venues.occasion_tags IS 'JSONB array de slugs que describen para qué ocasiones es ideal';
COMMENT ON COLUMN public.venues.music_profile IS 'JSONB que describe perfil musical';
COMMENT ON COLUMN public.venues.crowd_profile IS 'JSONB que describe el perfil de público típico';
COMMENT ON COLUMN public.venues.capacity_estimate IS 'Capacidad total aproximada del local';
COMMENT ON COLUMN public.venues.seated_capacity IS 'Cantidad aproximada de personas con asiento disponible';
COMMENT ON COLUMN public.venues.standing_allowed IS 'Indica si se permite público de pie';
COMMENT ON COLUMN public.venues.noise_level IS 'Nivel de ruido típico del local';
COMMENT ON COLUMN public.venues.pricing_profile IS 'JSONB que resume el perfil de precios';

-- ✅ 2. AJUSTES A TABLA profiles
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS referral_code text UNIQUE,
ADD COLUMN IF NOT EXISTS referred_by_user_id uuid;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_referred_by_user_fk') THEN
        ALTER TABLE public.profiles
        ADD CONSTRAINT profiles_referred_by_user_fk
        FOREIGN KEY (referred_by_user_id)
        REFERENCES public.profiles(id);
    END IF;
END $$;

COMMENT ON COLUMN public.profiles.preferences IS 'JSONB de preferencias del usuario';

-- ✅ 3. PROMOCIONES — CAMPOS NUEVOS
-- Primero aseguramos que la tabla promotions exista (si no existe, la creamos básica, pero asumimos que existe por el contexto)
-- Si no existe, fallará, pero el usuario dijo "ALTER TABLE", así que asumimos existencia.

-- Agregamos columnas con checks
ALTER TABLE public.promotions
ADD COLUMN IF NOT EXISTS promo_type text DEFAULT 'standard',
ADD COLUMN IF NOT EXISTS reward_tier text,
ADD COLUMN IF NOT EXISTS points_cost integer,
ADD COLUMN IF NOT EXISTS is_recurring boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS schedule_config jsonb DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS total_units integer;

-- Constraints (hacerlo en bloque DO para evitar error si ya existen)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'promotions_promo_type_check') THEN
        ALTER TABLE public.promotions ADD CONSTRAINT promotions_promo_type_check CHECK (promo_type IN ('standard', 'uv_reward'));
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'promotions_reward_tier_check') THEN
        ALTER TABLE public.promotions ADD CONSTRAINT promotions_reward_tier_check CHECK (reward_tier IN ('LOW', 'MID', 'HIGH'));
    END IF;
END $$;

-- ✅ 4. TABLA NUEVA: reward_units
CREATE TABLE IF NOT EXISTS public.reward_units (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    promotion_id uuid NOT NULL,
    venue_id uuid NOT NULL,
    user_id uuid,
    qr_token_id uuid,
    status text NOT NULL DEFAULT 'available',
    assigned_at timestamptz,
    consumed_at timestamptz,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT reward_units_status_check CHECK (status IN ('available','reserved','consumed','expired'))
);

-- FKs reward_units
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'reward_units_promo_fk') THEN
        ALTER TABLE public.reward_units ADD CONSTRAINT reward_units_promo_fk FOREIGN KEY (promotion_id) REFERENCES public.promotions(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'reward_units_venue_fk') THEN
        ALTER TABLE public.reward_units ADD CONSTRAINT reward_units_venue_fk FOREIGN KEY (venue_id) REFERENCES public.venues(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'reward_units_user_fk') THEN
        ALTER TABLE public.reward_units ADD CONSTRAINT reward_units_user_fk FOREIGN KEY (user_id) REFERENCES public.profiles(id);
    END IF;
    -- qr_tokens table must exist. If not, this will fail. Assuming it exists.
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'reward_units_qr_fk') THEN
        ALTER TABLE public.reward_units ADD CONSTRAINT reward_units_qr_fk FOREIGN KEY (qr_token_id) REFERENCES public.qr_tokens(id);
    END IF;
END $$;

-- ✅ 5. TABLA NUEVA: redemptions
CREATE TABLE IF NOT EXISTS public.redemptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    venue_id uuid NOT NULL,
    promotion_id uuid,
    reward_unit_id uuid,
    qr_token_id uuid,
    points_spent integer DEFAULT 0,
    status text NOT NULL DEFAULT 'confirmed',
    created_at timestamptz DEFAULT now(),
    confirmed_at timestamptz,
    cancelled_at timestamptz,
    metadata jsonb DEFAULT '{}'::jsonb,

    CONSTRAINT redemptions_status_check CHECK (status IN ('pending','confirmed','cancelled'))
);

-- FKs redemptions
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'redemptions_user_fk') THEN
        ALTER TABLE public.redemptions ADD CONSTRAINT redemptions_user_fk FOREIGN KEY (user_id) REFERENCES public.profiles(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'redemptions_venue_fk') THEN
        ALTER TABLE public.redemptions ADD CONSTRAINT redemptions_venue_fk FOREIGN KEY (venue_id) REFERENCES public.venues(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'redemptions_promo_fk') THEN
        ALTER TABLE public.redemptions ADD CONSTRAINT redemptions_promo_fk FOREIGN KEY (promotion_id) REFERENCES public.promotions(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'redemptions_unit_fk') THEN
        ALTER TABLE public.redemptions ADD CONSTRAINT redemptions_unit_fk FOREIGN KEY (reward_unit_id) REFERENCES public.reward_units(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'redemptions_qr_fk') THEN
        ALTER TABLE public.redemptions ADD CONSTRAINT redemptions_qr_fk FOREIGN KEY (qr_token_id) REFERENCES public.qr_tokens(id);
    END IF;
END $$;

-- ✅ 6. TABLA NUEVA: gamification_events
CREATE TABLE IF NOT EXISTS public.gamification_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_code text UNIQUE NOT NULL,
    target_type text NOT NULL,
    description text,
    points integer NOT NULL DEFAULT 0,
    is_active boolean DEFAULT true,
    config jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),

    CONSTRAINT gamification_events_target_check CHECK (target_type IN ('user','venue'))
);

-- ✅ 7. TABLA NUEVA: gamification_logs
CREATE TABLE IF NOT EXISTS public.gamification_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_code text NOT NULL,
    user_id uuid,
    venue_id uuid,
    points integer NOT NULL,
    source_entity text,
    source_id uuid,
    details jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now()
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'gamelog_user_fk') THEN
        ALTER TABLE public.gamification_logs ADD CONSTRAINT gamelog_user_fk FOREIGN KEY (user_id) REFERENCES public.profiles(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'gamelog_venue_fk') THEN
        ALTER TABLE public.gamification_logs ADD CONSTRAINT gamelog_venue_fk FOREIGN KEY (venue_id) REFERENCES public.venues(id);
    END IF;
END $$;

-- ✅ 8. LOGS GENERALES
-- 8.1. menu_logs
CREATE TABLE IF NOT EXISTS public.menu_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_id uuid NOT NULL,
    action text NOT NULL,
    old_value jsonb,
    new_value jsonb,
    changed_by uuid,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT menu_logs_action_check CHECK (action IN ('created','updated','deleted'))
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'menulog_venue_fk') THEN
        ALTER TABLE public.menu_logs ADD CONSTRAINT menulog_venue_fk FOREIGN KEY (venue_id) REFERENCES public.venues(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'menulog_user_fk') THEN
        ALTER TABLE public.menu_logs ADD CONSTRAINT menulog_user_fk FOREIGN KEY (changed_by) REFERENCES public.profiles(id);
    END IF;
END $$;

-- 8.2. promo_logs
CREATE TABLE IF NOT EXISTS public.promo_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    promotion_id uuid NOT NULL,
    venue_id uuid NOT NULL,
    action text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT promo_logs_action_check CHECK (action IN ('created','updated','activated','deactivated','unit_created','unit_consumed'))
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'promolog_promo_fk') THEN
        ALTER TABLE public.promo_logs ADD CONSTRAINT promolog_promo_fk FOREIGN KEY (promotion_id) REFERENCES public.promotions(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'promolog_venue_fk') THEN
        ALTER TABLE public.promo_logs ADD CONSTRAINT promolog_venue_fk FOREIGN KEY (venue_id) REFERENCES public.venues(id);
    END IF;
END $$;

-- 8.3. qr_logs
CREATE TABLE IF NOT EXISTS public.qr_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    qr_token_id uuid NOT NULL,
    action text NOT NULL,
    user_id uuid,
    venue_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT qr_logs_action_check CHECK (action IN ('scanned','validated','revoked','expired','used'))
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'qrlogs_qr_fk') THEN
        ALTER TABLE public.qr_logs ADD CONSTRAINT qrlogs_qr_fk FOREIGN KEY (qr_token_id) REFERENCES public.qr_tokens(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'qrlogs_user_fk') THEN
        ALTER TABLE public.qr_logs ADD CONSTRAINT qrlogs_user_fk FOREIGN KEY (user_id) REFERENCES public.profiles(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'qrlogs_venue_fk') THEN
        ALTER TABLE public.qr_logs ADD CONSTRAINT qrlogs_venue_fk FOREIGN KEY (venue_id) REFERENCES public.venues(id);
    END IF;
END $$;

-- ✅ 2.2. Nuevas columnas en public.checkins
ALTER TABLE public.checkins
  ADD COLUMN IF NOT EXISTS session_duration_minutes integer,
  ADD COLUMN IF NOT EXISTS visit_purpose jsonb DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS spend_bucket character varying;

COMMENT ON COLUMN public.checkins.session_duration_minutes IS 'Duración aproximada de la visita en minutos';
COMMENT ON COLUMN public.checkins.visit_purpose IS 'JSONB array de slugs que describen el propósito de la visita';
COMMENT ON COLUMN public.checkins.spend_bucket IS 'Bucket de gasto del check-in: bajo | medio | alto';
