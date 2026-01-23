"""add_payment_breakdown_columns

Revision ID: b2c3d4e5f6a7
Revises: 739832c39d62
Create Date: 2026-01-23

This migration adds breakdown columns to the payments table for mixed payments.
These columns store the individual amounts for each payment method when a payment
uses multiple methods (e.g., cash + transfer).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = '739832c39d62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add breakdown columns for mixed payments."""
    op.add_column(
        'payments',
        sa.Column('cash_amount', sa.Numeric(precision=10, scale=2), nullable=True)
    )
    op.add_column(
        'payments',
        sa.Column('transfer_amount', sa.Numeric(precision=10, scale=2), nullable=True)
    )
    op.add_column(
        'payments',
        sa.Column('card_amount', sa.Numeric(precision=10, scale=2), nullable=True)
    )


def downgrade() -> None:
    """Remove breakdown columns."""
    op.drop_column('payments', 'card_amount')
    op.drop_column('payments', 'transfer_amount')
    op.drop_column('payments', 'cash_amount')
