from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.notifications import Notification, UserDevice
from app.models.profiles import Profile
from .channels.email import email_channel
from .channels.push import push_channel
from app.core.config import settings
import logging

class NotificationService:
    def __init__(self):
        self.logger = logging.getLogger("uvicorn")
        self.super_admin_email = settings.SUPER_ADMIN_EMAIL

    def _get_base_template(self, title: str, content: str) -> str:
        """
        Plantilla Base HTML estilo UrbanVibe (Dark Mode)
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; background-color: #1a1b2e; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #23253a; border-radius: 12px; overflow: hidden; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
                .header {{ background-color: #232959; padding: 20px; text-align: center; }}
                .header h1 {{ margin: 0; color: #ffffff; font-size: 24px; letter-spacing: 2px; }}
                .content {{ padding: 30px; color: #e2e8f0; font-size: 16px; line-height: 1.6; }}
                .field {{ margin-bottom: 12px; border-bottom: 1px solid #33364f; padding-bottom: 8px; }}
                .label {{ color: #fa4e35; font-weight: bold; font-size: 12px; text-transform: uppercase; }}
                .value {{ color: #ffffff; font-size: 16px; margin-top: 4px; display: block; }}
                .footer {{ background-color: #151625; padding: 15px; text-align: center; color: #64748b; font-size: 12px; }}
                .btn {{ display: inline-block; background-color: #fa4e35; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><span style="color: #f2f1f0; font-weight: bold;">urban</span><span style="color: #fa4e35; font-weight: bold;">Vibe</span></h1>
                </div>
                <div class="content">
                    <h2 style="color: #ffffff; margin-top: 0;">{title}</h2>
                    {content}
                </div>
                <div class="footer">
                    <p>&copy; 2026 <span style="color: #f2f1f0; font-weight: bold;">urban</span><span style="color: #fa4e35; font-weight: bold;">Vibe</span> App. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """

    async def register_device(self, db: AsyncSession, user_id: str, token: str, platform: str = None):
        """
        Registra o actualiza el token de dispositivo para un usuario.
        """
        try:
            # Upsert logic for PostgreSQL
            stmt = insert(UserDevice).values(
                user_id=user_id,
                expo_token=token,
                platform=platform
            ).on_conflict_do_update(
                index_elements=['expo_token'],
                set_={
                    "user_id": user_id, 
                    "last_used_at": select(UserDevice.last_used_at).where(UserDevice.expo_token == token).scalar_subquery()
                    # Realmente queremos actualizar last_used_at a NOW, pero bueno.
                }
            )
            # Simplificado: Primero borramos tokens viejos de este user si queremos 1 dispositivo por user, 
            # pero mejor permitimos múltiples.
            # Mejor estrategia simple: Verificar si existe el token.
            
            # Revisar si el token ya existe
            query = select(UserDevice).where(UserDevice.expo_token == token)
            result = await db.execute(query)
            existing_device = result.scalars().first()
            
            if existing_device:
                existing_device.user_id = user_id
                existing_device.platform = platform
                # existing_device.last_used_at = datetime.utcnow()
            else:
                new_device = UserDevice(user_id=user_id, expo_token=token, platform=platform)
                db.add(new_device)
                
            await db.commit()
            self.logger.info(f"📱 Dispositivo registrado para User {user_id}: {token[:10]}...")
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando dispositivo: {e}")
            await db.rollback()

    async def send_in_app_notification(self, db: AsyncSession, user_id: str, title: str, body: str, type: str = "info", data: dict = None):
        """
        Crea notificación en BD y envía Push si hay tokens.
        """
        try:
            # 1. Guardar en BD (In-App History)
            notif = Notification(
                user_id=user_id,
                title=title,
                body=body,
                type=type,
                data=data
            )
            db.add(notif)
            await db.commit() # Commit para guardar ID
            
            # 2. Buscar dispositivos para Push
            query = select(UserDevice.expo_token).where(UserDevice.user_id == user_id)
            result = await db.execute(query)
            tokens = result.scalars().all()
            
            if tokens:
                await push_channel.send_broadcast_push(
                    tokens=list(tokens),
                    title=title,
                    body=body,
                    data=data
                )
                self.logger.info(f"📲 Push enviado a {len(tokens)} dispositivos de User {user_id}")
            else:
                self.logger.info(f"⚠️ User {user_id} no tiene dispositivos registrados para Push")

        except Exception as e:
            self.logger.error(f"❌ Error enviando notificación in-app/push: {e}")

    async def _get_admin_user_id(self, db: AsyncSession) -> str:
        """Intenta obtener el ID del usuario Super Admin por email."""
        query = select(Profile.id).where(Profile.email == self.super_admin_email)
        result = await db.execute(query)
        admin_id = result.scalar_one_or_none()
        return admin_id

    async def notify_new_user_created(self, user_data: dict, db: AsyncSession = None):
        """
        Notifica al Superadmin sobre un nuevo usuario registrado.
        """
        try:
            username = user_data.get('username', 'Desconocido')
            email = user_data.get('email', 'N/A')
            role = user_data.get('role', 'Usuario')
            
            subject = f"🚀 Nuevo Usuario: {username}"
            
            content = f"""
            <p>Se ha registrado un nuevo usuario en la plataforma.</p>
            <div class="field">
                <span class="label">Username</span>
                <span class="value">{username}</span>
            </div>
            <div class="field">
                <span class="label">Email</span>
                <span class="value">{email}</span>
            </div>
            <div class="field">
                <span class="label">Rol Inicial</span>
                <span class="value">{role}</span>
            </div>
            <a href="#" class="btn">Ver en Panel Admin</a>
            """
            
            html_body = self._get_base_template("Nuevo Tripulante 🚀", content)
            
            # 1. Email Admin
            await email_channel.send_simple_email(
                subject=subject,
                recipients=[self.super_admin_email],
                body=html_body
            )
            
            # 2. Notificación In-App/Push al Admin (Si db session disponible)
            if db:
                admin_id = await self._get_admin_user_id(db)
                if admin_id:
                    await self.send_in_app_notification(
                        db=db,
                        user_id=admin_id,
                        title="🚀 Nuevo Usuario",
                        body=f"{username} se ha unido a UrbanVibe.",
                        type="info",
                        data={"screen": "admin-users", "username": username}
                    )
                
            self.logger.info(f"✅ Notificación Nuevo Usuario procesada")

        except Exception as e:
            self.logger.error(f"❌ Error en notify_new_user_created: {e}")

    async def send_welcome_email(self, email: str, username: str):
        """
        Envía correo de bienvenida al usuario final.
        """
        try:
            subject = f"¡Bienvenido a UrbanVibe, {username}! 🚀"
            
            content = f"""
            <p>Hola <strong>{username}</strong>,</p>
            <p>Tu cuenta ha sido creada exitosamente. Estamos muy felices de que te unas a nuestra comunidad.</p>
            <p>Prepárate para descubrir los mejores lugares, eventos y experiencias de tu ciudad.</p>
            <br>
            <p style="color: #fa4e35; font-weight: bold; margin-top: 20px;">¡Nos vemos en la App!</p>
            <br>
            <div style="font-size: 36px; font-weight: bold; font-family: sans-serif; margin-top: 10px;">
                <span style="color: #f2f1f0;">urban</span><span style="color: #fa4e35;">Vibe</span>
            </div>
            """
            
            html_body = self._get_base_template("¡Bienvenido al Club!", content)
            
            await email_channel.send_simple_email(
                subject=subject,
                recipients=[email],
                body=html_body
            )
            self.logger.info(f"✅ Correo Bienvenida enviado a {email}")
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando bienvenida a usaurio: {e}")

    async def notify_new_venue_created(self, venue_data: dict, db: AsyncSession = None):
        """
        Notifica al Superadmin sobre un nuevo local creado.
        """
        try:
            venue_name = venue_data.get('name', 'Local Desconocido')
            owner_email = venue_data.get('owner_email', 'N/A')
            category = venue_data.get('category', 'N/A')
            
            subject = f"🏢 Nuevo Local: {venue_name}"
            
            content = f"""
            <p>Se ha creado un nuevo local esperando revisión/activación.</p>
            <div class="field">
                <span class="label">Local</span>
                <span class="value">{venue_name}</span>
            </div>
            <div class="field">
                <span class="label">Categoría ID</span>
                <span class="value">{category}</span>
            </div>
            <div class="field">
                <span class="label">Dueño</span>
                <span class="value">{owner_email}</span>
            </div>
            """
            
            html_body = self._get_base_template("Nuevo Local Creado 🏢", content)
            
            # 1. Email Admin
            await email_channel.send_simple_email(
                subject=subject,
                recipients=[self.super_admin_email],
                body=html_body
            )
            
            # 2. Notificación In-App/Push al Admin
            if db:
                admin_id = await self._get_admin_user_id(db)
                if admin_id:
                     await self.send_in_app_notification(
                        db=db,
                        user_id=admin_id,
                        title="🏢 Nuevo Local",
                        body=f"Se ha creado el local {venue_name}.",
                        type="info",
                        data={"screen": "admin-venues", "venue_name": venue_name}
                    )

            self.logger.info(f"✅ Notificación Nuevo Venue procesada para {venue_name}")

        except Exception as e:
            self.logger.error(f"❌ Error en notify_new_venue_created: {e}")

    async def notify_venue_review(self, db: AsyncSession, venue_name: str, owner_id: str, reviewer_name: str, rating: float):
        """
        Notifica al dueño de un local sobre una nueva reseña.
        """
        try:
            title = "Nueva Reseña ⭐️"
            body = f"{reviewer_name} calificó {venue_name} con {rating} estrellas."
            
            # 1. Notificación In-App/Push al Dueño
            await self.send_in_app_notification(
                db=db,
                user_id=owner_id,
                title=title,
                body=body,
                type="info",
                data={"screen": "venue-reviews", "venue_name": venue_name}
            )
        except Exception as e:
            self.logger.error(f"❌ Error notify_venue_review: {e}")

    async def notify_venue_like(self, db: AsyncSession, venue_name: str, owner_id: str, user_name: str):
        """
        Notifica al dueño cuando alguien agrega su local a favoritos.
        """
        try:
            title = "¡Nuevo Fan! ❤️"
            body = f"A {user_name} le gusta {venue_name}."
            
            # 1. Notificación In-App/Push al Dueño
            await self.send_in_app_notification(
                db=db,
                user_id=owner_id,
                title=title,
                body=body,
                type="success",
                data={"screen": "venue-detail", "venue_name": venue_name}
            )
        except Exception as e:
            self.logger.error(f"❌ Error notify_venue_like: {e}")

    async def send_venue_welcome_email(self, email: str, venue_name: str):
        """
        Envía correo de confirmación al crear un local.
        """
        try:
            subject = f"¡Tu local {venue_name} está en UrbanVibe! 🏢"
            
            content = f"""
            <p>Felicitaciones, has registrado <strong>{venue_name}</strong> exitosamente.</p>
            <p>Nuestro equipo revisará la información y te notificaremos cuando esté público.</p>
            <p>Mientras tanto, puedes completar el perfil de tu local agregando fotos, menú y horarios.</p>
            <br>
            <a href="#" class="btn">Gestionar mi Local</a>
            """
            
            html_body = self._get_base_template("¡Local Registrado!", content)
            
            await email_channel.send_simple_email(
                subject=subject,
                recipients=[email],
                body=html_body
            )
            self.logger.info(f"✅ Correo Bienvenida Local enviado a {email}")
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando bienvenida local: {e}")

            self.logger.error(f"❌ Error enviando bienvenida local: {e}")

    async def notify_venue_approved(self, db: AsyncSession, venue_name: str, owner_id: str):
        """
        Notifica al dueño que su local ha sido verificado/aprobado.
        """
        try:
            title = "🎉 ¡Local Verificado!"
            body = f"Tu local {venue_name} ha sido aprobado y ya es visible para todos."
            
            await self.send_in_app_notification(
                db=db,
                user_id=owner_id,
                title=title,
                body=body,
                type="success",
                data={"screen": "venue-detail", "venue_name": venue_name}
            )
        except Exception as e:
            self.logger.error(f"❌ Error notify_venue_approved: {e}")

notification_service = NotificationService()
