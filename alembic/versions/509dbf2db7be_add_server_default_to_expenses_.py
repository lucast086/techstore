"""add_server_default_to_expenses_timestamps

Revision ID: 509dbf2db7be
Revises: 2e2748d14e19
Create Date: 2025-12-03 15:54:31.446808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '509dbf2db7be'
down_revision: Union[str, Sequence[str], None] = '2e2748d14e19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'expenses',
        'created_at',
        server_default=sa.func.now(),
        existing_type=sa.DateTime(),
        existing_nullable=False
    )
    op.alter_column(
        'expenses',
        'updated_at',
        server_default=sa.func.now(),
        existing_type=sa.DateTime(),
        existing_nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'expenses',
        'created_at',
        server_default=None,
        existing_type=sa.DateTime(),
        existing_nullable=False
    )
    op.alter_column(
        'expenses',
        'updated_at',
        server_default=None,
        existing_type=sa.DateTime(),
        existing_nullable=False
    )
