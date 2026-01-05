from typing import List, Optional, Any, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.security import decode_supabase_jwt
from app.models.venues import Venue
from app.models.checkins import Checkin
from app.models.rewards import RewardUnit
from app.models.promotions import Promotion
from app.models.favorites import UserFavoriteVenue
from app.models.profiles import Profile
from app.schemas.venues import VenueResponse
from app.schemas.profiles import ProfileResponse
from app.api.v1.venues.schemas import VenueListResponse
from app.schemas.checkins import CheckinResponse
from sqlalchemy import func, desc

router = APIRouter()

# --- SCHEMAS ---

class ProfileSummary(BaseModel):
    id: UUID
    username: Optional[str] = "Viajero"
    avatar_url: Optional[str] = None
    points_current: int = 0

class VenueMapItem(BaseModel):
    id: UUID
    name: str
    location: Optional[Any] # GeoJSON dict or similar
    latitude: float
    longitude: float
    # Fields for SelectedVenueCard preview
    category_name: Optional[str] = None
    rating_average: float = 0.0
    price_tier: int = 1
    logo_url: Optional[str] = None
    cover_image_urls: List[str] = []
    address_display: Optional[str] = None
    is_verified: bool = False
    
class ExploreContextResponse(BaseModel):
    profile: Optional[ProfileSummary] = None
    map_venues: List[VenueMapItem] = []

class VenueFavoriteItem(BaseModel):
    id: UUID
    name: str
    category_name: Optional[str] = None
    rating_average: Optional[float] = 0.0
    price_tier: Optional[int] = 1
    logo_url: Optional[str] = None
    cover_image_urls: Optional[List[str]] = []

