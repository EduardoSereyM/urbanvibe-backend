from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from uuid import UUID

from app.api import deps
from app.services.notifications import notification_service
from app.models.profiles import Profile
from app.models.notifications import Notification
from app.schemas.notifications import DeviceRegistration, NotificationResponse

router = APIRouter()

class NewUserEvent(BaseModel):
    user_id: UUID
    email: str
    username: str
    role: str = "APP_USER"
    invitation_code: Optional[str] = None

# --- User Facing Endpoints ---

@router.post("/device", status_code=204)
async def register_device(
    registration: DeviceRegistration,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
):
    """
    Registra el Expo Push Token del usuario actual.
    """
    await notification_service.register_device(
        db=db,
        user_id=current_user.id,
        token=registration.token,
        platform=registration.platform
    )
    return None

@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
    skip: int = 0,
    limit: int = 20,
):
    """
    Obtiene el historial de notificaciones del usuario.
    """
    query = select(Notification)\
        .where(Notification.user_id == current_user.id)\
        .order_by(desc(Notification.created_at))\
        .offset(skip)\
        .limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/unread-count")
async def get_unread_count(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
):
    """
    Retorna la cantidad de notificaciones sin leer.
    """
    query = select(func.count())\
        .select_from(Notification)\
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
    
    count = await db.scalar(query) or 0
    return {"count": count}

@router.patch("/{notification_id}/read", status_code=204)
async def mark_notification_read(
    notification_id: UUID,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[Profile, Depends(deps.get_current_user)],
):
    """
    Marca una notificación como leída.
    """
    # Verify ownership
    query = select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id)
    result = await db.execute(query)
    notif = result.scalars().first()
    
    if not notif:
         raise HTTPException(status_code=404, detail="Notification not found")
         
    notif.is_read = True
    await db.commit()
    return None

# --- Webhooks / System Events ---

@router.post("/user-created", status_code=202)
async def notify_user_created_event(
    event: NewUserEvent,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    # current_user_id: Annotated[deps.UUID, Depends(deps.get_current_user_id)], # Open endpoint with validation
):
    """
    Endpoint llamado por el cliente cuando un usuario completa su registro.
    """
    print(f"🔔 Evento recibido: Nuevo usuario {event.username} ({event.email})")
    
    # Validar que el usuario realmente existe en la DB (Security check)
    stmt = select(Profile).where(Profile.id == event.user_id)
    result = await db.execute(stmt)
    user_exists = result.scalar_one_or_none()
    
    if not user_exists:
        print(f"⚠️ Alerta de Seguridad: Intento de notificación para usuario inexistente {event.user_id}")
        return {"message": "Invalid user"}
    
    # Notificar al admin (Email + Push)
    # Pasamos 'db' para que el servicio pueda buscar al admin y sus tokens
    await notification_service.notify_new_user_created(
        user_data=event.model_dump(),
        db=db 
    )
    
    # Enviar correo de bienvenida al Usuario
    await notification_service.send_welcome_email(
        email=event.email,
        username=event.username
    )
    
    # --- NUEVO: PROCESAR CÓDIGO DE INVITACIÓN ---
    if event.invitation_code:
        from app.services.referral_service import referral_service
        try:
            print(f"🎁 Procesando código de invitación: {event.invitation_code} para {event.user_id}")
            # Llamamos al servicio para vincular y premiar
            await referral_service.claim_referral_code(
                db=db,
                user_id=event.user_id,
                referral_code=event.invitation_code
            )
        except Exception as e:
            # No bloqueamos el registro por error de invitación, pero lo logueamos
            print(f"⚠️ Error al procesar invitación ({event.invitation_code}): {str(e)}")

    return {"message": "Notification queued and referral processed"}
