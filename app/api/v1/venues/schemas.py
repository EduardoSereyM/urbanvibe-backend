from typing import Any, Optional
from uuid import UUID

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict, Field, model_validator
from shapely.geometry import Point


class VenueBase(BaseModel):
    """Campos comunes a todas las vistas de Venue."""

    id: UUID
    name: str

    # Estado / reputación
    is_verified: bool = False
    trust_tier: Optional[str] = "standard"
    rating_average: float = 0.0
    review_count: int = 0
    verified_visits_monthly: int = 0
    is_founder_venue: bool = False

    # Precio
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    price_tier: Optional[int] = None
    avg_price_min: Optional[int] = None
    avg_price_max: Optional[int] = None
    currency_code: Optional[str] = "CLP"

    # Dirección básica
    address_display: Optional[str] = None

    # Ubicación geográfica (lat / lng)
    location: Optional[dict] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def parse_location(cls, data: Any) -> Any:
        """
        Si el objeto de entrada es una instancia ORM con columna `location`
        (GeoAlchemy2 Geography), la convertimos a un dict {lat, lng}.
        """
        if hasattr(data, "location") and data.location is not None:
            try:
                shape = to_shape(data.location)
                if isinstance(shape, Point):
                    base: dict[str, Any] = {}

                    # Campos que sabemos que pueden existir en el modelo ORM
                    for attr in [
                        "id",
                        "name",
                        "is_verified",
                        "trust_tier",
                        "rating_average",
                        "review_count",
                        "verified_visits_monthly",
                        "is_founder_venue",
                        "category_id",
                        "price_tier",
                        "avg_price_min",
                        "avg_price_max",
                        "currency_code",
                        "address_display",
                        "slug",
                        "slogan",
                        "logo_url",
                        "operational_status",
                        "legal_name",
                        "overview",
                        "cover_image_urls",
                        "address_street",
                        "address_number",
                        "city",
                        "region_state",
                        "country_code",
                        "timezone",
                        "google_place_id",
                        "directions_tip",
                        "opening_hours",
                        "payment_methods",
                        "features_config",
                        "favorites_count",  # ← AGREGADO
                    ]:
                        if hasattr(data, attr):
                            base[attr] = getattr(data, attr)
                    
                    if hasattr(data, "category") and data.category:
                        base["category_name"] = data.category.name

                    base["location"] = {"lat": shape.y, "lng": shape.x}
                    return base
            except Exception:
                return data

        # Fallback for non-ORM objects (if any) or validation when creating from dict
        # If it's a dict, we might need to preserve category_name if passed
        if isinstance(data, dict):
             return data
        
        # If it's ORM object but location is None or parse failed up there
        if hasattr(data, "category") and data.category:
             # We can't easily modify the ORM object to add category_name attribute dynamically 
             # without causing issues, but Pydantic with from_attributes=True
             # usually expects attributes to match.
             # However, since we are in `mode='before'`, we can return a dict representation.
             # But converting entire ORM to dict is expensive.
             # Easier approach: Add a property to the Model? No, modifying model again is annoying.
             # Best regex approach: Return a getter proxy?
             # Or just manually map it if we are returning `base` dict above.
             pass

        return data


class VenueMapPreviewResponse(VenueBase):
    """
    Schema optimizado para el modal del mapa.
    Hereda de VenueBase y no agrega nada más por ahora.
    """
    logo_url: Optional[str] = None


class VenueListResponse(VenueBase):
    """
    Schema para la lista de locales (pantalla list.tsx).
    Incluye algo más de información visual.
    """

    slug: Optional[str] = None
    slogan: Optional[str] = None
    logo_url: Optional[str] = None
    operational_status: Optional[str] = "open"


class VenueDetailResponse(VenueListResponse):
    """
    Schema para el detalle del local.
    Extiende la lista con información más completa.
    """

    legal_name: Optional[str] = None
    overview: Optional[str] = None
    cover_image_urls: list[str] = Field(default_factory=list)

    address_street: Optional[str] = None
    address_number: Optional[str] = None
    city: Optional[str] = None
    region_state: Optional[str] = None
    country_code: Optional[str] = None
    timezone: Optional[str] = None

    google_place_id: Optional[str] = None
    directions_tip: Optional[str] = None

    opening_hours: Optional[dict] = None
    payment_methods: Optional[dict] = None
    features_config: Optional[dict] = None
    favorites_count: int = 0
