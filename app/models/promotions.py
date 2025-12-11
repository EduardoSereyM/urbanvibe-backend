import uuid
import enum

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class Promotion(Base):
    __tablename__ = "promotions"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)
    
    title = Column(String, nullable=False)
    # description = Column(Text)  <-- Removed as it doesn't exist in DB
    image_url = Column(String)
    
    # Standard fields
    active_days = Column(JSONB, default={})
    target_audience = Column(JSONB, default={})
    
    # New Gamification fields
    promo_type = Column(String, default='standard') # 'standard', 'uv_reward'
    reward_tier = Column(String, nullable=True) # 'LOW', 'MID', 'HIGH'
    points_cost = Column(Integer, nullable=True)
    
    is_recurring = Column(Boolean, default=False)
    schedule_config = Column(JSONB, default={})
    total_units = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # start_date = Column(DateTime(timezone=True))
    # end_date = Column(DateTime(timezone=True))
    
    valid_until = Column(DateTime(timezone=True), nullable=False)
    
    is_highlighted = Column(Boolean, default=False)
    highlight_until = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PromotionType(str, enum.Enum):
    STANDARD = "standard"
    UV_REWARD = "uv_reward"


