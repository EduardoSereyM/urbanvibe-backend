-- 010_gamification_levels.sql

-- 1. Create LEVELS table
CREATE TABLE IF NOT EXISTS public.levels (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text UNIQUE NOT NULL,
    min_points integer NOT NULL,
    benefits jsonb DEFAULT '[]'::jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 2. Seed LEVELS
INSERT INTO public.levels (name, min_points, benefits) VALUES
('Bronce', 0, '["Acceso básico"]'::jsonb),
('Plata', 1000, '["Descuento 5%"]'::jsonb),
('Oro', 5000, '["Descuento 10%", "Acceso VIP"]'::jsonb),
('Embajador', 20000, '["Descuento 20%", "Eventos Exclusivos", "Prioridad"]'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- 3. Seed GAMIFICATION EVENTS
INSERT INTO public.gamification_events (event_code, target_type, description, points, is_active) VALUES
('CHECKIN', 'user', 'Check-in estándar en un local', 10, true),
('REVIEW', 'user', 'Reseña aprobada de un local', 20, true),
('REFERRAL_USER', 'user', 'Invitar a un amigo que se registra', 50, true),
('REFERRAL_VENUE', 'user', 'Invitar a un local que se registra', 500, true),
('EVENT_ATTENDANCE', 'user', 'Asistencia validada a evento', 30, true)
ON CONFLICT (event_code) DO NOTHING;

-- 4. Fix profiles FK (Drop old INT column if exists, Create UUID column)
DO $$
BEGIN
    -- Check if column exists but is NOT UUID (e.g. Integer) or just force drop to be safe and clean
    -- Simple approach: Drop if exists to ensure clean state for this new feature
    -- (Warning: Data loss if real data existed, but user confirmed 30 pts were fake/static)
    
    -- We'll check if it exists and drop it to recreate correctly
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='current_level_id') THEN
         -- We can't easily check type in DO block logic without more query, but dropping and re-adding is robust here
         ALTER TABLE public.profiles DROP COLUMN current_level_id;
    END IF;

    ALTER TABLE public.profiles ADD COLUMN current_level_id uuid;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_current_level_fk') THEN
        ALTER TABLE public.profiles ADD CONSTRAINT profiles_current_level_fk FOREIGN KEY (current_level_id) REFERENCES public.levels(id);
    END IF;
END $$;
