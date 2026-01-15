-- 011_advanced_gamification.sql

-- 1. BADGES Table
CREATE TABLE IF NOT EXISTS public.badges (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text UNIQUE NOT NULL,
    description text,
    icon_url text,
    category text DEFAULT 'GENERAL', -- EXPLORER, SOCIAL, ELITE
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 2. USER BADGES (Junction)
CREATE TABLE IF NOT EXISTS public.user_badges (
    user_id uuid NOT NULL,
    badge_id uuid NOT NULL,
    awarded_at timestamptz DEFAULT now(),
    
    PRIMARY KEY (user_id, badge_id),
    CONSTRAINT user_badges_user_fk FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    CONSTRAINT user_badges_badge_fk FOREIGN KEY (badge_id) REFERENCES public.badges(id) ON DELETE CASCADE
);

-- 3. CHALLENGES Table
CREATE TABLE IF NOT EXISTS public.challenges (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text UNIQUE NOT NULL, -- e.g. JAN_EXPLORER_2026
    title text NOT NULL,
    description text,
    
    -- Logic Config
    challenge_type text NOT NULL, -- CHECKIN_COUNT, VENUE_CATEGORY, etc.
    target_value integer NOT NULL DEFAULT 1,
    filters jsonb DEFAULT '{}'::jsonb, -- e.g. {"venue_category": "bar"}
    
    -- Validity
    period_start timestamptz,
    period_end timestamptz,
    is_active boolean DEFAULT true,
    
    -- Rewards
    reward_points integer DEFAULT 0,
    reward_badge_id uuid, -- Optional badge reward
    
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    
    CONSTRAINT challenges_reward_badge_fk FOREIGN KEY (reward_badge_id) REFERENCES public.badges(id) ON DELETE SET NULL
);

-- 4. USER CHALLENGE PROGRESS
CREATE TABLE IF NOT EXISTS public.user_challenge_progress (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    challenge_id uuid NOT NULL,
    
    current_value integer DEFAULT 0,
    is_completed boolean DEFAULT false,
    completed_at timestamptz,
    last_updated_at timestamptz DEFAULT now(),
    
    CONSTRAINT ucp_unique_user_challenge UNIQUE (user_id, challenge_id),
    CONSTRAINT ucp_user_fk FOREIGN KEY (user_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    CONSTRAINT ucp_challenge_fk FOREIGN KEY (challenge_id) REFERENCES public.challenges(id) ON DELETE CASCADE
);

-- SEED: Some initial Badges
INSERT INTO public.badges (name, description, category, icon_url) VALUES
('Pionero', 'Uno de los primeros usuarios de UrbanVibe', 'ELITE', 'https://urbanvibe.app/badges/pioneer.png'),
('Rey de la Noche', 'Experto en bares y discotecas', 'SOCIAL', 'https://urbanvibe.app/badges/nightking.png'),
('Explorador', 'Haz hecho check-in en 5 restaurantes distintos', 'EXPLORER', 'https://urbanvibe.app/badges/explorer.png')
ON CONFLICT (name) DO NOTHING;
