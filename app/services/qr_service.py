import hmac
import hashlib
import urllib.parse
from uuid import UUID
from fastapi import HTTPException, status
from app.core.config import settings

class QRService:
    @staticmethod
    def generate_static_qr(venue_id: UUID) -> str:
        """
        Generates a signed QR URL string: uv://checkin?v={venue_id}&s={hmac_signature}
        """
        venue_str = str(venue_id)
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            venue_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"uv://checkin?v={venue_str}&s={signature}"

    @staticmethod
    def validate_qr(token_id: str) -> dict:
        """
        Parses the QR string, verifies the signature, and returns the venue_id.
        Expected format: uv://checkin?v={venue_id}&s={signature}
        """
        try:
            parsed = urllib.parse.urlparse(token_id)
            if parsed.scheme != "uv":
                raise ValueError("Invalid scheme")
            
            params = urllib.parse.parse_qs(parsed.query)
            venue_id_str = params.get("v", [None])[0]
            signature = params.get("s", [None])[0]
            
            if not venue_id_str or not signature:
                raise ValueError("Missing parameters")
            
            # Re-calculate signature
            expected_signature = hmac.new(
                settings.SECRET_KEY.encode(),
                venue_id_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                raise ValueError("Invalid signature")
            
            return {"venue_id": UUID(venue_id_str)}
            
        except (ValueError, IndexError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid QR token: {str(e)}"
            )

qr_service = QRService()
