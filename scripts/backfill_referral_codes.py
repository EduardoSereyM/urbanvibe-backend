import asyncio
import sys
import os
import random
import string
from sqlalchemy import select

# Añadir directorio raíz al path (un nivel arriba de scripts/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.models.profiles import Profile
from app.models.venues import Venue

def generate_uv_code() -> str:
    """Genera un código alfanumérico único con formato UV-XXXXXX."""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(6))
    return f"UV-{code}"

async def backfill_codes():
    async with AsyncSessionLocal() as db:
        print("🚀 Iniciando backfill independiente de códigos (UV-XXXXXX)...")

        # 1. Backfill para Profiles
        stmt_profiles = select(Profile).where(Profile.referral_code == None)
        profiles_to_update = (await db.execute(stmt_profiles)).scalars().all()
        
        print(f"📊 Encontrados {len(profiles_to_update)} perfiles sin código.")
        for profile in profiles_to_update:
            new_code = generate_uv_code()
            profile.referral_code = new_code
            print(f"  ✅ Usuario {profile.username or profile.id}: {new_code}")

        # 2. Backfill para Venues
        stmt_venues = select(Venue).where(Venue.referral_code == None)
        venues_to_update = (await db.execute(stmt_venues)).scalars().all()
        
        print(f"📊 Encontrados {len(venues_to_update)} locales sin código.")
        for venue in venues_to_update:
            new_code = generate_uv_code()
            venue.referral_code = new_code
            print(f"  ✅ Local {venue.name}: {new_code}")

        await db.commit()
        print("\n✨ Backfill completado exitosamente.")

if __name__ == "__main__":
    asyncio.run(backfill_codes())
