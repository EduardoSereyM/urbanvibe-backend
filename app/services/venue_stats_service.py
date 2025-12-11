"""
Helper function to update venue statistics in the database.
This should be called after any review create/update/delete operation.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.venues import Venue
from app.models.reviews import Review


async def update_venue_statistics(db: AsyncSession, venue_id: UUID) -> None:
    """
    Calcula y actualiza rating_average y review_count en la tabla venues.
    
    Args:
        db: Database session
        venue_id: ID del venue a actualizar
    """
    # Calcular estadísticas desde reviews
    stats_query = select(
        func.avg(Review.general_score).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).where(
        Review.venue_id == venue_id,
        Review.deleted_at.is_(None)
    )
    
    result = await db.execute(stats_query)
    stats = result.one()
    
    # Actualizar venue
    venue_query = select(Venue).where(Venue.id == venue_id)
    venue_result = await db.execute(venue_query)
    venue = venue_result.scalar_one_or_none()
    
    if venue:
        venue.rating_average = float(stats.avg_rating) if stats.avg_rating else 0.0
        venue.review_count = stats.review_count or 0
        # No need to call db.add() since venue is already tracked
        # db.commit() will be called by the caller
