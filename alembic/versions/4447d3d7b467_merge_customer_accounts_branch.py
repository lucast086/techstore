"""Merge customer accounts branch

Revision ID: 4447d3d7b467
Revises: add_customer_accounts, db1b8739bca5
Create Date: 2025-09-27 23:00:51.994302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4447d3d7b467'
down_revision: Union[str, Sequence[str], None] = ('add_customer_accounts', 'db1b8739bca5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
