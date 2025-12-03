-- Script para asignar roles B2B a usuarios existentes
-- Ejecutar en Supabase SQL Editor

-- 1. Verificar que existan los roles en app_roles
SELECT * FROM public.app_roles;

-- 2. Asignar rol VENUE_OWNER al usuario demo para sus venues
-- Usuario demo: a09db2c6-ee06-49df-b0f6-f55c6184a83c
INSERT INTO public.venue_team (venue_id, user_id, role_id, is_active)
SELECT 
    v.id as venue_id,
    v.owner_id as user_id,
    (SELECT id FROM public.app_roles WHERE name = 'VENUE_OWNER') as role_id,
    true as is_active
FROM public.venues v
WHERE v.owner_id = 'a09db2c6-ee06-49df-b0f6-f55c6184a83c'
  AND NOT EXISTS (
    SELECT 1 FROM public.venue_team vt 
    WHERE vt.venue_id = v.id 
      AND vt.user_id = v.owner_id
  );

-- 3. Asignar VENUE_OWNER a todos los owners de venues existentes
INSERT INTO public.venue_team (venue_id, user_id, role_id, is_active)
SELECT 
    v.id as venue_id,
    v.owner_id as user_id,
    (SELECT id FROM public.app_roles WHERE name = 'VENUE_OWNER') as role_id,
    true as is_active
FROM public.venues v
WHERE v.owner_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM public.venue_team vt 
    WHERE vt.venue_id = v.id 
      AND vt.user_id = v.owner_id
  );

-- 4. Verificar los roles asignados
SELECT 
    u.email,
    p.id as profile_id,
    v.name as venue_name,
    ar.name as role_name,
    vt.is_active
FROM public.venue_team vt
JOIN public.profiles p ON vt.user_id = p.id
JOIN auth.users u ON p.id = u.id
JOIN public.venues v ON vt.venue_id = v.id
JOIN public.app_roles ar ON vt.role_id = ar.id
ORDER BY u.email, v.name;

-- 5. Asignar SUPER_ADMIN a un usuario específico (opcional)
-- Reemplaza 'admin@urbanvibe.cl' con el email del usuario que quieres hacer SUPER_ADMIN
/*
UPDATE auth.users
SET raw_app_meta_data = jsonb_set(
    COALESCE(raw_app_meta_data, '{}'::jsonb),
    '{app_role}',
    '"SUPER_ADMIN"'
)
WHERE email = 'admin@urbanvibe.cl';
*/
