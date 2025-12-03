from datetime import datetime, timedelta
from typing import Any, Union

import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def decode_supabase_jwt(token: str) -> dict:
    """
    Decodes a JWT token issued by Supabase using the SUPABASE_JWT_SECRET.
    """

    try:
        # Supabase JWT secret is often Base64 encoded.
        # We try to decode it first.
        import base64
        secret_candidates = []
        
        # Candidate 1: Base64 decoded bytes
        try:
            decoded = base64.b64decode(settings.SUPABASE_JWT_SECRET)
            secret_candidates.append(decoded)
        except Exception:
            pass
            
        # Candidate 2: Raw string
        secret_candidates.append(settings.SUPABASE_JWT_SECRET)

        last_error = None
        
        for secret in secret_candidates:
            try:
                payload = jwt.decode(
                    token, 
                    secret, 
                    algorithms=[settings.ALGORITHM],
                    options={"verify_aud": False},
                    leeway=60  # Allow 60 seconds of clock skew
                )
                return payload
            except jwt.InvalidTokenError as e:
                last_error = e
                continue
        
        # If we get here, all candidates failed
        if last_error:
            raise last_error
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        print(f"❌ DEBUG: JWT Decode Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
