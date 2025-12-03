from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.venues import VenueResponse, QRCodeResponse
from app.api.v1.venues.schemas import (
    VenueMapPreviewResponse,
    VenueListResponse,
)
from app.api.v1.venues.service import (
    get_venues_map_preview,
    get_venues_list_view,
)
from app.services.venues_service import venues_service
from app.services.qr_service import qr_service
from app.services.qr_token_service import qr_token_service
from app.schemas.qr_tokens import QrTokenResponse
from app.models.profiles import Profile

router = APIRouter()


@router.get(
    "/",
    response_model=List[VenueResponse],
    summary="Read Venues (legacy)",
)
async def read_venues(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    skip: int = 0,
    limit: int = 100,
):
    """
    Endpoint legacy: lista de venues con schema antiguo.
    """
    venues = await venues_service.get_venues(db, skip=skip, limit=limit)
    return venues


@router.get(
    "/map",
    response_model=List[VenueMapPreviewResponse],
    summary="Listado de locales para el mapa (vista liviana)",
)
async def read_venues_map(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    skip: int = 0,
    limit: int = 200,
):
    """
    Endpoint optimizado para el mapa.
    Usa get_venues_map_preview y VenueMapPreviewResponse.
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
    Endpoint optimizado para la lista de locales.
    Usa get_venues_list_view y VenueListResponse.
    """
    venues = await get_venues_list_view(db, skip=skip, limit=limit)
    return venues


@router.get(
    "/{venue_id}/qr",
    response_model=QRCodeResponse,
    summary="Get Venue QR",
)
async def get_venue_qr(
    venue_id: UUID,
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
):
    """
    Endpoint existente para obtener QR del local.
    """
    qr_content = qr_service.generate_static_qr(venue_id)
    return QRCodeResponse(qr_content=qr_content)


@router.post(
    "/{venue_id}/qr-checkin",
    response_model=QrTokenResponse,
    summary="Generate Dynamic Check-in QR",
)
async def generate_checkin_qr(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
):
    """
    Genera un QR dinámico para check-in.
    Requiere ser dueño del local o admin.
    """
    # TODO: Check permissions (is owner or admin)
    # For now assuming user has access if they can call this (frontend checks)
    # But backend should enforce it.
    
    return await qr_token_service.generate_checkin_token(db, venue_id, current_user.id)
