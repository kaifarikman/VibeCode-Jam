import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..core.security import create_access_token
from ..database import get_session
from ..schemas import (
    AuthCodeVerify,
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthRequestCode,
    AuthSuccessResponse,
)
from ..models import User
from ..services.auth import (
    authenticate_user,
    generate_code,
    register_user,
    store_code,
    verify_code,
)
from ..services.email import EmailService


router = APIRouter(prefix='/auth', tags=['auth'])
logger = logging.getLogger(__name__)


@router.post('/register', status_code=status.HTTP_202_ACCEPTED)
async def register(
    payload: AuthRegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    try:
        settings = get_settings()
        user = await register_user(session, payload.email, payload.password, payload.full_name)
        code = generate_code()
        await store_code(session, user, code)
        await session.commit()

        email_service = EmailService(settings)

        async def fire_and_forget():
            try:
                await email_service.send_login_code(payload.email, code)
                logger.info('Login code sent successfully to %s', payload.email)
            except Exception as exc:  # noqa: BLE001
                logger.error('Failed to send login code to %s: %s', payload.email, exc, exc_info=True)

        asyncio.create_task(fire_and_forget())
        return {'detail': 'Код подтверждения отправлен на почту'}
    except ValueError as exc:
        await session.rollback()
        if str(exc) == 'USER_ALREADY_VERIFIED':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пользователь уже зарегистрирован. Выполните вход.',
            ) from exc
        error_msg = str(exc)
        if error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Не удалось обработать регистрацию',
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error('Error in register: %s', exc, exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Внутренняя ошибка сервера. Попробуйте позже.'
        ) from exc


@router.post('/verify', response_model=AuthSuccessResponse)
async def verify(
    payload: AuthCodeVerify,
    session: AsyncSession = Depends(get_session),
):
    user = await verify_code(session, payload.email, payload.code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный код подтверждения или код истёк. Запросите новый код.',
        )
    await session.commit()

    # После успешной верификации возвращаем токен для автоматического входа
    token = create_access_token(str(user.id))
    return AuthSuccessResponse(access_token=token, user=user)


@router.post('/login', response_model=AuthSuccessResponse)
async def login(
    payload: AuthLoginRequest,
    session: AsyncSession = Depends(get_session),
):
    user = await authenticate_user(session, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный email или пароль',
        )
    await session.commit()

    token = create_access_token(str(user.id))
    return AuthSuccessResponse(access_token=token, user=user)


@router.post('/request-code', status_code=status.HTTP_202_ACCEPTED)
async def request_code(
    payload: AuthRequestCode,
    session: AsyncSession = Depends(get_session),
):
    """Запросить новый код подтверждения"""
    try:
        settings = get_settings()
        user = await session.scalar(
            select(User).where(User.email == payload.email)
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден',
            )
        
        code = generate_code()
        await store_code(session, user, code)
        await session.commit()

        email_service = EmailService(settings)

        async def fire_and_forget():
            try:
                await email_service.send_login_code(payload.email, code)
                logger.info('Login code sent successfully to %s', payload.email)
            except Exception as exc:  # noqa: BLE001
                logger.error('Failed to send login code to %s: %s', payload.email, exc, exc_info=True)

        asyncio.create_task(fire_and_forget())
        return {'detail': 'Код подтверждения отправлен на почту'}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.error('Error in request_code: %s', exc, exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Внутренняя ошибка сервера. Попробуйте позже.'
        ) from exc


