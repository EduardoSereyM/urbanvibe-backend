from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from fastapi import HTTPException, status
from geopy.distance import geodesic

from app.models.checkins import Checkin
from app.models.venues import Venue
from app.services.qr_token_service import qr_token_service
from app.core.config import settings
from geoalchemy2.shape import to_shape

class CheckinService:
    @staticmethod
    async def process_checkin(
        db: AsyncSession,
        user_id: UUID,
        token_str: str,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None
    ) -> Checkin:
        
        # Validate dynamic QR token
        qr_token = await qr_token_service.validate_token(db, token_str)
        venue_id = qr_token.venue_id
        
        geofence_passed = False
        
        # Fetch venue to check location
        result = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue = result.scalar_one_or_none()
        
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
            
        if venue.location is not None and user_lat is not None and user_lng is not None:
            # Calculate distance
            venue_point = to_shape(venue.location)
            # venue_point.y is lat, venue_point.x is lng
            venue_coords = (venue_point.y, venue_point.x)
            user_coords = (user_lat, user_lng)
            
            try:
                distance = geodesic(user_coords, venue_coords).meters
                
                if distance < 100: # 100 meters geofence
                    geofence_passed = True
            except Exception:
                # If coordinates are invalid, just ignore geofence
                pass
        
        # Create checkin record
        new_checkin = Checkin(
            user_id=user_id,
            venue_id=venue_id,
            status="confirmed" if geofence_passed else "pending",
            geofence_passed=geofence_passed,
            token_id=qr_token.id, # Link to the QrToken record
            location=f"POINT({user_lng} {user_lat})",
            user_accuracy_m=0 # We could pass this if available
        )
        
        db.add(new_checkin)
        
        # Mark token as used
        await qr_token_service.mark_token_used(db, qr_token, user_id)
        
        try:
            await db.commit()
            await db.refresh(new_checkin)
            
            # --- Notificaciones ---
            from app.services.notifications import notification_service
            from app.models.profiles import Profile
            
            # 1. Obtener datos del usuario para el mensaje
            user_res = await db.execute(select(Profile).where(Profile.id == user_id))
            user_profile = user_res.scalar_one_or_none()
            user_name = user_profile.username if user_profile else "Un usuario"
            
            # 2. Notificar al Usuario (Feedback exitoso)
            await notification_service.send_in_app_notification(
                db=db,
                user_id=user_id,
                title="Check-in Exitoso ✅",
                body=f"Bienvenido a {venue.name}. ¡Disfruta tu visita!",
                type="success",
                data={"screen": "venue-detail", "id": str(venue_id)}
            )
            
            # 3. Notificar al Dueño del Local
            if venue.owner_id:
                await notification_service.send_in_app_notification(
                    db=db,
                    user_id=venue.owner_id,
                    title="Nuevo Check-in 📍",
                    body=f"{user_name} ha realizado check-in en {venue.name}.",
                    type="info",
                    data={"screen": "venue-checkins", "venue_id": str(venue_id)}
                )

        except Exception as e:
            await db.rollback()
            # Check for unique constraint violation
            if "ux_checkins_user_venue_day" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya has hecho check-in en este local hoy."
                )
            # Re-raise other errors
            raise e
        
        return new_checkin

    async def get_user_checkins(
        self,
        db: AsyncSession,
        user_id: UUID,
        limit: int = 20
    ):
        stmt = (
            select(Checkin, Venue.name.label("venue_name"))
            .join(Venue, Checkin.venue_id == Venue.id)
            .where(Checkin.user_id == user_id)
            .order_by(Checkin.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()
        
        # Map to CheckinResponse structure manually since we have extra fields
        checkins = []
        for checkin, venue_name in rows:
            checkin.venue_name = venue_name # Attach venue_name to the ORM object (or dict)
            checkins.append(checkin)
            
        return checkins

checkin_service = CheckinService()
