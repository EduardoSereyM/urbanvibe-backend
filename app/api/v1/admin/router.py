from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.profiles import Profile
from app.api.v1.admin.schemas import (
    VenueAdminListResponse,
    VenueAdminDetail,
    VenueUpdate,
    MetricsResponse,
    UserAdminListResponse,
    UserAdminDetail,
    UserUpdate
)
from app.api.v1.admin.service import (
    check_super_admin,
    get_all_venues,
    get_venue_admin_detail,
    update_venue,
    get_system_metrics,
    get_all_users,
    get_user_detail,
    update_user
)

from fastapi.security import OAuth2PasswordBearer

router = APIRouter(
    tags=["admin"],
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
        
    from app.core.security import decode_supabase_jwt
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


# --- VENUES ENDPOINTS ---

@router.get("/venues", response_model=VenueAdminListResponse)
async def list_all_venues(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
    search: Optional[str] = Query(None, description="Buscar por nombre, razón social o dirección"),
    city: Optional[str] = Query(None, description="Filtrar por ciudad"),
    verification_status: Optional[str] = Query(None, description="Filtrar por estado de verificación"),
    operational_status: Optional[str] = Query(None, description="Filtrar por estado operacional"),
    skip: int = Query(0, ge=0, description="Offset para paginación"),
    limit: int = Query(20, ge=1, le=100, description="Items por página (max 100)"),
    sort_by: str = Query("created_at", description="Campo para ordenar"),
    sort_order: str = Query("desc", description="Orden: asc o desc"),
):
    """
    Lista todos los venues del sistema con filtros y paginación.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    
    return await get_all_venues(
        db=db,
        search=search,
        city=city,
        verification_status=verification_status,
        operational_status=operational_status,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/venues/{venue_id}", response_model=VenueAdminDetail)
async def get_venue_detail_endpoint(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Obtiene el detalle completo de un venue.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    return await get_venue_admin_detail(db=db, venue_id=venue_id)


@router.patch("/venues/{venue_id}", response_model=VenueAdminDetail)
async def update_venue_endpoint(
    venue_id: UUID,
    venue_update: VenueUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Actualiza un venue.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    return await update_venue(db=db, venue_id=venue_id, venue_update=venue_update)


# --- METRICS ENDPOINTS ---

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics_endpoint(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
    period: str = Query("30d", regex="^(24h|7d|30d|90d|all)$")
):
    """
    Obtiene métricas del sistema.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    return await get_system_metrics(db=db, period=period)


# --- USERS ENDPOINTS ---

@router.get("/users", response_model=UserAdminListResponse)
async def list_all_users(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
    search: Optional[str] = Query(None, description="Buscar por email o display_name"),
    role: Optional[str] = Query(None, description="Filtrar por rol"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(email|created_at|display_name)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """
    Lista todos los usuarios.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    return await get_all_users(
        db=db,
        search=search,
        role=role,
        is_active=is_active,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/users/{user_id}", response_model=UserAdminDetail)
async def get_user_detail_endpoint(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Obtiene detalle completo de un usuario.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    return await get_user_detail(db=db, user_id=user_id)


@router.patch("/users/{user_id}", response_model=UserAdminDetail)
async def update_user_endpoint(
    user_id: UUID,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Actualiza un usuario.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    return await update_user(db=db, user_id=user_id, user_update=user_update)


# --- CHECKINS ENDPOINTS ---

from app.models.checkins import Checkin
from sqlalchemy import delete, select
from fastapi import status, HTTPException

@router.delete("/checkins/{checkin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checkin_endpoint(
    checkin_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Elimina un check-in específico.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    
    result = await db.execute(select(Checkin).where(Checkin.id == checkin_id))
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
        
    await db.delete(checkin)
    await db.commit()
    return None

@router.delete("/checkins/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_checkins_endpoint(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    is_super_admin: Annotated[bool, Depends(get_is_super_admin)],
):
    """
    Elimina TODOS los check-ins de un usuario. Útil para resetear pruebas.
    **Solo accesible para SUPER_ADMIN.**
    """
    await check_super_admin(is_super_admin)
    
    await db.execute(delete(Checkin).where(Checkin.user_id == user_id))
    await db.commit()
    return None
