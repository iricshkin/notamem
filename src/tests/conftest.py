import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from litestar.plugins.sqlalchemy import base

TEST_DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@localhost/notamem_test_db'


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(base.UUIDBase.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(base.UUIDAuditBase.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=db_engine) as session:
        yield session
        await session.rollback()
