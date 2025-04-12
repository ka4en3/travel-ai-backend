# app/db/sessions.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from utils.config import settings

engine = create_async_engine(
    settings.db_async_url,
    connect_args={"timeout": settings.DB_CONNECT_TIMEOUT},
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that yields an AsyncSession for use with FastAPI.
    """
    async with async_session_factory() as session:
        yield session
