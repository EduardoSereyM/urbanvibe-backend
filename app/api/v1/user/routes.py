from fastapi import APIRouter, Depends
from app.api import deps
from app.models.profiles import Profile
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

class ProfileResponse(BaseModel):
    id: UUID
    username: str | None
    full_name: str | None
    email: str | None
    role_id: int = 5
    # Add other fields as needed
    class Config:
        from_attributes = True

@router.get("/me", response_model=ProfileResponse)
def get_user_me(
    current_user: Profile = Depends(deps.get_current_user),
):
    """
    Get current user profile.
    """
    return current_user
