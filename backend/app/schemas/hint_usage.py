"""Схемы для работы с подсказками"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class HintUsageCreate(BaseModel):
    """Схема для создания использования подсказки"""
    task_id: uuid.UUID = Field(..., description='ID задачи')
    vacancy_id: uuid.UUID | None = Field(None, description='ID вакансии')
    hint_level: str = Field(..., description='Уровень подсказки (surface, medium, deep)')


class HintUsageRead(BaseModel):
    """Схема для чтения использования подсказки"""
    id: uuid.UUID
    user_id: uuid.UUID
    task_id: uuid.UUID
    vacancy_id: uuid.UUID | None
    hint_level: str
    penalty: float
    created_at: datetime

    class Config:
        from_attributes = True


class HintRequest(BaseModel):
    """Запрос на получение подсказки"""
    task_id: uuid.UUID = Field(..., description='ID задачи')
    hint_level: str = Field(..., description='Уровень подсказки (surface, medium, deep)')


class HintResponse(BaseModel):
    """Ответ с подсказкой"""
    content: str = Field(..., description='Содержание подсказки')
    penalty: float = Field(..., description='Штраф в баллах')
    remaining_hints: int = Field(..., description='Количество оставшихся подсказок')

