
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def inspect_storage():
    print("🔍 Inspecting Storage State...")
    async with AsyncSessionLocal() as session:
        try:
            # 1. Check Buckets
            print("\n--- BUCKETS ---")
            result = await session.execute(text("select id, name, public, owner from storage.buckets;"))
            buckets = result.fetchall()
            for b in buckets:
                print(f"Bucket: {b.id} | Name: {b.name} | Public: {b.public} | Owner: {b.owner}")

            # 2. Check Policies
            print("\n--- POLICIES (storage.objects) ---")
            result = await session.execute(text("""
                SELECT policyname, roles, cmd, qual, with_check 
                FROM pg_policies 
                WHERE schemaname = 'storage' AND tablename = 'objects';
            """))
            policies = result.fetchall()
            for p in policies:
                print(f"Policy: {p.policyname}")
                print(f"  Cmd: {p.cmd} | Roles: {p.roles}")
                print(f"  Using: {p.qual}")
                print(f"  Check: {p.with_check}")
                print("-" * 30)
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_storage())
