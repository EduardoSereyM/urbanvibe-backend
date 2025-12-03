from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint
from fastapi import HTTPException, status

from app.models.venues import Venue
from app.api.v1.venues_admin.schemas import (
    VenueCreate,
    VenueSummaryForOwner,
    MyVenuesResponse,
    VenueB2BDetail,
    VenueFeaturesConfig,
    OpeningHoursConfig,
    VenueAddress,
)


async def check_b2b_permissions(
    db: AsyncSession,
    user_id: UUID,
    is_super_admin: bool = False
) -> bool:
    """
    Verifica si el usuario tiene permisos B2B.
    Retorna True si el usuario tiene al menos uno de estos roles:
    - SUPER_ADMIN (via JWT claim)
    - VENUE_OWNER
    - VENUE_MANAGER
    - VENUE_STAFF
    
    Roles que NO tienen acceso B2B:
    - APP_USER
    - APP_PREMIUM_USER
    """
    # SUPER_ADMIN siempre tiene acceso
    if is_super_admin:
        return True
    
    # Verificar si el usuario es owner de algún venue
    stmt = select(Venue).where(
        and_(
            Venue.owner_id == user_id,
            Venue.deleted_at.is_(None)
        )
    ).limit(1)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return True
    
    # Verificar si tiene roles B2B en venue_team
    try:
        result = await db.execute(
            text("""
                SELECT COUNT(*) 
                FROM public.venue_team vt
                JOIN public.app_roles ar ON vt.role_id = ar.id
                WHERE vt.user_id = :user_id
                  AND vt.is_active = true
                  AND ar.name IN ('SUPER_ADMIN', 'VENUE_OWNER', 'VENUE_MANAGER', 'VENUE_STAFF')
            """),
            {"user_id": str(user_id)}
        )
        count = result.scalar()
        if count and count > 0:
            return True
    except Exception:
        # Si la tabla venue_team no existe o hay error, continuar
        pass
    
    return False


async def get_user_venues(
    db: AsyncSession,
    user_id: UUID,
    is_super_admin: bool = False
) -> MyVenuesResponse:
    """
    Obtiene todos los venues donde el usuario tiene algún rol B2B.
    Si es SUPER_ADMIN, puede devolver todos los venues.
    
    Raises:
        HTTPException 403: Si el usuario no tiene permisos B2B
    """
    # ✅ VERIFICACIÓN DE PERMISOS B2B
    has_b2b_access = await check_b2b_permissions(db, user_id, is_super_admin)
    
    if not has_b2b_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta sección. Se requiere rol de Local."
        )
    
    # ✅ Si llegamos aquí, el usuario SÍ tiene permisos
    if is_super_admin:
        # SUPER_ADMIN puede ver todos los venues
        stmt = select(Venue).where(Venue.deleted_at.is_(None))
    else:
        # Usuario normal: solo venues donde es owner
        # TODO: Agregar lógica de venue_team cuando esté disponible
        stmt = select(Venue).where(
            and_(
                Venue.owner_id == user_id,
                Venue.deleted_at.is_(None)
            )
        )
    
    result = await db.execute(stmt)
    venues = result.scalars().all()
    
    venue_summaries = []
    for venue in venues:
        # Parse features_config
        features = None
        if venue.features_config:
            features = VenueFeaturesConfig(**venue.features_config)
        
        # Determinar roles del usuario en este venue
        roles = []
        if venue.owner_id == user_id:
            roles.append("VENUE_OWNER")
        # TODO: Agregar roles desde venue_team
        
        summary = VenueSummaryForOwner(
            id=venue.id,
            type=None,  # Campo no existe en el modelo actual
            parent_id=None,  # Campo no existe en el modelo actual
            name=venue.name,
            city=venue.city,
            operational_status=venue.operational_status,
            is_founder_venue=venue.is_founder_venue or False,
            verification_status=venue.verification_status or "pending",
            roles=roles,
            features_config=features,
            logo_url=venue.logo_url,
            created_at=venue.created_at or datetime.now()
        )
        venue_summaries.append(summary)
    
    return MyVenuesResponse(venues=venue_summaries)


