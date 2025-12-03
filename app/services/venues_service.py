from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.venues import Venue

class VenuesService:
    @staticmethod
    async def get_venues(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        # Add filters here later (lat, lng, radius, etc.)
    ) -> List[Venue]:
        query = select(Venue).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

venues_service = VenuesService()