class UserPromotionBFFItem(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    promo_type: str 
    reward_tier: Optional[str] = None
    points_cost: Optional[int] = None
    is_active: bool
    can_redeem: bool = False
    redeem_alert: Optional[str] = None

class VenueDetailBFFResponse(BaseModel):
    venue: VenueResponse
    is_favorite: bool
    active_promotions: List[UserPromotionBFFItem]

class VenueListItemBFF(VenueListResponse):
    is_favorite: bool = False

class WalletSummary(BaseModel):
    pending_rewards: int = 0

class ProfileContextBFFResponse(BaseModel):
    profile: ProfileResponse
    recent_checkins: List[CheckinResponse] = []
    wallet_summary: WalletSummary


# --- ENDPOINTS ---

@router.get("/explore-context", response_model=ExploreContextResponse)
async def get_explore_context(
    db: AsyncSession = Depends(deps.get_db),
    token_auth: Optional[deps.HTTPAuthorizationCredentials] = Depends(deps.security_optional)
):
    """
    BFF Endpoint: Returns minimal Profile + All Venues for Map.
    """
    response = ExploreContextResponse()
    
    current_user_id = None
    if token_auth:
        try:
            payload = decode_supabase_jwt(token_auth.credentials)
            current_user_id = payload.get("sub")
        except Exception:
            pass
            
    if current_user_id:
        stmt_profile = select(Profile).where(Profile.id == current_user_id)
        result_profile = await db.execute(stmt_profile)
        user = result_profile.scalar_one_or_none()
        
        if user:
            display_name = user.username or user.display_name or "Viajero"
            if display_name == "Viajero" and user.email:
                 display_name = user.email.split("@")[0]
            
            response.profile = ProfileSummary(
                id=user.id,
                username=display_name,
                avatar_url=user.avatar_url,
                points_current=user.points_current
            )
    
    # Fetch all operational venues with location
    stmt_venues = (
        select(Venue)
        .where(Venue.operational_status == 'open')
        .where(Venue.latitude.isnot(None))
        .where(Venue.longitude.isnot(None))
    )
    result_venues = await db.execute(stmt_venues)
    venues_list = result_venues.scalars().all()
    
    map_items = []
    for v in venues_list:
        if v.latitude and v.longitude:
            cat_name = v.category.name if v.category else "Venue"
            map_items.append(VenueMapItem(
                id=v.id,
                name=v.name,
                location={"lat": v.latitude, "lng": v.longitude},
                latitude=v.latitude,
                longitude=v.longitude,
                category_name=cat_name,
                rating_average=v.rating_average or 0.0,
                price_tier=v.price_tier or 1,
                logo_url=v.logo_url,
                cover_image_urls=v.cover_image_urls or [],
                address_display=v.address_display,
                is_verified=v.is_verified or False
            ))
            
    response.map_venues = map_items
    return response

@router.get("/favorites", response_model=List[VenueFavoriteItem])
async def get_my_favorites_hydrated_mobile(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
):
    """
    Obtiene lista completa de favoritos.
    """
    stmt = (
        select(Venue)
        .join(UserFavoriteVenue, Venue.id == UserFavoriteVenue.venue_id)
        .where(UserFavoriteVenue.user_id == current_user_id)
    )
    result = await db.execute(stmt)
    venues = result.scalars().all()
    
    items = []
    for v in venues:
        cat_name = v.category.name if v.category else None 
        items.append(VenueFavoriteItem(
            id=v.id,
            name=v.name,
            category_name=cat_name,
            rating_average=v.rating_average,
            price_tier=v.price_tier,
            logo_url=v.logo_url,
            cover_image_urls=v.cover_image_urls or []
        ))
    return items

@router.get("/venue-details/{venue_id}", response_model=VenueDetailBFFResponse)
async def get_venue_details_bff(
    venue_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    token_auth: Optional[deps.HTTPAuthorizationCredentials] = Depends(deps.security_optional),
):
    """
    BFF Endpoint: Full Venue Details + User Context (Fav, Promos).
    """
    # 1. Resolve User (Optional)
    current_user_id = None
    user_points = 0
    if token_auth:
        try:
            payload = decode_supabase_jwt(token_auth.credentials)
            current_user_id = payload.get("sub")
            if current_user_id:
                res_u = await db.execute(select(Profile.points_current).where(Profile.id == current_user_id))
                user_points = res_u.scalar() or 0
        except Exception:
            pass

    # 2. Fetch Venue
    stmt = select(Venue).where(Venue.id == venue_id)
    result = await db.execute(stmt)
    venue = result.scalar_one_or_none()
    
    if not venue:
         from fastapi import HTTPException
         raise HTTPException(status_code=404, detail="Local no encontrado")

    # 3. Check Favorite (Parallelizable)
    is_favorite = False
    if current_user_id:
        stmt_fav = select(UserFavoriteVenue).where(
            UserFavoriteVenue.user_id == current_user_id,
            UserFavoriteVenue.venue_id == venue_id
        )
        res_fav = await db.execute(stmt_fav)
        if res_fav.scalar_one_or_none():
            is_favorite = True

    # 4. Fetch Active Promotions & Compute Redemtion
    stmt_promos = select(Promotion).where(
        Promotion.venue_id == venue_id,
        Promotion.is_active == True
    )
    res_promos = await db.execute(stmt_promos)
    promotions = res_promos.scalars().all()
    
    promo_items = []
    for p in promotions:
        can_redeem = False
        alert_msg = None
        
        if not current_user_id:
            can_redeem = False
            alert_msg = "Inicia sesión"
        else:
            cost = p.points_cost or 0
            if cost > 0:
                if user_points >= cost:
                    can_redeem = True
                else:
                    can_redeem = False
                    alert_msg = f"Faltan {cost - user_points} pts"
            else:
                can_redeem = True
        
        promo_items.append(UserPromotionBFFItem(
            id=p.id,
            title=p.title,
            description=None, 
            image_url=p.image_url,
            promo_type=p.promo_type,
            reward_tier=p.reward_tier,
            points_cost=p.points_cost or 0,
            is_active=p.is_active,
            can_redeem=can_redeem,
            redeem_alert=alert_msg
        ))

    return VenueDetailBFFResponse(
        venue=venue, 
        is_favorite=is_favorite,
        active_promotions=promo_items
    )

@router.get("/venues-list", response_model=List[VenueListItemBFF])
async def get_venues_list_bff(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    token_auth: Optional[deps.HTTPAuthorizationCredentials] = Depends(deps.security_optional),
    skip: int = 0,
    limit: int = 50,
):
    """
    BFF Endpoint for Venue List Screen.
    Returns lightweight venue list + is_favorite status.
    """
    # 1. Fetch Venues (Lightweight View)
    from app.api.v1.venues.service import get_venues_list_view
    venues = await get_venues_list_view(db, skip=skip, limit=limit)

    # 2. Resolve User & Favorites
    current_user_id = None
    if token_auth:
        try:
            payload = decode_supabase_jwt(token_auth.credentials)
            current_user_id = payload.get("sub")
        except Exception:
            pass

    favorite_ids = set()
    if current_user_id:
        stmt = select(UserFavoriteVenue.venue_id).where(UserFavoriteVenue.user_id == current_user_id)
        result = await db.execute(stmt)
        favorite_ids = set(result.scalars().all())

    # 3. Map Response
    results = []
    for venue in venues:
        item = VenueListItemBFF.model_validate(venue)
        item.is_favorite = venue.id in favorite_ids
        results.append(item)

    return results

@router.get("/profile-context", response_model=ProfileContextBFFResponse)
async def get_profile_context_bff(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
    auth_creds: Annotated[deps.HTTPAuthorizationCredentials, Depends(deps.security)],
):
    """
    BFF Endpoint for Profile Screen (Tab).
    Aggregates Profile + Recent Checkins + Wallet Summary.
    """
    # 1. Fetch Profile (Reuse logic from profiles.read_me roughly)
    # We do a direct join to be fast
    from sqlalchemy import text
    query = text("""
        SELECT p.*, r.name as role_name
        FROM public.profiles p
        LEFT JOIN public.app_roles r ON p.role_id = r.id
        WHERE p.id = :user_id
    """)
    result = await db.execute(query, {"user_id": current_user_id})
    row = result.mappings().first()
    
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Profile not found")

    # Resolve Username/Email fallback logic
    token_str = auth_creds.credentials
    payload = decode_supabase_jwt(token_str)
    jwt_email = payload.get("email", "")
    
    final_email = row.get("email") or jwt_email
    final_username = row.get("username")
    if not final_username:
         user_meta = payload.get("user_metadata", {})
         final_username = user_meta.get("username") or user_meta.get("display_name") or "Usuario"
         
    role_name = row.get("role_name") or "APP_USER"
    role_id = row.get("role_id") or 5
    
    profile_resp = ProfileResponse(
        id=row["id"],
        reputation_score=row["reputation_score"] or 0,
        points_current=row["points_current"] or 0,
        username=final_username,
        email=final_email,
        avatar_url=row.get("avatar_url"),
        role_id=role_id,
        role_name=role_name,
        roles=[role_name]
    )

    # 2. Fetch Recent Checkins (Limit 5)
    # Join with Venue to get Venue Name
    stmt_checkins = (
        select(Checkin, Venue.name.label("venue_name"))
        .join(Venue, Checkin.venue_id == Venue.id)
        .where(Checkin.user_id == current_user_id)
        .order_by(desc(Checkin.created_at))
        .limit(5)
    )
    res_checkins = await db.execute(stmt_checkins)
    checkin_rows = res_checkins.all() # list of (Checkin, venue_name)
    
    formatted_checkins = []
    for chk, v_name in checkin_rows:
        # Pydantic via from_attributes uses attributes, but we have venue_name separately.
        # We construct dict or patch object
        c_dict = {
            "id": chk.id, # BigInt
            "user_id": chk.user_id,
            "venue_id": chk.venue_id,
            "venue_name": v_name,
            "status": chk.status,
            "geofence_passed": chk.geofence_passed or False,
            "created_at": chk.created_at
        }
        formatted_checkins.append(CheckinResponse(**c_dict))

    # 3. Wallet Summary (Available Rewards)
    stmt_wallet = (
        select(func.count())
        .select_from(RewardUnit)
        .where(RewardUnit.user_id == current_user_id)
        .where(RewardUnit.status == 'available')
    )
    res_wallet = await db.execute(stmt_wallet)
    pending_count = res_wallet.scalar() or 0

    return ProfileContextBFFResponse(
        profile=profile_resp,
        recent_checkins=formatted_checkins,
        wallet_summary=WalletSummary(pending_rewards=pending_count)
    )

