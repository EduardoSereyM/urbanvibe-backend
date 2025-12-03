# Guía de Pruebas con Postman - Panel de Administración

## 🎯 Configuración Inicial

### 1. Crear una Colección en Postman

1. Click en "New" → "Collection"
2. Nombre: "UrbanVibe Admin API"
3. Click "Create"

---

### 2. Configurar Variables de Entorno

1. Click en "Environments" (icono de ojo arriba a la derecha)
2. Click "Add"
3. Nombre: "UrbanVibe Local"
4. Agregar variables:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` |
| `api_version` | `/api/v1` | `/api/v1` |
| `token` | `demo` | `demo` |

5. Click "Save"
6. Selecciona el environment "UrbanVibe Local" en el dropdown arriba a la derecha

---

## 🔐 Configuración de Autenticación

### Opción 1: Bearer Token (Recomendado)

Para cada request:

1. Ve a la pestaña **"Authorization"**
2. **Type:** Selecciona `Bearer Token`
3. **Token:** Escribe `{{token}}` (usa la variable de entorno)

### Opción 2: Header Manual

Alternativamente, en la pestaña **"Headers"**:

| Key | Value |
|-----|-------|
| `Authorization` | `Bearer {{token}}` |

---

## 📋 Endpoints a Probar

### Test 1: Listar Todos los Venues

**Request:**
- **Method:** `GET`
- **URL:** `{{base_url}}{{api_version}}/admin/venues`
- **Authorization:** Bearer Token → `{{token}}`

**Query Params (Opcionales):**

| Key | Value | Description |
|-----|-------|-------------|
| `limit` | `10` | Items por página |
| `skip` | `0` | Offset |
| `search` | `bar` | Búsqueda |
| `city` | `Santiago` | Filtro por ciudad |
| `sort_by` | `name` | Ordenar por |
| `sort_order` | `asc` | Orden |

**Pasos en Postman:**
1. Click "Add Request"
2. Nombre: "List All Venues"
3. Method: `GET`
4. URL: `{{base_url}}{{api_version}}/admin/venues`
5. Authorization → Bearer Token → `{{token}}`
6. (Opcional) Params → Agregar query params
7. Click "Send"

**Respuesta Esperada (200 OK):**
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

---

### Test 2: Búsqueda de Venues

**Request:**
- **Method:** `GET`
- **URL:** `{{base_url}}{{api_version}}/admin/venues?search=bar&city=Santiago`
- **Authorization:** Bearer Token → `{{token}}`

**Pasos en Postman:**
1. Duplica el request anterior (Right click → Duplicate)
2. Nombre: "Search Venues"
3. Params → Agregar:
   - `search`: `bar`
   - `city`: `Santiago`
4. Click "Send"

**Respuesta Esperada (200 OK):**
- Solo venues que contengan "bar" en nombre/legal_name/dirección
- Y que estén en Santiago

---

### Test 3: Detalle de Venue

**Request:**
- **Method:** `GET`
- **URL:** `{{base_url}}{{api_version}}/admin/venues/{venue_id}`
- **Authorization:** Bearer Token → `{{token}}`

**Pasos en Postman:**
1. Copia un `id` de la respuesta del Test 1
2. Click "Add Request"
3. Nombre: "Get Venue Detail"
4. Method: `GET`
5. URL: `{{base_url}}{{api_version}}/admin/venues/PEGA_EL_ID_AQUI`
6. Authorization → Bearer Token → `{{token}}`
7. Click "Send"

**Respuesta Esperada (200 OK):**
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

---

### Test 4: Paginación

**Request:**
- **Method:** `GET`
- **URL:** `{{base_url}}{{api_version}}/admin/venues?skip=0&limit=5`
- **Authorization:** Bearer Token → `{{token}}`

**Pasos en Postman:**
1. Duplica el request "List All Venues"
2. Nombre: "Pagination Test"
3. Params → Modificar:
   - `skip`: `0`
   - `limit`: `5`
4. Click "Send"
5. Verifica que solo retorne 5 items

**Luego prueba la siguiente página:**
- Cambia `skip` a `5`
- Click "Send"
- Deberías ver los siguientes 5 items

---

### Test 5: Ordenamiento

**Request:**
- **Method:** `GET`
- **URL:** `{{base_url}}{{api_version}}/admin/venues?sort_by=name&sort_order=asc`
- **Authorization:** Bearer Token → `{{token}}`

**Pasos en Postman:**
1. Duplica el request "List All Venues"
2. Nombre: "Sort by Name"
3. Params → Agregar:
   - `sort_by`: `name`
   - `sort_order`: `asc`
4. Click "Send"
5. Verifica que los venues estén ordenados alfabéticamente

**Prueba otros ordenamientos:**
- `sort_by=created_at&sort_order=desc` (más recientes primero)
- `sort_by=rating_average&sort_order=desc` (mejor rating primero)

---

## ❌ Tests de Seguridad (403 Forbidden)

### Test 6: Usuario NO SUPER_ADMIN

**Importante:** Este test solo funciona si tienes un token de un usuario que NO sea SUPER_ADMIN.

**Pasos:**
1. Duplica el request "List All Venues"
2. Nombre: "Test 403 - Non Admin"
3. Authorization → Bearer Token → Cambia a un token de usuario normal
4. Click "Send"

**Respuesta Esperada (403 Forbidden):**
```json
{
  "detail": "Acceso denegado. Se requiere rol de SUPER_ADMIN."
}
```

---

## 🔧 Tips de Postman

### 1. Guardar Responses como Ejemplos

Después de un request exitoso:
1. Click en "Save Response"
2. Click "Save as Example"
3. Nombre: "Success Response"

Esto te permite ver ejemplos de respuestas sin hacer el request.

### 2. Tests Automáticos

En la pestaña "Tests" de cada request, puedes agregar:

```javascript
// Verificar status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Verificar que retorne venues
pm.test("Response has venues array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('venues');
    pm.expect(jsonData.venues).to.be.an('array');
});

