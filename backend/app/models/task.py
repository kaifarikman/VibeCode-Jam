"""Модель для алгоритмических задач (как на Codeforces)"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Task(Base):
    """Алгоритмическая задача с тестами"""
    __tablename__ = 'tasks'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)  # Название задачи
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Условие задачи
    topic: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # Тема/категория (массивы, строки, графы и т.д.)
    difficulty: Mapped[str] = mapped_column(
        String(20), default='medium'
    )  # easy, medium, hard - уровень сложности
    open_tests: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON массив открытых тестов [{input: "...", output: "..."}, ...]
    hidden_tests: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON массив закрытых тестов [{input: "...", output: "..."}, ...]
    vacancy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('vacancies.id', ondelete='SET NULL'), nullable=True
    )  # Привязка к вакансии (опционально)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    vacancy: Mapped['Vacancy | None'] = relationship(back_populates='tasks')
    solutions: Mapped[list['TaskSolution']] = relationship(back_populates='task')

