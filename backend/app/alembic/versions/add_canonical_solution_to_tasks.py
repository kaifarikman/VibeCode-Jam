"""add canonical solution to tasks

Revision ID: add_canonical_solution_to_tasks
Revises: add_hints_hint_usages
Create Date: 2025-??-?? ???

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_canonical_solution_to_tasks'
down_revision: Union[str, None] = 'add_hints_hint_usages'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('canonical_solution', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'canonical_solution')

