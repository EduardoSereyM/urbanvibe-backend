from sqlalchemy import Column, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class UserFavoriteVenue(Base):
    __tablename__ = "user_favorite_venues"
    __table_args__ = (
        {"schema": "public"}
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), primary_key=True, nullable=False)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
