# app/api/v1/venues/routes.py


from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.venues.schemas import VenueMapPreviewResponse
from app.api.v1.venues.service import get_venues_map_preview

router = APIRouter()


@router.get(
    "/map",
    response_model=List[VenueMapPreviewResponse],
    summary="Listado de locales para el mapa",
)
async def read_venues_map(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    skip: int = 0,
    limit: int = 200,
):
    """
    Endpoint optimizado para el mapa:
    devuelve solo los campos necesarios para markers y modal.
    """
    venues = await get_venues_map_preview(db, skip=skip, limit=limit)
    return venues
