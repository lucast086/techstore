"""merge multiple heads

Revision ID: 74f19d95e808
Revises: 3fa1191cd4d7, e190c34b6a04
Create Date: 2025-11-25 05:34:47.832962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74f19d95e808'
down_revision: Union[str, Sequence[str], None] = ('3fa1191cd4d7', 'e190c34b6a04')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
