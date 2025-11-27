"""Модель для отслеживания использования подсказок пользователями"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class HintUsage(Base):
    """Использование подсказки пользователем"""
    __tablename__ = 'hint_usages'

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
    hint_level: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # surface, medium, deep
    penalty: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # Штраф в баллах (5.0, 15.0, 30.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped['User'] = relationship(back_populates='hint_usages')
    task: Mapped['Task'] = relationship(back_populates='hint_usages')
    vacancy: Mapped['Vacancy | None'] = relationship()

