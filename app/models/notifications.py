from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

from app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=False, index=True)
    
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    type = Column(String, default="info") # info, warning, success, error
    
    is_read = Column(Boolean, default=False)
    data = Column(JSONB, nullable=True) # Metadata extra para navegación (ej: { "screen": "venue-detail", "id": "..." })
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("Profile", backref="notifications")

class UserDevice(Base):
    __tablename__ = "user_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=False, index=True)
    
    expo_token = Column(String, nullable=False, unique=True) # El token de Expo Push
    platform = Column(String, nullable=True) # ios, android, web
    
    last_used_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("Profile", backref="devices")
