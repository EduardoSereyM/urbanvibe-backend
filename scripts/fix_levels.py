import asyncio
import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.levels import Level
from app.models.profiles import Profile

async def fix_levels():
    async with AsyncSessionLocal() as db:
        print("[INFO] Searching for default level 'Bronce'...")
        result = await db.execute(select(Level).where(Level.name == "Bronce"))
        level = result.scalar_one_or_none()
        
        if not level:
            print("[ERROR] Level 'Explorador Novato' not found!")
            print("[INFO] Listing ALL levels in database:")
            all_levels = await db.execute(select(Level))
            for l in all_levels.scalars().all():
                print(f" - {l.name} (ID: {l.id})")
            return

        print(f"[OK] Found Level: {level.name} (ID: {level.id})")
        
        # Updates profiles with no level
        print("[INFO] Updating profiles with NULL current_level_id...")
        stmt = (
            update(Profile)
            .where(Profile.current_level_id == None)
            .values(current_level_id=level.id)
            .execution_options(synchronize_session="fetch")
        )
        
        result_update = await db.execute(stmt)
        await db.commit()
        
        print(f"[OK] Updated {result_update.rowcount} profiles to use default level.")

if __name__ == "__main__":
    asyncio.run(fix_levels())
