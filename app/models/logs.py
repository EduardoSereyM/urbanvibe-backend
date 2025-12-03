import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class MenuLog(Base):
    __tablename__ = "menu_logs"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)
    
    action = Column(String, nullable=False) # 'created','updated','deleted'
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PromoLog(Base):
    __tablename__ = "promo_logs"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    promotion_id = Column(UUID(as_uuid=True), ForeignKey("public.promotions.id"), nullable=False)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)
    
    action = Column(String, nullable=False) # 'created','updated','activated','deactivated','unit_created','unit_consumed'
    meta_data = Column("metadata", JSONB, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class QRLog(Base):
    __tablename__ = "qr_logs"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qr_token_id = Column(UUID(as_uuid=True), ForeignKey("public.qr_tokens.id"), nullable=False)
    
    action = Column(String, nullable=False) # 'scanned','validated','revoked','expired','used'
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=True)
    
    meta_data = Column("metadata", JSONB, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VenuePointsLog(Base):
    __tablename__ = "venue_points_logs"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)
    
    delta = Column(Integer, nullable=False)
    reason = Column(String(50), nullable=False)
    meta_data = Column("metadata", JSONB, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


