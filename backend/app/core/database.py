import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.models import Base

logger = logging.getLogger(__name__)

# Async Engine & Session for high-performance FastAPI endpoints
async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

# Sync Engine & Session (for migrations, DDL initialization, and synchronous ETL workers)
sync_engine = create_engine(
    settings.sync_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def init_db() -> None:
    """
    Verifica l'estensione PostGIS e crea le tabelle e gli indici spaziali
    se non ancora presenti.
    """
    logger.info("Connecting to PostgreSQL and checking PostGIS extension...")
    with sync_engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        Base.metadata.create_all(bind=conn)
    logger.info("Database initialized successfully.")
