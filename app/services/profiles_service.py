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

profiles_service = ProfilesService()
