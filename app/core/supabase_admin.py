from supabase import create_client, Client
from app.core.config import settings

def get_supabase_admin() -> Client:
    """
    Retorna un cliente de Supabase con privilegios de SERVICE_ROLE.
    Úsalo con precaución solo para tareas administrativas (ej: actualizar metadata de usuarios).
    """
    if not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_SERVICE_KEY no está configurada")
        
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
