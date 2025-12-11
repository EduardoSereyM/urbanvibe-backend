from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, delete

from app.api import deps
from app.api import deps
from app.schemas.profiles import ProfileResponse, ProfileUpdate
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
            # Supabase stores custom claims in app_metadata
            app_metadata = payload.get("app_metadata", {})
            app_role = app_metadata.get("app_role")
            
            if app_role:
                roles.add(app_role)
        except Exception:
            pass
    

    

    
    # Si no tiene ningún rol B2B, es APP_USER por defecto
    if not roles:
        roles.add("APP_USER")
    
    return sorted(list(roles))


@router.get("/me", response_model=ProfileResponse)
async def read_me(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
    auth_creds: Annotated[deps.HTTPAuthorizationCredentials, Depends(deps.security)],
):
    """
    Obtiene el perfil del usuario actual usando la arquitectura de Roles Explícitos.
    Fuente de Verdad: public.profiles.role_id
    """
    # Consulta directa uniendo perfiles y roles
    query = text("""
        SELECT p.*, r.name as role_name
        FROM public.profiles p
        LEFT JOIN public.app_roles r ON p.role_id = r.id
        WHERE p.id = :user_id
    """)
    

    
    result = await db.execute(query, {"user_id": current_user_id})
    row = result.mappings().first()

    # --- STRICT ROLE LOGIC: Single Source of Truth ---
    # We rely ONLY on p.role_id and the joined role name.
    # No dynamic "get_user_roles" calculation.
    
    role_id = row.get("role_id") if row else 5 # Default 5 (APP_USER)
    role_name = row.get("role_name") if row else "APP_USER"

    # Fallback for old users without username
    username = row.get("username") if row else "Usuario"
    email = row.get("email") if row else ""
    if not username and email:
        username = email.split("@")[0]
        
    final_roles = [role_name] if role_name else ["APP_USER"]

    print(f"DEBUG: /me -> Email: {email}, Role ID: {role_id}, Role Name: {role_name}")

    return ProfileResponse(
        id=row["id"] if row else current_user_id,
        reputation_score=row["reputation_score"] if row else 0,
        points_current=row["points_current"] if row else 0,
        username=username, 
        email=email,
        avatar_url=row.get("avatar_url"), # Added avatar_url mapping
        role_id=role_id,   # <-- THE TRUTH
        role_name=role_name,
        roles=final_roles
    )


@router.patch("/me", response_model=ProfileResponse)
async def update_me(
    profile_update: ProfileUpdate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
):
    """
    Actualiza el perfil del usuario actual (ej: avatar).
    """
    # 1. Update in DB
    updated_profile = await profiles_service.update_profile(
        db, 
        current_user_id, 
        profile_update.model_dump(exclude_unset=True)
    )
    
    if not updated_profile:
        # Should not happen if authenticated, but safe check
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Profile not found")

    # 2. Re-fetch full object to respect the /me query logic (roles, etc)
    # Reuse logical query from read_me or just return updated fields?
    # Ideally should return consistent ProfileResponse. 
    # For speed, let's call read_me logic or extract it.
    # To avoid code duplication, we can call the read_me function logic or simple return 
    # but read_me does complex joins for roles.
    
    # Let's do a simple returning constructing ProfileResponse from updated_profile + assumed roles (as user cannot change roles here)
    # But wait, read_me does role lookup.
    # Let's re-execute the read_me logic properly.
    
    # Reuse read_me logic (copy-paste for now to avoid refactoring huge function)
    query = text("""
        SELECT p.*, r.name as role_name
        FROM public.profiles p
        LEFT JOIN public.app_roles r ON p.role_id = r.id
        WHERE p.id = :user_id
    """)
    result = await db.execute(query, {"user_id": current_user_id})
    row = result.mappings().first()
    
    role_id = row.get("role_id") if row else 5
    role_name = row.get("role_name") if row else "APP_USER"

    username = row.get("username") if row else "Usuario"
    email = row.get("email") if row else ""
    if not username and email:
        username = email.split("@")[0]
        
    final_roles = [role_name] if role_name else ["APP_USER"]

    return ProfileResponse(
        id=row["id"],
        reputation_score=row["reputation_score"],
        points_current=row["points_current"],
        username=username, 
        email=email,
        avatar_url=row.get("avatar_url"),
        role_id=role_id,
        role_name=role_name,
        roles=final_roles
    )

from app.models.favorites import UserFavoriteVenue
from sqlalchemy import delete
from uuid import UUID

@router.post("/me/favorites/{venue_id}", status_code=201)
async def add_favorite(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
):
    """Agrega un local a favoritos."""
    # Check if exists
    stmt = select(UserFavoriteVenue).where(
        UserFavoriteVenue.user_id == current_user_id,
        UserFavoriteVenue.venue_id == venue_id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return {"message": "Ya está en favoritos"}
        
    fav = UserFavoriteVenue(user_id=current_user_id, venue_id=venue_id)
    db.add(fav)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
        
    return {"message": "Agregado a favoritos"}

@router.delete("/me/favorites/{venue_id}")
async def remove_favorite(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
):
    """Elimina un local de favoritos."""
    stmt = delete(UserFavoriteVenue).where(
        UserFavoriteVenue.user_id == current_user_id,
        UserFavoriteVenue.venue_id == venue_id
    )
    await db.execute(stmt)
    await db.commit()
    return {"message": "Eliminado de favoritos"}

@router.get("/me/favorites")
async def get_my_favorites(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
):
    """Obtiene los IDs de los locales favoritos."""
    stmt = select(UserFavoriteVenue.venue_id).where(
        UserFavoriteVenue.user_id == current_user_id
    )
    result = await db.execute(stmt)
    venue_ids = result.scalars().all()
    return venue_ids
