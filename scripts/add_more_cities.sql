-- Add cities for other regions
DO $$
DECLARE
    reg_valpo BIGINT;
    reg_biobio BIGINT;
    reg_coq BIGINT;
    reg_arauc BIGINT;
BEGIN
    SELECT id INTO reg_valpo FROM public.regions WHERE name = 'Valparaíso';
    IF reg_valpo IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            (reg_valpo, 'Valparaíso'),
            (reg_valpo, 'Viña del Mar'),
            (reg_valpo, 'Concón'),
            (reg_valpo, 'Quilpué'),
            (reg_valpo, 'Villa Alemana')
        ON CONFLICT DO NOTHING;
    END IF;

    SELECT id INTO reg_biobio FROM public.regions WHERE name = 'Biobío';
    IF reg_biobio IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            (reg_biobio, 'Concepción'),
            (reg_biobio, 'Talcahuano'),
            (reg_biobio, 'San Pedro de la Paz'),
            (reg_biobio, 'Chiguayante')
        ON CONFLICT DO NOTHING;
    END IF;

    SELECT id INTO reg_coq FROM public.regions WHERE name = 'Coquimbo';
    IF reg_coq IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            (reg_coq, 'La Serena'),
            (reg_coq, 'Coquimbo'),
            (reg_coq, 'Ovalle')
        ON CONFLICT DO NOTHING;
    END IF;

    SELECT id INTO reg_arauc FROM public.regions WHERE name = 'Araucanía';
    IF reg_arauc IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            (reg_arauc, 'Temuco'),
            (reg_arauc, 'Villarrica'),
            (reg_arauc, 'Pucón')
        ON CONFLICT DO NOTHING;
    END IF;
END $$;
