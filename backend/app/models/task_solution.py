"""Модель для хранения решений задач пользователями"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TaskSolution(Base):
    """Решение задачи пользователем"""
    __tablename__ = 'task_solutions'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False
    )
    vacancy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('vacancies.id', ondelete='SET NULL'), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default='attempted'
    )  # attempted, solved
    verdict: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # ACCEPTED, WRONG ANSWER, TIME LIMIT EXCEEDED, etc.
    solution_code: Mapped[str] = mapped_column(Text, nullable=False)  # Код решения
    language: Mapped[str] = mapped_column(String(50), nullable=False)  # python, typescript, go, java
    test_results: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )  # Результаты тестов
    execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('executions.id', ondelete='SET NULL'), nullable=True
    )  # Связь с execution для отслеживания
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped['User'] = relationship(back_populates='task_solutions')
    task: Mapped['Task'] = relationship(back_populates='solutions')
    vacancy: Mapped['Vacancy | None'] = relationship()
    execution: Mapped['Execution | None'] = relationship()

