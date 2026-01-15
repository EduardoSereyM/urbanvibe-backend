from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
from geoalchemy2 import Geography
from app.models.levels import Level

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "public"}

    # En DDL: id uuid NOT NULL (FK a auth.users)
    id = Column(UUID(as_uuid=True), primary_key=True)
    
    username = Column(String, unique=True)
    email = Column(String)  # Read-only copy from Auth
    full_name = Column(String)
    display_name = Column(String)
    
    # Personal Info
    national_id = Column(String)
    birth_date = Column(Date)
    gender = Column(String)
    is_influencer = Column(Boolean, default=False)
    
    # Preferences & Attributes
    preferences = Column(JSONB, nullable=True, default={"dietary": [], "interests": [], "accessibility": {}})
    favorite_cuisines = Column(ARRAY(String)) # Postgres Array
    price_preference = Column(SmallInteger) # 1-4
    
    # Reputación & Contadores
    reputation_score = Column(Integer, default=0)
    current_level_id = Column(UUID(as_uuid=True), ForeignKey("public.levels.id"), nullable=True)
    points_current = Column(Integer, default=0)
    points_lifetime = Column(Integer, default=0)
    
    reviews_count = Column(Integer, default=0)
    photos_count = Column(Integer, default=0)
    verified_checkins_count = Column(Integer, default=0)
    
    # Referidos system
    referral_code = Column(String, unique=True, nullable=True)
    referred_by_user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    
    # Locations (Using USER-DEFINED in SQL, but likely Geography/Architecture dependent. 
    # For now, we omit complex geo-types here unless using GeoAlchemy specific types or just handling as columns if needed later)
    # home_location = Column(Geography...
    current_city = Column(String)
    
    is_verified = Column(Boolean, default=False)
    status = Column(String, server_default="active")
    
    avatar_url = Column(String)
    bio = Column(String)
    website = Column(String)
    
    role_id = Column(Integer, ForeignKey("public.app_roles.id"), default=5)  # 5 = APP_USER
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    current_level = relationship("Level", foreign_keys=[current_level_id], lazy="selectin")