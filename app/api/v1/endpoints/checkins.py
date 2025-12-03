from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.checkins import CheckinCreate, CheckinResponse
from app.services.checkin_service import checkin_service
from app.models.profiles import Profile

router = APIRouter()

@router.post("/", response_model=CheckinResponse)
async def create_checkin(
    checkin_in: CheckinCreate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)]
):
    return await checkin_service.process_checkin(
        db=db,
        user_id=current_user.id,
        token_str=checkin_in.token_id,
        user_lat=checkin_in.user_lat,
        user_lng=checkin_in.user_lng
    )

@router.post("/scan", response_model=CheckinResponse)
async def scan_qr(
    checkin_in: CheckinCreate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)]
):
    """
    Escanea un QR dinámico y procesa el check-in.
    """
    return await checkin_service.process_checkin(
        db=db,
        user_id=current_user.id,
        token_str=checkin_in.token_id,
        user_lat=checkin_in.user_lat,
        user_lng=checkin_in.user_lng
    )

from typing import List

@router.get("/me", response_model=List[CheckinResponse])
async def get_my_checkins(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)]
):
    """
    Obtiene el historial de check-ins del usuario actual.
    """
    return await checkin_service.get_user_checkins(
        db=db,
        user_id=current_user.id
    )
