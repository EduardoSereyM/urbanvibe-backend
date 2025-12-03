"""
Script de diagnóstico para verificar imports y rutas
"""
import sys
import traceback

print("=" * 60)
print("DIAGNÓSTICO DE IMPORTS")
print("=" * 60)

# Test 1: Import básico de FastAPI
try:
    from fastapi import FastAPI
    print("✓ FastAPI importado correctamente")
except Exception as e:
    print(f"✗ Error importando FastAPI: {e}")

# Test 2: Import de geoalchemy2
try:
    from geoalchemy2.shape import to_shape
    print("✓ geoalchemy2 importado correctamente")
except Exception as e:
    print(f"✗ Error importando geoalchemy2: {e}")

# Test 3: Import de shapely
try:
    from shapely.geometry import Point
    print("✓ shapely importado correctamente")
except Exception as e:
    print(f"✗ Error importando shapely: {e}")

# Test 4: Import del schema
try:
    from app.api.v1.venues.schemas import VenueMapPreviewResponse
    print("✓ VenueMapPreviewResponse importado correctamente")
except Exception as e:
    print(f"✗ Error importando VenueMapPreviewResponse:")
    traceback.print_exc()

# Test 5: Import del service
try:
    from app.api.v1.venues.service import get_venues_map_preview
    print("✓ get_venues_map_preview importado correctamente")
except Exception as e:
    print(f"✗ Error importando get_venues_map_preview:")
    traceback.print_exc()

# Test 6: Import del router
try:
    from app.api.v1.endpoints.venues import router
    print("✓ Router de venues importado correctamente")
    print(f"  Rutas registradas: {len(router.routes)}")
    for route in router.routes:
        if hasattr(route, 'path'):
            print(f"    - {route.methods} {route.path}")
except Exception as e:
    print(f"✗ Error importando router de venues:")
    traceback.print_exc()

# Test 7: Import de la app completa
try:
    from app.main import app
    print("✓ App principal importada correctamente")
    print(f"\nRutas registradas en la app:")
    for route in app.routes:
        if hasattr(route, 'path') and 'venues' in route.path:
            print(f"  - {route.methods} {route.path}")
except Exception as e:
    print(f"✗ Error importando app principal:")
    traceback.print_exc()

print("=" * 60)
