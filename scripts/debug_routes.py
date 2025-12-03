import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.main import app

print("Registered Routes:")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"{route.methods} {route.path}")
    elif hasattr(route, "routes"):
        # Mounted router
        pass

# Also check api_router specifically if needed, but app.routes should show flattened paths