async def create_founder_venue(
    db: AsyncSession,
    venue_data: VenueCreate,
    owner_user_id: UUID
) -> VenueB2BDetail:
    """
    Crea una casa matriz (local fundador) para el usuario actual.
    """
    # Crear el objeto location usando PostGIS
    location_wkt = f"POINT({venue_data.longitude} {venue_data.latitude})"
    
    # Preparar opening_hours JSON
    opening_hours_json = None
    if venue_data.opening_hours:
        opening_hours_json = venue_data.opening_hours.model_dump()
    
    # Preparar features_config
    features_config_json = {"chat": False}
    
    # Crear el venue
    new_venue = Venue(
        legal_name=venue_data.legal_name,
        name=venue_data.name,
        slogan=venue_data.slogan,
        overview=venue_data.overview,
        category_id=venue_data.category_id,
        location=location_wkt,  # GeoAlchemy2 manejará la conversión
        latitude=venue_data.latitude,
        longitude=venue_data.longitude,
        opening_hours=opening_hours_json,
        operational_status="open",
        owner_id=owner_user_id,
        features_config=features_config_json,
        
        # Nuevos campos
        logo_url=venue_data.logo_url,
        cover_image_urls=venue_data.cover_image_urls,
        price_tier=venue_data.price_tier,
        currency_code=venue_data.currency_code,
        payment_methods=venue_data.payment_methods,
        google_place_id=venue_data.google_place_id,
        directions_tip=venue_data.directions_tip,
        seo_title=venue_data.seo_title,
        seo_description=venue_data.seo_description,
        
        company_tax_id=venue_data.company_tax_id,
        ownership_proof_url=venue_data.ownership_proof_url,
        is_founder_venue=venue_data.is_founder_venue,

        # Attributes
        connectivity_features=venue_data.connectivity_features,
        accessibility_features=venue_data.accessibility_features,
        space_features=venue_data.space_features,
        comfort_features=venue_data.comfort_features,
        audience_features=venue_data.audience_features,
        entertainment_features=venue_data.entertainment_features,
        dietary_options=venue_data.dietary_options,
        access_features=venue_data.access_features,
        security_features=venue_data.security_features,
        mood_tags=venue_data.mood_tags,
        occasion_tags=venue_data.occasion_tags,
        
        music_profile=venue_data.music_profile,
        crowd_profile=venue_data.crowd_profile,
        
        capacity_estimate=venue_data.capacity_estimate,
        seated_capacity=venue_data.seated_capacity,
        standing_allowed=venue_data.standing_allowed,
        noise_level=venue_data.noise_level,
    )
    
    # Agregar datos de dirección si vienen
    if venue_data.address:
        new_venue.address_display = venue_data.address.address_display
        new_venue.city = venue_data.address.city
        new_venue.region_state = venue_data.address.region_state
        new_venue.country_code = venue_data.address.country_code
    
    db.add(new_venue)
    await db.commit()
    await db.refresh(new_venue)
    
    # TODO: Crear entrada en venue_team con rol VENUE_OWNER
    
    # Mapear a VenueB2BDetail
    return await _map_to_b2b_detail(new_venue)


async def get_venue_b2b_detail(
    db: AsyncSession,
    venue_id: UUID,
    user_id: UUID,
    is_super_admin: bool = False
) -> VenueB2BDetail:
    """
    Obtiene el detalle B2B de un venue específico.
    Valida autorización del usuario.
    """
    # Buscar el venue
    stmt = select(Venue).where(
        and_(
            Venue.id == venue_id,
            Venue.deleted_at.is_(None)
        )
    )
    result = await db.execute(stmt)
    venue = result.scalar_one_or_none()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Validar autorización
    is_authorized = False
    
    if is_super_admin:
        is_authorized = True
    elif venue.owner_id == user_id:
        is_authorized = True
    # TODO: Verificar en venue_team si el usuario tiene rol activo
    
    if not is_authorized:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this venue"
        )
    
    return await _map_to_b2b_detail(venue)


