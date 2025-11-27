"""Модель для хранения метрик решенных задач"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .task_solution import TaskSolution


class TaskMetric(Base):
    __tablename__ = 'task_metrics'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_solution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('task_solutions.id', ondelete='CASCADE'),
        unique=True,
        nullable=False,
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
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    verdict: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tests_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tests_passed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    average_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    solution: Mapped['TaskSolution'] = relationship(back_populates='metric')


