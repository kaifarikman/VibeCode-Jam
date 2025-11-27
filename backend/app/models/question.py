import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    order: Mapped[int] = mapped_column(default=0)  # Порядок отображения
    question_type: Mapped[str] = mapped_column(
        String(50), default='text'
    )  # text, choice, multiple_choice, etc.
    options: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON строка с вариантами ответов для choice типов
    difficulty: Mapped[str] = mapped_column(
        String(20), default='medium'
    )  # easy, medium, hard - уровень сложности задачи
    vacancy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('vacancies.id', ondelete='SET NULL'), nullable=True
    )  # Привязка к вакансии
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    answers: Mapped[list['Answer']] = relationship(
        back_populates='question', cascade='all, delete-orphan'
    )
    vacancy: Mapped['Vacancy | None'] = relationship(back_populates='questions')


class Answer(Base):
    __tablename__ = 'answers'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('questions.id', ondelete='CASCADE'), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped['User'] = relationship(back_populates='answers')
    question: Mapped['Question'] = relationship(back_populates='answers')

