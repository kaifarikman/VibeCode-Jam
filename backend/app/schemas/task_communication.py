"""Схемы для коммуникации после сдачи задачи"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TaskCommunicationRead(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    vacancy_id: uuid.UUID | None
    solution_id: uuid.UUID
    question: str
    answer: str | None = None
    status: str
    ml_score: float | None = None
    ml_feedback: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskCommunicationAnswer(BaseModel):
    answer: str = Field(..., min_length=1, description='Ответ пользователя на вопрос')

