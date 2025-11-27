"""Роуты для авторизации модератора"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.security import create_access_token
from ..database import get_session
from ..models import Moderator
from ..schemas.auth import AuthLoginRequest, AuthSuccessResponse
from ..schemas.user import UserRead
from ..services.moderator_auth import authenticate_moderator

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/moderator-auth', tags=['moderator-auth'])
settings = get_settings()


@router.post('/login', response_model=AuthSuccessResponse)
async def moderator_login(
    payload: AuthLoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """Вход модератора"""
    moderator = await authenticate_moderator(session, payload.email, payload.password)
    if not moderator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный email или пароль',
        )
    await session.commit()

    # Создаем токен для модератора
    token = create_access_token(str(moderator.id))
    
    # Создаем UserRead-совместимый объект для фронтенда
    user_read = UserRead(
        id=moderator.id,
        email=moderator.email,
        full_name=None,
        is_admin=False,
        is_verified=True,
        created_at=moderator.created_at,
        last_login_at=moderator.last_login_at,
    )
    
    return AuthSuccessResponse(
        access_token=token,
        user=user_read
    )

