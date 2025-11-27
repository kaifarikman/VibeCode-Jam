"""Модель для привязки задач контеста к пользователю"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserContestTasks(Base):
    """Привязка задач контеста к пользователю для конкретной вакансии"""
    __tablename__ = 'user_contest_tasks'
    __table_args__ = (
        UniqueConstraint('user_id', 'vacancy_id', name='uq_user_vacancy_contest_tasks'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('vacancies.id', ondelete='CASCADE'), nullable=False, index=True
    )
    task_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=False
    )  # Массив ID задач (3 задачи)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped['User'] = relationship(back_populates='contest_tasks')
    vacancy: Mapped['Vacancy'] = relationship(back_populates='user_contest_tasks')

