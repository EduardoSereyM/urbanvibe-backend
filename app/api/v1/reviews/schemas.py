from pydantic import BaseModel, constr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# --- Shared ---
class ReactionBase(BaseModel):
    reaction_type: str = "helpful"

class ReactionCreate(ReactionBase):
    pass

class ReactionSchema(ReactionBase):
    id: int
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Reply Schemas ---
class ReviewReplyPayload(BaseModel):
    response: constr(min_length=1, max_length=1000)

# --- Reporting Schemas ---
class ContentReportCreate(BaseModel):
    target_type: str # 'review', 'venue', 'photo', 'user'
    target_id: UUID
    reason: str
    details: Optional[str] = None

class ContentReportSchema(ContentReportCreate):
    id: UUID
    reporter_id: Optional[UUID]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Review Schemas (Updated for V12.3) ---
class ReviewBase(BaseModel):
    general_score: float
    sub_scores: Optional[Dict[str, Any]] = {}
    comment: Optional[str] = None
    media_urls: Optional[List[str]] = []

class ReviewCreate(ReviewBase):
    venue_id: UUID
    checkin_id: Optional[int] = None

class ReviewUpdate(BaseModel):
    comment: Optional[str] = None
    general_score: Optional[float] = None
    media_urls: Optional[List[str]] = None

class ReviewSchema(ReviewBase):
    id: UUID
    venue_id: UUID
    user_id: UUID
    created_at: datetime
    helpful_count: int = 0
    report_count: int = 0
    
    # Owner Response
    owner_response: Optional[str] = None
    owner_responded_at: Optional[datetime] = None
    owner_responded_by: Optional[UUID] = None
    
    # User info (simplified for list view)
    user_display_name: Optional[str] = None
    user_avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True
