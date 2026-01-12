
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

SQL_SCRIPT = """
-- Grant usage on public schema
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

-- Grant table permissions specifically for profiles (and others to be safe)
GRANT ALL ON TABLE public.profiles TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.venues TO anon, authenticated, service_role;
GRANT ALL ON TABLE public.checkins TO anon, authenticated, service_role;

-- Grant sequence permissions (for IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- Ensure authenticated users can actually select from profiles
-- (Duplicate of above but being explicit)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.profiles TO authenticated;
"""

async def fix_permissions():
    print("🔧 Applying GRANT permissions to tables...")
    async with AsyncSessionLocal() as session:
        try:
            statements = [s.strip() for s in SQL_SCRIPT.split(';') if s.strip()]
            for statement in statements:
                print(f"Executing: {statement[:50]}...")
                await session.execute(text(statement))
            
            await session.commit()
            print("✅ Permissions granted successfully.")
            
        except Exception as e:
            print(f"❌ Error granting permissions: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(fix_permissions())
