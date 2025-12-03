# Test de Verificación de Permisos B2B

## ✅ Cambios Implementados

### Archivo: `app/api/v1/venues_admin/service.py`

**Nueva función `check_b2b_permissions()`:**
- Verifica si el usuario tiene permisos B2B
- Retorna `True` si el usuario tiene al menos uno de estos roles:
  - `SUPER_ADMIN` (via JWT claim)
  - `VENUE_OWNER` (owner_id en venues)
  - `VENUE_STAFF` (en venue_team)
  - `VENUE_MANAGER` (en venue_team)
- Retorna `False` para usuarios `APP_USER`

**Actualización de `get_user_venues()`:**
- Ahora verifica permisos ANTES de ejecutar la query
- Lanza `HTTPException 403` si el usuario no tiene permisos B2B
- Mensaje de error en español: "No tienes permisos para acceder a esta sección. Se requiere rol de Local."

---

## 🧪 Tests de Verificación

### Test 1: Usuario APP_USER (sin permisos B2B) ❌

**Usuario:** `usuario@urbanvibe.cl` (rol: APP_USER)

```bash
# Login y obtener token
curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"usuario@urbanvibe.cl","password":"password123"}'

# Intentar acceder a /me/venues
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/venues-admin/me/venues
```

**Respuesta esperada:**
```json
{
  "detail": "No tienes permisos para acceder a esta sección. Se requiere rol de Local."
}
```
**Status:** `403 Forbidden` ✅

---

### Test 2: Usuario VENUE_OWNER (con permisos B2B) ✅

**Usuario:** `local@urbanvibe.cl` (tiene venues con owner_id)

```bash
# Login y obtener token
curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"local@urbanvibe.cl","password":"password123"}'

# Acceder a /me/venues
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/venues-admin/me/venues
```

**Respuesta esperada:**
```json
{
  "venues": [
    {
      "id": "uuid",
      "name": "Mi Local",
      "roles": ["VENUE_OWNER"],
      ...
    }
  ]
}
```
**Status:** `200 OK` ✅

---

### Test 3: Usuario SUPER_ADMIN ✅

**Usuario:** `admin@urbanvibe.cl` (claim `app_role: "SUPER_ADMIN"`)

```bash
# Login y obtener token con claim SUPER_ADMIN
curl -H "Authorization: Bearer <token_con_claim_superadmin>" \
     http://localhost:8000/api/v1/venues-admin/me/venues
```

**Respuesta esperada:**
```json
{
  "venues": [...]  // Todos los venues del sistema
}
```
**Status:** `200 OK` ✅

---

### Test 4: Usuario con rol en venue_team ✅

**Usuario:** Usuario con entrada en `venue_team` con rol `VENUE_STAFF`

```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/venues-admin/me/venues
```

**Respuesta esperada:**
```json
{
  "venues": [...]  // Venues donde tiene rol activo
}
```
**Status:** `200 OK` ✅

---

## 📋 Checklist de Verificación

- [ ] Usuario APP_USER recibe 403 Forbidden
- [ ] Usuario VENUE_OWNER recibe 200 OK
- [ ] Usuario VENUE_STAFF recibe 200 OK  
- [ ] Usuario VENUE_MANAGER recibe 200 OK
- [ ] Usuario SUPER_ADMIN recibe 200 OK
- [ ] El mensaje de error está en español
- [ ] Usuarios autorizados pueden ver array vacío (200 OK con `{"venues": []}`)

---

## 🔍 Verificación en Base de Datos

### Verificar roles de un usuario:

```sql
-- Ver si el usuario es owner de algún venue
SELECT v.id, v.name, v.owner_id
FROM public.venues v
WHERE v.owner_id = '<user_id>'
  AND v.deleted_at IS NULL;

-- Ver roles en venue_team
SELECT 
    u.email,
    v.name as venue_name,
    ar.name as role_name,
    vt.is_active
FROM public.venue_team vt
JOIN public.profiles p ON vt.user_id = p.id
JOIN auth.users u ON p.id = u.id
JOIN public.venues v ON vt.venue_id = v.id
JOIN public.app_roles ar ON vt.role_id = ar.id
WHERE p.id = '<user_id>';
```

---

## 🚀 Próximos Pasos

1. **Reiniciar el servidor** para aplicar cambios
2. **Ejecutar los tests** con diferentes tipos de usuarios
3. **Verificar logs** del servidor para confirmar el comportamiento
4. **Actualizar frontend** para manejar el error 403 apropiadamente

---

## 💡 Notas Técnicas

- La función `check_b2b_permissions()` es reutilizable para otros endpoints B2B
- Maneja gracefully el caso donde `venue_team` no existe aún
- SUPER_ADMIN siempre tiene acceso (bypass de todas las verificaciones)
- La verificación se hace ANTES de la query para optimizar rendimiento
