"""Add task metrics table

Revision ID: 2025010201
Revises: 2025010101
Create Date: 2025-01-02 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2025010201'
down_revision: Union[str, None] = '2025010101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'task_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('task_solution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('task_solutions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vacancy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vacancies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('verdict', sa.String(length=50), nullable=True),
        sa.Column('tests_total', sa.Integer(), nullable=True),
        sa.Column('tests_passed', sa.Integer(), nullable=True),
        sa.Column('total_duration_ms', sa.Integer(), nullable=True),
        sa.Column('average_duration_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_task_metrics_task_solution_id', 'task_metrics', ['task_solution_id'], unique=True)
    op.create_index('ix_task_metrics_user_id', 'task_metrics', ['user_id'])
    op.create_index('ix_task_metrics_task_id', 'task_metrics', ['task_id'])
    op.create_index('ix_task_metrics_vacancy_id', 'task_metrics', ['vacancy_id'])


def downgrade() -> None:
    op.drop_index('ix_task_metrics_vacancy_id', table_name='task_metrics')
    op.drop_index('ix_task_metrics_task_id', table_name='task_metrics')
    op.drop_index('ix_task_metrics_user_id', table_name='task_metrics')
    op.drop_index('ix_task_metrics_task_solution_id', table_name='task_metrics')
    op.drop_table('task_metrics')

