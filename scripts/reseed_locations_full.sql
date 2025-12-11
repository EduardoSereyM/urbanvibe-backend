-- Reseed Locations with FULL Metropolitan Region Communes
-- Wrapped in a single DO block to ensure atomic execution via SQLAlchemy

DO $$
DECLARE
    reg_rm BIGINT;
    reg_valpo BIGINT;
    reg_biobio BIGINT;
    reg_coq BIGINT;
    reg_arauc BIGINT;
BEGIN
    -- 1. Clean existing data
    -- Using EXECUTE for DDL/Truncate inside PL/pgSQL
    EXECUTE 'TRUNCATE TABLE public.cities RESTART IDENTITY CASCADE';
    EXECUTE 'TRUNCATE TABLE public.regions RESTART IDENTITY CASCADE';
    EXECUTE 'TRUNCATE TABLE public.countries RESTART IDENTITY CASCADE';

    -- 2. Insert Country
    INSERT INTO public.countries (code, name) VALUES ('CL', 'Chile');

    -- 3. Insert Regions
    INSERT INTO public.regions (country_code, name) VALUES 
        ('CL', 'Arica y Parinacota'),
        ('CL', 'Tarapacá'),
        ('CL', 'Antofagasta'),
        ('CL', 'Atacama'),
        ('CL', 'Coquimbo'),
        ('CL', 'Valparaíso'),
        ('CL', 'Región Metropolitana'),
        ('CL', 'O''Higgins'),
        ('CL', 'Maule'),
        ('CL', 'Ñuble'),
        ('CL', 'Biobío'),
        ('CL', 'Araucanía'),
        ('CL', 'Los Ríos'),
        ('CL', 'Los Lagos'),
        ('CL', 'Aysén'),
        ('CL', 'Magallanes');

    -- 4. Get IDs
    SELECT id INTO reg_rm FROM public.regions WHERE name = 'Región Metropolitana';
    SELECT id INTO reg_valpo FROM public.regions WHERE name = 'Valparaíso';
    SELECT id INTO reg_biobio FROM public.regions WHERE name = 'Biobío';
    SELECT id INTO reg_coq FROM public.regions WHERE name = 'Coquimbo';
    SELECT id INTO reg_arauc FROM public.regions WHERE name = 'Araucanía';

    -- 5. Insert Communes
    IF reg_rm IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            -- Provincia de Santiago
            (reg_rm, 'Santiago'),
            (reg_rm, 'Cerrillos'),
            (reg_rm, 'Cerro Navia'),
            (reg_rm, 'Conchalí'),
            (reg_rm, 'El Bosque'),
            (reg_rm, 'Estación Central'),
            (reg_rm, 'Huechuraba'),
            (reg_rm, 'Independencia'),
            (reg_rm, 'La Cisterna'),
            (reg_rm, 'La Florida'),
            (reg_rm, 'La Granja'),
            (reg_rm, 'La Pintana'),
            (reg_rm, 'La Reina'),
            (reg_rm, 'Las Condes'),
            (reg_rm, 'Lo Barnechea'),
            (reg_rm, 'Lo Espejo'),
            (reg_rm, 'Lo Prado'),
            (reg_rm, 'Macul'),
            (reg_rm, 'Maipú'),
            (reg_rm, 'Ñuñoa'),
            (reg_rm, 'Pedro Aguirre Cerda'),
            (reg_rm, 'Peñalolén'),
            (reg_rm, 'Providencia'),
            (reg_rm, 'Pudahuel'),
            (reg_rm, 'Quilicura'),
            (reg_rm, 'Quinta Normal'),
            (reg_rm, 'Recoleta'),
            (reg_rm, 'Renca'),
            (reg_rm, 'San Joaquín'),
            (reg_rm, 'San Miguel'),
            (reg_rm, 'San Ramón'),
            (reg_rm, 'Vitacura'),
            -- Provincia de Cordillera
            (reg_rm, 'Puente Alto'),
            (reg_rm, 'Pirque'),
            (reg_rm, 'San José de Maipo'),
            -- Provincia de Chacabuco
            (reg_rm, 'Colina'),
            (reg_rm, 'Lampa'),
            (reg_rm, 'Tiltil'),
            -- Provincia de Maipo
            (reg_rm, 'San Bernardo'),
            (reg_rm, 'Buin'),
            (reg_rm, 'Calera de Tango'),
            (reg_rm, 'Paine'),
            -- Provincia de Melipilla
            (reg_rm, 'Melipilla'),
            (reg_rm, 'Alhué'),
            (reg_rm, 'Curacaví'),
            (reg_rm, 'María Pinto'),
            (reg_rm, 'San Pedro'),
            -- Provincia de Talagante
            (reg_rm, 'Talagante'),
            (reg_rm, 'El Monte'),
            (reg_rm, 'Isla de Maipo'),
            (reg_rm, 'Padre Hurtado'),
            (reg_rm, 'Peñaflor');
    END IF;

    IF reg_valpo IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            (reg_valpo, 'Valparaíso'), (reg_valpo, 'Viña del Mar'), (reg_valpo, 'Concón'), (reg_valpo, 'Quilpué'), (reg_valpo, 'Villa Alemana');
    END IF;

    IF reg_biobio IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            (reg_biobio, 'Concepción'), (reg_biobio, 'Talcahuano'), (reg_biobio, 'San Pedro de la Paz'), (reg_biobio, 'Chiguayante');
    END IF;

    IF reg_coq IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            (reg_coq, 'La Serena'), (reg_coq, 'Coquimbo'), (reg_coq, 'Ovalle');
    END IF;

    IF reg_arauc IS NOT NULL THEN
        INSERT INTO public.cities (region_id, name) VALUES 
            (reg_arauc, 'Temuco'), (reg_arauc, 'Villarrica'), (reg_arauc, 'Pucón');
    END IF;
    
END $$;
