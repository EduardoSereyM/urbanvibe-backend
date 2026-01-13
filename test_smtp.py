
import asyncio
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
import logging

# Configuración Hardcodeada para testear (reemplaza con valores reales si fallan las variables de entorno)
# O mejor, imprimimos lo que lee de config.

import os
from dotenv import load_dotenv

load_dotenv()

# Mock settings class if needed, or import
try:
    from app.core.config import settings
    print(f"✅ Config cargada.")
    print(f"USER: {settings.MAIL_USERNAME}")
    print(f"SERVER: {settings.MAIL_SERVER}")
    print(f"PORT: {settings.MAIL_PORT}")
    print(f"SSL: {settings.MAIL_SSL_TLS}")
    print(f"TLS: {settings.MAIL_STARTTLS}")
except ImportError:
    print("❌ No se pudo importar settings. Usando valores manuales de prueba.")
    # Fallback values if app context fails
    class Settings:
        MAIL_USERNAME = "contacto@urbanvibe.cl"
        MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "Abb1582esm.ComUV")
        MAIL_FROM = "contacto@urbanvibe.cl"
        MAIL_PORT = 465
        MAIL_SERVER = "mail.urbanvibe.cl"
        MAIL_STARTTLS = False
        MAIL_SSL_TLS = True
    settings = Settings()

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

async def test_send_email():
    print("🚀 Iniciando prueba de envío de correo...")
    
    fm = FastMail(conf)
    
    body = """
    <h1>Prueba de envío SMTP</h1>
    <p>Si lees esto, la configuración SMTP funciona correctamente.</p>
    """
    
    message = MessageSchema(
        subject="Test SMTP UrbanVibe",
        recipients=["admin@urbanvibe.cl"], # Enviando al admin
        body=body,
        subtype=MessageType.html
    )
    
    try:
        await fm.send_message(message)
        print("✅ Correo enviado exitosamente!")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_send_email())
