-- Trigger para actualizar rating_average y review_count automáticamente
-- Este trigger se ejecuta después de INSERT, UPDATE o DELETE en la tabla reviews

-- Función que actualiza las estadísticas del venue
CREATE OR REPLACE FUNCTION update_venue_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar estadísticas para el venue afectado
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
$$ LANGUAGE plpgsql;

-- Eliminar trigger anterior si existe
DROP TRIGGER IF EXISTS trigger_update_venue_stats ON public.reviews;

-- Crear trigger que se ejecuta después de INSERT, UPDATE o DELETE
CREATE TRIGGER trigger_update_venue_stats
    AFTER INSERT OR UPDATE OR DELETE ON public.reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_venue_stats();

-- Actualizar todos los venues existentes con los valores correctos
UPDATE public.venues v
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
    );
