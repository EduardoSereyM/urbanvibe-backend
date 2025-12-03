import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class QRToken(Base):
    __tablename__ = "qr_tokens"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)  # 'checkin', 'promo', 'invite'
    scope = Column(String, nullable=False)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)
    
    # Future use
    promotion_id = Column(UUID(as_uuid=True), ForeignKey("public.promotions.id"), nullable=True)
    campaign_key = Column(String, nullable=True)

    # Validity
    valid_from = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    max_uses = Column(Integer, default=1, nullable=False)
    used_count = Column(Integer, default=0, nullable=False)

    # Revocation
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_by = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    revoked_reason = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_used_by = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)

    meta = Column(JSONB, default={}, nullable=True)
