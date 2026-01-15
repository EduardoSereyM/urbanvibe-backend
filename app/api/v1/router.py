
from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    venue_team,
    contact,
    checkins,
    promotions,
    # reviews - if needed
)
from app.api.v1.auth import router as auth_router
from app.api.v1.venues.routes import router as venues_public_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.venues_admin.router import router as venues_admin_router
from app.api.v1.admin.router import router as admin_router
from app.api.v1.endpoints import mobile # BFF
from app.api.v1.endpoints import mobile # BFF
from app.api.v1.endpoints import notifications # Notifications
from app.api.v1.admin.gamification import router as gamification_admin_router

api_router = APIRouter()

api_router.include_router(mobile.router, prefix="/mobile", tags=["Mobile BFF"])
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(profiles_router, prefix="/profiles", tags=["User Profile"])
api_router.include_router(venues_public_router, prefix="/venues", tags=["Venues Public"])
api_router.include_router(venue_team.router, prefix="/venue-team", tags=["Venue Team"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["Checkins Basic"])
api_router.include_router(promotions.router, prefix="/promotions", tags=["Promotions User"])

# Admin / B2B
api_router.include_router(venues_admin_router, prefix="/venues-admin", tags=["Venues Admin B2B"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
from app.api.v1.reviews.router import router as reviews_router
api_router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(gamification_admin_router, prefix="/admin/gamification", tags=["Admin Gamification"])
