from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class QrTokenCreate(BaseModel):
    type: str = "checkin"
    scope: str = "checkin"
    valid_until: datetime
    max_uses: int = 1

class QrTokenResponse(BaseModel):
    qr_content: str
    expires_in: int
    token_id: UUID
    valid_until: datetime
