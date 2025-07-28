"""Initial empty migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-07-28 03:04:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Initial migration - no tables yet."""
    pass


def downgrade() -> None:
    """Nothing to downgrade."""
    pass