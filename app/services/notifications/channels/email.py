from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from pydantic import EmailStr
from typing import List
import logging

# Configuración de conexión (Single Source of Truth en config.py)
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class EmailChannel:
    def __init__(self):
        self.fm = FastMail(conf)
        self.logger = logging.getLogger("uvicorn")

    async def send_simple_email(self, subject: str, recipients: List[EmailStr], body: str, attachments: List[str] = None):
        """
        Envía un correo simple (HTML).
        """
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=MessageType.html,
                attachments=attachments or []
            )
            await self.fm.send_message(message)
            self.logger.info(f"📧 Email enviado a {recipients}: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error enviando email: {e}")
            return False

email_channel = EmailChannel()
