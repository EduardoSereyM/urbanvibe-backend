from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Any, List, Dict
from uuid import UUID
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

class VenueBase(BaseModel):
    name: str
    slogan: Optional[str] = None
    overview: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    cover_image_urls: Optional[List[str]] = []
    menu_media_urls: Optional[List[Dict[str, Any]]] = []
    
    # Contact & Loc
    address_display: Optional[str] = None
    city: Optional[str] = None
    region_state: Optional[str] = None
    country_code: Optional[str] = "CL"
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    
    # Price & Ops
    price_tier: Optional[int] = 1
    currency_code: Optional[str] = "CLP"
    operational_status: Optional[str] = "open"
    opening_hours: Optional[Dict[str, Any]] = {}

    trust_tier: Optional[str] = None
    is_verified: bool = False
    verification_status: Optional[str] = None
    is_founder_venue: Optional[bool] = False
    verified_visits_monthly: int = 0
    rating_average: float = 0.0
    review_count: int = 0
    favorites_count: int = 0
    
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

class VenueResponse(VenueBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    location: Optional[Dict[str, float]] = None

    @model_validator(mode='before')
    @classmethod
    def parse_location(cls, data: Any) -> Any:
        # Handle SQLAlchemy model instance
        if hasattr(data, 'location') and data.location is not None:
            # If it's a WKBElement (GeoAlchemy2), convert to shape
            try:
                shape = to_shape(data.location)
                if isinstance(shape, Point):
                    # Convert ORM object to dict to include all fields
                    return {
                        "id": data.id,
                        "name": data.name,
                        "slogan": data.slogan,
                        "overview": data.overview,
                        "category_id": data.category_id,
                        "category_name": getattr(data, 'category_name', None),
                        
                        # Branding
                        "logo_url": data.logo_url,
                        "cover_image_urls": data.cover_image_urls or [],
                        "menu_media_urls": data.menu_media_urls or [],
                        
                        # Contact & Location
                        "address_display": data.address_display,
                        "city": data.city,
                        "region_state": data.region_state,
                        "country_code": data.country_code,
                        "website": data.website,
                        "contact_email": data.contact_email,
                        "contact_phone": data.contact_phone,
                        
                        # Price & Operations
                        "price_tier": data.price_tier,
                        "currency_code": data.currency_code,
                        "operational_status": data.operational_status,
                        "opening_hours": data.opening_hours or {},
                        
                        # Trust & Metrics - use database values directly
                        "trust_tier": data.trust_tier,
                        "is_verified": data.is_verified,
                        "verification_status": data.verification_status,
                        "is_founder_venue": data.is_founder_venue,
                        "verified_visits_monthly": data.verified_visits_monthly,
                        "rating_average": float(data.rating_average) if data.rating_average else 0.0,
                        "review_count": data.review_count or 0,
                        "favorites_count": (lambda: (
                            print(f"🔍 SCHEMA: data.favorites_count = {data.favorites_count}"),
                            print(f"🔍 SCHEMA: hasattr = {hasattr(data, 'favorites_count')}"),
                            print(f"🔍 SCHEMA: Final value = {data.favorites_count or 0}"),
                            data.favorites_count or 0
                        )[3])(),
                        
                        "location": {"lat": shape.y, "lng": shape.x},
                        
                        # Extended attributes
                        "connectivity_features": data.connectivity_features or [],
                        "accessibility_features": data.accessibility_features or [],
                        "space_features": data.space_features or [],
                        "comfort_features": data.comfort_features or [],
                        "audience_features": data.audience_features or [],
                        "entertainment_features": data.entertainment_features or [],
                        "dietary_options": data.dietary_options or [],
                        "access_features": data.access_features or [],
                        "security_features": data.security_features or [],
                        "mood_tags": data.mood_tags or [],
                        "occasion_tags": data.occasion_tags or [],
                        "music_profile": data.music_profile or {},
                        "crowd_profile": data.crowd_profile or {},
                        "pricing_profile": data.pricing_profile or {},
                        "capacity_estimate": data.capacity_estimate,
                        "seated_capacity": data.seated_capacity,
                        "standing_allowed": data.standing_allowed,
                        "noise_level": data.noise_level,
                    }
            except Exception:
                pass
        return data

class QRCodeResponse(BaseModel):
    qr_content: str
    type: str = "static"