async def _map_to_b2b_detail(venue: Venue) -> VenueB2BDetail:
    """
    Mapea un objeto Venue ORM a VenueB2BDetail.
    """
    # Parse opening_hours
    opening_hours = None
    if venue.opening_hours:
        try:
            opening_hours = OpeningHoursConfig(**venue.opening_hours)
        except Exception:
            pass
    
    # Parse features_config
    features = None
    if venue.features_config:
        try:
            features = VenueFeaturesConfig(**venue.features_config)
        except Exception:
            features = VenueFeaturesConfig(chat=False)
            
    # Parse address
    address = None
    if venue.address_display or venue.city:
        address = VenueAddress(
            address_display=venue.address_display,
            city=venue.city,
            region_state=venue.region_state,
            country_code=venue.country_code
        )
    
    return VenueB2BDetail(
        id=venue.id,
        type=None,
        parent_id=None,
        name=venue.name,
        legal_name=venue.legal_name,
        slogan=venue.slogan,
        overview=venue.overview,
        category_id=venue.category_id,
        owner_id=venue.owner_id,
        
        # Location
        latitude=venue.latitude,
        longitude=venue.longitude,
        address=address,
        google_place_id=venue.google_place_id,
        directions_tip=venue.directions_tip,
        
        # Media
        logo_url=venue.logo_url,
        cover_image_urls=venue.cover_image_urls,
        
        # Details
        opening_hours=opening_hours,
        operational_status=venue.operational_status or "open",
        price_tier=venue.price_tier,
        currency_code=venue.currency_code,
        payment_methods=venue.payment_methods,
        
        # Status
        is_founder_venue=venue.is_founder_venue or False,
        verification_status=venue.verification_status or "pending",
        features_config=features,
        
        # Stats
        verified_visits_all_time=venue.verified_visits_all_time or 0,
        verified_visits_monthly=venue.verified_visits_monthly or 0,
        rating_average=venue.rating_average or 0.0,
        review_count=venue.review_count or 0,
        
        # SEO
        seo_title=venue.seo_title,
        seo_description=venue.seo_description,
        
        # B2B
        company_tax_id=venue.company_tax_id,
        ownership_proof_url=venue.ownership_proof_url,
        
        points_balance=venue.points_balance,
        
        created_at=venue.created_at or datetime.now(),
        updated_at=venue.updated_at or datetime.now()
    )


# --- CHECKINS SERVICE ---

from app.models.checkins import Checkin
from app.models.profiles import Profile
from app.api.v1.venues_admin.schemas import VenueCheckinListResponse, VenueCheckinDetail

