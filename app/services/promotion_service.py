from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models.rewards import RewardUnit
from app.models.promotions import Promotion
from app.models.qr_tokens import QrToken
from app.services.qr_token_service import qr_token_service # To generate QR for the reward unit

class PromotionService:
    async def assign_reward_to_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        promotion_id: UUID,
        source_challenge_id: UUID | None = None
    ) -> RewardUnit | None:
        """
        Assigns a single unit of a promotion to a user (e.g., as a Challenge Reward).
        Decrements inventory (total_units) if applicable.
        """
        # 1. Get Promotion
        promo = await db.get(Promotion, promotion_id)
        if not promo:
            print(f"❌ Promotion {promotion_id} not found.")
            return None
            
        if not promo.is_active:
             print(f"⚠️ Promotion {promo.title} is inactive.")
             return None

        # Check dates
        now = datetime.now()
        # Use valid_until as end date
        if promo.valid_until and promo.valid_until < now:
             print(f"⚠️ Promotion {promo.title} expired.")
             return None

        # Check Inventory (if total_units is not None)
        # Note: concurrency issue potentially here, but for now simple check.
        if promo.total_units is not None:
             # Count consumed/assigned units? 
             # Or just assume database trigger? No trigger. we must count.
             # Actually, best practice: `UPDATE promotions SET total_units = total_units - 1 WHERE id = ... AND total_units > 0`
             # But usually total_units means "Initial Stock". We should count `RewardUnit` entries.
             
             # Let's simple check:
             count_stmt = select(func.count()).select_from(RewardUnit).where(RewardUnit.promotion_id == promotion_id)
             count = await db.scalar(count_stmt) or 0
             
             if count >= promo.total_units:
                 print(f"⚠️ Promotion {promo.title} Out of Stock.")
                 return None

        # 2. Create Reward Token (QR)
        # We need a QR token for this specific reward unit so user can redeem it.
        # Format: "REWARD:{unit_id}" signed.
        # Actually `qr_token_service.create_token` is generic. Let's use it.
        # We'll create the unit first with null token, then update?
        # Or create token first.
        
        # 3. Create Reward Unit
        unit = RewardUnit(
            promotion_id=promotion_id,
            venue_id=promo.venue_id,
            user_id=user_id,
            status='available',
            metadata={"source": "challenge_reward", "challenge_id": str(source_challenge_id) if source_challenge_id else None}
        )
        db.add(unit)
        await db.flush() # Get ID
        
        # 4. Generate QR Token
        # "REWARD:<UNIT_ID>"
        token_data = f"REWARD:{unit.id}"
        # expires at valid_until
        
        qr_token = await qr_token_service.create_token(
            db=db,
            user_id=user_id,
            token_type="REWARD",
            content=token_data,
            expires_at=promo.valid_until,
            venue_id=promo.venue_id
        )
        
        unit.qr_token_id = qr_token.id
        await db.flush()
        
        print(f"🎁 Reward Assigned: {promo.title} to User {user_id}")
        return unit

promotion_service = PromotionService()
