"""Merge heads before upgrade

Revision ID: b3b17c96f189
Revises: 2025010101, f8a04c6b0d55
Create Date: 2025-11-27 14:25:49.301483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3b17c96f189'
down_revision: Union[str, None] = ('2025010101', 'f8a04c6b0d55')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
