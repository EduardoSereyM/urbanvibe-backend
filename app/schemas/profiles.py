from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import List

class ProfileBase(BaseModel):
    reputation_score: int = 0
    points_current: int = 0

    # Extended Attributes
    preferences: dict = {}
    dietary_restrictions: List[str] = []
    accessibility_needs: List[str] = []
    music_preferences: List[str] = []
    vibe_preferences: List[str] = []
    avg_spend_willingness: int = 2

class ProfileResponse(ProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    roles: List[str] = []  # Lista de roles del usuario (ej: ["VENUE_OWNER", "SUPER_ADMIN"])
