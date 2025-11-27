"""Схемы для решений задач"""

from __future__ import annotations

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
    test_results: list[dict[str, Any]] | None = Field(None, description='Результаты тестов')


class TaskSolutionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    task_id: uuid.UUID
    vacancy_id: uuid.UUID | None
    status: str  # attempted, solved
    verdict: str | None
    language: str
    test_results: list[dict[str, Any]] | None
    metric: TaskMetricRead | None = None
    ml_correctness: float | None = None
    ml_efficiency: float | None = None
    ml_clean_code: float | None = None
    ml_feedback: str | None = None
    ml_passed: bool | None = None
    anti_cheat_flag: bool | None = None
    anti_cheat_reason: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


from .task_metric import TaskMetricRead  # noqa: E402  (circular import workaround)

