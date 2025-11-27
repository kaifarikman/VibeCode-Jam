import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QuestionBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description='Текст вопроса')
    order: int = Field(default=0, ge=0, description='Порядок отображения')
    question_type: str = Field(default='text', description='Тип вопроса: text, choice, multiple_choice')
    options: str | None = Field(None, description='JSON строка с вариантами ответов для choice типов')
    difficulty: str = Field(default='medium', description='Уровень сложности: easy, medium, hard')
    vacancy_id: uuid.UUID | None = Field(None, description='ID вакансии, к которой привязан вопрос')


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    text: str | None = Field(None, min_length=1, max_length=2000, description='Текст вопроса')
    order: int | None = Field(None, ge=0, description='Порядок отображения')
    question_type: str | None = Field(None, description='Тип вопроса: text, choice, multiple_choice')
    options: str | None = Field(None, description='JSON строка с вариантами ответов для choice типов')
    difficulty: str | None = Field(None, description='Уровень сложности: easy, medium, hard')
    vacancy_id: uuid.UUID | None = Field(None, description='ID вакансии, к которой привязан вопрос')


class QuestionRead(QuestionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

