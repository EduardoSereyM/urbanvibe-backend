
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

SQL_SCRIPT = """
-- Drop the nuclear "Allow All" policies
drop policy if exists "Debug Allow All Authenticated" on storage.objects;
drop policy if exists "Debug Public Read" on storage.objects;

-- Restore secure policies for urbanvibe_media

-- 1. Public Read Access (anyone can view files)
create policy "Public Access urbanvibe_media"
on storage.objects for select
to public
using ( bucket_id = 'urbanvibe_media' );

-- 2. Authenticated Insert (any authenticated user can upload)
create policy "Authenticated Insert urbanvibe_media"
on storage.objects for insert
to authenticated
with check ( bucket_id = 'urbanvibe_media' );

-- 3. Owner Update (users can only update their own files)
create policy "Owner Update urbanvibe_media"
on storage.objects for update
to authenticated
using ( bucket_id = 'urbanvibe_media' and auth.uid() = owner );

-- 4. Owner Delete (users can only delete their own files)
create policy "Owner Delete urbanvibe_media"
on storage.objects for delete
to authenticated
using ( bucket_id = 'urbanvibe_media' and auth.uid() = owner );

-- Restore secure policies for venues-media (if still in use)

-- 1. Public Read Access
create policy "Public Access venues-media"
on storage.objects for select
to public
using ( bucket_id = 'venues-media' );

-- 2. Authenticated Insert
create policy "Authenticated Insert venues-media"
on storage.objects for insert
to authenticated
with check ( bucket_id = 'venues-media' );

-- 3. Owner Update
create policy "Owner Update venues-media"
on storage.objects for update
to authenticated
using ( bucket_id = 'venues-media' and auth.uid() = owner );

-- 4. Owner Delete
create policy "Owner Delete venues-media"
on storage.objects for delete
to authenticated
using ( bucket_id = 'venues-media' and auth.uid() = owner );
"""

async def restore_secure_policies():
    print("🔒 Restoring Secure Storage Policies...")
    async with AsyncSessionLocal() as session:
        try:
            statements = [s.strip() for s in SQL_SCRIPT.split(';') if s.strip()]
            for statement in statements:
                print(f"Executing: {statement[:50]}...")
                try:
                    await session.execute(text(statement))
                except Exception as e:
                    print(f"Warning (ignore if policy doesn't exist): {e}")
            
            await session.commit()
            print("✅ Secure policies restored successfully.")
            
        except Exception as e:
            print(f"❌ Error restoring policies: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(restore_secure_policies())
