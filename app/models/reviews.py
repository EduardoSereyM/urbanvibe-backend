from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text, Numeric, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
# Avoid circular import at runtime by using string reference in ForeignKey, which is already there.
# But we ensure Venue is imported to registry.
# However, usually __init__.py handles this.
# Let's try to verify if 'venues' table name is correct in Venue model.
from app.db.base import Base

import uuid

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=False)
    checkin_id = Column(Integer, ForeignKey("public.checkins.id"), nullable=True)
    
    general_score = Column(Numeric(precision=3, scale=1), nullable=False)
    sub_scores = Column(JSONB, default={})
    comment = Column(Text, nullable=True)
    media_urls = Column(ARRAY(Text), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Interaction Metrics
    helpful_count = Column(Integer, default=0)
    report_count = Column(Integer, default=0)
    
    # Owner Response (V12.3)
    owner_response = Column(Text, nullable=True)
    owner_responded_at = Column(DateTime(timezone=True), nullable=True)
    owner_responded_by = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)

    # Relationships
    venue = relationship("Venue", backref="reviews")
    user = relationship("Profile", foreign_keys=[user_id], backref="reviews")
    checkin = relationship("Checkin", backref="review")
    # owner_responder = relationship("Profile", foreign_keys=[owner_responded_by]) # Optional, avoids circular dependency issues if simple

class ReviewReaction(Base):
    __tablename__ = "review_reactions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(UUID(as_uuid=True), ForeignKey("public.reviews.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=False)
    reaction_type = Column(String, default="helpful")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    review = relationship("Review", backref="reactions")
    user = relationship("Profile", backref="review_reactions")
