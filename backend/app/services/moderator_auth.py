from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Moderator
from ..services.auth import hash_password, verify_password


async def authenticate_moderator(session: AsyncSession, email: str, password: str) -> Moderator | None:
    """Аутентификация модератора"""
    moderator = await session.scalar(select(Moderator).where(Moderator.email == email))
    if not moderator or not moderator.is_active:
        return None
    if not verify_password(password, moderator.password_hash):
        return None
    moderator.last_login_at = datetime.now(tz=timezone.utc)
    await session.flush()
    return moderator


async def create_moderator(
    session: AsyncSession, email: str, password: str
) -> Moderator:
    """Создать нового модератора"""
    existing = await session.scalar(select(Moderator).where(Moderator.email == email))
    if existing:
        raise ValueError(f'Moderator with email {email} already exists')
    
    moderator = Moderator(
        email=email,
        password_hash=hash_password(password),
        is_active=True,
    )
    session.add(moderator)
    await session.flush()
    return moderator

