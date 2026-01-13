import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.venues import Venue

async def inspect():
    async with AsyncSessionLocal() as session:
        print("--- INSPECCIONANDO TABLA VENUES ---")
        
        # 1. Total Count
        stmt_all = select(Venue)
        result_all = await session.execute(stmt_all)
        all_venues = result_all.scalars().all()
        print(f"Total venues encontrados: {len(all_venues)}")
        
        if not all_venues:
            print("⚠️ LA BASE DE DATOS ESTÁ VACÍA (Tabla venues)")
            return

        # 2. Status Breakdown
        open_count = sum(1 for v in all_venues if v.operational_status == 'open')
        print(f"Venues con operational_status='open': {open_count}")
        
        # 3. Valid Location Breakdown
        loc_count = sum(1 for v in all_venues if v.latitude is not None and v.longitude is not None)
        print(f"Venues con coordenadas válidas: {loc_count}")
        
        # 4. Valid for Explore (Open + Location)
        valid_count = sum(1 for v in all_venues if v.operational_status == 'open' and v.latitude and v.longitude)
        print(f"Venues VÁLIDOS para Explore (Open + Coords): {valid_count}")
        
        # 5. Muestra de fallos
        print("\n--- DETALLE DE LOS PRIMEROS 5 VENUES ---")
        for v in all_venues[:5]:
            cat_name = "N/A"
            try:
                # Intento de acceso a relación (simulando problema de lazy load o data faltante)
                cat_name = v.category.name if v.category else "None"
            except Exception as e:
                cat_name = f"ERROR: {e}"
            
            print(f"ID: {v.id} | Name: {v.name} | Cat: {cat_name} | Lat/Lng: {v.latitude}/{v.longitude}")

if __name__ == "__main__":
    asyncio.run(inspect())
