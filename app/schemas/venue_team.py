from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

# Shared properties
class VenueTeamBase(BaseModel):
    is_active: bool = True

# Properties to receive on creation (Alta de personal)
class TeamMemberCreate(BaseModel):
    email: EmailStr
    full_name: str
    role_id: int = Field(..., description="3 for Manager, 4 for Staff")

# Properties to receive on update (Baja logic uses is_active=False)
class TeamMemberUpdate(BaseModel):
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

# Properties to return to client
class TeamMemberResponse(VenueTeamBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    venue_id: UUID
    user_id: UUID
    role_id: int
    created_at: datetime
    
    # Joined fields (will be populated by query)
    full_name: Optional[str] = None
    email: Optional[str] = None
    role_name: Optional[str] = None
