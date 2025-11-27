import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.security import decode_access_token
from ..database import get_session
from ..models import Moderator


settings = get_settings()
oauth2_moderator_scheme = OAuth2PasswordBearer(
    tokenUrl=f'{settings.api_v1_str}/moderator-auth/login'
)


async def get_current_moderator(
    token: str = Depends(oauth2_moderator_scheme),
    session: AsyncSession = Depends(get_session),
) -> Moderator:
    """Получить текущего модератора из токена"""
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )

    moderator_id_str = payload.get('sub')
    if not moderator_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )

    try:
        moderator_id = uuid.UUID(str(moderator_id_str))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid moderator ID'
        )

    moderator = await session.scalar(
        select(Moderator).where(
            Moderator.id == moderator_id,
            Moderator.is_active == True
        )
    )
    if not moderator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Moderator not found or inactive'
        )
    return moderator

