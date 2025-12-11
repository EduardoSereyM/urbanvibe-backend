DO $$
BEGIN
    -- Enable RLS
    ALTER TABLE public.countries ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.regions ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.cities ENABLE ROW LEVEL SECURITY;

    -- Drop existing policies to avoid conflict
    DROP POLICY IF EXISTS "Paises visibles" ON public.countries;
    DROP POLICY IF EXISTS "Regiones visibles" ON public.regions;
    DROP POLICY IF EXISTS "Ciudades visibles" ON public.cities;

    -- Create policies
    CREATE POLICY "Paises visibles" ON public.countries FOR SELECT USING (true);
    CREATE POLICY "Regiones visibles" ON public.regions FOR SELECT USING (true);
    CREATE POLICY "Ciudades visibles" ON public.cities FOR SELECT USING (true);
END $$;
