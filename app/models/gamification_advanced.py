from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class Badge(Base):
    __tablename__ = "badges"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    icon_url = Column(String)
    category = Column(String, default='GENERAL')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = {"schema": "public"}

    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), primary_key=True)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("public.badges.id"), primary_key=True)
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())

class Challenge(Base):
    __tablename__ = "challenges"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    
    challenge_type = Column(String, nullable=False) # CHECKIN_COUNT, etc.
    target_value = Column(Integer, default=1)
    filters = Column(JSONB, default={})
    
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    reward_points = Column(Integer, default=0)
    reward_badge_id = Column(UUID(as_uuid=True), ForeignKey("public.badges.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

class UserChallengeProgress(Base):
    __tablename__ = "user_challenge_progress"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"))
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("public.challenges.id"))
    
    current_value = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now())
