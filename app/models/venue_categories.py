from sqlalchemy import Column, Integer, String
from app.db.base import Base

class VenueCategory(Base):
    __tablename__ = "venue_categories"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icon_slug = Column(String, nullable=True)
