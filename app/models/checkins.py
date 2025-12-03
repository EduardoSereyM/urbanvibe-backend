from sqlalchemy import Column, String, Integer, Boolean, Float, BigInteger, ForeignKey, DateTime, Date, Text, SmallInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from geoalchemy2 import Geography
from app.db.base import Base

class Checkin(Base):
    __tablename__ = "checkins"
    __table_args__ = {"schema": "public"}

    # CORRECCIÓN: En DDL es 'bigint GENERATED ALWAYS AS IDENTITY'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.profiles.id"), nullable=False)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("public.venues.id"), nullable=False)

    # Geo
    location = Column(Geography(geometry_type="POINT", srid=4326))
    user_accuracy_m = Column(Float)
    geofence_passed = Column(Boolean, default=False)
    
    # Token y Estado
    token_id = Column(UUID(as_uuid=True), ForeignKey("public.qr_tokens.id"), unique=True, nullable=False)
    status = Column(String, default="pending") 
    
    # Gamificación
    points_awarded = Column(Integer, default=0)
    
    # Fechas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checkin_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Nuevos campos
    session_duration_minutes = Column(Integer, nullable=True)
    visit_purpose = Column(JSONB, nullable=True, default=[])
    spend_bucket = Column(String, nullable=True)