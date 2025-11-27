import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Execution(Base):
    __tablename__ = 'executions'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    language: Mapped[str] = mapped_column(String(50), nullable=False)  # python, typescript, go, java
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default='pending'
    )  # pending, running, completed, failed
    files: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)  # {path: content}
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)  # stdout, stderr, exit_code, duration_ms
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True
    )
    vacancy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('vacancies.id', ondelete='SET NULL'), nullable=True
    )
    is_submit: Mapped[bool] = mapped_column(default=False)  # True если это Submit, False если Run
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped['User'] = relationship(back_populates='executions')

