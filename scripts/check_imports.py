import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    print("Attempting to import app.api.v1.venues_admin.router...")
    from app.api.v1.venues_admin import router
    print("SUCCESS: Import successful!")
except Exception as e:
    print(f"FAILED: Import failed with error: {e}")
    sys.exit(1)
