import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal as SessionLocal
from app.models.venues import Venue

async def debug_insert():
    async with SessionLocal() as db:
        try:
            print("Attempting to insert a test venue...")
            
            # Create a dummy venue
            new_venue = Venue(
                name="Debug Venue",
                legal_name="Debug Venue SpA",
                latitude=-33.4489,
                longitude=-70.6693,
                location="POINT(-70.6693 -33.4489)",
                company_tax_id="11.222.333-4",
                ownership_proof_url="https://example.com/doc.pdf"
            )
            
            db.add(new_venue)
            await db.commit()
            print("SUCCESS: Venue inserted successfully!")
            
        except Exception as e:
            print("\nFAILED: Error inserting venue:")
            print(f"{type(e).__name__}: {e}")
            
            # Rollback to be safe
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(debug_insert())
