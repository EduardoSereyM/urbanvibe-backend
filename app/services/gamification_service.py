from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.gamification import GamificationLog, GamificationEvent
from app.models.profiles import Profile
from app.models.levels import Level
from app.services.notifications import notification_service # For level up alerts
from app.services.challenge_service import challenge_service

class GamificationService:
    async def register_event(
        self,
        db: AsyncSession,
        user_id: UUID,
        event_code: str,
        source_id: UUID | None = None,
        venue_id: UUID | None = None,
        details: dict = {}
    ):
        """
        Registers a gamification event, adds points, and checks for level up.
        Returns the points added.
        """
        # 1. Get Event Configuration
        result = await db.execute(select(GamificationEvent).where(GamificationEvent.event_code == event_code))
        event = result.scalar_one_or_none()
        
        if not event or not event.is_active:
            print(f"⚠️ Evento o regla {event_code} no configurada. No se suman puntos.")
            return 0

        points_to_add = event.points
        
        # 2. Add to Logs
        new_log = GamificationLog(
            event_code=event_code,
            user_id=user_id,
            venue_id=venue_id,
            points=points_to_add,
            source_entity=event.target_type, 
            source_id=source_id,
            details=details
        )
        db.add(new_log)
        
        # 3. Update Target Points
        if event.target_type == 'user' and user_id:
            profile_res = await db.execute(select(Profile).where(Profile.id == user_id))
            profile = profile_res.scalar_one_or_none()
            
            if profile:
                # Initialize if None
                if profile.points_current is None: profile.points_current = 0
                if profile.reputation_score is None: profile.reputation_score = 0
                if profile.points_lifetime is None: profile.points_lifetime = 0
                
                profile.points_current += points_to_add
                profile.reputation_score += points_to_add 
                profile.points_lifetime += points_to_add
                
                # 4. Check Level Up
                await self._check_level_up(db, profile)
                
                # 5. Evaluate Challenges (Advanced Gamification)
                await challenge_service.evaluate_event(db, user_id, event_code, details)

        elif event.target_type == 'venue' and venue_id:
            from app.models.venues import Venue
            venue_res = await db.execute(select(Venue).where(Venue.id == venue_id))
            venue = venue_res.scalar_one_or_none()
            
            if venue:
                if venue.points_balance is None: venue.points_balance = 0
                venue.points_balance += points_to_add
                
                # Log to venue specific logs
                from app.models.logs import VenuePointsLog
                log = VenuePointsLog(
                    venue_id=venue_id,
                    delta=points_to_add,
                    reason=event_code,
                    metadata=details
                )
                db.add(log)

        # Flush changes so they are visible in current transaction
        await db.flush()

        return points_to_add

    async def _check_level_up(self, db: AsyncSession, profile: Profile):
        current_xp = profile.reputation_score or 0
        
        # Determine appropriate level
        stmt = select(Level).where(Level.min_points <= current_xp).order_by(desc(Level.min_points)).limit(1)
        result = await db.execute(stmt)
        new_level = result.scalar_one_or_none()
        
        if new_level and new_level.id != profile.current_level_id:
            old_level_id = profile.current_level_id
            
            # Update Level
            profile.current_level_id = new_level.id
            print(f"🎉 Level Up! User {profile.username} promoted to {new_level.name}")
            
            # Notify User
            try:
                await notification_service.send_in_app_notification(
                    db=db,
                    user_id=profile.id,
                    title="¡Subiste de Nivel! 🚀",
                    body=f"Felicidades, ahora eres nivel {new_level.name}. ¡Disfruta tus nuevos beneficios!",
                    type="gamification",
                    data={"screen": "profile", "level_id": str(new_level.id)}
                )
            except Exception as e:
                print(f"Error sending level up notification: {e}")

gamification_service = GamificationService()
