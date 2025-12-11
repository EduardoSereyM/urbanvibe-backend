from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class VenueTeam(Base):
    __tablename__ = "venue_team"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=False, index=True)
    
    # 3 = VENUE_MANAGER, 4 = VENUE_STAFF
    role_id = Column(Integer, ForeignKey("public.app_roles.id"), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
