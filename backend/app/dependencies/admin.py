from fastapi import Depends, HTTPException, status

from ..dependencies.auth import get_current_user
from ..models import User


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверяет, является ли пользователь админом"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied. Admin privileges required.',
        )
    return current_user

