"""fix_customer_transactions_created_at_default

Revision ID: 2f6b7ca83c23
Revises: cdf3f4a27197
Create Date: 2025-10-11 20:49:42.171199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f6b7ca83c23'
down_revision: Union[str, Sequence[str], None] = 'cdf3f4a27197'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add default value to created_at column
    op.execute("""
        ALTER TABLE customer_transactions
        ALTER COLUMN created_at SET DEFAULT now()
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove default value from created_at column
    op.execute("""
        ALTER TABLE customer_transactions
        ALTER COLUMN created_at DROP DEFAULT
    """)
