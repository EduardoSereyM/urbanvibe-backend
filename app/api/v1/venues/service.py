from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.venues import Venue


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
