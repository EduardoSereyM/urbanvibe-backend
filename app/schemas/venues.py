from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, Any, List, Dict
from uuid import UUID
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

class VenueBase(BaseModel):
    name: str
    trust_tier: Optional[str] = None
    is_verified: bool = False
    verified_visits_monthly: int = 0
    rating_average: float = 0.0
    
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
                    # We can't modify the SQLAlchemy instance directly safely if it's attached to a session in a way that forbids it,
                    # but Pydantic v2 validation runs on the data.
                    # We need to return a dict or object that has 'location' as a dict.
                    # Since we are in 'before' mode, 'data' is the ORM object.
                    # We can construct a dict with the fields we need.
                    
                    # Convert ORM object to dict to modify it safely for Pydantic
                    # This is a bit expensive but safe. 
                    # Alternatively, we can just return the object if we didn't need to transform 'location'.
                    # But we DO need to transform location.
                    
                    return {
                        "id": data.id,
                        "name": data.name,
                        "trust_tier": data.trust_tier,
                        "is_verified": data.is_verified,
                        "verified_visits_monthly": data.verified_visits_monthly,
                        "rating_average": data.rating_average,
                        "location": {"lat": shape.y, "lng": shape.x},
                        
                        # Include extended attributes in the dict
                        "connectivity_features": data.connectivity_features,
                        "accessibility_features": data.accessibility_features,
                        "space_features": data.space_features,
                        "comfort_features": data.comfort_features,
                        "audience_features": data.audience_features,
                        "entertainment_features": data.entertainment_features,
                        "dietary_options": data.dietary_options,
                        "access_features": data.access_features,
                        "security_features": data.security_features,
                        "mood_tags": data.mood_tags,
                        "occasion_tags": data.occasion_tags,
                        "music_profile": data.music_profile,
                        "crowd_profile": data.crowd_profile,
                        "pricing_profile": data.pricing_profile,
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
