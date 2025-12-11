"""
ACTIVE VENUE SERVICE - Use this file for all venue-related operations.

This service provides optimized queries for different venue views:
- get_venues_map_preview: Lightweight data for map markers
- get_venues_list_view: Data for venue list screens
- get_venue_by_id: Full venue details (calculates favorites_count dynamically)

Routes using this service: app/api/v1/venues/routes.py
"""

from typing import List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.venues import Venue
from app.models.favorites import UserFavoriteVenue


async def get_venues_map_preview(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 200,
    only_open: bool = True,
) -> List[Venue]:
    """
    Devuelve la lista de venues para el mapa (vista liviana).
    Retorna instancias ORM de Venue; la transformación a dict {lat, lng}
    la hace Pydantic en VenueMapPreviewResponse.
    """
    stmt = select(Venue)

    if only_open:
        stmt = stmt.where(Venue.operational_status == "open")

    if hasattr(Venue, "deleted_at"):
        stmt = stmt.where(Venue.deleted_at.is_(None))

    stmt = (
        stmt.order_by(
            Venue.is_verified.desc(),
            Venue.rating_average.desc(),
            Venue.verified_visits_monthly.desc(),
            Venue.name.asc(),
        )
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_venues_list_view(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    only_open: bool = True,
) -> List[Venue]:
    """
    Devuelve la lista de venues para la pantalla de listado.
    Usa los mismos filtros básicos que el mapa, pero el schema de salida
    será VenueListResponse.
    """
    stmt = select(Venue)

    if only_open:
        stmt = stmt.where(Venue.operational_status == "open")

    if hasattr(Venue, "deleted_at"):
        stmt = stmt.where(Venue.deleted_at.is_(None))

    stmt = (
        stmt.order_by(
            Venue.is_verified.desc(),
            Venue.rating_average.desc(),
            Venue.review_count.desc(),
            Venue.name.asc(),
        )
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_venue_by_id(
    db: AsyncSession,
    venue_id: UUID,
) -> Venue | None:
    """
    Obtiene el detalle completo de un venue por su ID.
    
    IMPORTANTE: 
    - favorites_count: Calculado dinámicamente desde user_favorite_venues
    - rating_average: Leído de la DB (actualizado por update_venue_statistics)
    - review_count: Leído de la DB (actualizado por update_venue_statistics)
    
    Returns:
        Venue object con estadísticas, o None si no existe.
    """
    stmt = select(Venue).where(Venue.id == venue_id)
    
    if hasattr(Venue, "deleted_at"):
        stmt = stmt.where(Venue.deleted_at.is_(None))
        
    result = await db.execute(stmt)
    venue = result.scalars().first()
    
    if venue:
        # Solo calcular favorites_count dinámicamente
        # rating_average y review_count se leen de la DB
        count_stmt = select(func.count()).select_from(UserFavoriteVenue).where(
            UserFavoriteVenue.venue_id == venue_id
        )
        count_res = await db.execute(count_stmt)
        venue.favorites_count = count_res.scalar() or 0
        
    return venue
