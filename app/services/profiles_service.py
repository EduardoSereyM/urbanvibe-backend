from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.profiles import Profile

class ProfilesService:
    @staticmethod
    async def get_profile(db: AsyncSession, user_id: UUID) -> Optional[Profile]:
        result = await db.execute(select(Profile).where(Profile.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_profile(db: AsyncSession, user_id: UUID, update_data: dict) -> Optional[Profile]:
        """
        Actualiza el perfil del usuario.
        Retorna el perfil actualizado o None si no existe.
        """
        stmt = select(Profile).where(Profile.id == user_id)
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        # Apply updates
        for key, value in update_data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)
        
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile

profiles_service = ProfilesService()
