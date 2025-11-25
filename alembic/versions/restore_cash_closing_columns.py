"""Restore cash_closings payment breakdown columns

Revision ID: restore_cash_cols
Revises: 74f19d95e808
Create Date: 2025-11-25

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

revision: str = "restore_cash_cols"
down_revision: Union[str, Sequence[str], None] = "74f19d95e808"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Re-add columns that were incorrectly dropped."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = [c["name"] for c in inspector.get_columns("cash_closings")]

    columns_to_add = [
        ("sales_cash", "Cash sales total"),
        ("sales_credit", "Credit sales total"),
        ("sales_transfer", "Transfer sales total"),
        ("sales_mixed", "Mixed payment sales total"),
        ("expenses_cash", "Cash expenses total"),
        ("expenses_transfer", "Transfer expenses total"),
        ("expenses_card", "Card expenses total"),
    ]

    for col_name, comment in columns_to_add:
        if col_name not in existing_cols:
            op.add_column(
                "cash_closings",
                sa.Column(
                    col_name,
                    sa.DECIMAL(precision=10, scale=2),
                    nullable=False,
                    server_default="0.00",
                    comment=comment,
                ),
            )


def downgrade() -> None:
    """Remove columns if needed."""
    pass
