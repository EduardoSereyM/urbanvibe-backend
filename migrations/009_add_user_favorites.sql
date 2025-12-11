CREATE TABLE IF NOT EXISTS public.user_favorite_venues (
    user_id uuid NOT NULL,
    venue_id uuid NOT NULL,
    created_at timestamptz DEFAULT now(),
    PRIMARY KEY (user_id, venue_id)
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_fav_venue_user_fk') THEN
        ALTER TABLE public.user_favorite_venues ADD CONSTRAINT user_fav_venue_user_fk FOREIGN KEY (user_id) REFERENCES public.profiles(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_fav_venue_venue_fk') THEN
        ALTER TABLE public.user_favorite_venues ADD CONSTRAINT user_fav_venue_venue_fk FOREIGN KEY (venue_id) REFERENCES public.venues(id);
    END IF;
END $$;
