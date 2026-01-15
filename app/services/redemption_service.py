from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.profiles import Profile
from app.models.promotions import Promotion
from app.models.gamification_advanced import RewardUnit
from fastapi import HTTPException

class RedemptionService:
    """
    Gestiona el canje de puntos por recompensas físicas o digitales en los locales.
    """

    async def redeem_promotion(
        self, 
        db: AsyncSession, 
        user_id: UUID, 
        promotion_id: UUID
    ):
        """
        Procesa el canje: resta puntos y genera un RewardUnit disponible.
        """
        # 1. Obtener datos
        prom_stmt = select(Promotion).where(Promotion.id == promotion_id)
        promotion = (await db.execute(prom_stmt)).scalar_one_or_none()
        
        if not promotion or not promotion.is_active:
            raise HTTPException(status_code=404, detail="Promoción no disponible")
            
        if promotion.promo_type != 'uv_reward' or not promotion.points_cost:
            raise HTTPException(status_code=400, detail="Esta promoción no es canjeable por puntos")

        # 2. Verificar puntos del usuario
        prof_stmt = select(Profile).where(Profile.id == user_id)
        profile = (await db.execute(prof_stmt)).scalar_one_or_none()
        
        if not profile or profile.points_current < promotion.points_cost:
            raise HTTPException(status_code=400, detail="Puntos insuficientes")

        # 3. Verificar stock si aplica
        if promotion.total_units is not None:
            count_stmt = select(RewardUnit).where(RewardUnit.promotion_id == promotion_id)
            # Simplificado: Aquí deberías contar unidades no expiradas
            
        # 4. Transacción: Restar puntos y Crear registros
        profile.points_current -= promotion.points_cost
        
        from app.models.rewards import RewardUnit, Redemption
        
        # Generar el cupón (RewardUnit)
        reward = RewardUnit(
            promotion_id=promotion.id,
            venue_id=promotion.venue_id,
            user_id=user_id,
            status='available',
            assigned_at=datetime.now()
        )
        db.add(reward)
        await db.flush() # Para obtener el ID del reward

        # Registrar el gasto (Redemption)
        redemption = Redemption(
            user_id=user_id,
            venue_id=promotion.venue_id,
            promotion_id=promotion.id,
            reward_unit_id=reward.id,
            points_spent=promotion.points_cost,
            status='confirmed', # Puntos ya descontados
            confirmed_at=datetime.now()
        )
        db.add(redemption)
        
        # Guardar log de gamificación histórico
        from app.models.gamification import GamificationLog
        log = GamificationLog(
            event_code="REWARD_REDEEM",
            user_id=user_id,
            venue_id=promotion.venue_id,
            points=-promotion.points_cost,
            details={
                "promotion_title": promotion.title,
                "reward_unit_id": str(reward.id)
            }
        )
        db.add(log)
        
        await db.commit()
        
        return {
            "status": "success",
            "reward_id": reward.id,
            "remaining_points": profile.points_current,
            "message": f"¡Canje exitoso! Tu '{promotion.title}' está listo en tu billetera."
        }

    async def validate_at_venue(self, db: AsyncSession, reward_id: UUID, venue_id: UUID):
        """
        Llamado por el local al escanear el QR del usuario.
        """
        stmt = select(RewardUnit).where(RewardUnit.id == reward_id)
        reward = (await db.execute(stmt)).scalar_one_or_none()
        
        if not reward:
            return {"success": False, "message": "Cupón no encontrado"}
            
        if reward.venue_id != venue_id:
            return {"success": False, "message": "Este cupón no pertenece a este local"}
            
        if reward.status != 'available':
            return {"success": False, "message": f"El cupón ya está {reward.status}"}

        # Marcar como consumido
        reward.status = 'consumed'
        reward.consumed_at = datetime.now()
        await db.commit()
        
        return {"success": True, "message": "¡Recompensa validada correctamente!"}

redemption_service = RedemptionService()
