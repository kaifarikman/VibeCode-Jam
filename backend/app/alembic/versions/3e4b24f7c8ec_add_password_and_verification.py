"""add password hash and verification flags

Revision ID: 3e4b24f7c8ec
Revises: 6a7c625306ad
Create Date: 2025-11-26 02:30:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3e4b24f7c8ec'
down_revision: Union[str, None] = '6a7c625306ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('password_hash', sa.String(length=255), nullable=False, server_default=''),
    )
    op.add_column(
        'users',
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'password_hash')

