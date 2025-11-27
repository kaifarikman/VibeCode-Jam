"""Схемы для модератора"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from ..models import Moderator


class ModeratorRead(BaseModel):
    """Схема для чтения данных модератора"""
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None

    @classmethod
    def from_orm(cls, moderator: Moderator):
        """Создать ModeratorRead из модели Moderator"""
        return cls(
            id=moderator.id,
            email=moderator.email,
            is_active=moderator.is_active,
            created_at=moderator.created_at,
            last_login_at=moderator.last_login_at,
        )

    class Config:
        from_attributes = True


class ModeratorCreate(BaseModel):
    """Схема для создания модератора"""
    email: EmailStr = Field(..., description='Email модератора')
    password: str = Field(..., min_length=8, max_length=128, description='Пароль')

