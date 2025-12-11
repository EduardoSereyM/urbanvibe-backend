
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

SQL_SCRIPT = """
-- Drop strict policies to replace with broad one
drop policy if exists "Authenticated Insert urbanvibe_media" on storage.objects;
drop policy if exists "Owner Manage urbanvibe_media" on storage.objects;
drop policy if exists "Owner Delete urbanvibe_media" on storage.objects;

-- Create a BROAD policy for Authenticated users
-- Allows Insert, Update, Select, Delete as long as it's in the right bucket
create policy "Authenticated Full Access urbanvibe_media"
on storage.objects for all
to authenticated
using ( bucket_id = 'urbanvibe_media' )
with check ( bucket_id = 'urbanvibe_media' );

-- Ensure Public Select is still there (it was in inspect output, but safe to re-assert)
drop policy if exists "Public Access urbanvibe_media" on storage.objects;
create policy "Public Access urbanvibe_media"
on storage.objects for select
using ( bucket_id = 'urbanvibe_media' );
"""

async def apply_broad_policies():
    print("🚀 Applying BROAD Storage Policies...")
    async with AsyncSessionLocal() as session:
        try:
            statements = [s.strip() for s in SQL_SCRIPT.split(';') if s.strip()]
            for statement in statements:
                print(f"Executing: {statement[:50]}...")
                await session.execute(text(statement))
            
            await session.commit()
            print("✅ Broad policies applied successfully.")
            
        except Exception as e:
            print(f"❌ Error applying policies: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(apply_broad_policies())
