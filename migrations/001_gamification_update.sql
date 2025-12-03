-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. AJUSTES A TABLA venues
ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS menu_media_urls jsonb DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS menu_last_updated_at timestamptz;

ALTER TABLE public.venues
ADD COLUMN IF NOT EXISTS referral_code text UNIQUE,
ADD COLUMN IF NOT EXISTS referred_by_user_id uuid,
ADD COLUMN IF NOT EXISTS referred_by_venue_id uuid;

ALTER TABLE public.venues
ADD CONSTRAINT venues_referred_by_user_fk
FOREIGN KEY (referred_by_user_id)
REFERENCES public.profiles(id);

ALTER TABLE public.venues
ADD CONSTRAINT venues_referred_by_venue_fk
FOREIGN KEY (referred_by_venue_id)
REFERENCES public.venues(id);

-- 2. AJUSTES A TABLA profiles
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS referral_code text UNIQUE,
ADD COLUMN IF NOT EXISTS referred_by_user_id uuid;

ALTER TABLE public.profiles
ADD CONSTRAINT profiles_referred_by_user_fk
FOREIGN KEY (referred_by_user_id)
REFERENCES public.profiles(id);

-- 3. PROMOCIONES — CAMPOS NUEVOS
ALTER TABLE public.promotions
ADD COLUMN IF NOT EXISTS promo_type text
    CHECK (promo_type IN ('standard', 'uv_reward'))
    DEFAULT 'standard',

ADD COLUMN IF NOT EXISTS reward_tier text
    CHECK (reward_tier IN ('LOW', 'MID', 'HIGH')),

ADD COLUMN IF NOT EXISTS points_cost integer,

ADD COLUMN IF NOT EXISTS is_recurring boolean DEFAULT false,

ADD COLUMN IF NOT EXISTS schedule_config jsonb DEFAULT '{}'::jsonb,

ADD COLUMN IF NOT EXISTS total_units integer;

-- 4. TABLA NUEVA: reward_units (vouchers individuales)
CREATE TABLE IF NOT EXISTS public.reward_units (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    promotion_id uuid NOT NULL,
    venue_id uuid NOT NULL,
    user_id uuid,
    qr_token_id uuid,
    status text NOT NULL
        CHECK (status IN ('available','reserved','consumed','expired'))
        DEFAULT 'available',
    assigned_at timestamptz,
    consumed_at timestamptz,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT reward_units_promo_fk FOREIGN KEY (promotion_id)
        REFERENCES public.promotions(id),

    CONSTRAINT reward_units_venue_fk FOREIGN KEY (venue_id)
        REFERENCES public.venues(id),

    CONSTRAINT reward_units_user_fk FOREIGN KEY (user_id)
        REFERENCES public.profiles(id),

    CONSTRAINT reward_units_qr_fk FOREIGN KEY (qr_token_id)
        REFERENCES public.qr_tokens(id)
);

-- 5. TABLA NUEVA: redemptions (uso concreto de promoción/beneficio)
CREATE TABLE IF NOT EXISTS public.redemptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    venue_id uuid NOT NULL,
    promotion_id uuid,
    reward_unit_id uuid,
    qr_token_id uuid,
    points_spent integer DEFAULT 0,
    status text NOT NULL 
        CHECK (status IN ('pending','confirmed','cancelled'))
        DEFAULT 'confirmed',
    created_at timestamptz DEFAULT now(),
    confirmed_at timestamptz,
    cancelled_at timestamptz,
    metadata jsonb DEFAULT '{}'::jsonb,

    CONSTRAINT redemptions_user_fk FOREIGN KEY (user_id)
      REFERENCES public.profiles(id),

    CONSTRAINT redemptions_venue_fk FOREIGN KEY (venue_id)
      REFERENCES public.venues(id),

    CONSTRAINT redemptions_promo_fk FOREIGN KEY (promotion_id)
      REFERENCES public.promotions(id),

    CONSTRAINT redemptions_unit_fk FOREIGN KEY (reward_unit_id)
      REFERENCES public.reward_units(id),

    CONSTRAINT redemptions_qr_fk FOREIGN KEY (qr_token_id)
      REFERENCES public.qr_tokens(id)
);

-- 6. TABLA NUEVA: gamification_events (catálogo global)
CREATE TABLE IF NOT EXISTS public.gamification_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_code text UNIQUE NOT NULL,
    target_type text NOT NULL
        CHECK (target_type IN ('user','venue')),
    description text,
    points integer NOT NULL DEFAULT 0,
    is_active boolean DEFAULT true,
    config jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 7. TABLA NUEVA: gamification_logs
CREATE TABLE IF NOT EXISTS public.gamification_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    event_code text NOT NULL,
    user_id uuid,
    venue_id uuid,
    points integer NOT NULL,
    source_entity text,        -- 'checkin', 'promotion', 'redemption', 'referral', etc.
    source_id uuid,            -- id de la entidad origen
    details jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT gamelog_user_fk FOREIGN KEY (user_id)
        REFERENCES public.profiles(id),

    CONSTRAINT gamelog_venue_fk FOREIGN KEY (venue_id)
        REFERENCES public.venues(id)
);

-- 8. TABLAS NUEVAS DE LOGS GENERALES
-- 8.1. Logs de menú
CREATE TABLE IF NOT EXISTS public.menu_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    venue_id uuid NOT NULL,
    action text NOT NULL
        CHECK (action IN ('created','updated','deleted')),
    old_value jsonb,
    new_value jsonb,
    changed_by uuid,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT menulog_venue_fk FOREIGN KEY (venue_id)
        REFERENCES public.venues(id),

    CONSTRAINT menulog_user_fk FOREIGN KEY (changed_by)
        REFERENCES public.profiles(id)
);

-- 8.2. Logs de promociones
CREATE TABLE IF NOT EXISTS public.promo_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    promotion_id uuid NOT NULL,
    venue_id uuid NOT NULL,
    action text NOT NULL
        CHECK (action IN ('created','updated','activated','deactivated','unit_created','unit_consumed')),
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT promolog_promo_fk FOREIGN KEY (promotion_id)
        REFERENCES public.promotions(id),

    CONSTRAINT promolog_venue_fk FOREIGN KEY (venue_id)
        REFERENCES public.venues(id)
);

-- 8.3. Logs de QR
CREATE TABLE IF NOT EXISTS public.qr_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    qr_token_id uuid NOT NULL,
    action text NOT NULL
        CHECK (action IN ('scanned','validated','revoked','expired','used')),
    user_id uuid,
    venue_id uuid,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamptz DEFAULT now(),

    CONSTRAINT qrlogs_qr_fk FOREIGN KEY (qr_token_id)
        REFERENCES public.qr_tokens(id),

    CONSTRAINT qrlogs_user_fk FOREIGN KEY (user_id)
        REFERENCES public.profiles(id),

    CONSTRAINT qrlogs_venue_fk FOREIGN KEY (venue_id)
        REFERENCES public.venues(id)
);
