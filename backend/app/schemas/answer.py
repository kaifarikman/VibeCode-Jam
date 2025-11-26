from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AnswerBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description='Текст ответа')


class AnswerCreate(AnswerBase):
    question_id: uuid.UUID | None = Field(None, description='ID вопроса (опционально, берется из URL)')


class AnswerRead(AnswerBase):
    id: uuid.UUID
    user_id: uuid.UUID
    question_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnswerWithQuestion(AnswerRead):
    question: QuestionRead

    class Config:
        from_attributes = True


# Для избежания циклических импортов
from .question import QuestionRead  # noqa: E402

AnswerWithQuestion.model_rebuild()

