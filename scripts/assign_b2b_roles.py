"""
Script para asignar roles B2B a usuarios existentes
Ejecutar después de crear venues para asignar automáticamente VENUE_OWNER
"""
import asyncio
from sqlalchemy import select, text
from app.db.session import get_db
from app.models.venues import Venue
from uuid import UUID


async def assign_owner_roles():
    """
    Asigna rol VENUE_OWNER a todos los owners de venues existentes
    """
    print("=" * 70)
    print("ASIGNANDO ROLES B2B A OWNERS DE VENUES")
    print("=" * 70)
    
    async for db in get_db():
        try:
            # Obtener el role_id de VENUE_OWNER
            result = await db.execute(
                text("SELECT id FROM public.app_roles WHERE name = 'VENUE_OWNER'")
            )
            role_row = result.first()
            
            if not role_row:
                print("❌ Error: Rol VENUE_OWNER no existe en app_roles")
                print("   Ejecuta primero el script de creación de roles")
                return
            
            venue_owner_role_id = role_row[0]
            print(f"✅ Rol VENUE_OWNER encontrado: ID {venue_owner_role_id}")
            
            # Obtener todos los venues con owner_id
            result = await db.execute(
                select(Venue).where(Venue.owner_id.isnot(None))
            )
            venues = result.scalars().all()
            
            print(f"\n📊 Encontrados {len(venues)} venues con owner_id")
            
            # Asignar rol a cada owner
            assigned_count = 0
            skipped_count = 0
            
            for venue in venues:
                # Verificar si ya existe el rol
                check_result = await db.execute(
                    text("""
                        SELECT 1 FROM public.venue_team 
                        WHERE venue_id = :venue_id 
                          AND user_id = :user_id
                    """),
                    {
                        "venue_id": str(venue.id),
                        "user_id": str(venue.owner_id)
                    }
                )
                
                if check_result.first():
                    skipped_count += 1
                    continue
                
                # Insertar el rol
                await db.execute(
                    text("""
                        INSERT INTO public.venue_team 
                        (venue_id, user_id, role_id, is_active)
                        VALUES (:venue_id, :user_id, :role_id, true)
                    """),
                    {
                        "venue_id": str(venue.id),
                        "user_id": str(venue.owner_id),
                        "role_id": venue_owner_role_id
                    }
                )
                assigned_count += 1
                print(f"  ✅ Asignado VENUE_OWNER a {venue.owner_id} para venue '{venue.name}'")
            
            await db.commit()
            
            print("\n" + "=" * 70)
            print("RESUMEN")
            print("=" * 70)
            print(f"✅ Roles asignados: {assigned_count}")
            print(f"⏭️  Ya existían: {skipped_count}")
            print(f"📊 Total venues procesados: {len(venues)}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            await db.rollback()
        finally:
            break


if __name__ == "__main__":
    asyncio.run(assign_owner_roles())
