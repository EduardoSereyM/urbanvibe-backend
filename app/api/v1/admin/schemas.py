from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.schemas.opening_hours import OpeningHours


class VenueOwnerInfo(BaseModel):
    """Información del dueño del venue"""
    id: UUID
    display_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None


class VenueTeamMember(BaseModel):
    """Miembro del equipo del venue"""
    user_id: UUID
    display_name: Optional[str] = None
    email: EmailStr
    role: str  # VENUE_OWNER, VENUE_MANAGER, VENUE_STAFF
    is_active: bool
    joined_at: Optional[datetime] = None


class VenueMetrics(BaseModel):
    """Métricas del venue"""
    total_verified_visits: int = 0
    verified_visits_this_month: int = 0
    rating_average: float = 0.0
    total_reviews: int = 0


class VenueAddressInfo(BaseModel):
    """Información de dirección del venue"""
    address_display: Optional[str] = None
    city: Optional[str] = None
    region_state: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_street: Optional[str] = None
    address_number: Optional[str] = None
    directions_tip: Optional[str] = None


class VenueContactInfo(BaseModel):
    """Información de contacto del venue"""
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class VenueFeatures(BaseModel):
    """Features del venue"""
    has_parking: bool = False
    has_wifi: bool = False
    accepts_reservations: bool = False
    is_pet_friendly: bool = False
    # Permitir otros campos
    model_config = ConfigDict(extra="allow")


class VenueUpdate(BaseModel):
    """Schema para actualizar un venue"""
    name: Optional[str] = None
    legal_name: Optional[str] = None
    slogan: Optional[str] = None
    overview: Optional[str] = None
    verification_status: Optional[str] = None  # pending, verified, rejected
    operational_status: Optional[str] = None
    is_operational: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_founder_venue: Optional[bool] = None
    address_street: Optional[str] = None
    address_number: Optional[str] = None
    city: Optional[str] = None
    region_state: Optional[str] = None
    country_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    directions_tip: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    features_config: Optional[Dict[str, Any]] = None
    admin_notes: Optional[str] = None
    referral_code: Optional[str] = None
    owner_id: Optional[UUID] = None
    company_tax_id: Optional[str] = None
    category_id: Optional[int] = None
    payment_methods: Optional[Dict[str, Any]] = None
    opening_hours: Optional[Dict[str, Any]] = None
    
    # Media
    logo_url: Optional[str] = None
    cover_image_urls: Optional[List[str]] = None
    menu_media_urls: Optional[List[str]] = None
    ownership_proof_url: Optional[str] = None
    
    # Extended Features
    connectivity_features: Optional[List[str]] = None
    accessibility_features: Optional[List[str]] = None
    space_features: Optional[List[str]] = None
    comfort_features: Optional[List[str]] = None
    audience_features: Optional[List[str]] = None
    entertainment_features: Optional[List[str]] = None
    dietary_options: Optional[List[str]] = None
    access_features: Optional[List[str]] = None
    security_features: Optional[List[str]] = None
    mood_tags: Optional[List[str]] = None
    occasion_tags: Optional[List[str]] = None
    
    # Profiles
    music_profile: Optional[Dict[str, Any]] = None
    crowd_profile: Optional[Dict[str, Any]] = None
    pricing_profile: Optional[Dict[str, Any]] = None
    
    # Capacity & Noise
    capacity_estimate: Optional[int] = None
    seated_capacity: Optional[int] = None
    standing_allowed: Optional[bool] = None
    noise_level: Optional[str] = None
    
    price_tier: Optional[int] = None
    avg_price_min: Optional[int] = None
    avg_price_max: Optional[int] = None
    currency_code: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    legal_name: Optional[str] = None
    city: Optional[str] = None
    address_display: Optional[str] = None
    verification_status: Optional[str] = "pending"
    operational_status: Optional[str] = "open"
    is_operational: bool = True
    rating_average: float = 0.0
    review_count: int = 0
    verified_visits_all_time: int = 0
    created_at: datetime
    owner: Optional[VenueOwnerInfo] = None


