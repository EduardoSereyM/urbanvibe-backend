import asyncio
from sqlalchemy import text
from app.db.base import SessionLocal

async def check_schema():
    async with SessionLocal() as db:
        try:
            # Check if columns exist in venues table
            result = await db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'venues' 
                AND column_name IN ('company_tax_id', 'ownership_proof_url');
            """))
            columns = result.scalars().all()
            print(f"Found columns: {columns}")
            
            if 'company_tax_id' not in columns or 'ownership_proof_url' not in columns:
                print("MISSING COLUMNS! Please run the migration SQL.")
            else:
                print("Columns exist.")
                
        except Exception as e:
            print(f"Error checking schema: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
