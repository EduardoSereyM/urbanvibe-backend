-- 012_challenge_rewards.sql

-- Add reward_promotion_id to challenges table
ALTER TABLE public.challenges 
ADD COLUMN IF NOT EXISTS reward_promotion_id uuid;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'challenges_reward_promo_fk') THEN
        ALTER TABLE public.challenges 
        ADD CONSTRAINT challenges_reward_promo_fk 
        FOREIGN KEY (reward_promotion_id) 
        REFERENCES public.promotions(id) 
        ON DELETE SET NULL;
    END IF;
END $$;
