from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class OpeningHoursException(BaseModel):
    date: str
    label: Optional[str] = None
    open: Optional[str] = None
    close: Optional[str] = None
    closed: bool = False


class OpeningHoursRegularSlot(BaseModel):
    day: str  # 'monday'...'sunday'
    open: Optional[str] = None
    close: Optional[str] = None
    closed: bool = False


class OpeningHoursConfig(BaseModel):
    timezone: str = "America/Santiago"
    regular: List[OpeningHoursRegularSlot]
    exceptions: List[OpeningHoursException] = []


class VenueAddress(BaseModel):
    address_display: Optional[str] = None
    city: Optional[str] = None
    region_state: Optional[str] = None
    country_code: Optional[str] = "CL"


class VenueFeaturesConfig(BaseModel):
    chat: bool = False
    checkins_history_days: Optional[int] = None
    advanced_dashboard: Optional[bool] = None


class VenueCreate(BaseModel):
    legal_name: Optional[str] = None
    name: str
    slogan: Optional[str] = None
    overview: Optional[str] = None
    category_id: Optional[int] = None
    opening_hours: Optional[OpeningHoursConfig] = None
    latitude: float = Field(..., description="Latitude in WGS84")
    longitude: float = Field(..., description="Longitude in WGS84")
    address: Optional[VenueAddress] = None
    
    # Media
    logo_url: Optional[str] = None
    cover_image_urls: Optional[List[str]] = None
    
    # Details
    price_tier: Optional[int] = Field(None, ge=1, le=4)
    currency_code: Optional[str] = "CLP"
    payment_methods: Optional[Dict[str, bool]] = None
    
    # Location Extras
    google_place_id: Optional[str] = None
    directions_tip: Optional[str] = None
    
    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    
    # B2B
    company_tax_id: Optional[str] = Field(None, max_length=50)
    ownership_proof_url: Optional[str] = None
    is_founder_venue: bool = False

    # Attributes
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
    
    music_profile: Optional[Dict] = {}
    crowd_profile: Optional[Dict] = {}
    
    capacity_estimate: Optional[int] = None
    seated_capacity: Optional[int] = None
    standing_allowed: bool = False
    noise_level: Optional[str] = "moderate"


class VenueSummaryForOwner(BaseModel):
    id: UUID
    type: Optional[str] = None
    parent_id: Optional[UUID] = None
    name: str
    city: Optional[str] = None
    operational_status: Optional[str] = None
    is_founder_venue: bool = False
    verification_status: str
    roles: List[str] = []
    features_config: Optional[VenueFeaturesConfig] = None
    logo_url: Optional[str] = None
    created_at: datetime


class MyVenuesResponse(BaseModel):
    venues: List[VenueSummaryForOwner]


class VenueB2BDetail(BaseModel):
    id: UUID
    type: Optional[str]
    parent_id: Optional[UUID]
    name: str
    legal_name: Optional[str]
    slogan: Optional[str]
    overview: Optional[str]
    category_id: Optional[int]
    owner_id: Optional[UUID] = None
    
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[VenueAddress] = None
    google_place_id: Optional[str] = None
    directions_tip: Optional[str] = None
    
    # Media
    logo_url: Optional[str] = None
    cover_image_urls: Optional[List[str]] = None
    
    # Details
    opening_hours: Optional[OpeningHoursConfig]
    operational_status: Optional[str]
    price_tier: Optional[int] = None
    currency_code: Optional[str] = None
    payment_methods: Optional[Dict[str, bool]] = None
    
    # Status
    is_founder_venue: bool
    verification_status: str
    features_config: Optional[VenueFeaturesConfig]
    
    # Stats
    verified_visits_all_time: int
    verified_visits_monthly: int
    rating_average: float
    review_count: int
    
    # SEO
    seo_title: Optional[str] = None
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class OpeningHoursException(BaseModel):
    date: str
    label: Optional[str] = None
    open: Optional[str] = None
    close: Optional[str] = None
    closed: bool = False


class OpeningHoursRegularSlot(BaseModel):
    day: str  # 'monday'...'sunday'
    open: Optional[str] = None
    close: Optional[str] = None
    closed: bool = False


class OpeningHoursConfig(BaseModel):
    timezone: str = "America/Santiago"
    regular: List[OpeningHoursRegularSlot]
    exceptions: List[OpeningHoursException] = []


class VenueAddress(BaseModel):
    address_display: Optional[str] = None
    city: Optional[str] = None
    region_state: Optional[str] = None
    country_code: Optional[str] = "CL"


class VenueFeaturesConfig(BaseModel):
    chat: bool = False
    checkins_history_days: Optional[int] = None
    advanced_dashboard: Optional[bool] = None


