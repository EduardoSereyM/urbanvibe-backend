import asyncio
import logging
from sqlalchemy import text
from app.db.session import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migration():
    logger.info("Connecting to database...")
    
    # Define steps separately because asyncpg cannot execute multiple statements at once
    steps = [
        """
        CREATE TABLE IF NOT EXISTS public.user_favorite_venues (
            user_id uuid NOT NULL,
            venue_id uuid NOT NULL,
            created_at timestamptz DEFAULT now(),
            PRIMARY KEY (user_id, venue_id)
        )
        """,
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_fav_venue_user_fk') THEN
                ALTER TABLE public.user_favorite_venues ADD CONSTRAINT user_fav_venue_user_fk FOREIGN KEY (user_id) REFERENCES public.profiles(id);
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_fav_venue_venue_fk') THEN
                ALTER TABLE public.user_favorite_venues ADD CONSTRAINT user_fav_venue_venue_fk FOREIGN KEY (venue_id) REFERENCES public.venues(id);
            END IF;
        END $$
        """
    ]

    async with engine.begin() as conn:
        for i, sql in enumerate(steps):
            logger.info(f"Executing step {i+1}...")
            try:
                await conn.execute(text(sql))
            except Exception as e:
                logger.error(f"Error applying step {i+1}: {e}")
                raise

    logger.info("Migration 009 applied successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
