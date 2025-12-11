import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    FetchedValue,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.sql import func
from geoalchemy2 import Geography

from app.db.base import Base


class Venue(Base):
    __tablename__ = "venues"
    __table_args__ = {"schema": "public"}

    # Identidad básica
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legal_name = Column(String(150), nullable=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(150), unique=True, nullable=True)
    slogan = Column(String(100), nullable=True)
    overview = Column(Text, nullable=True)

    # Categoría (FK opcional)
    category_id = Column(Integer, ForeignKey("public.venue_categories.id"), nullable=True)
    category = relationship("VenueCategory", lazy="joined")

    # Branding / media
    logo_url = Column(Text, nullable=True)
    cover_image_urls = Column(JSONB, nullable=True, default=[])

    # Geo / ubicación
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    geohash = Column(String(12), nullable=True)
    google_place_id = Column(String(255), nullable=True, unique=True)

    address_display = Column(String(255), nullable=True)
    address_street = Column(String(100), nullable=True)
    address_number = Column(String(20), nullable=True)
    directions_tip = Column(Text, nullable=True)
    
    # Ubicación extendida
    city = Column(String(100), nullable=True)
    region_state = Column(String(100), nullable=True)
    country_code = Column(String(10), nullable=True)

    # Precio
    contact_email = Column(String(255), nullable=True)
    website = Column(Text, nullable=True)

    price_tier = Column(SmallInteger, nullable=True, default=1)
    avg_price_min = Column(Float, nullable=True, default=0.0)
    avg_price_max = Column(Float, nullable=True, default=0.0)
    currency_code = Column(String(3), nullable=True, default='CLP')
    payment_methods = Column(JSONB, nullable=True, default={})

    # Confianza / reputación
    is_verified = Column(Boolean, nullable=True, default=False)
    verification_status = Column(String(20), nullable=True, default="pending")  # pending, verified, rejected
    is_founder_venue = Column(Boolean, nullable=True, default=False)
    is_featured = Column(Boolean, nullable=True, default=False)

    verified_visits_all_time = Column(Integer, nullable=True, default=0)
    verified_visits_monthly = Column(Integer, nullable=True, default=0)

    trust_tier = Column(String(20), nullable=True, default="standard")
    rating_average = Column(Float, nullable=True, default=0.0)
    review_count = Column(Integer, nullable=True, default=0)
    favorites_count = Column(Integer, nullable=True, default=0)
    
    # SEO / búsqueda
    seo_title = Column(String(70), nullable=True)
    seo_description = Column(String(160), nullable=True)
    search_vector = Column(TSVECTOR, FetchedValue(), nullable=True)

    # Features / administración
    features_config = Column(JSONB, nullable=True, default={"chat": False})
    admin_notes = Column(Text, nullable=True)

    # Documentación B2B
    company_tax_id = Column(String(50), nullable=True)
    ownership_proof_url = Column(Text, nullable=True)
    
    # Estado Operativo
    operational_status = Column(String(20), nullable=True, default="open")
    is_operational = Column(Boolean, nullable=True, default=True)
    opening_hours = Column(JSONB, nullable=True, default={})

    # Gamification / Menú
    menu_media_urls = Column(JSONB, nullable=True, default=[])
    menu_last_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Referidos
    referral_code = Column(String(50), unique=True, nullable=True)
    referred_by_user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    referred_by_venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=True)
    
    # Nuevas columnas de características (JSONB)
    connectivity_features = Column(JSONB, nullable=True, default=[])
    accessibility_features = Column(JSONB, nullable=True, default=[])
    space_features = Column(JSONB, nullable=True, default=[])
    comfort_features = Column(JSONB, nullable=True, default=[])
    audience_features = Column(JSONB, nullable=True, default=[])
    entertainment_features = Column(JSONB, nullable=True, default=[])
    dietary_options = Column(JSONB, nullable=True, default=[])
    access_features = Column(JSONB, nullable=True, default=[])
    security_features = Column(JSONB, nullable=True, default=[])
    mood_tags = Column(JSONB, nullable=True, default=[])
    occasion_tags = Column(JSONB, nullable=True, default=[])
    music_profile = Column(JSONB, nullable=True, default={})
    crowd_profile = Column(JSONB, nullable=True, default={})
    
    capacity_estimate = Column(SmallInteger, nullable=True)
    seated_capacity = Column(SmallInteger, nullable=True)
    standing_allowed = Column(Boolean, nullable=True, default=False)
    noise_level = Column(String, nullable=True)
    pricing_profile = Column(JSONB, nullable=True, default={})

    # Dueño / auditoría
    owner_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=True)

    # Notifications logic
    last_read_reviews_at = Column(DateTime(timezone=True), nullable=True)

    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
    )

    # B2B Economy
    points_balance = Column(Integer, nullable=False, default=0)