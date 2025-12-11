# app/api/v1/venues/routes.py


from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api import deps
from app.api.v1.venues.schemas import VenueMapPreviewResponse, VenueDetailResponse, VenueListResponse
from app.api.v1.venues.service import get_venues_map_preview, get_venue_by_id, get_venues_list_view

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


@router.get(
    "/list",
    response_model=List[VenueListResponse],
    summary="Listado de locales para la pantalla de lista",
)
async def read_venues_list(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    skip: int = 0,
    limit: int = 50,
):
    """
    Endpoint para listar locales con paginación.
    """
    venues = await get_venues_list_view(db, skip=skip, limit=limit)
    return venues


@router.get(
    "/{venue_id}",
    response_model=VenueDetailResponse,
    summary="Obtiene el detalle completo de un local",
)
async def get_venue_detail_endpoint(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
):
    """
    Retorna toda la información pública de un venue.
    """
    venue = await get_venue_by_id(db, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )
    return venue
