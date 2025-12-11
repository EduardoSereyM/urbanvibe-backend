"""
DEPRECATED: This service is LEGACY and NOT USED by active endpoints.

Active venue endpoints use: app/api/v1/venues/service.py
Active venue routes are in: app/api/v1/venues/routes.py

This file is kept for backward compatibility but should not be modified.
If you need to work with venues, use the files mentioned above.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.models.venues import Venue

class VenuesService:
    """
    DEPRECATED: Use app/api/v1/venues/service.py instead.
    """
    
    @staticmethod
    async def get_venues(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
    ) -> List[Venue]:
        """DEPRECATED: Use get_venues_map_preview or get_venues_list_view instead."""
        query = select(Venue).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_venue(
        db: AsyncSession,
        venue_id: UUID
    ) -> Optional[Venue]:
        """DEPRECATED: Use get_venue_by_id from app/api/v1/venues/service.py instead."""
        query = select(Venue).where(Venue.id == venue_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

venues_service = VenuesService()
