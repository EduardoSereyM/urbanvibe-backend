from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
import logging

from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Log the connection URL (without password) for debugging
safe_url = settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "REDACTED"
logger.info(f"Connecting to database at: ...@{safe_url}")

engine = create_async_engine(
    settings.DATABASE_URL,
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
