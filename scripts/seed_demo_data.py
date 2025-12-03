import asyncio
import os
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models.venues import Venue
from app.models.profiles import Profile
from app.models.checkins import Checkin 
from app.core.config import settings
from geoalchemy2.elements import WKTElement

# --- CONFIGURACIÓN ---
DEMO_USER_ID = UUID("a09db2c6-ee06-49df-b0f6-f55c6184a83c") 

async def seed_data():
    print("🌱 Iniciando Seeding de Datos...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        connect_args={"ssl": "require", "prepared_statement_cache_size": 0}
    )
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as db:
        print(f"👤 Actualizando perfil para: {DEMO_USER_ID}")
        
        # 1. Perfil
        demo_profile = Profile(
            id=DEMO_USER_ID,
            username="urbanvibe_tester",
            display_name="Tester Oficial",
            reputation_score=100,
            points_current=500,
            is_verified=True,
            status="active"
        )
        await db.merge(demo_profile)

        print("🏗️ Creando Locales...")
        
        # 2. Locales
        venues_data = [
            Venue(
                name="Bar La Junta",
                overview="El clásico de Lastarria. Cervezas y buena vibra.",
                slug="bar-la-junta-lastarria-v4", # Slug único V4
                trust_tier="verified_safe",
                is_verified=True,
                verified_visits_monthly=120,
                location=WKTElement("POINT(-70.6415 -33.4372)", srid=4326) 
            ),
            Venue(
                name="Café del Barrio",
                overview="Café de especialidad y coworking.",
                slug="cafe-del-barrio-v4", # Slug único V4
                trust_tier="standard",
                is_verified=True,
                verified_visits_monthly=45,
                location=WKTElement("POINT(-70.6420 -33.4380)", srid=4326)
            )
        ]
        
        created_venues = []
        for v in venues_data:
            # CORRECCIÓN: Capturamos el objeto 'merged' que devuelve db.merge
            merged_venue = await db.merge(v)
            created_venues.append(merged_venue)
        
        # Hacemos flush para asegurar que los venues tienen ID asignado (si son nuevos)
        await db.flush() 

        print("📍 Generando Check-ins...")
        # 3. Check-ins
        try:
            for venue in created_venues:
                # Aseguramos que venue.id no sea None
                if not venue.id:
                    print(f"⚠️ Venue {venue.name} no tiene ID, saltando checkin...")
                    continue

                checkin = Checkin(
                    user_id=DEMO_USER_ID,
                    venue_id=venue.id, # Ahora sí debería tener valor
                    token_id=f"token_seed_{venue.slug}", 
                    status="confirmed",
                    geofence_passed=True,
                    points_awarded=10,
                    location=WKTElement("POINT(-70.6415 -33.4372)", srid=4326)
                )
                db.add(checkin)
            
            await db.commit()
            print("✅ Seeding completado con éxito.")
            
        except Exception as e:
            print(f"⚠️ Nota: Posible duplicado o conflicto en checkins: {e}")
            # Hacemos rollback parcial si falla checkins, pero intentamos salvar venues
            await db.rollback()
            print("   (Se hizo rollback de la transacción para evitar estado inconsistente)")

if __name__ == "__main__":
    asyncio.run(seed_data())