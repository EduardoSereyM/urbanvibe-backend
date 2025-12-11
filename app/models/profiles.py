from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from app.db.base import Base
from geoalchemy2 import Geography

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "public"}

    # En DDL: id uuid NOT NULL (FK a auth.users)
    id = Column(UUID(as_uuid=True), primary_key=True)
    
    username = Column(String, unique=True)
    email = Column(String)  # Read-only copy from Auth
    full_name = Column(String)
    display_name = Column(String)
    
    # Reputación
    reputation_score = Column(Integer, default=0)
    points_current = Column(Integer, default=0)
    points_lifetime = Column(Integer, default=0)
    
    preferences = Column(JSONB, nullable=True, default={})
    
    # Referidos
    referral_code = Column(String, unique=True, nullable=True)
    referred_by_user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    
    is_verified = Column(Boolean, default=False)
    status = Column(String, server_default="active")
    
    avatar_url = Column(String)
    bio = Column(String)
    
    role_id = Column(Integer, ForeignKey("public.app_roles.id"), default=5)  # 5 = APP_USER
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())