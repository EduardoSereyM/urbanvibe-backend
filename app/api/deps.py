from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.core.security import decode_supabase_jwt
from app.core.config import settings
from app.services.profiles_service import profiles_service
from app.models.profiles import Profile

security = HTTPBearer(auto_error=True)

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> Profile:
    token = credentials.credentials

    # -------------------------
    # DEMO MODE: token = "demo"
    # -------------------------
    if settings.DEMO_MODE and token == "demo":
        # Usuario tester creado por scripts.seed_demo_data
        demo_user_id = UUID("a09db2c6-ee06-49df-b0f6-f55c6184a83c")

        user = await profiles_service.get_profile(db, user_id=demo_user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demo user not found. Did you run the seed_demo_data script?",
            )
        return user

    # -------------------------
    # Flujo normal: Supabase JWT
    # -------------------------
    try:
        payload = decode_supabase_jwt(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = UUID(user_id_str)

    except Exception as e:
        print(f"❌ DEBUG: Token validation error: {str(e)}")
        print(f"❌ DEBUG: Token type: {type(token)}")
        # print(f"❌ DEBUG: Token: {token}") 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await profiles_service.get_profile(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UUID:
    """
    Extracts User ID from JWT without verifying existence in DB.
    Useful for endpoints that handle 'first login' or missing profile scenarios.
    """
    token = credentials.credentials

    # DEMO MODE
    if settings.DEMO_MODE and token == "demo":
        return UUID("a09db2c6-ee06-49df-b0f6-f55c6184a83c")

    try:
        payload = decode_supabase_jwt(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials (no sub)",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UUID(user_id_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


security_optional = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_optional)],
) -> Profile | None:
    if not credentials:
        return None

    token = credentials.credentials

    # -------------------------
    # DEMO MODE: token = "demo"
    # -------------------------
    if settings.DEMO_MODE and token == "demo":
        demo_user_id = UUID("a09db2c6-ee06-49df-b0f6-f55c6184a83c")
        return await profiles_service.get_profile(db, user_id=demo_user_id)

    # -------------------------
    # Flujo normal: Supabase JWT
    # -------------------------
    try:
        payload = decode_supabase_jwt(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None

        user_id = UUID(user_id_str)
        return await profiles_service.get_profile(db, user_id=user_id)

    except Exception:
        return None

async def get_current_active_superuser(
    current_user: Annotated[Profile, Depends(get_current_user)],
) -> Profile:
    """
    Checks if the current user is a superuser.
    """
    # 1. Hardcoded email check (Simplest for now)
    superuser_emails = ["administradorapp@urbanvibe.cl"]
    if current_user.email in superuser_emails:
        return current_user
        
    # 2. Check Role (if implemented in Profile or App Metadata)
    # Since we don't have roles readily available in Profile model easily (maybe), let's stick to email auth for MVP.
    # Or check if there is a 'role' column? No. 
    # But usually app_metadata in JWT has it.
    
    # Let's assume for now, email whitelist is enough, plus we can check a future is_superuser field.
    
    raise HTTPException(
        status_code=403,
        detail="The user doesn't have enough privileges"
    )

def get_current_user_auth_metadata(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> HTTPAuthorizationCredentials:
    """
    Returns the raw auth credentials (JWT token container).
    Useful when you need to decode the token manually to access metadata not in the DB.
    """
    return credentials