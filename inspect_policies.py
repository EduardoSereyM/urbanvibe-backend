
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

SQL_SCRIPT = """
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE schemaname = 'storage' AND tablename = 'objects';
"""

async def inspect():
    print("🔍 Inspecting Storage Policies...")
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text(SQL_SCRIPT))
            rows = result.fetchall()
            
            if not rows:
                print("❌ No policies found for storage.objects!")
            
            for row in rows:
                print(f"Policy: {row.policyname}")
                print(f"  Command: {row.cmd}")
                print(f"  Roles: {row.roles}")
                print(f"  USING: {row.qual}")
                print(f"  WITH CHECK: {row.with_check}")
                print("-" * 20)
                
        except Exception as e:
            print(f"❌ Error inspecting policies: {e}")

if __name__ == "__main__":
    asyncio.run(inspect())
