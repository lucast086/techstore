"""Fix transactiontype enum case to lowercase

This migration converts enum values from UPPERCASE to lowercase
to match the Python enum values defined in TransactionType.

Revision ID: fix_enum_case_001
Revises: 509dbf2db7be
Create Date: 2025-12-03

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "fix_enum_case_001"
down_revision = "509dbf2db7be"
branch_labels = None
depends_on = None


def upgrade():
    """Convert transactiontype enum values to lowercase."""
    conn = op.get_bind()

    # Check current enum values
    result = conn.execute(
        text("SELECT unnest(enum_range(NULL::transactiontype))::text AS val")
    )
    current_values = [row[0] for row in result]

    # If values are already lowercase, skip
    if all(v.islower() or v == 'void_sale' for v in current_values):
        print("Enum values are already lowercase, skipping migration")
        return

    # PostgreSQL doesn't allow direct rename of enum values in older versions
    # We need to: 1) Create new enum, 2) Update columns, 3) Drop old enum, 4) Rename new

    # Step 1: Create new enum with lowercase values
    op.execute("""
        CREATE TYPE transactiontype_new AS ENUM (
            'sale', 'payment', 'credit_note', 'debit_note',
            'credit_application', 'opening_balance', 'adjustment',
            'repair_deposit', 'void_sale'
        )
    """)

    # Step 2: Update the column to use the new enum
    # First, we need to alter the column to text, then back to enum
    op.execute("""
        ALTER TABLE customer_transactions
        ALTER COLUMN transaction_type TYPE text
    """)

    # Step 3: Convert uppercase values to lowercase
    op.execute("""
        UPDATE customer_transactions
        SET transaction_type = LOWER(transaction_type)
    """)

    # Step 4: Convert column to new enum type
    op.execute("""
        ALTER TABLE customer_transactions
        ALTER COLUMN transaction_type TYPE transactiontype_new
        USING transaction_type::transactiontype_new
    """)

    # Step 5: Drop old enum and rename new one
    op.execute("DROP TYPE transactiontype")
    op.execute("ALTER TYPE transactiontype_new RENAME TO transactiontype")


def downgrade():
    """Convert back to uppercase (not recommended)."""
    # This is a one-way migration - don't downgrade
    pass