class VenueAdminListItem(BaseModel):
    """Item en la lista de venues para admin"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    legal_name: Optional[str] = None
    city: Optional[str] = None
    address_display: Optional[str] = None
    verification_status: Optional[str] = "pending"
    operational_status: Optional[str] = "open"
    is_operational: bool = True
    is_verified: bool = False
    rating_average: float = 0.0
    total_reviews: int = 0
    total_verified_visits: int = 0
    created_at: datetime
    owner: Optional[VenueOwnerInfo] = None


class VenueAdminListResponse(BaseModel):
    """Respuesta paginada de lista de venues"""
    venues: List[VenueAdminListItem]
    total: int
    skip: int
    limit: int


class VenueAdminDetail(BaseModel):
    """Detalle completo de un venue para admin"""
    model_config = ConfigDict(from_attributes=True)
    
    # Información básica
    id: UUID
    name: str
    legal_name: Optional[str] = None
    slogan: Optional[str] = None
    overview: Optional[str] = None
    
    # Estado
    verification_status: Optional[str] = "pending"
    operational_status: Optional[str] = "open"
    is_operational: bool = True
    is_verified: bool = False
    is_founder_venue: bool = False
    
    # Dirección
    address: VenueAddressInfo
    directions_tip: Optional[str] = None
    
    # Contacto
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    
    # Métricas
    metrics: VenueMetrics
    
    # Equipo
    team: List[VenueTeamMember] = []
    
    # Configuración
    features_config: Optional[dict] = None
    opening_hours: Optional[OpeningHours] = None
    
    # Extended Attributes
    connectivity_features: Optional[List[str]] = []
    accessibility_features: Optional[List[str]] = []
    space_features: Optional[List[str]] = []
    comfort_features: Optional[List[str]] = []
    audience_features: Optional[List[str]] = []
    entertainment_features: Optional[List[str]] = []
    dietary_options: Optional[List[str]] = []
    access_features: Optional[List[str]] = []
    security_features: Optional[List[str]] = []
    mood_tags: Optional[List[str]] = []
    occasion_tags: Optional[List[str]] = []
    
    music_profile: Optional[Dict[str, Any]] = {}
    crowd_profile: Optional[Dict[str, Any]] = {}
    pricing_profile: Optional[Dict[str, Any]] = {}

    capacity_estimate: Optional[int] = None
    seated_capacity: Optional[int] = None
    standing_allowed: Optional[bool] = False
    noise_level: Optional[str] = None
    payment_methods: Optional[dict] = None
    
    # Auditoría
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: Optional[UUID] = None
    owner: Optional[VenueOwnerInfo] = None
    
    # Missing fields
    category_id: Optional[int] = None
    company_tax_id: Optional[str] = None
    admin_notes: Optional[str] = None
    referral_code: Optional[str] = None
    
    # Media
    logo_url: Optional[str] = None
    cover_image_urls: Optional[List[str]] = None
    menu_media_urls: Optional[List[str]] = None
    menu_last_updated_at: Optional[datetime] = None
    ownership_proof_url: Optional[str] = None
    
    # Price
    price_tier: Optional[int] = None
    avg_price_min: Optional[int] = None
    avg_price_max: Optional[int] = None
    currency_code: Optional[str] = None


# --- USERS SCHEMAS ---

class UserRoleInfo(BaseModel):
    role_name: str
    venue_id: Optional[UUID] = None
    venue_name: Optional[str] = None
    is_active: bool = True
    assigned_at: Optional[datetime] = None


class UserAuthInfo(BaseModel):
    created_at: Optional[datetime] = None
    last_sign_in_at: Optional[datetime] = None
    email_confirmed_at: Optional[datetime] = None
    phone: Optional[str] = None
    phone_confirmed_at: Optional[datetime] = None


class UserActivityInfo(BaseModel):
    total_venues_owned: int = 0
    total_reviews: int = 0
    total_check_ins: int = 0
    last_activity_at: Optional[datetime] = None


class VenueOwnedInfo(BaseModel):
    id: UUID
    name: str
    role: str
    is_active: bool = True


class UserAdminListItem(BaseModel):
    """Item en la lista de usuarios para admin"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: Optional[str] = None
    display_name: Optional[str] = None
    reputation_score: int = 0
    points_current: int = 0
    roles: List[str] = []
    created_at: Optional[datetime] = None
    last_sign_in_at: Optional[datetime] = None
    is_active: bool = True
    total_venues: int = 0
    total_reviews: int = 0


class UserAdminListResponse(BaseModel):
    """Respuesta paginada de lista de usuarios"""
    users: List[UserAdminListItem]
    total: int
    skip: int
    limit: int


class UserAdminDetail(BaseModel):
    """Detalle completo de usuario para admin"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: Optional[str] = None
    display_name: Optional[str] = None
    reputation_score: int = 0
    points_current: int = 0
    points_lifetime: int = 0
    
    roles: List[UserRoleInfo] = []
    auth_info: UserAuthInfo
    activity: UserActivityInfo
    venues_owned: List[VenueOwnedInfo] = []


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    display_name: Optional[str] = None
    reputation_score: Optional[int] = None
    points_current: Optional[int] = None
    is_active: Optional[bool] = None


# --- METRICS SCHEMAS ---

class MetricsTotals(BaseModel):
    total_users: int = 0
    total_venues: int = 0
    total_reviews: int = 0
    total_verified_visits: int = 0
    active_users_last_30d: int = 0


class MetricsVenuesByStatus(BaseModel):
    verified: int = 0
    pending: int = 0
    rejected: int = 0


class MetricsVenuesByOperational(BaseModel):
    operational: int = 0
    inactive: int = 0


class CityCount(BaseModel):
    city: str
    count: int


class MetricsVenues(BaseModel):
    by_status: MetricsVenuesByStatus
    by_operational_status: MetricsVenuesByOperational
    by_city: List[CityCount] = []
    founder_venues: int = 0


class MetricsUsersByRole(BaseModel):
    APP_USER: int = 0
    VENUE_OWNER: int = 0
    VENUE_MANAGER: int = 0
    VENUE_STAFF: int = 0
    SUPER_ADMIN: int = 0


class MetricsUsers(BaseModel):
    by_role: MetricsUsersByRole
    new_users_last_30d: int = 0
    active_users_last_7d: int = 0


class MetricsActivity(BaseModel):
    reviews_last_30d: int = 0
    check_ins_last_30d: int = 0
    new_venues_last_30d: int = 0


class TopVenue(BaseModel):
    id: UUID
    name: str
    city: Optional[str] = None
    rating_average: float = 0.0
    total_reviews: int = 0
    total_verified_visits: int = 0


class RecentActivityItem(BaseModel):
    type: str  # new_venue, new_user, venue_verified
    venue_name: Optional[str] = None
    user_email: Optional[str] = None
    timestamp: datetime


class MetricsResponse(BaseModel):
    totals: MetricsTotals
    venues: MetricsVenues
    users: MetricsUsers
    activity: MetricsActivity
    top_venues: List[TopVenue] = []
    recent_activity: List[RecentActivityItem] = []
