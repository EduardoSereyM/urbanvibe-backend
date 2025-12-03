# Guía de Verificación - Panel de Administración

## 🎯 Endpoints Implementados

### 1. `GET /api/v1/admin/venues`
Lista todos los venues con filtros y paginación.

### 2. `GET /api/v1/admin/venues/{venue_id}`
Detalle completo de un venue.

---

## 🧪 Tests de Verificación

### Paso 1: Reiniciar el servidor

```bash
# Detener el servidor (Ctrl+C)
# Reiniciar:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Paso 2: Verificar en Swagger

1. **Abrir Swagger:** `http://localhost:8000/docs`

2. **Buscar la sección "admin"**
   - Debería aparecer una nueva sección con 2 endpoints

3. **Autorizar como SUPER_ADMIN**
   - Click en "Authorize"
   - Ingresa: `demo` (si DEMO_MODE=True)
   - Click "Authorize"

---

### Test 1: Listar Todos los Venues (SUPER_ADMIN) ✅

**Endpoint:** `GET /api/v1/admin/venues`

**En Swagger:**
1. Click en el endpoint
2. Click "Try it out"
3. Deja los parámetros por defecto o prueba con:
   - `limit`: 10
   - `sort_by`: name
   - `sort_order`: asc
4. Click "Execute"

**Respuesta esperada:**
```json
{
  "venues": [
    {
      "id": "uuid",
      "name": "Nombre del Local",
      "legal_name": "Razón Social",
      "city": "Santiago",
      "address_display": "Av. Principal 123",
      "verification_status": "pending",
      "operational_status": "open",
      "rating_average": 4.5,
      "review_count": 150,
      "verified_visits_all_time": 1200,
      "created_at": "2024-01-15T10:30:00Z",
      "owner": {
        "id": "uuid",
        "display_name": "Juan Pérez",
        "email": "owner@example.com",
        "phone": "+56912345678"
      }
    }
  ],
  "total": 45,
  "skip": 0,
  "limit": 10
}
```

**Status:** `200 OK` ✅

---

### Test 2: Búsqueda y Filtros ✅

**Endpoint:** `GET /api/v1/admin/venues?search=bar&city=Santiago`

**En Swagger:**
1. Click "Try it out"
2. Ingresa:
   - `search`: bar
   - `city`: Santiago
3. Click "Execute"

**Respuesta esperada:**
- Solo venues que contengan "bar" en nombre/legal_name/dirección
- Y que estén en Santiago
- Status: `200 OK`

---

### Test 3: Detalle Completo de Venue ✅

**Endpoint:** `GET /api/v1/admin/venues/{venue_id}`

**En Swagger:**
1. Copia un `id` de la lista anterior
2. Click en el endpoint de detalle
3. Click "Try it out"
4. Pega el `venue_id`
5. Click "Execute"

**Respuesta esperada:**
```json
{
  "id": "uuid",
  "name": "Nombre del Local",
  "legal_name": "Razón Social S.A.",
  "slogan": "El mejor lugar",
  "overview": "Descripción completa...",
  "verification_status": "pending",
  "operational_status": "open",
  "is_founder_venue": false,
  
  "address": {
    "address_display": "Av. Principal 123",
    "city": "Santiago",
    "region_state": "Metropolitana",
    "country_code": "CL",
    "latitude": -33.4372,
    "longitude": -70.6506
  },
  
  "contact_phone": "+56912345678",
  "contact_email": "contacto@local.cl",
  "website": "https://local.cl",
  
  "metrics": {
    "total_verified_visits": 1200,
    "verified_visits_this_month": 85,
    "rating_average": 4.5,
    "total_reviews": 150
  },
  
  "team": [
    {
      "user_id": "uuid",
      "display_name": "Juan Pérez",
      "email": "owner@example.com",
      "role": "VENUE_OWNER",
      "is_active": true,
      "joined_at": "2024-01-15T10:30:00Z"
    }
  ],
  
  "features_config": {...},
  "opening_hours": {...},
  "amenities": {...},
  "payment_methods": {...},
  
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-03-20T15:45:00Z",
  "owner_id": "uuid"
}
```

**Status:** `200 OK` ✅

---

### Test 4: Usuario NO SUPER_ADMIN (403) ❌

**Importante:** Para este test necesitas un token de un usuario que NO sea SUPER_ADMIN.

**Opción 1: Crear usuario de prueba**
```sql
-- En Supabase SQL Editor
-- Crear un usuario APP_USER
INSERT INTO auth.users (email, encrypted_password)
VALUES ('test@urbanvibe.cl', crypt('password123', gen_salt('bf')));
```

**Opción 2: Usar modo DEMO**
Si estás en modo DEMO, el token "demo" es de un usuario VENUE_OWNER, no SUPER_ADMIN, así que debería recibir 403.

**Prueba:**
```bash
curl -H "Authorization: Bearer <token_no_super_admin>" \
     http://localhost:8000/api/v1/admin/venues
```

**Respuesta esperada:**
```json
{
  "detail": "Acceso denegado. Se requiere rol de SUPER_ADMIN."
}
```

**Status:** `403 Forbidden` ✅

---

## 🔍 Verificación en Base de Datos

### Ver información de owner

```sql
SELECT 
    v.id,
    v.name,
    v.owner_id,
    u.email as owner_email,
    u.raw_user_meta_data->>'display_name' as owner_name
FROM public.venues v
LEFT JOIN auth.users u ON v.owner_id = u.id
WHERE v.deleted_at IS NULL
LIMIT 5;
```

### Ver equipo de un venue

```sql
SELECT 
    vt.venue_id,
    v.name as venue_name,
    u.email as member_email,
    ar.name as role_name,
    vt.is_active
FROM public.venue_team vt
JOIN public.venues v ON vt.venue_id = v.id
JOIN auth.users u ON vt.user_id = u.id
JOIN public.app_roles ar ON vt.role_id = ar.id
WHERE v.id = '<venue_id>';
```

---

## ✅ Checklist de Verificación

- [ ] Servidor reinicia sin errores
- [ ] Sección "admin" aparece en Swagger
- [ ] `GET /admin/venues` retorna lista de venues
- [ ] Paginación funciona (`skip`, `limit`)
- [ ] Búsqueda funciona (`search`)
- [ ] Filtros funcionan (`city`, `operational_status`)
- [ ] Ordenamiento funciona (`sort_by`, `sort_order`)
- [ ] `GET /admin/venues/{id}` retorna detalle completo
- [ ] Información de owner se incluye
- [ ] Información de team se incluye
- [ ] Usuario NO SUPER_ADMIN recibe 403
- [ ] Campos de auditoría presentes (`created_at`, `updated_at`)

---

## 🐛 Troubleshooting

### Error: "admin" no aparece en Swagger
- Verifica que reiniciaste el servidor
- Revisa que `app/api/v1/router.py` incluye el admin_router

### Error 403 con SUPER_ADMIN
- Verifica que el JWT tenga el claim `app_role: "SUPER_ADMIN"`
- En modo DEMO, el token "demo" NO es SUPER_ADMIN por defecto

### Error: owner es null
- Normal si el venue no tiene `owner_id` asignado
- Verifica en la BD: `SELECT owner_id FROM venues WHERE id = '<id>'`

### Error: team está vacío
- Normal si no hay registros en `venue_team` para ese venue
- Ejecuta el script `assign_b2b_roles.sql` para asignar roles

---

## 🚀 Próximos Pasos

1. **Crear usuario SUPER_ADMIN de prueba**
2. **Probar todos los endpoints**
3. **Verificar permisos (403 para no-admin)**
4. **Implementar en frontend**
