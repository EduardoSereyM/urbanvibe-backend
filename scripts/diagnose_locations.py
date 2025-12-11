import asyncio
import os
import sys
sys.path.append(os.getcwd())
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def check_locations():
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
    
    print("\n🌍 Verifying Location Data...")
    
    async with engine.connect() as conn:
        # Check Countries
        result = await conn.execute(text("SELECT count(*) FROM countries"))
        count_countries = result.scalar()
        print(f"🇨🇱 Countries: {count_countries}")
        
        # Check Regions
        result = await conn.execute(text("SELECT id, name FROM regions"))
        regions = result.fetchall()
        print(f"📍 Regions found: {len(regions)}")
        for r in regions:
            # Check cities for each region
            c_result = await conn.execute(text(f"SELECT count(*) FROM cities WHERE region_id = {r.id}"))
            c_count = c_result.scalar()
            print(f"   - {r.name} (ID: {r.id}): {c_count} cities")

if __name__ == "__main__":
    asyncio.run(check_locations())
