"""Модель для хранения коммуникации после сдачи задачи"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Float, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TaskCommunication(Base):
    __tablename__ = 'task_communications'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False, index=True
    )
    vacancy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('vacancies.id', ondelete='SET NULL'), nullable=True, index=True
    )
    solution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('task_solutions.id', ondelete='CASCADE'), nullable=False, index=True
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    ml_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ml_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    solution: Mapped['TaskSolution'] = relationship(back_populates='communications')
    user: Mapped['User'] = relationship()
    task: Mapped['Task'] = relationship()
    vacancy: Mapped['Vacancy | None'] = relationship()