class VenueCreate(BaseModel):
    legal_name: Optional[str] = None
    name: str
    slogan: Optional[str] = None
    overview: Optional[str] = None
    category_id: Optional[int] = None
    opening_hours: Optional[OpeningHoursConfig] = None
    latitude: float = Field(..., description="Latitude in WGS84")
    longitude: float = Field(..., description="Longitude in WGS84")
    address: Optional[VenueAddress] = None
    
    # Media
    logo_url: Optional[str] = None
    cover_image_urls: Optional[List[str]] = None
    
    # Details
    price_tier: Optional[int] = Field(None, ge=1, le=4)
    currency_code: Optional[str] = "CLP"
    payment_methods: Optional[Dict[str, bool]] = None
    
    # Location Extras
    google_place_id: Optional[str] = None
    directions_tip: Optional[str] = None
    
    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    
    # B2B
    company_tax_id: Optional[str] = Field(None, max_length=50)
    ownership_proof_url: Optional[str] = None
    is_founder_venue: bool = False

    # Attributes
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
    
    music_profile: Optional[Dict] = {}
    crowd_profile: Optional[Dict] = {}
    
    capacity_estimate: Optional[int] = None
    seated_capacity: Optional[int] = None
    standing_allowed: bool = False
    noise_level: Optional[str] = "moderate"


class VenueSummaryForOwner(BaseModel):
    id: UUID
    type: Optional[str] = None
    parent_id: Optional[UUID] = None
    name: str
    city: Optional[str] = None
    operational_status: Optional[str] = None
    is_founder_venue: bool = False
    verification_status: str
    roles: List[str] = []
    features_config: Optional[VenueFeaturesConfig] = None
    logo_url: Optional[str] = None
    created_at: datetime


class MyVenuesResponse(BaseModel):
    venues: List[VenueSummaryForOwner]


class VenueB2BDetail(BaseModel):
    id: UUID
    type: Optional[str]
    parent_id: Optional[UUID]
    name: str
    legal_name: Optional[str]
    slogan: Optional[str]
    overview: Optional[str]
    category_id: Optional[int]
    owner_id: Optional[UUID] = None
    
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[VenueAddress] = None
    google_place_id: Optional[str] = None
    directions_tip: Optional[str] = None
    
    # Media
    logo_url: Optional[str] = None
    cover_image_urls: Optional[List[str]] = None
    
    # Details
    opening_hours: Optional[OpeningHoursConfig]
    operational_status: Optional[str]
    price_tier: Optional[int] = None
    currency_code: Optional[str] = None
    payment_methods: Optional[Dict[str, bool]] = None
    
    # Status
    is_founder_venue: bool
    verification_status: str
    features_config: Optional[VenueFeaturesConfig]
    
    # Stats
    verified_visits_all_time: int
    verified_visits_monthly: int
    rating_average: float
    review_count: int
    
    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    
    # B2B
    company_tax_id: Optional[str] = None
    ownership_proof_url: Optional[str] = None
    
    points_balance: int = 0
    
    created_at: datetime
    updated_at: datetime


class VenueCheckinDetail(BaseModel):
    id: int
    user_id: UUID
    user_display_name: Optional[str] = None
    user_email: Optional[str] = None
    status: str
    geofence_passed: bool
    points_awarded: int
    created_at: datetime

class VenueCheckinListResponse(BaseModel):
    checkins: List[VenueCheckinDetail]


class CheckinStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(confirmed|rejected|pending)$")


class PromotionBase(BaseModel):
    title: str
    # description: Optional[str] = None
    image_url: Optional[str] = None
    active_days: Optional[Dict] = None
    target_audience: Optional[Dict] = None
    
    promo_type: str = "standard"  # standard, uv_reward
    reward_tier: Optional[str] = None  # LOW, MID, HIGH
    points_cost: Optional[int] = None
    
    is_recurring: bool = False
    schedule_config: Optional[Dict] = {}
    total_units: Optional[int] = None
    
    is_active: bool = True
    # start_date: Optional[datetime] = None
    # end_date: Optional[datetime] = None
    
    valid_until: Optional[datetime] = None
    
    is_highlighted: bool = False
    highlight_until: Optional[datetime] = None


class PromotionCreate(PromotionBase):
    pass


class Promotion(PromotionBase):
    id: UUID
    venue_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VenuePointsLog(BaseModel):
    id: UUID
    venue_id: UUID
    delta: int
    reason: str
    metadata: Optional[Dict] = {}
    created_at: datetime

    class Config:
        from_attributes = True


class ValidateRewardRequest(BaseModel):
    qr_content: str


class ValidateRewardResponse(BaseModel):
    success: bool
    message: str
    points_earned: Optional[int] = 0
