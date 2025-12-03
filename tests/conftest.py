import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.session import get_db
from app.core.config import settings

# Use a separate test database or the same one if acceptable for this task
# For safety in a real env, we'd use a test DB. 
# Given constraints, we will mock the session or use the main one carefully.
# Since we cannot create tables, we assume the DB is ready.
# We will override the dependency to use a transaction-rolling session if possible,
# but asyncpg + sqlalchemy transaction rollback in tests is complex without nested transaction support.
# For this MVP verification, we will use the real DB but be careful or just test read-only endpoints mostly.

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
