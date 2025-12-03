import jwt
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.qr_tokens import QRToken
from app.schemas.qr_tokens import QrTokenResponse

logger = logging.getLogger(__name__)

class QrTokenService:
    async def generate_checkin_token(self, db: AsyncSession, venue_id: UUID, user_id: UUID) -> QrTokenResponse:
        now = datetime.now(timezone.utc)
        expires_in = settings.QR_TOKEN_DEFAULT_TTL_SECONDS
        valid_until = now + timedelta(seconds=expires_in)

        # Create DB record
        db_token = QRToken(
            type="checkin",
            scope="checkin",
            venue_id=venue_id,
            valid_until=valid_until,
            created_by=user_id,
            max_uses=1 # One-time use for check-in
        )
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)

        # Generate JWT
        payload = {
            "iss": settings.QR_JWT_ISSUER,
            "aud": settings.QR_JWT_AUDIENCE,
            "type": "qr_checkin",
            "scope": "checkin",
            "jti": str(db_token.id),
            "sub": f"venue:{venue_id}",
            "venue_id": str(venue_id),
            "iat": now,
            "exp": valid_until
        }
        
        token_str = jwt.encode(payload, settings.QR_JWT_SECRET, algorithm=settings.ALGORITHM)

        return QrTokenResponse(
            qr_content=token_str,
            expires_in=expires_in,
            token_id=db_token.id,
            valid_until=valid_until
        )

    async def validate_token(self, db: AsyncSession, token_str: str) -> QRToken:
        try:
            payload = jwt.decode(
                token_str,
                settings.QR_JWT_SECRET,
                algorithms=[settings.ALGORITHM],
                audience=settings.QR_JWT_AUDIENCE,
                issuer=settings.QR_JWT_ISSUER
            )
            logger.info(f"🔍 QR Payload Decoded: {payload}")
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ QR Validation Failed: ExpiredSignatureError")
            raise HTTPException(status_code=400, detail="QR expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"⚠️ QR Validation Failed: InvalidTokenError - {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid QR")

        if payload.get("type") != "qr_checkin" or payload.get("scope") != "checkin":
            logger.warning(f"⚠️ QR Validation Failed: Invalid type/scope - {payload.get('type')}/{payload.get('scope')}")
            raise HTTPException(status_code=400, detail="Invalid QR type")

        token_id = payload.get("jti")
        if not token_id:
            raise HTTPException(status_code=400, detail="Invalid QR ID")

        # Check DB
        result = await db.execute(select(QRToken).where(QRToken.id == token_id))
        db_token = result.scalar_one_or_none()

        if not db_token:
            logger.warning(f"⚠️ QR Validation Failed: Token ID {token_id} not found in DB")
            raise HTTPException(status_code=400, detail="QR token not found")

        if db_token.is_revoked:
            logger.warning(f"⚠️ QR Validation Failed: Token {token_id} is revoked")
            raise HTTPException(status_code=400, detail="QR revoked")

        if db_token.used_count >= db_token.max_uses:
            logger.warning(f"⚠️ QR Validation Failed: Token {token_id} already used ({db_token.used_count}/{db_token.max_uses})")
            raise HTTPException(status_code=400, detail="QR already used")
            
        # Check expiration (DB source of truth)
        if db_token.valid_until < datetime.now(timezone.utc):
             logger.warning(f"⚠️ QR Validation Failed: Token {token_id} expired in DB")
             raise HTTPException(status_code=400, detail="QR expired (db)")

        return db_token

    async def mark_token_used(self, db: AsyncSession, token: QRToken, user_id: UUID):
        token.used_count += 1
        token.last_used_at = datetime.now(timezone.utc)
        token.last_used_by = user_id
        db.add(token)
        # Commit should be handled by the caller

qr_token_service = QrTokenService()
