"""Fix missing columns in sales table

Revision ID: fix_sales_cols
Revises: add_updated_at_trans
Create Date: 2025-11-25

This migration adds missing payment breakdown columns to sales table.
The original migration e190c34b6a04 may not have run properly in production.
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "fix_sales_cols"
down_revision = "add_updated_at_trans"
branch_labels = None
depends_on = None


def upgrade():
    """Add missing columns to sales table if they don't exist."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = [c["name"] for c in inspector.get_columns("sales")]

    columns_to_add = [
        ("cash_amount", "Cash payment amount"),
        ("transfer_amount", "Transfer payment amount"),
        ("card_amount", "Card payment amount"),
        ("credit_amount", "Credit payment amount"),
    ]

    for col_name, comment in columns_to_add:
        if col_name not in existing_cols:
            op.add_column(
                "sales",
                sa.Column(
                    col_name,
                    sa.DECIMAL(precision=10, scale=2),
                    nullable=True,
                    comment=comment,
                ),
            )


def downgrade():
    """Remove columns if needed."""
    pass
