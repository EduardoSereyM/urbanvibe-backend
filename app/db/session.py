from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
import logging

from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Log the connection URL (without password) for debugging
safe_url = settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "REDACTED"
logger.info(f"Connecting to database at: ...@{safe_url}")

# Fix for Render/Heroku providing postgresql:// but we need postgresql+asyncpg://
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    db_url,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args={
        "server_settings": {
            "jit": "off",  # Optimization for asyncpg with pgbouncer/pooler
        },
        "ssl": "require",
        "prepared_statement_cache_size": 0, # Recommended for transaction poolers, but verify if needed
    },
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
