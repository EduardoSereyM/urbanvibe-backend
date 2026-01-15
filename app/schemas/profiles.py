from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import List
from datetime import date

class ProfileBase(BaseModel):
    reputation_score: int = 0
    points_current: int = 0

    # Extended Attributes
    # Extended Attributes
    national_id: str | None = None
    birth_date: date | None = None # ISO Format 'YYYY-MM-DD'
    gender: str | None = None
    is_influencer: bool = False
    
    favorite_cuisines: List[str] = []
    price_preference: int | None = None # 1-4
    
    preferences: dict = {}
    
    # Counters
    reviews_count: int = 0
    photos_count: int = 0
    verified_checkins_count: int = 0
    
    # Referrals
    referral_code: str | None = None
    
    website: str | None = None
    bio: str | None = None
    
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
    full_name: str | None = None
    avatar_url: str | None = None
    role_id: int | None = None  # SINGLE SOURCE OF TRUTH
    role_name: str | None = None
    roles: List[str] = []  # Deprecated but kept for backward compat if needed, will mirror role_name
    
    current_level_name: str | None = None
    
    @property
    def current_level_name_computed(self):
        # Allow Pydantic to read from ORM relationship if available
        if hasattr(self, 'current_level') and self.current_level:
            return self.current_level.name
        return None
    
    # Or cleaner: update services to populate it? 
    # Or use Pydantic computed_field (v2)?
    # Since we are using from_attributes=True, we can just define a validator or use a getter.
    # But for "ProfileResponse" usually we just map it.
    # Let's add it as an optional field and update `get_profile` to join it? 
    # We added `lazy="selectin"` which is async compatible (mostly) but requires `await`? 
    # Actually `selectin` works with async session if object is retrieved via `await db.get`.
    # Pydantic v2 `from_attributes` might try to access it synchronously.
    # Safe bet: `mobile.py` constructs the response manually or we rely on `level_name` being populated in service.
    # Let's add the field here primarily.


class ProfileUpdate(BaseModel):
    """Schema para actualizar el perfil del usuario."""
    avatar_url: str | None = None
    full_name: str | None = None
    bio: str | None = None
    website: str | None = None
    
    # New Fields
    national_id: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    is_influencer: bool | None = None
    
    favorite_cuisines: List[str] | None = None
    price_preference: int | None = None
    
    preferences: dict | None = None


