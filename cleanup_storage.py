
import asyncio
from app.core.supabase_admin import get_supabase_admin

async def cleanup_storage():
    """
    Elimina el bucket 'avatars' si existe y está vacío (o se fuerza).
    """
    print("🧹 Cleaning up Supabase Storage...")
    try:
        supabase = get_supabase_admin()
        
        # 1. Delete bucket 'avatars'
        try:
             res = supabase.storage.empty_bucket('avatars')
             print(f"Empty bucket result: {res}")
             supabase.storage.delete_bucket('avatars')
             print("✅ Bucket 'avatars' deleted successfully.")
        except Exception as e:
            print(f"⚠️ Could not delete bucket 'avatars' (maybe it doesn't exist or is not empty): {e}")

    except Exception as e:
        print(f"❌ Error cleaning up storage: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_storage())
