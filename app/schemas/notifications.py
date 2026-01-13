from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class DeviceRegistration(BaseModel):
    token: str
    platform: Optional[str] = "unknown"

class NotificationResponse(BaseModel):
    id: UUID
    title: str
    body: str
    type: str # info, warning, success
    is_read: bool
    data: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
