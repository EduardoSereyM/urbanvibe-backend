from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request body for login endpoint"""
    username: EmailStr  # OAuth2 usa 'username' pero puede ser email
    password: str


class TokenResponse(BaseModel):
    """Response from login endpoint"""
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    """Request body for register endpoint"""
    email: EmailStr
    password: str
    full_name: str | None = None
