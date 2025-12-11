import asyncio
import os
import sys
sys.path.append(os.getcwd())
import logging
from sqlalchemy import text
from app.db.session import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_sql_file(filename):
    logger.info(f"Reading SQL file: {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    logger.info("Connecting to database...")
    async with engine.begin() as conn:
        logger.info(f"Executing SQL...")
        await conn.execute(text(sql_content))
    
    logger.info("SQL execution completed successfully!")
    await engine.dispose()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_sql_script.py <path_to_sql_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    asyncio.run(run_sql_file(sql_file))
