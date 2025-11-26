import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QuestionBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description='Текст вопроса')
    order: int = Field(default=0, ge=0, description='Порядок отображения')


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    text: str | None = Field(None, min_length=1, max_length=2000, description='Текст вопроса')
    order: int | None = Field(None, ge=0, description='Порядок отображения')


class QuestionRead(QuestionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

