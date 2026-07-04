from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Using DeclarativeBase makes it simple to swap SQLite for PostgreSQL —
    only the DATABASE_URL connection string needs to change.
    """

    pass


async def get_db() -> AsyncSession:
    """Dependency that provides a database session per request."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables on startup (used for development/first-run).

    In production, prefer running Alembic migrations instead:
        alembic upgrade head
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
