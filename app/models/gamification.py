import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class GamificationEvent(Base):
    __tablename__ = "gamification_events"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_code = Column(String, unique=True, nullable=False)
    target_type = Column(String, nullable=False) # 'user', 'venue'
    description = Column(Text)
    points = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    config = Column(JSONB, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class GamificationLog(Base):
    __tablename__ = "gamification_logs"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_code = Column(String, nullable=False)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=True)
    
    points = Column(Integer, nullable=False)
    source_entity = Column(String) # 'checkin', 'promotion', etc.
    source_id = Column(UUID(as_uuid=True))
    details = Column(JSONB, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
