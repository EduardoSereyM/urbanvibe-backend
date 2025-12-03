import asyncio
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from gotrue.errors import AuthApiError

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    sys.exit(1)

# Initialize Supabase Client with Service Role Key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

async def get_or_create_user(email, password):
    """
    Creates a user if not exists, otherwise returns the user object.
    Uses admin API to confirm email automatically.
    """
    print(f"Processing user: {email}")
    try:
        # Try to get user by email (admin list_users doesn't filter by email directly in all versions easily, 
        # but we can try to create and catch error, or search)
        # Efficient way: Try to create. If fails saying exists, fetch ID.
        
        # Note: supabase-py admin.create_user returns a UserResponse
        user_attributes = {
            "email": email,
            "password": password,
            "email_confirm": True
        }
        user = supabase.auth.admin.create_user(user_attributes)
        print(f"  - Created new user: {user.user.id}")
        return user.user
        
    except AuthApiError as e:
        if "User already registered" in str(e) or "duplicate key" in str(e):
            print("  - User already exists, fetching details...")
            # Fetch user ID. Admin list users is paginated.
            # Alternatively, since we have the email, we can't easily "get" by email via admin API without listing.
            # Hack: Attempt sign in to get ID? No, we are admin.
            # Better: List users and filter.
            # For this script, we assume not too many users, or we just iterate.
            # Actually, supabase-py `list_users` might allow filtering? 
            # Current supabase-py/gotrue-py doesn't support server-side email filter on list_users well yet.
            # Let's try listing (limit 100) and finding.
            users = supabase.auth.admin.list_users(page=1, per_page=1000)
            for u in users:
                if u.email == email:
                    print(f"  - Found existing user: {u.id}")
                    return u
            print(f"  - Error: User says registered but not found in first 1000 users.")
            return None
        else:
            print(f"  - Error creating user: {e}")
            raise e
    except Exception as e:
        print(f"  - Unexpected error: {e}")
        raise e

def upsert_profile(user_id, updates):
    """
    Upserts profile data for a given user_id.
    """
    print(f"  - Updating profile for {user_id}...")
    data = {"id": user_id, **updates}
    try:
        response = supabase.table("profiles").upsert(data).execute()
        # response.data is the list of upserted rows
        print(f"  - Profile updated: {updates}")
        return response.data
    except Exception as e:
        print(f"  - Error updating profile: {e}")
        raise e

def get_or_create_venue(name, slug, location_wkt):
    """
    Creates or retrieves a venue by slug.
    """
    print(f"Processing venue: {name}")
    try:
        # Check if exists
        res = supabase.table("venues").select("*").eq("slug", slug).execute()
        if res.data:
            print(f"  - Venue already exists: {res.data[0]['id']}")
            return res.data[0]
        
        # Create
        venue_data = {
            "name": name,
            "slug": slug,
            "location": location_wkt, # PostGIS expects string for geography if casted or handled by backend, 
                                      # but via Supabase-py/PostgREST, we might need to be careful.
                                      # Usually PostgREST accepts WKT for geography columns.
            "trust_tier": "verified_safe",
            "is_verified": True
        }
        res = supabase.table("venues").insert(venue_data).execute()
        print(f"  - Created venue: {res.data[0]['id']}")
        return res.data[0]
    except Exception as e:
        print(f"  - Error processing venue: {e}")
        raise e

def get_role_id(role_name):
    print(f"Fetching role ID for: {role_name}")
    try:
        res = supabase.table("app_roles").select("id").eq("name", role_name).execute()
        if res.data:
            return res.data[0]['id']
        print(f"  - Role {role_name} not found.")
        return None
    except Exception as e:
        print(f"  - Error fetching role: {e}")
        raise e

def link_user_to_venue(user_id, venue_id, role_id):
    print(f"Linking user {user_id} to venue {venue_id} with role {role_id}")
    try:
        # Check if link exists
        res = supabase.table("venue_team")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("venue_id", venue_id)\
            .execute()
            
        if res.data:
            print("  - Link already exists.")
            return
            
        link_data = {
            "user_id": user_id,
            "venue_id": venue_id,
            "role_id": role_id
        }
        supabase.table("venue_team").insert(link_data).execute()
        print("  - Link created.")
    except Exception as e:
        print(f"  - Error linking user to venue: {e}")
        raise e

async def main():
    print("--- STARTING SEED SCRIPT ---")

    # 1. Explorador
    user_exp = await get_or_create_user("usuario@urbanvibe.cl", "password123")
    if user_exp:
        upsert_profile(user_exp.id, {"username": "explorer_juan"})

    # 2. Super Admin
    user_admin = await get_or_create_user("admin@urbanvibe.cl", "password123")
    if user_admin:
        upsert_profile(user_admin.id, {"reputation_score": 100})

    # 3. Dueño Local
    user_owner = await get_or_create_user("local@urbanvibe.cl", "password123")
    if user_owner:
        upsert_profile(user_owner.id, {"is_verified": True})

    # 4. Local y Vinculación
    venue = get_or_create_venue(
        "Bar La Junta (Test)", 
        "bar-la-junta-test", 
        "POINT(-70.6341 33.4378)"
    )
    
    if venue and user_owner:
        role_id = get_role_id("VENUE_OWNER")
        if role_id:
            link_user_to_venue(user_owner.id, venue['id'], role_id)
        else:
            print("Skipping link because role VENUE_OWNER was not found.")

    print("--- SEED SCRIPT COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(main())
