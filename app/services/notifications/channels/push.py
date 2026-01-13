from exponent_server_sdk import (
    PushClient,
    PushMessage,
    PushServerError,
    DeviceNotRegisteredError
)
from typing import List, Dict, Any
import logging

class PushChannel:
    def __init__(self):
        self.logger = logging.getLogger("uvicorn")
        # Expo SDK client
        self.client = PushClient()

    async def send_push_notification(self, token: str, title: str, body: str, data: Dict[str, Any] = None):
        """
        Envía una notificación push a un token de Expo.
        Puede extenderse para manejar listas de tokens.
        """
        if not token:
            return False
            
        try:
            response = self.client.publish(
                PushMessage(to=token, title=title, body=body, data=data)
            )
            
            try:
                # Verificar respuesta de tickets
                response.validate_response()
                self.logger.info(f"📲 Push enviado a {token}: {title}")
                return True
            except DeviceNotRegisteredError:
                self.logger.warning(f"⚠️ Token inválido/expirado: {token}")
                # Aquí podríamos invalidar el token en la DB si tuviéramos acceso directo
                return False
            except PushServerError as exc:
                self.logger.error(f"❌ Error servidor Push: {exc.errors}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error general Push: {e}")
            return False

    async def send_broadcast_push(self, tokens: List[str], title: str, body: str, data: Dict[str, Any] = None):
        """
        Envía push a múltiples destinatarios.
        """
        if not tokens:
            return
            
        # Expo SDK recomienda batches, pero para volumen bajo, iterar o send_messages es OK
        # La librería maneja batches automáticamente si pasamos lista de PushMessage
        messages = [
            PushMessage(to=token, title=title, body=body, data=data)
            for token in tokens
        ]
        
        try:
            self.client.publish_multiple(messages)
            self.logger.info(f"📲 Broadcast Push enviado a {len(tokens)} dispositivos.")
        except Exception as e:
            self.logger.error(f"❌ Error Broadcast Push: {e}")

push_channel = PushChannel()
