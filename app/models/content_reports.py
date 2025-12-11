from sqlalchemy import Column, String, ForeignKey, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid

class ContentReport(Base):
    __tablename__ = "content_reports"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_type = Column(String, nullable=False) # 'review', 'venue', 'photo', 'user'
    target_id = Column(UUID(as_uuid=True), nullable=False)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=True)
    
    reason = Column(String, nullable=False) # 'spam', 'harassment', 'fake', 'off_topic'
    details = Column(Text, nullable=True)
    status = Column(String, default="pending") # 'pending', 'resolved', 'dismissed'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    reporter = relationship("Profile", backref="submitted_reports")
