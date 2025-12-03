from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.auth.schemas import TokenResponse
from app.core.security import decode_supabase_jwt

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(deps.get_db)],
):
    """
    Endpoint de login compatible con OAuth2.
    
    - En modo DEMO (DEMO_MODE=true): acepta cualquier usuario/contraseña y retorna token "demo"
    - En modo REAL (DEMO_MODE=false): valida credenciales contra Supabase Auth
    """
    from app.core.config import settings
    from app.services.auth_service import auth_service
    
    # Modo DEMO: retornar token "demo"
    if settings.DEMO_MODE:
        return TokenResponse(
            access_token="demo",
            token_type="bearer"
        )
    
    # Modo REAL: autenticar con Supabase
    # OAuth2PasswordRequestForm usa 'username' pero esperamos email
    email = form_data.username
    password = form_data.password
    
    # Autenticar y obtener token JWT real
    access_token = await auth_service.authenticate_user(email, password)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

