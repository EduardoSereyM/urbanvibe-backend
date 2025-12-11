import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.supabase_admin import get_supabase_admin

async def test_admin():
    print("Testing Supabase Admin Client...")
    print(f"URL: {settings.SUPABASE_URL}")
    print(f"Has Service Key: {bool(settings.SUPABASE_SERVICE_KEY)}")
    
    if not settings.SUPABASE_SERVICE_KEY:
        print("❌ SUPABASE_SERVICE_KEY is missing!")
        return

    try:
        admin_client = get_supabase_admin()
        print("✅ Admin client initialized.")
        
        # Try to list users to verify permission (limit 1)
        # Note: gotrue-py might use list_users()
        print("Attempting to list users...")
        users = admin_client.auth.admin.list_users(page=1, per_page=1)
        print(f"✅ Successfully listed users. Count: {len(users)}")
        
    except Exception as e:
        print(f"❌ Error using admin client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_admin())
