from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.gamification_advanced import Challenge, UserChallengeProgress, UserBadge, Badge
from app.models.profiles import Profile
from app.services.notifications import notification_service
from app.services.promotion_service import promotion_service

class ChallengeService:
    async def evaluate_event(
        self,
        db: AsyncSession,
        user_id: UUID,
        event_code: str, # From GamificationEvent (e.g. CHECKIN, REVIEW)
        details: dict = {}
    ):
        """
        Evaluates active challenges based on the user's action.
        """
        now = datetime.now()
        
        # 1. Map Event Code to Challenge Type
        # Allow flexible mapping. For now: CHECKIN -> CHECKIN_COUNT
        challenge_type_map = {
            "CHECKIN": "CHECKIN_COUNT",
            "REVIEW": "REVIEW_COUNT",
            "REFERRAL_USER": "REFERRAL_COUNT"
        }
        
        target_type = challenge_type_map.get(event_code)
        if not target_type:
            return # No challenges for this event type yet
            
        # 2. Find Active Challenges
        stmt = select(Challenge).where(
            and_(
                Challenge.challenge_type == target_type,
                Challenge.is_active == True,
                # Date Range Check (Handle Nulls as "Always Active" if desired, or strict range)
                # Let's assume nullable means open.
                (Challenge.period_start == None) | (Challenge.period_start <= now),
                (Challenge.period_end == None) | (Challenge.period_end >= now)
            )
        )
        challenges = (await db.execute(stmt)).scalars().all()
        
        for challenge in challenges:
            await self._process_challenge_progress(db, user_id, challenge, details)

    async def _process_challenge_progress(self, db: AsyncSession, user_id: UUID, challenge: Challenge, details: dict):
        # 3. Check Filters (e.g. valid only for "Bars")
        # details example: {"venue_category": "bar", "venue_id": "..."}
        if challenge.filters:
            # Simple exact match for now. Can be expanded to complex logic.
            for key, val in challenge.filters.items():
                if details.get(key) != val:
                    return # Skip if filter mismatch

        # 4. Get/Create Progress
        stmt = select(UserChallengeProgress).where(
            UserChallengeProgress.user_id == user_id,
            UserChallengeProgress.challenge_id == challenge.id
        )
        progress = (await db.execute(stmt)).scalar_one_or_none()
        
        if not progress:
            progress = UserChallengeProgress(user_id=user_id, challenge_id=challenge.id, current_value=0)
            db.add(progress)
        
        if progress.is_completed:
            return # Already done
            
        # 5. Update Progress
        progress.current_value += 1
        progress.last_updated_at = datetime.now()
        
        # 6. Check Completion
        if progress.current_value >= challenge.target_value:
            await self._complete_challenge(db, user_id, challenge, progress)

    async def _complete_challenge(self, db: AsyncSession, user_id: UUID, challenge: Challenge, progress: UserChallengeProgress):
        progress.is_completed = True
        progress.completed_at = datetime.now()
        
        rewards_msg = []
        
        # Award Points?
        if challenge.reward_points > 0:
            # We need to add points without triggering infinite loop. 
            # Direct update profile or call a "silent" method in GamificationService?
            # Or GamificationService calls this, so we should separate "Add Points" logic.
            # Best: Update profile directly here for rewards, logging as "CHALLENGE_REWARD".
            
            # For simplicity, let's update profile directly here to avoid circular imports if GamificationService imports this.
            # Wait, better to use GamificationService but avoiding `register_event` loop.
            # Or just raw DB update. 
            stmt = select(Profile).where(Profile.id == user_id)
            profile = (await db.execute(stmt)).scalar_one_or_none()
            if profile:
                profile.points_current += challenge.reward_points
                profile.reputation_score += challenge.reward_points
                rewards_msg.append(f"+{challenge.reward_points} pts")
        
        # Award Badge?
        if challenge.reward_badge_id:
            badge = await db.get(Badge, challenge.reward_badge_id)
            if badge:
                # Check if already has badge (unique constraint usually, but let's check)
                existing_badge_stmt = select(UserBadge).where(UserBadge.user_id==user_id, UserBadge.badge_id==badge.id)
                if not (await db.execute(existing_badge_stmt)).scalar_one_or_none():
                    new_badge = UserBadge(user_id=user_id, badge_id=badge.id)
                    db.add(new_badge)
                    rewards_msg.append(f"Medalla {badge.name}")

        # Grant Promotion Reward?
        if challenge.reward_promotion_id:
             unit = await promotion_service.assign_reward_to_user(
                 db=db, 
                 user_id=user_id, 
                 promotion_id=challenge.reward_promotion_id,
                 source_challenge_id=challenge.id
             )
             if unit:
                 rewards_msg.append("¡Cupón/Recompensa VIP!")

        # Notify
        try:
             await notification_service.send_in_app_notification(
                db=db,
                user_id=user_id,
                title=f"¡Reto Completado: {challenge.title}! 🏆",
                body=f"Has ganado: {', '.join(rewards_msg)}",
                type="gamification_challenge",
                data={"screen": "challenges", "challenge_id": str(challenge.id)}
            )
        except Exception as e:
            print(f"Error notification challenge: {e}")

challenge_service = ChallengeService()
