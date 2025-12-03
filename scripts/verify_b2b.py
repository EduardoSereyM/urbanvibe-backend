"""
Script de verificación para el módulo B2B Venues Admin
Verifica imports, sintaxis y que los endpoints existentes no se rompieron
"""
import sys
import traceback

print("=" * 70)
print("VERIFICACIÓN DEL MÓDULO B2B VENUES ADMIN")
print("=" * 70)

# Test 1: Verificar imports del módulo venues_admin
print("\n1️⃣ Verificando imports del módulo venues_admin...")
try:
    from app.api.v1.venues_admin.schemas import (
        VenueCreate,
        MyVenuesResponse,
        VenueB2BDetail,
    )
    print("   ✅ Schemas importados correctamente")
except Exception as e:
    print(f"   ❌ Error en schemas: {e}")
    traceback.print_exc()

try:
    from app.api.v1.venues_admin.service import (
        get_user_venues,
        create_founder_venue,
        get_venue_b2b_detail,
    )
    print("   ✅ Service importado correctamente")
except Exception as e:
    print(f"   ❌ Error en service: {e}")
    traceback.print_exc()

try:
    from app.api.v1.venues_admin.router import router
    print("   ✅ Router importado correctamente")
    print(f"   📊 Rutas registradas: {len(router.routes)}")
    for route in router.routes:
        if hasattr(route, 'path'):
            print(f"      - {list(route.methods)[0]} {route.path}")
except Exception as e:
    print(f"   ❌ Error en router: {e}")
    traceback.print_exc()

# Test 2: Verificar que el router principal se carga correctamente
print("\n2️⃣ Verificando router principal...")
try:
    from app.api.v1.router import api_router
    print("   ✅ Router principal importado correctamente")
    
    # Contar rutas de venues-admin
    admin_routes = [r for r in api_router.routes if hasattr(r, 'path') and 'venues-admin' in r.path]
    print(f"   📊 Rutas venues-admin en api_router: {len(admin_routes)}")
    for route in admin_routes:
        print(f"      - {list(route.methods)[0]} {route.path}")
except Exception as e:
    print(f"   ❌ Error en router principal: {e}")
    traceback.print_exc()

# Test 3: Verificar que endpoints existentes siguen funcionando
print("\n3️⃣ Verificando endpoints existentes...")
try:
    from app.api.v1.endpoints.venues import router as venues_router
    print("   ✅ Router de venues (B2C) importado correctamente")
    print(f"   📊 Rutas B2C: {len(venues_router.routes)}")
except Exception as e:
    print(f"   ❌ Error en venues B2C: {e}")

try:
    from app.api.v1.endpoints.profiles import router as profiles_router
    print("   ✅ Router de profiles importado correctamente")
except Exception as e:
    print(f"   ❌ Error en profiles: {e}")

try:
    from app.api.v1.auth.routes import router as auth_router
    print("   ✅ Router de auth importado correctamente")
except Exception as e:
    print(f"   ❌ Error en auth: {e}")

# Test 4: Verificar que la app principal se carga
print("\n4️⃣ Verificando app principal...")
try:
    from app.main import app
    print("   ✅ App principal importada correctamente")
    
    # Contar todas las rutas
    all_routes = [r for r in app.routes if hasattr(r, 'path')]
    venues_admin_routes = [r for r in all_routes if 'venues-admin' in r.path]
    venues_b2c_routes = [r for r in all_routes if '/venues/' in r.path and 'admin' not in r.path]
    
    print(f"   📊 Total de rutas en la app: {len(all_routes)}")
    print(f"   📊 Rutas venues-admin: {len(venues_admin_routes)}")
    print(f"   📊 Rutas venues B2C: {len(venues_b2c_routes)}")
    
    print("\n   Rutas venues-admin registradas:")
    for route in venues_admin_routes:
        print(f"      - {list(route.methods)[0]} {route.path}")
    
except Exception as e:
    print(f"   ❌ Error en app principal: {e}")
    traceback.print_exc()

# Test 5: Verificar modelos
print("\n5️⃣ Verificando modelos...")
try:
    from app.models.venues import Venue
    print("   ✅ Modelo Venue importado correctamente")
except Exception as e:
    print(f"   ❌ Error en modelo Venue: {e}")

# Test 6: Verificar dependencias
print("\n6️⃣ Verificando dependencias...")
try:
    from app.api import deps
    print("   ✅ Dependencias (deps) importadas correctamente")
except Exception as e:
    print(f"   ❌ Error en deps: {e}")

try:
    from app.core.security import decode_supabase_jwt
    print("   ✅ Security importado correctamente")
except Exception as e:
    print(f"   ❌ Error en security: {e}")

print("\n" + "=" * 70)
print("VERIFICACIÓN COMPLETADA")
print("=" * 70)
