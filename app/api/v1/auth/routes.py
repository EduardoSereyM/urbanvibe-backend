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


@router.post("/claim-business-role")
async def claim_business_role(
    current_user: Annotated[deps.Profile, Depends(deps.get_current_user)],
):
    """
    Asigna explícitamente el rol VENUE_OWNER al usuario actual.
    Se usa cuando un usuario se registra con intención de negocio.
    """
    from app.core.supabase_admin import get_supabase_admin
    
    try:
        admin_client = get_supabase_admin()
        user_id = str(current_user.id)
        
        # 1. Obtener usuario actual de Supabase para ver metadata actual
        user_response = admin_client.auth.admin.get_user_by_id(user_id)
        user = user_response.user
        
        current_metadata = user.app_metadata or {}
        current_role = current_metadata.get("app_role")
        
        # 2. Si ya tiene el rol, no hacer nada
        if current_role == "VENUE_OWNER":
            return {"message": "User already has VENUE_OWNER role"}
            
        # 3. Actualizar app_metadata
        # Nota: Supabase Auth usa 'app_metadata' para claims seguros que van al JWT
        admin_client.auth.admin.update_user_by_id(
            user_id, 
            {"app_metadata": {**current_metadata, "app_role": "VENUE_OWNER"}}
        )
        
        return {"message": "Role VENUE_OWNER assigned successfully"}
        
    except Exception as e:
        print(f"❌ Error assigning role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign role: {str(e)}"
        )

