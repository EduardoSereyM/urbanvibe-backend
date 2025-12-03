from typing import Optional
from fastapi import HTTPException, status
from supabase import create_client, Client
from app.core.config import settings


class AuthService:
    """
    Servicio de autenticación usando Supabase Auth.
    """
    
    def __init__(self):
        """Inicializa el cliente de Supabase."""
        self.supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_KEY
        )
    
    async def authenticate_user(self, email: str, password: str) -> str:
        """
        Autentica un usuario con Supabase Auth.
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
            
        Returns:
            Token JWT de Supabase si la autenticación es exitosa
            
        Raises:
            HTTPException: Si las credenciales son inválidas o hay un error
        """
        try:
            # Intentar autenticar con Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Verificar que la respuesta tenga sesión y token
            if not response.session or not response.session.access_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return response.session.access_token
            
        except HTTPException:
            # Re-lanzar excepciones HTTP que ya creamos
            raise
            
        except Exception as e:
            # Capturar cualquier otro error (conexión, etc.)
            error_message = str(e)
            
            # Supabase retorna errores específicos que podemos parsear
            if "Invalid login credentials" in error_message or "invalid" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Error genérico para otros casos
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication error: {error_message}"
            )


# Instancia singleton del servicio
auth_service = AuthService()
