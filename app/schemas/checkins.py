from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class CheckinCreate(BaseModel):
    token_id: str
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None
    # venue_id is optional in request if it's embedded in the token, but good to have if needed.
    # The prompt says: "Opcional: venue_id: UUID si decides enviarlo explícito"
    venue_id: Optional[UUID] = None

class CheckinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: UUID
    venue_id: UUID
    venue_name: Optional[str] = None
    status: str
    geofence_passed: bool
    created_at: datetime

    # Extended Attributes
    session_duration_minutes: Optional[int] = None
    visit_purpose: Optional[List[str]] = []
    spend_bucket: Optional[str] = None

class CheckinUpdate(BaseModel):
    session_duration_minutes: Optional[int] = None
    visit_purpose: Optional[List[str]] = []
    spend_bucket: Optional[str] = None
