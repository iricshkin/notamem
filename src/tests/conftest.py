import pytest_asyncio
from src.app import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from litestar.plugins.sqlalchemy import base
from sqlalchemy.orm import sessionmaker
from litestar.testing import AsyncTestClient

TEST_DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@localhost/notamem_test_db'


@pytest_asyncio.fixture
async def test_client(db_session: AsyncSession) -> AsyncTestClient:
    async with AsyncTestClient(app) as client:
        yield client


# Фикстура для движка базы данных
@pytest_asyncio.fixture()
async def db_engine():
    # Создает движок с подключением к тестовой базе данных
    engine = create_async_engine(
        TEST_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(
            base.UUIDBase.metadata.create_all
        )
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_engine: base.UUIDBase.metadata.drop_all(
                sync_engine, checkfirst=True
            )
        )
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session_maker(db_engine):
    return sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )


# Фикстура для сессии базы данных
@pytest_asyncio.fixture
async def db_session(async_session_maker) -> AsyncSession:
    AsyncSessionLocal = async_session_maker
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
