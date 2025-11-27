"""add_hints_and_hint_usages

Revision ID: add_hints_hint_usages
Revises: 51a5f45afcb4
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_hints_hint_usages'
down_revision: Union[str, None] = '51a5f45afcb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поле hints в таблицу tasks
    op.add_column('tasks', sa.Column('hints', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Создаем таблицу hint_usages
    op.create_table(
        'hint_usages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vacancy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('hint_level', sa.String(length=20), nullable=False),
        sa.Column('penalty', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vacancy_id'], ['vacancies.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Удаляем таблицу hint_usages
    op.drop_table('hint_usages')
    
    # Удаляем поле hints из таблицы tasks
    op.drop_column('tasks', 'hints')

