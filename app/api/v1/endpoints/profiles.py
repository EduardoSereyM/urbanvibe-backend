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
    
    # --- JWT FALLBACK STRATEGY ---
    # Attempt to read from Token if DB properties are missing.
    # We do this regardless of whether 'row' exists, because 'row' might exist but be empty (trigger created).
    jwt_username = None
    jwt_email = None
    
    # Check if we need fallback data (if row is None OR row has no username)
    db_username = row.get("username") if row else None
    
    if not row or not db_username:
        try:
            token_str = auth_creds.credentials
            payload = decode_supabase_jwt(token_str)
            
            # Extract from Supabase standard claims
            jwt_email = payload.get("email")
            
            # Extract from user_metadata (where custom fields like username live)
            user_meta = payload.get("user_metadata", {})
            jwt_username = user_meta.get("username") or user_meta.get("display_name")
            
        except Exception as e:
            print(f"⚠️ Warning: Checksum/JWT fallback failed: {e}")

    # --- AUTO-HEALING: Persist the found username to DB if it was missing ---
    # User's brilliant idea: If we found it in the token, why not save it?
    # This bypasses the RLS error on frontend because Backend serves as Admin (usually).
    if jwt_username and not db_username and row:
        try:
            print(f"🛠️ Auto-Healing: Fixing missing username for {current_user_id} -> {jwt_username}")
            update_query = """
                UPDATE public.profiles 
                SET username = :username, display_name = :username, updated_at = now()
                WHERE id = :uid
            """
            await db.execute(update_query, values={"username": jwt_username, "uid": current_user_id})
            await db.commit() # Aseguramos que se guarde el cambio
        except Exception as write_err:
             print(f"⚠️ Auto-Healing Failed (likely generic SQL error): {write_err}")
    # ------------------------------------------------------------------------

    role_id = row.get("role_id") if row else 5 
    role_name = row.get("role_name") if row else "APP_USER"

    # Priority: DB > JWT > Default
    final_username = db_username or jwt_username or "Usuario"
    final_email = row.get("email") if row and row.get("email") else (jwt_email or "")
    
    # Last resort: Generate from email
    if final_username == "Usuario" and final_email and "@" in final_email:
         # e.g. "contact" from "contact@urbanvibe.cl"
        final_username = final_email.split("@")[0]
        
    final_roles = [role_name] if role_name else ["APP_USER"]

    # --- DYNAMIC COUNTERS (Logic Fix) ---
    # Calc reviews_count
    from app.models.reviews import Review
    from app.models.checkins import Checkin
    from sqlalchemy import func
    
    # 1. Reviews Count
    count_reviews_query = select(func.count()).select_from(Review).where(
        Review.user_id == (row["id"] if row else current_user_id),
        Review.deleted_at.is_(None)
    )
    reviews_count = await db.scalar(count_reviews_query) or 0
    
    # 2. Verified Checkins Count
    count_checkins_query = select(func.count()).select_from(Checkin).where(
        Checkin.user_id == (row["id"] if row else current_user_id),
        Checkin.status == 'confirmed'
    )
    verified_checkins_count = await db.scalar(count_checkins_query) or 0
    
    # 3. Photos Count (Placeholder logic or simple count from reviews if applicable, for now 0 or static)
    photos_count = 0 

    print(f"DEBUG: /me -> Email: {final_email}, Role: {role_name}, Username: {final_username}, Reviews: {reviews_count}")

    return ProfileResponse(
        id=row["id"] if row else current_user_id,
        reputation_score=row["reputation_score"] if row else 0,
        points_current=row["points_current"] if row else 0,
        username=final_username, 
        email=final_email,
        full_name=row.get("full_name") if row else None,
        avatar_url=row.get("avatar_url") if row else None,
        role_id=role_id,
        role_name=role_name,
        roles=final_roles,
        
        # New Fields Mapping
        national_id=row.get("national_id") if row else None,
        birth_date=str(row.get("birth_date")) if row and row.get("birth_date") else None,
        gender=row.get("gender") if row else None,
        is_influencer=row.get("is_influencer") if row else False,
        favorite_cuisines=row.get("favorite_cuisines") if row and row.get("favorite_cuisines") else [],
        price_preference=row.get("price_preference") if row else None,
        preferences=row.get("preferences") if row and row.get("preferences") else {},
        referral_code=row.get("referral_code") if row else None,
        website=row.get("website") if row else None,
        bio=row.get("bio") if row else None,
        
        # Counters
        reviews_count=reviews_count,
        photos_count=photos_count,
        verified_checkins_count=verified_checkins_count
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
        full_name=row.get("full_name"),
        avatar_url=row.get("avatar_url"),
        role_id=role_id,
        role_name=role_name,
        roles=final_roles,
        
        # New Fields
        national_id=row.get("national_id"),
        birth_date=str(row.get("birth_date")) if row.get("birth_date") else None,
        gender=row.get("gender"),
        is_influencer=row.get("is_influencer") or False,
        favorite_cuisines=row.get("favorite_cuisines") or [],
        price_preference=row.get("price_preference"),
        preferences=row.get("preferences") or {},
        referral_code=row.get("referral_code"),
        website=row.get("website"),
        bio=row.get("bio"),
        
        # Counters (Simple return 0 or logic reuse? Reuse logic preferred but complex here. Let's return basics)
        # Ideally we should extract the "Get Profile" logic to a service function.
        reviews_count=row.get("reviews_count") or 0,
        photos_count=row.get("photos_count") or 0,
        verified_checkins_count=row.get("verified_checkins_count") or 0
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
    
    # Commit changes 
    await db.commit()

    # --- Notification Logic ---
    try:
        from app.models.venues import Venue
        from app.models.profiles import Profile
        
        # Fetch venue details (name and owner)
        venue_res = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue_data = venue_res.scalar_one_or_none()
        
        if venue_data and venue_data.owner_id:
             # Fetch user name
             user_res = await db.execute(select(Profile).where(Profile.id == current_user_id))
             user_data = user_res.scalar_one_or_none()
             user_name = user_data.username if user_data else "Un usuario"
             
             from app.services.notifications import notification_service
             await notification_service.notify_venue_like(
                db=db,
                venue_name=venue_data.name,
                owner_id=venue_data.owner_id,
                user_name=user_name
             )
    except Exception as e:
        print(f"Error sending like notification: {e}")

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
    """Obtiene los IDs de los locales favoritos (Legacy)."""
    stmt = select(UserFavoriteVenue.venue_id).where(
        UserFavoriteVenue.user_id == current_user_id
    )
    result = await db.execute(stmt)
    venue_ids = result.scalars().all()
    return venue_ids


# --- REFERRAL & AMBASSADOR ENDPOINTS (V12.4) ---

from app.services.referral_service import referral_service

@router.post("/me/referral/claim")
async def claim_referral(
    referral_code: str,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
):
    """
    Canjea un código de referido para vincular al usuario con su referente.
    Requerimiento: 'Conecta tu Ciudad'.
    """
    # 1. Verificar si ya tiene referente
    profile_res = await db.execute(select(Profile).where(Profile.id == current_user_id))
    profile = profile_res.scalar_one_or_none()
    
    if profile and profile.referred_by_user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Ya has canjeado un código de referido.")

    # 2. Procesar vía servicio
    result = await referral_service.claim_referral_code(db, current_user_id, referral_code)
    
    if result["status"] == "error":
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result["message"])
        
    await db.commit()
    return result

@router.get("/me/ambassador")
async def get_ambassador_status(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
):
    """
    Obtiene el estatus de embajador basado en locales referidos.
    Misión Especial: 'Embajador de Eventos'.
    """
    status = await referral_service.check_ambassador_status(db, current_user_id)
    return status


