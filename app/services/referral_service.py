from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.models.profiles import Profile
from app.models.venues import Venue
from app.services.gamification_service import gamification_service
from app.services.notifications import notification_service

class ReferralService:
    """
    Gestiona el sistema de referidos para Usuarios y Locales.
    Alineado con los requerimientos de 'Conecta tu Ciudad'.
    """

    @staticmethod
    def generate_code() -> str:
        """Genera un código alfanumérico único con formato UV-XXXXXX."""
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(chars) for _ in range(6))
        return f"UV-{code}"

    async def claim_referral_code(
        self, 
        db: AsyncSession, 
        user_id: UUID, 
        referral_code: str
    ):
        """
        Procesa un código de referido tras el registro de un nuevo usuario.
        Puede ser referido por otro Usuario o por un Local.
        """
        # 1. Buscar al referente (puede ser Profile o Venue según el diseño)
        # Primero buscamos en Profiles
        stmt_profile = select(Profile).where(Profile.referral_code == referral_code)
        referrer_profile = (await db.execute(stmt_profile)).scalar_one_or_none()

        if referrer_profile:
            return await self._process_user_referral(db, user_id, referrer_profile)

        # Si no es usuario, buscamos si es un Local (Referidos B2B2C)
        stmt_venue = select(Venue).where(Venue.referral_code == referral_code)
        referrer_venue = (await db.execute(stmt_venue)).scalar_one_or_none()

        if referrer_venue:
            return await self._process_venue_referral(db, user_id, referrer_venue)

        return {"status": "error", "message": "Código de referido inválido"}

    async def _process_user_referral(self, db: AsyncSession, new_user_id: UUID, referrer: Profile):
        """Premia a un usuario por invitar a su amigo."""
        # Evitar auto-referidos
        if new_user_id == referrer.id:
            return {"status": "error", "message": "No puedes referirte a ti mismo"}

        # 1. Vincular en el perfil del nuevo usuario
        stmt = update(Profile).where(Profile.id == new_user_id).values(referred_by_user_id=referrer.id)
        await db.execute(stmt)

        # 2. Premiar al referente (Lógica Gamificación)
        # Evento: REFERRAL_USER (500 pts según visión)
        points = await gamification_service.register_event(
            db=db,
            user_id=referrer.id,
            event_code="REFERRAL_USER",
            details={"referred_user_id": str(new_user_id)}
        )

        # 3. Notificar al referente
        await notification_service.send_in_app_notification(
            db=db,
            user_id=referrer.id,
            title="¡Nuevo Amigo en UrbanVibe! 👥",
            body=f"Alguien se unió con tu código. ¡Has ganado {points} puntos!",
            type="gamification"
        )
        
        return {"status": "success", "referrer_type": "user", "points_awarded": points}

    async def _process_venue_referral(self, db: AsyncSession, new_user_id: UUID, venue: Venue):
        """Premia al local por traer nuevos usuarios a la app."""
        # 1. Vincular
        # Nota: El esquema de profiles no tiene referred_by_venue_id, 
        # pero podemos marcarlo en metadata o simplemente premiar al local.
        
        # 2. Premiar al Local (Gamificación B2B)
        # Los locales ganan visibilidad o puntos de local.
        venue.points_balance += 100 # Recompensa por atraer tráfico
        
        return {"status": "success", "referrer_type": "venue"}

    async def check_ambassador_status(self, db: AsyncSession, user_id: UUID):
        """
        Verifica el progreso del reto 'Conecta tu Ciudad'.
        Si el usuario refirió locales, calculamos su nivel VIP.
        """
        # Contar locales referidos por este usuario
        stmt = select(func.count()).select_from(Venue).where(Venue.referred_by_user_id == user_id)
        count = (await db.execute(stmt)).scalar() or 0

        # Niveles definidos en requerimientos:
        # Nivel 1: 1 local = 10% dto
        # Nivel 2: 5 locales = Pase ilimitado
        # Nivel 3: 10 locales = Socio/Embajador
        
        status = "Explorador"
        if count >= 10: status = "Embajador de la Ciudad / Socio"
        elif count >= 5: status = "Viajero VIP"
        elif count >= 1: status = "Promotor Inicial"

        return {
            "venues_referred": count,
            "status_title": status,
            "next_goal": 5 if count < 5 else 10 if count < 10 else None
        }

referral_service = ReferralService()
