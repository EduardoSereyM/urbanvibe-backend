
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def inspect_schema_policies():
    print("Inspecting 'profiles' table policies...")
    async with AsyncSessionLocal() as session:
        try:
            # Query policies for 'profiles' table
            result = await session.execute(text("""
                SELECT policyname, cmd, roles, qual, with_check 
                FROM pg_policies 
                WHERE tablename = 'profiles';
            """))
            policies = result.fetchall()
            
            if not policies:
                print("No policies found for table 'profiles'. If RLS is enabled, access is denied by default.")
            else:
                for p in policies:
                    print(f" - Name: {p[0]}, Cmd: {p[1]}, Roles: {p[2]}, Qual: {p[3]}")

            # Check if RLS is enabled
            result_rls = await session.execute(text("""
                SELECT relrowsecurity 
                FROM pg_class 
                WHERE relname = 'profiles';
            """))
            rls_enabled = result_rls.scalar()
            print(f"RLS Enabled: {rls_enabled}")
            
        except Exception as e:
            print(f"❌ Error inspecting policies: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_schema_policies())
