"""Add performance indexes for repair deposits

Revision ID: 21c7a72117d8
Revises: ab0541798b68
Create Date: 2025-09-28 20:22:03.060538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21c7a72117d8'
down_revision: Union[str, Sequence[str], None] = 'ab0541798b68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add composite indexes for common queries
    op.create_index("ix_repair_deposits_repair_id_status", "repair_deposits", ["repair_id", "status"])
    op.create_index("ix_repair_deposits_customer_id_status", "repair_deposits", ["customer_id", "status"])
    op.create_index("ix_repair_deposits_sale_id", "repair_deposits", ["sale_id"])

    # Add indexes for repairs queries
    op.create_index("ix_repairs_customer_id_status", "repairs", ["customer_id", "status"])
    op.create_index("ix_repairs_created_at", "repairs", ["created_at"])

    # Add indexes for customer transactions
    op.create_index("ix_customer_transactions_customer_id_type", "customer_transactions", ["customer_id", "transaction_type"])
    op.create_index("ix_customer_transactions_created_at", "customer_transactions", ["created_at"])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove indexes
    op.drop_index("ix_customer_transactions_created_at", table_name="customer_transactions")
    op.drop_index("ix_customer_transactions_customer_id_type", table_name="customer_transactions")
    op.drop_index("ix_repairs_created_at", table_name="repairs")
    op.drop_index("ix_repairs_customer_id_status", table_name="repairs")
    op.drop_index("ix_repair_deposits_sale_id", table_name="repair_deposits")
    op.drop_index("ix_repair_deposits_customer_id_status", table_name="repair_deposits")
    op.drop_index("ix_repair_deposits_repair_id_status", table_name="repair_deposits")
