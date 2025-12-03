from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.security import decode_supabase_jwt
from app.models.profiles import Profile
from app.api.v1.venues_admin.schemas import (
    MyVenuesResponse,
    VenueCreate,
    VenueB2BDetail,
)
from app.api.v1.venues_admin.service import (
    get_user_venues,
    create_founder_venue,
    get_venue_b2b_detail,
)

router = APIRouter(
    tags=["venues_admin"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_is_super_admin(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> bool:
    """
    Verifica si el usuario tiene el claim app_role = 'SUPER_ADMIN' en el JWT.
    También verifica whitelist de emails para Super Admin.
    """
    if token == "demo":
        return True
        
    try:
        payload = decode_supabase_jwt(token)
        
        # 1. Check explicit claim
        app_role = payload.get("app_role")
        if app_role == "SUPER_ADMIN":
            return True
            
        # 2. Check email whitelist
        email = payload.get("email")
        if email == "administradorapp@urbanvibe.cl":
            return True
            
        return False
    except Exception:
        return False


@router.get("/me/venues", response_model=MyVenuesResponse)
async def list_my_venues(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Devuelve todos los venues donde el usuario actual tiene algún rol B2B.
    Si es SUPER_ADMIN, puede ver todos los venues.
    """
    return await get_user_venues(
        db=db,
        user_id=current_user.id,
        is_super_admin=is_super_admin
    )


@router.post("/venues", response_model=VenueB2BDetail, status_code=201)
async def create_venue(
    venue_data: VenueCreate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
):
    """
    Crea una casa matriz (local fundador) para el usuario actual.
    """
    return await create_founder_venue(
        db=db,
        venue_data=venue_data,
        owner_user_id=current_user.id
    )


@router.get("/venues/{venue_id}", response_model=VenueB2BDetail)
async def get_venue_detail(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Devuelve el detalle B2B de un venue específico.
    Requiere que el usuario sea owner, miembro del equipo, o SUPER_ADMIN.
    """
    return await get_venue_b2b_detail(
        db=db,
        venue_id=venue_id,
        user_id=current_user.id,
        is_super_admin=is_super_admin
    )


from app.api.v1.venues_admin.schemas import VenueCheckinListResponse
from app.api.v1.venues_admin.service import get_venue_checkins

@router.get("/venues/{venue_id}/checkins", response_model=VenueCheckinListResponse)
async def get_venue_checkins_endpoint(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Obtiene el historial de check-ins de un venue.
    """
    return await get_venue_checkins(
        db=db,
        venue_id=venue_id,
        user_id=current_user.id,
        is_super_admin=is_super_admin
    )


from app.api.v1.venues_admin.schemas import CheckinStatusUpdate, VenueCheckinDetail
from app.api.v1.venues_admin.service import update_checkin_status

@router.put("/venues/{venue_id}/checkins/{checkin_id}/status", response_model=VenueCheckinDetail)
async def update_checkin_status_endpoint(
    venue_id: UUID,
    checkin_id: int,
    status_update: CheckinStatusUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Actualiza el estado de un check-in (confirmar/rechazar).
    """
    return await update_checkin_status(
        db=db,
        venue_id=venue_id,
        checkin_id=checkin_id,
        new_status=status_update.status,
        user_id=current_user.id,
        is_super_admin=is_super_admin
    )


# --- PROMOTIONS & REWARDS ENDPOINTS ---

from app.api.v1.venues_admin.schemas import (
    Promotion, 
    PromotionCreate, 
    VenuePointsLog, 
    ValidateRewardRequest, 
    ValidateRewardResponse
)
from app.api.v1.venues_admin.service import (
    get_venue_promotions,
    create_venue_promotion,
    get_venue_points_logs,
    validate_reward_qr
)

@router.get("/venues/{venue_id}/promotions", response_model=List[Promotion])
async def get_venue_promotions_endpoint(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Obtiene las promociones de un venue.
    """
    return await get_venue_promotions(
        db=db,
        venue_id=venue_id,
        user_id=current_user.id,
        is_super_admin=is_super_admin
    )

@router.post("/venues/{venue_id}/promotions", response_model=Promotion, status_code=201)
async def create_venue_promotion_endpoint(
    venue_id: UUID,
    promotion_data: PromotionCreate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Crea una nueva promoción.
    """
    return await create_venue_promotion(
        db=db,
        venue_id=venue_id,
        promotion_data=promotion_data,
        user_id=current_user.id,
        is_super_admin=is_super_admin
    )

@router.get("/venues/{venue_id}/points-logs", response_model=List[VenuePointsLog])
async def get_venue_points_logs_endpoint(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Obtiene el historial de puntos del venue.
    """
    return await get_venue_points_logs(
        db=db,
        venue_id=venue_id,
        user_id=current_user.id,
        is_super_admin=is_super_admin
    )

@router.post("/venues/{venue_id}/validate-reward", response_model=ValidateRewardResponse)
async def validate_reward_endpoint(
    venue_id: UUID,
    request: ValidateRewardRequest,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Valida un QR de recompensa.
    """
    return await validate_reward_qr(
        db=db,
        venue_id=venue_id,
        qr_content=request.qr_content,
        user_id=current_user.id,
        is_super_admin=is_super_admin
    )


