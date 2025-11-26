from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .core.config import get_settings


settings = get_settings()
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,  # Пересоздание соединений каждый час
    pool_size=10,
    max_overflow=20,
)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with async_session_factory() as session:
        yield session


