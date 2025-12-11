
from sqlalchemy import Column, String, Integer
from app.db.base import Base

class AppRole(Base):
    __tablename__ = "app_roles"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
