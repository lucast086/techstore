"""Add updated_at column to customer_transactions table

Revision ID: add_updated_at_trans
Revises: restore_cash_closing_columns
Create Date: 2025-11-25

This migration adds the missing updated_at column to customer_transactions table.
The model inherits from BaseModel which includes TimestampMixin with updated_at,
but the original migration did not include this column.
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_updated_at_trans"
down_revision = "restore_cash_cols"
branch_labels = None
depends_on = None


def upgrade():
    """Add updated_at column to customer_transactions if it doesn't exist."""
    conn = op.get_bind()

    # Check if updated_at column already exists
    result = conn.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'customer_transactions'
                AND column_name = 'updated_at'
            );
            """
        )
    )
    column_exists = result.scalar()

    if not column_exists:
        op.add_column(
            "customer_transactions",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
                comment="Record last update timestamp",
            ),
        )

        # Set updated_at = created_at for existing records
        op.execute(
            """
            UPDATE customer_transactions
            SET updated_at = created_at
            WHERE updated_at IS NULL OR updated_at = now();
            """
        )


def downgrade():
    """Remove updated_at column from customer_transactions."""
    conn = op.get_bind()

    # Check if column exists before dropping
    result = conn.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'customer_transactions'
                AND column_name = 'updated_at'
            );
            """
        )
    )
    column_exists = result.scalar()

    if column_exists:
        op.drop_column("customer_transactions", "updated_at")
