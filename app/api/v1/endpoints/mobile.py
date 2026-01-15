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
from app.models.reviews import Review
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

# --- Extended Schemas for Gamification ---
class BadgeBFFItem(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    category: str
    awarded_at: Optional[Any] = None

class ChallengeBFFItem(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    challenge_type: str
    target_value: int
    current_value: int
    is_completed: bool
    reward_points: int
    end_date: Optional[Any] = None

class ProfileContextBFFResponse(BaseModel):
    profile: ProfileResponse
    recent_checkins: List[CheckinResponse] = []
    wallet_summary: WalletSummary
    earned_badges: List[BadgeBFFItem] = []
    active_challenges: List[ChallengeBFFItem] = []
    referral_code: Optional[str] = None
    ambassador_status: Optional[str] = None


# --- ENDPOINTS ---
# ... (existing endpoints) ...

@router.get("/profile-context", response_model=ProfileContextBFFResponse)
async def get_profile_context_bff(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)],
    auth_creds: Annotated[deps.HTTPAuthorizationCredentials, Depends(deps.security)],
):
    """
    BFF Endpoint for Profile Screen (Tab).
    Aggregates Profile + Recent Checkins + Wallet Summary + Gamification.
    """
    # 1. Fetch Profile (Reuse logic from profiles.read_me roughly)
    # We do a direct join to be fast
    from sqlalchemy import text
    query = text("""
        SELECT p.*, r.name as role_name, l.name as current_level_name, l.id as current_level_id
        FROM public.profiles p
        LEFT JOIN public.app_roles r ON p.role_id = r.id
        LEFT JOIN public.levels l ON p.current_level_id = l.id
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
    
    # Calculate Dynamic Counters
    stmt_reviews = select(func.count()).select_from(Review).where(Review.user_id == current_user_id)
    res_reviews = await db.execute(stmt_reviews)
    reviews_count_val = res_reviews.scalar() or 0

    stmt_verified_checkins = select(func.count()).select_from(Checkin).where(
        Checkin.user_id == current_user_id, 
        Checkin.status == 'confirmed'
    )
    res_verified_checkins = await db.execute(stmt_verified_checkins)
    verified_checkins_val = res_verified_checkins.scalar() or 0

    profile_resp = ProfileResponse(
        id=row["id"],
        reputation_score=row["reputation_score"] or 0,
        points_current=row["points_current"] or 0,
        current_level_name=row.get("current_level_name"), # Mapped from join
        username=final_username,
        email=final_email,
        full_name=row.get("full_name"),
        avatar_url=row.get("avatar_url"),
        bio=row.get("bio"),
        website=row.get("website"),
        role_id=role_id,
        role_name=role_name,
        roles=[role_name],
        
        # Extended fields
        national_id=row.get("national_id"),
        birth_date=row.get("birth_date"),
        gender=row.get("gender"),
        is_influencer=row.get("is_influencer"),
        favorite_cuisines=row.get("favorite_cuisines") or [],
        price_preference=row.get("price_preference"),
        preferences=row.get("preferences") or {},
        referral_code=row.get("referral_code"),
        
        # Dynamic Counters
        reviews_count=reviews_count_val,
        verified_checkins_count=verified_checkins_val,
        photos_count=row.get("photos_count") or 0
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

    # 4. Fetch Earned Badges
    from app.models.gamification_advanced import UserBadge, Badge
    stmt_badges = (
        select(Badge, UserBadge.awarded_at)
        .join(UserBadge, Badge.id == UserBadge.badge_id)
        .where(UserBadge.user_id == current_user_id)
        .order_by(desc(UserBadge.awarded_at))
    )
    res_badges = await db.execute(stmt_badges)
    # Returns list of (Badge, awarded_at) due to select(Badge, UserBadge.awarded_at)
    badges_rows = res_badges.all() 
    
    formatted_badges = []
    for badge, awarded_at in badges_rows:
        formatted_badges.append(BadgeBFFItem(
            id=badge.id,
            name=badge.name,
            description=badge.description,
            icon_url=badge.icon_url,
            category=badge.category,
            awarded_at=awarded_at
        ))

    # 5. Fetch Active Challenges
    from app.models.gamification_advanced import UserChallengeProgress, Challenge
    stmt_challenges = (
        select(Challenge, UserChallengeProgress)
        .join(UserChallengeProgress, Challenge.id == UserChallengeProgress.challenge_id)
        .where(UserChallengeProgress.user_id == current_user_id)
        .where(UserChallengeProgress.is_completed == False)
        .where(Challenge.is_active == True)
        # Check dates implicitly via Challenge.is_active or add date check if strict
    )
    res_challenges = await db.execute(stmt_challenges)
    challenges_rows = res_challenges.all() # (Challenge, UserChallengeProgress)
    
    formatted_challenges = []
    for chal, prog in challenges_rows:
        formatted_challenges.append(ChallengeBFFItem(
            id=chal.id,
            title=chal.title,
            description=chal.description,
            challenge_type=chal.challenge_type,
            target_value=chal.target_value,
            current_value=prog.current_value,
            is_completed=prog.is_completed,
            reward_points=chal.reward_points,
            end_date=chal.period_end
        ))

    # 6. Referral Data (V12.4)
    from app.services.referral_service import referral_service
    ambassador_data = await referral_service.check_ambassador_status(db, current_user_id)
    # Convert dictionary to a readable string for the current schema
    ambassador_status_str = f"{ambassador_data['status_title']} ({ambassador_data['venues_referred']} locales)"

    return ProfileContextBFFResponse(
        profile=profile_resp,
        recent_checkins=formatted_checkins,
        wallet_summary=WalletSummary(pending_rewards=pending_count),
        earned_badges=formatted_badges,
        active_challenges=formatted_challenges,
        referral_code=row.get("referral_code"),
        ambassador_status=ambassador_status_str
    )


@router.get("/explore-context", response_model=ExploreContextResponse)
async def get_explore_context_bff(
    current_user_id: Annotated[UUID, Depends(deps.get_current_user_id)],
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    auth_creds: Annotated[Any, Depends(deps.get_current_user_auth_metadata)]
):
    """
    BFF Endpoint for Explore Screen (Map).
    Aggregates Profile Summary + Venues for Map.
    """
    # 1. Fetch Profile Summary
    stmt_profile = select(Profile).where(Profile.id == current_user_id)
    res_profile = await db.execute(stmt_profile)
    profile = res_profile.scalar_one_or_none()
    
    profile_summary = None
    if profile:
        # Username fallback
        display_name = profile.username 
        if not display_name:
            token_str = auth_creds.credentials
            payload = decode_supabase_jwt(token_str)
            user_meta = payload.get("user_metadata", {})
            display_name = user_meta.get("username") or user_meta.get("display_name") or "Viajero"

        profile_summary = ProfileSummary(
            id=profile.id,
            username=display_name,
            avatar_url=profile.avatar_url,
            points_current=profile.points_current
        )

    # 2. Fetch Map Venues 
    # Logic similar to get_venues_list but ensuring lat/lng.
    # For now, return all ACTIVE venues.
    stmt_venues = select(Venue).where(Venue.is_operational == True)
    res_venues = await db.execute(stmt_venues)
    venues = res_venues.scalars().all()
    
    map_items = []
    for v in venues:
        if v.latitude and v.longitude: # Only map valid coords
             menu_media = v.menu_media_urls or [] # List[dict]
             cover_images = v.cover_image_urls or []
             # ensure cover_images is list of str
             
             map_items.append(VenueMapItem(
                 id=v.id,
                 name=v.name,
                 location={"lat": v.latitude, "lng": v.longitude}, # Legacy
                 latitude=v.latitude,
                 longitude=v.longitude,
                 category_name=v.category.name if v.category else None,
                 rating_average=v.rating_average or 0.0,
                 price_tier=v.price_tier or 1,
                 logo_url=v.logo_url,
                 cover_image_urls=cover_images, 
                 address_display=v.address_display,
                 is_verified=v.is_verified
             ))

    return ExploreContextResponse(
        profile=profile_summary,
        map_venues=map_items
    )

