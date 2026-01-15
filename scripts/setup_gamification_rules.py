import asyncio
import os
import sys
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def setup_events():
    async with AsyncSessionLocal() as db:
        print("🚀 Configurando nuevos eventos de Gamificación...")
        
        # 1. REFERRAL_USER (500 pts por invitar amigos)
        # 2. MENU_UPDATE (100 pts para el local por actualizar carta)
        # 3. QUALITY_REVIEW (200 pts por reseñas de calidad)
        
        events = [
            ("REFERRAL_USER", "user", "Premio por invitar a un nuevo usuario", 500),
            ("MENU_UPDATE", "venue", "Premio al local por actualizar su menú/carta", 100),
            ("QUALITY_REVIEW", "user", "Reseña de calidad verificada", 200),
            ("REFERRAL_VENUE", "user", "Premio por registrar un nuevo local", 1000)
        ]
        
        for code, target, desc, pts in events:
            sql = text("""
                INSERT INTO public.gamification_events (event_code, target_type, description, points, is_active)
                VALUES (:code, :target, :desc, :pts, true)
                ON CONFLICT (event_code) DO UPDATE SET
                    points = EXCLUDED.points,
                    description = EXCLUDED.description;
            """)
            await db.execute(sql, {"code": code, "target": target, "desc": desc, "pts": pts})
        
        await db.commit()
        print("✅ Eventos configurados correctamente.")

if __name__ == "__main__":
    asyncio.run(setup_events())
