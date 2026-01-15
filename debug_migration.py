import asyncio
import logging
from sqlalchemy import text
from app.db.session import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    logger.info("Connecting to database for DEBUG migration...")
    
    migration_steps = [
        # 1. Create Levels
        """CREATE TABLE IF NOT EXISTS public.levels (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text UNIQUE NOT NULL,
            min_points integer NOT NULL,
            benefits jsonb DEFAULT '[]'::jsonb,
            created_at timestamptz DEFAULT now(),
            updated_at timestamptz DEFAULT now()
        )""",

        # 2. Seed Levels
        """INSERT INTO public.levels (name, min_points, benefits) VALUES
            ('Bronce', 0, '["Acceso básico"]'::jsonb),
            ('Plata', 1000, '["Descuento 5%"]'::jsonb),
            ('Oro', 5000, '["Descuento 10%", "Acceso VIP"]'::jsonb),
            ('Embajador', 20000, '["Descuento 20%", "Eventos Exclusivos", "Prioridad"]'::jsonb)
            ON CONFLICT (name) DO NOTHING""",

        # 3. Seed Events
        """INSERT INTO public.gamification_events (event_code, target_type, description, points, is_active) VALUES
            ('CHECKIN', 'user', 'Check-in estándar en un local', 10, true),
            ('REVIEW', 'user', 'Reseña aprobada de un local', 20, true),
            ('REFERRAL_USER', 'user', 'Invitar a un amigo que se registra', 50, true),
            ('REFERRAL_VENUE', 'user', 'Invitar a un local que se registra', 500, true),
            ('EVENT_ATTENDANCE', 'user', 'Asistencia validada a evento', 30, true)
            ON CONFLICT (event_code) DO NOTHING""",

        # 4. Add FK
        """DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='current_level_id') THEN
                ALTER TABLE public.profiles ADD COLUMN current_level_id uuid;
            END IF;

            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_current_level_fk') THEN
                ALTER TABLE public.profiles ADD CONSTRAINT profiles_current_level_fk FOREIGN KEY (current_level_id) REFERENCES public.levels(id);
            END IF;
        END $$"""
    ]

    async with engine.begin() as conn:
        for i, step in enumerate(migration_steps):
            logger.info(f"Executing step {i+1}/{len(migration_steps)}...")
            try:
                await conn.execute(text(step))
            except Exception as e:
                logger.error(f"Error in step {i+1}: {e}")
                raise

    logger.info("Debug Migration applied successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
