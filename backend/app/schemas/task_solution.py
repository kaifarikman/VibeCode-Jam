"""Схемы для решений задач"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskSolutionBase(BaseModel):
    task_id: uuid.UUID = Field(..., description='ID задачи')
    vacancy_id: uuid.UUID | None = Field(None, description='ID вакансии (для контеста)')
    solution_code: str = Field(..., description='Код решения')
    language: str = Field(..., description='Язык программирования')


class TaskSolutionCreate(TaskSolutionBase):
    execution_id: uuid.UUID | None = Field(None, description='ID execution')
    verdict: str | None = Field(None, description='Вердикт (ACCEPTED, WRONG ANSWER, etc.)')
    test_results: dict[str, Any] | None = Field(None, description='Результаты тестов')


class TaskSolutionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    task_id: uuid.UUID
    vacancy_id: uuid.UUID | None
    status: str  # attempted, solved
    verdict: str | None
    language: str
    test_results: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

