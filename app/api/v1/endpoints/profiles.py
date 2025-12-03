from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api import deps
from app.schemas.profiles import ProfileResponse
from app.services.profiles_service import profiles_service
from app.core.security import decode_supabase_jwt

router = APIRouter()


async def get_user_roles(
    db: AsyncSession,
    user_id: str,
    token: str = None
) -> List[str]:
    """
    Obtiene todos los roles del usuario desde:
    1. JWT claim (app_role)
    2. venue_team (roles B2B)
    3. owner_id en venues (implica VENUE_OWNER)
    """
    roles = set()
    
    # 1. Verificar JWT claim para SUPER_ADMIN
    if token:
        try:
            payload = decode_supabase_jwt(token)
            app_role = payload.get("app_role")
            if app_role:
                roles.add(app_role)
        except Exception:
            pass
    
    # 2. Verificar si es owner de algún venue
    try:
        result = await db.execute(
            text("""
                SELECT COUNT(*) 
                FROM public.venues 
                WHERE owner_id = :user_id 
                  AND deleted_at IS NULL
            """),
            {"user_id": user_id}
        )
        count = result.scalar()
        if count and count > 0:
            roles.add("VENUE_OWNER")
    except Exception:
        pass
    
    # 3. Verificar roles en venue_team
    try:
        result = await db.execute(
            text("""
                SELECT DISTINCT ar.name
                FROM public.venue_team vt
                JOIN public.app_roles ar ON vt.role_id = ar.id
                WHERE vt.user_id = :user_id
                  AND vt.is_active = true
            """),
            {"user_id": user_id}
        )
        team_roles = result.scalars().all()
        roles.update(team_roles)
    except Exception:
        pass
    
    # Si no tiene ningún rol B2B, es APP_USER por defecto
    if not roles:
        roles.add("APP_USER")
    
    return sorted(list(roles))


@router.get("/me", response_model=ProfileResponse)
async def read_me(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[deps.Profile, Depends(deps.get_current_user)],
    token: str = Depends(deps.oauth2_scheme) if hasattr(deps, 'oauth2_scheme') else None
):
    """
    Obtiene el perfil del usuario actual incluyendo sus roles.
    
    Roles posibles:
    - SUPER_ADMIN: Administrador del sistema
    - VENUE_OWNER: Dueño de al menos un local
    - VENUE_MANAGER: Manager de un local
    - VENUE_STAFF: Staff de un local
    - APP_PREMIUM_USER: Usuario premium
    - APP_USER: Usuario normal (por defecto)
    """
    profile = await profiles_service.get_profile(db, user_id=current_user.id)
    
    # Obtener roles del usuario
    user_roles = await get_user_roles(db, str(current_user.id), token)
    
    # Crear respuesta con roles
    return ProfileResponse(
        id=profile.id,
        reputation_score=profile.reputation_score,
        points_current=profile.points_current,
        roles=user_roles
    )
