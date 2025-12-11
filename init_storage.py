
import asyncio
from app.core.supabase_admin import get_supabase_admin

async def init_storage():
    """
    Inicializa el bucket 'avatars' si no existe.
    """
    print("🚀 Initializing Supabase Storage...")
    try:
        supabase = get_supabase_admin()
        
        # 1. Check if bucket exists
        buckets = supabase.storage.list_buckets()
        
        # Note: buckets is usually a list of objects or dicts
        # We need to robustly check if 'avatars' is in it.
        # Based on Supabase-py, buckets return list of bucket objects
        
        avatar_bucket_exists = False
        if buckets:
             # handle potential response structure variations
             if isinstance(buckets, list):
                 for b in buckets:
                     # Supabase JS/Python client return objects with 'name' attr or dict
                     b_name = b.name if hasattr(b, 'name') else b.get('name')
                     if b_name == 'avatars':
                         avatar_bucket_exists = True
                         break

        if avatar_bucket_exists:
            print("✅ Bucket 'avatars' already exists.")
        else:
            print("📦 Creating bucket 'avatars'...")
            # Create public bucket for avatars
            supabase.storage.create_bucket('avatars', options={'public': True})
            print("✅ Bucket 'avatars' created successfully.")

    except Exception as e:
        print(f"❌ Error initializing storage: {e}")

if __name__ == "__main__":
    asyncio.run(init_storage())
