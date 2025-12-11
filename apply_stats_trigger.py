"""
Script para aplicar el trigger de actualización de estadísticas de venues
"""
import asyncio
import logging
from sqlalchemy import text
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_trigger():
    logger.info("Aplicando trigger de estadísticas de venues...")
    
    migration_steps = [
        # Función que actualiza las estadísticas del venue
        """CREATE OR REPLACE FUNCTION update_venue_stats()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE public.venues
            SET 
                rating_average = COALESCE(
                    (SELECT AVG(general_score)::FLOAT 
                     FROM public.reviews 
                     WHERE venue_id = COALESCE(NEW.venue_id, OLD.venue_id) 
                     AND deleted_at IS NULL),
                    0.0
                ),
                review_count = COALESCE(
                    (SELECT COUNT(*)::INTEGER 
                     FROM public.reviews 
                     WHERE venue_id = COALESCE(NEW.venue_id, OLD.venue_id) 
                     AND deleted_at IS NULL),
                    0
                )
            WHERE id = COALESCE(NEW.venue_id, OLD.venue_id);
            
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql""",
        
        # Eliminar trigger anterior si existe
        "DROP TRIGGER IF EXISTS trigger_update_venue_stats ON public.reviews",
        
        # Crear trigger
        """CREATE TRIGGER trigger_update_venue_stats
            AFTER INSERT OR UPDATE OR DELETE ON public.reviews
            FOR EACH ROW
            EXECUTE FUNCTION update_venue_stats()""",
        
        # Actualizar todos los venues existentes
        """UPDATE public.venues v
        SET 
            rating_average = COALESCE(
                (SELECT AVG(general_score)::FLOAT 
                 FROM public.reviews r 
                 WHERE r.venue_id = v.id 
                 AND r.deleted_at IS NULL),
                0.0
            ),
            review_count = COALESCE(
                (SELECT COUNT(*)::INTEGER 
                 FROM public.reviews r 
                 WHERE r.venue_id = v.id 
                 AND r.deleted_at IS NULL),
                0
            )"""
    ]
    
    async with engine.begin() as conn:
        for i, step in enumerate(migration_steps):
            logger.info(f"Ejecutando paso {i+1}/{len(migration_steps)}...")
            try:
                await conn.execute(text(step))
            except Exception as e:
                logger.error(f"Error en paso {i+1}: {e}")
                raise
    
    logger.info("✅ Trigger creado y datos actualizados exitosamente!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(apply_trigger())