// Verificar paginación
pm.test("Response has pagination info", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('total');
    pm.expect(jsonData).to.have.property('skip');
    pm.expect(jsonData).to.have.property('limit');
});
```

### 3. Pre-request Scripts

Para generar datos dinámicos:

```javascript
// Generar timestamp
pm.environment.set("timestamp", new Date().toISOString());

// Generar número aleatorio
pm.environment.set("random", Math.floor(Math.random() * 1000));
```

---

## 📦 Exportar/Importar Colección

### Exportar:
1. Click derecho en la colección
2. "Export"
3. Formato: Collection v2.1
4. "Export"
5. Guarda el archivo JSON

### Importar:
1. Click "Import"
2. Arrastra el archivo JSON
3. Click "Import"

---

## 🎨 Organizar Requests

Crea carpetas dentro de la colección:

1. **Admin Panel**
   - List All Venues
   - Search Venues
   - Get Venue Detail
   - Pagination Test
   - Sort Test

2. **Security Tests**
   - Test 403 - Non Admin
   - Test 401 - No Token

---

## ✅ Checklist de Pruebas

- [ ] GET /admin/venues retorna 200
- [ ] Búsqueda funciona correctamente
- [ ] Filtros funcionan (city, operational_status)
- [ ] Paginación funciona (skip, limit)
- [ ] Ordenamiento funciona (sort_by, sort_order)
- [ ] GET /admin/venues/{id} retorna detalle completo
- [ ] Owner info se incluye en lista
- [ ] Team info se incluye en detalle
- [ ] Usuario NO SUPER_ADMIN recibe 403
- [ ] Sin token recibe 401

---

## 🚀 Próximos Pasos

1. **Crea la colección** en Postman
2. **Configura el environment** con las variables
3. **Prueba cada endpoint** siguiendo esta guía
4. **Guarda los ejemplos** de respuestas exitosas
5. **Exporta la colección** para compartir con el equipo
