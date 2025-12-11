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
    username: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    role_id: int | None = None  # SINGLE SOURCE OF TRUTH
    role_name: str | None = None
    roles: List[str] = []  # Deprecated but kept for backward compat if needed, will mirror role_name


class ProfileUpdate(BaseModel):
    """Schema para actualizar el perfil del usuario."""
    avatar_url: str | None = None
    # Future-proof: se pueden agregar más campos aquí
    preferences: dict | None = None


