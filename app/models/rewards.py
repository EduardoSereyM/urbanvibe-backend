import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class RewardUnit(Base):
    __tablename__ = "reward_units"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    promotion_id = Column(UUID(as_uuid=True), ForeignKey("public.promotions.id"), nullable=False)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    qr_token_id = Column(UUID(as_uuid=True), ForeignKey("public.qr_tokens.id"), nullable=True)
    
    status = Column(String, nullable=False, default='available') # 'available','reserved','consumed','expired'
    
    assigned_at = Column(DateTime(timezone=True))
    consumed_at = Column(DateTime(timezone=True))
    
    # Mapped to 'metadata' column in DB, but named 'meta_data' in Python to avoid conflict with Base.metadata
    meta_data = Column("metadata", JSONB, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Redemption(Base):
    __tablename__ = "redemptions"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=False)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)
    
    promotion_id = Column(UUID(as_uuid=True), ForeignKey("public.promotions.id"), nullable=True)
    reward_unit_id = Column(UUID(as_uuid=True), ForeignKey("public.reward_units.id"), nullable=True)
    qr_token_id = Column(UUID(as_uuid=True), ForeignKey("public.qr_tokens.id"), nullable=True)
    
    points_spent = Column(Integer, default=0)
    status = Column(String, nullable=False, default='confirmed') # 'pending','confirmed','cancelled'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    meta_data = Column("metadata", JSONB, default={})
