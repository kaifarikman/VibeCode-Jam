"""Схемы для метрик задач"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class TaskMetricRead(BaseModel):
    id: uuid.UUID
    task_solution_id: uuid.UUID
    user_id: uuid.UUID
    task_id: uuid.UUID
    vacancy_id: uuid.UUID | None
    language: str
    verdict: str | None
    tests_total: int | None
    tests_passed: int | None
    total_duration_ms: int | None
    average_duration_ms: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


