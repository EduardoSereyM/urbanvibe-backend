
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, exists
from datetime import datetime

from app.api import deps
from app.models.promotions import Promotion, PromotionType
from app.models.rewards import Redemption, RewardUnit
from app.models.profiles import Profile
from app.api.v1.venues_admin.schemas import PromotionResponse # Reusing schema or creating new? Let's check schemas.

router = APIRouter()

# Schema for User View (can be same as Admin but maybe safer to have specific)
# For now reusing PromotionResponse from venues_admin/schemas is okay if it doesn't leak sensitive info.
# Use Pydantic models for responses.

# RESPONSE SCHEMAS
from pydantic import BaseModel
from typing import Optional, Dict

class UserPromotionResponse(BaseModel):
    id: UUID
    venue_id: UUID
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    promo_type: str  # 'standard' | 'uv_reward'
    reward_tier: Optional[str] = None
    points_cost: Optional[int] = None
    is_active: bool
    
    # -----------------------------------------------------------
    # FASE 1.2: Server-Side Validation Fields
    # -----------------------------------------------------------
    can_redeem: bool = False
    redeem_alert: Optional[str] = None # Mensaje pre-calculado para la UI (ej: "Te faltan 200 pts")

class ClaimResponse(BaseModel):
    success: bool
    redemption_id: UUID
    qr_content: str
    points_spent: int
    message: str

class WalletItemResponse(BaseModel):
    id: UUID
    venue_name: str
    venue_id: UUID
    promotion_title: str
    promo_type: str
    qr_content: str
    status: str
    created_at: datetime
    points_spent: int


# 1. GET /venues/{venue_id}/promotions
@router.get("/venues/{venue_id}/promotions", response_model=List[UserPromotionResponse])
async def get_venue_promotions_user(
    venue_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Profile = Depends(deps.get_current_user_optional) 
):
    """
    Lista las promociones activas con validación de puntos PRE-CALCULADA.
    """
    stmt = select(Promotion).where(
        Promotion.venue_id == venue_id,
        Promotion.is_active == True,
    )
    result = await db.execute(stmt)
    promotions = result.scalars().all()
    
    # Logic for Computed Fields
    response_list = []
    
    user_points = current_user.points_current if current_user else 0
    
    for p in promotions:
        # Convert SQLAlchemy model to Pydantic dict
        p_dict = {
            "id": p.id,
            "venue_id": p.venue_id,
            "title": p.title,
            "description": p.description,
            "image_url": p.image_url,
            "promo_type": p.promo_type,
            "reward_tier": p.reward_tier,
            "points_cost": p.points_cost or 0,
            "is_active": p.is_active,
        }
        
        # Validation Logic
        can_redeem = False
        alert_msg = None
        
        if not current_user:
            can_redeem = False
            alert_msg = "Inicia sesión para canjear"
        else:
            cost = p.points_cost or 0
            if cost > 0:
                if user_points >= cost:
                    can_redeem = True
                    alert_msg = None # Ready to claim
                else:
                    can_redeem = False
                    missing = cost - user_points
                    alert_msg = f"Te faltan {missing} pts"
            else:
                # Standard promo (cost 0) -> Always redeemable if active
                can_redeem = True
                alert_msg = None

        p_dict["can_redeem"] = can_redeem
        p_dict["redeem_alert"] = alert_msg
        
        response_list.append(UserPromotionResponse(**p_dict))

    return response_list


# 2. POST /promotions/{promotion_id}/claim
@router.post("/promotions/{promotion_id}/claim", response_model=ClaimResponse)
async def claim_promotion(
    promotion_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Profile = Depends(deps.get_current_user)
):
    """
    Canjea una promoción (Reward). Descuenta puntos y genera Redemption.
    """
    # a. Get Promotion
    stmt = select(Promotion).where(Promotion.id == promotion_id)
    result = await db.execute(stmt)
    promo = result.scalar_one_or_none()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")
        
    if not promo.is_active:
        raise HTTPException(status_code=400, detail="Esta promoción ya no está activa")

    # b. Check Points (if reward)
    points_cost = 0
    if promo.promo_type == 'uv_reward': # or specific Enum check
        points_cost = promo.points_cost or 0
        if current_user.points_current < points_cost:
             raise HTTPException(status_code=400, detail=f"No tienes suficientes puntos. Necesitas {points_cost}.")
    
    # c. Deduct Points
    if points_cost > 0:
        current_user.points_current -= points_cost
        # Log points transaction? (TODO: Add to PointsLog)
        
    # d. Create Redemption / QR
    # For simplicity, using Redemption ID as QR content or a dedicated Token
    import uuid
    qr_code = f"UV-PROMO-{uuid.uuid4().hex[:8].upper()}"
    
    redemption = Redemption(
        user_id=current_user.id,
        venue_id=promo.venue_id,
        promotion_id=promo.id,
        points_spent=points_cost,
        status="pending", # 'confirmed' upon scan
        # qr_content=qr_code # If model has it
    )
    # Assuming Redemption model might need updates or we use a separate RewardUnit.
    # Analyzing previous conversation, schema mentions 'Redemption' and 'RewardUnit'. 
    # Let's check models later. use Redemption for now.
    
    db.add(redemption)
    await db.commit()
    await db.refresh(redemption)
    
    return ClaimResponse(
        success=True,
        redemption_id=redemption.id,
        qr_content=str(redemption.id), # Use ID as QR for simplicity for now
        points_spent=points_cost,
        message="¡Canje exitoso!"
    )

# 3. GET /me/wallet
@router.get("/me/wallet", response_model=List[WalletItemResponse])
async def get_my_wallet(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Profile = Depends(deps.get_current_user)
):
    """
    Obtiene los canjes activos (wallet) del usuario.
    """
    # Join Redemption -> Promotion -> Venue
    # Need to import Venue model
    from app.models.venues import Venue
    
    stmt = (
        select(Redemption, Promotion, Venue)
        .join(Promotion, Redemption.promotion_id == Promotion.id)
        .join(Venue, Redemption.venue_id == Venue.id)
        .where(
            Redemption.user_id == current_user.id,
            Redemption.status == 'pending' # Only show usable ones
        )
        .order_by(Redemption.created_at.desc())
    )
    
    result = await db.execute(stmt)
    items = []
    for red, promo, venue in result:
        items.append(WalletItemResponse(
            id=red.id,
            venue_name=venue.name,
            venue_id=venue.id,
            promotion_title=promo.title,
            promo_type=promo.promo_type,
            qr_content=str(red.id),
            status=red.status,
            created_at=red.created_at,
            points_spent=red.points_spent
        ))
        
    return items
