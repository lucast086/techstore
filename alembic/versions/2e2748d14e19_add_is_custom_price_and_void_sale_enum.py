"""add_is_custom_price_and_void_sale_enum

Revision ID: 2e2748d14e19
Revises: fix_sales_cols
Create Date: 2025-11-26 03:11:30.820936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e2748d14e19'
down_revision: Union[str, Sequence[str], None] = 'fix_sales_cols'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add void_sale to transactiontype enum
    op.execute("ALTER TYPE transactiontype ADD VALUE IF NOT EXISTS 'void_sale'")

    # Add is_custom_price column to sale_items
    op.add_column(
        "sale_items",
        sa.Column("is_custom_price", sa.Boolean(), nullable=True, server_default="false"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove is_custom_price column
    op.drop_column("sale_items", "is_custom_price")

    # Note: Cannot remove enum values in PostgreSQL without recreating the type
