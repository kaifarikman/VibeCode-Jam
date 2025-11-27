"""merge heads add canonical solution and moderators

Revision ID: f8a04c6b0d55
Revises: add_canonical_solution_to_tasks, add_moderators_table
Create Date: 2025-??-?? ???

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8a04c6b0d55'
down_revision: Union[str, Sequence[str], None] = (
    'add_canonical_solution_to_tasks',
    'add_moderators_table',
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

