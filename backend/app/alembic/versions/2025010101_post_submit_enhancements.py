"""Add ML evaluation fields and task communications table

Revision ID: 2025010101
Revises: add_canonical_solution_to_tasks
Create Date: 2025-01-01 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2025010101'
down_revision: Union[str, None] = 'add_canonical_solution_to_tasks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('task_solutions', sa.Column('ml_correctness', sa.Float(), nullable=True))
    op.add_column('task_solutions', sa.Column('ml_efficiency', sa.Float(), nullable=True))
    op.add_column('task_solutions', sa.Column('ml_clean_code', sa.Float(), nullable=True))
    op.add_column('task_solutions', sa.Column('ml_feedback', sa.Text(), nullable=True))
    op.add_column('task_solutions', sa.Column('ml_passed', sa.Boolean(), nullable=True))
    op.add_column('task_solutions', sa.Column('anti_cheat_flag', sa.Boolean(), nullable=True))
    op.add_column('task_solutions', sa.Column('anti_cheat_reason', sa.Text(), nullable=True))

    op.add_column('user_contest_tasks', sa.Column('next_difficulty', sa.String(length=20), nullable=True))
    op.add_column('user_contest_tasks', sa.Column('next_reason', sa.Text(), nullable=True))

    op.create_table(
        'task_communications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vacancy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vacancies.id', ondelete='SET NULL'), nullable=True),
        sa.Column('solution_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('task_solutions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('ml_score', sa.Float(), nullable=True),
        sa.Column('ml_feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_task_communications_user_id', 'task_communications', ['user_id'])
    op.create_index('ix_task_communications_task_id', 'task_communications', ['task_id'])
    op.create_index('ix_task_communications_vacancy_id', 'task_communications', ['vacancy_id'])
    op.create_index('ix_task_communications_solution_id', 'task_communications', ['solution_id'])


def downgrade() -> None:
    op.drop_index('ix_task_communications_solution_id', table_name='task_communications')
    op.drop_index('ix_task_communications_vacancy_id', table_name='task_communications')
    op.drop_index('ix_task_communications_task_id', table_name='task_communications')
    op.drop_index('ix_task_communications_user_id', table_name='task_communications')
    op.drop_table('task_communications')

    op.drop_column('user_contest_tasks', 'next_reason')
    op.drop_column('user_contest_tasks', 'next_difficulty')

    op.drop_column('task_solutions', 'anti_cheat_reason')
    op.drop_column('task_solutions', 'anti_cheat_flag')
    op.drop_column('task_solutions', 'ml_passed')
    op.drop_column('task_solutions', 'ml_feedback')
    op.drop_column('task_solutions', 'ml_clean_code')
    op.drop_column('task_solutions', 'ml_efficiency')
    op.drop_column('task_solutions', 'ml_correctness')

