from fastapi import APIRouter
from app.api.v1.endpoints import health, venues, profiles, checkins, qr, contact
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.public.routes import router as public_router
from app.api.v1.venues_admin.router import router as venues_admin_router
from app.api.v1.admin.router import router as admin_router

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(checkins.router, prefix="/checkins", tags=["checkins"])
# api_router.include_router(qr.router, prefix="/qr", tags=["qr"])

api_router.include_router(auth_router,   prefix="/auth",   tags=["auth"])
api_router.include_router(public_router, prefix="/public", tags=["public"])
api_router.include_router(venues_admin_router, prefix="/venues-admin", tags=["venues_admin"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