async def get_venue_checkins(
    db: AsyncSession,
    venue_id: UUID,
    user_id: UUID,
    is_super_admin: bool = False,
    limit: int = 50
) -> VenueCheckinListResponse:
    """
    Obtiene los check-ins de un venue.
    """
    # 1. Verificar permisos
    # Primero obtenemos el venue para ver quién es el owner
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
        
    is_authorized = False
    if is_super_admin:
        is_authorized = True
    elif venue.owner_id == user_id:
        is_authorized = True
    # TODO: Check venue_team
    
    if not is_authorized:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver los check-ins de este local")

    # 2. Query Checkins
    stmt = (
        select(Checkin, Profile)
        .join(Profile, Checkin.user_id == Profile.id)
        .where(Checkin.venue_id == venue_id)
        .order_by(Checkin.created_at.desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    checkin_details = []
    for checkin, profile in rows:
        detail = VenueCheckinDetail(
            id=checkin.id,
            user_id=checkin.user_id,
            user_display_name=profile.display_name or profile.username or "Usuario Anónimo", # Fallback
            user_email=None, # Profile object does not have email attribute
            status=checkin.status,
            geofence_passed=checkin.geofence_passed,
            points_awarded=checkin.points_awarded,
            created_at=checkin.created_at
        )
        checkin_details.append(detail)
        
    return VenueCheckinListResponse(checkins=checkin_details)


async def update_checkin_status(
    db: AsyncSession,
    venue_id: UUID,
    checkin_id: int,
    new_status: str,
    user_id: UUID,
    is_super_admin: bool = False
) -> VenueCheckinDetail:
    """
    Actualiza el estado de un check-in.
    """
    # 1. Verificar permisos
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
        
    is_authorized = False
    if is_super_admin:
        is_authorized = True
    elif venue.owner_id == user_id:
        is_authorized = True
    # TODO: Check venue_team
    
    if not is_authorized:
        raise HTTPException(status_code=403, detail="No tienes permiso para gestionar este local")

    # 2. Buscar Check-in
    stmt = (
        select(Checkin, Profile)
        .join(Profile, Checkin.user_id == Profile.id)
        .where(and_(Checkin.id == checkin_id, Checkin.venue_id == venue_id))
    )
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Check-in no encontrado")
        
    checkin, profile = row
    
    # 3. Actualizar estado
    checkin.status = new_status
    
    # Si se confirma, asegurar que se otorguen puntos si corresponde (lógica simplificada por ahora)
    if new_status == 'confirmed' and checkin.points_awarded == 0:
        checkin.points_awarded = 10 # Valor por defecto, debería venir de configuración
        # Actualizar puntos del usuario
        profile.points_current += 10
        profile.points_lifetime += 10
        
    await db.commit()
    await db.refresh(checkin)
    
    return VenueCheckinDetail(
        id=checkin.id,
        user_id=checkin.user_id,
        user_display_name=profile.display_name or profile.username or "Usuario Anónimo",
        user_email=None,
        status=checkin.status,
        geofence_passed=checkin.geofence_passed,
        points_awarded=checkin.points_awarded,
        created_at=checkin.created_at
    )


# --- PROMOTIONS & REWARDS SERVICE ---

from app.models.promotions import Promotion
from app.models.logs import VenuePointsLog
from app.api.v1.venues_admin.schemas import PromotionCreate, ValidateRewardResponse

async def get_venue_promotions(
    db: AsyncSession,
    venue_id: UUID,
    user_id: UUID,
    is_super_admin: bool = False
) -> List[Promotion]:
    """
    Obtiene todas las promociones de un venue.
    """
    # 1. Verificar permisos (Reutilizar lógica o simplificar)
    has_access = await check_b2b_permissions(db, user_id, is_super_admin)
    if not has_access:
        # Check specific venue ownership if not general B2B access (though check_b2b covers most)
        result = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue = result.scalar_one_or_none()
        if not venue or (venue.owner_id != user_id and not is_super_admin):
             raise HTTPException(status_code=403, detail="No tienes permiso para ver promociones de este local")

    stmt = select(Promotion).where(Promotion.venue_id == venue_id).order_by(Promotion.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_venue_promotion(
    db: AsyncSession,
    venue_id: UUID,
    promotion_data: PromotionCreate,
    user_id: UUID,
    is_super_admin: bool = False
) -> Promotion:
    """
    Crea una nueva promoción para el venue.
    """
    # 1. Verificar permisos
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
        
    if not is_super_admin and venue.owner_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear promociones en este local")

    # 2. Crear Promoción
    # Ensure valid_until is populated (required by DB)
    promo_data_dict = promotion_data.model_dump()
    if not promo_data_dict.get("valid_until"):
        # Default to 30 days from now if not provided
        from datetime import timedelta
        promo_data_dict["valid_until"] = datetime.now() + timedelta(days=30)

    new_promo = Promotion(
        venue_id=venue_id,
        **promo_data_dict
    )
    
    db.add(new_promo)
    await db.commit()
    await db.refresh(new_promo)
    
    return new_promo


async def get_venue_points_logs(
    db: AsyncSession,
    venue_id: UUID,
    user_id: UUID,
    is_super_admin: bool = False
) -> List[VenuePointsLog]:
    """
    Obtiene el historial de puntos del venue.
    """
    # 1. Verificar permisos
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
        
    if not is_super_admin and venue.owner_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver el historial de puntos")

    stmt = select(VenuePointsLog).where(VenuePointsLog.venue_id == venue_id).order_by(VenuePointsLog.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def validate_reward_qr(
    db: AsyncSession,
    venue_id: UUID,
    qr_content: str,
    user_id: UUID,
    is_super_admin: bool = False
) -> ValidateRewardResponse:
    """
    Valida un QR de recompensa (V4).
    Simulación por ahora, ya que falta integrar con tabla de QRs reales.
    """
    # 1. Verificar permisos del local
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
        
    if not is_super_admin and venue.owner_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para validar recompensas en este local")

    # TODO: Implementar validación real contra tabla qr_tokens y reward_units
    # Por ahora, simulamos éxito si el QR tiene cierto formato o fallamos
    
    # Simulación de éxito
    points_earned = 2 # Puntos que gana el local por validar
    
    # Registrar log de puntos para el local
    log = VenuePointsLog(
        venue_id=venue_id,
        delta=points_earned,
        reason="reward_validation",
        meta_data={"qr_content": qr_content}
    )
    db.add(log)
    
    # Actualizar balance del venue (trigger lo haría, pero aquí lo hacemos manual si no hay trigger)
    venue.points_balance += points_earned
    
    await db.commit()
    
    return ValidateRewardResponse(
        success=True,
        message="Recompensa validada exitosamente",
        points_earned=points_earned
    )


