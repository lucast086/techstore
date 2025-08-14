"""Update PaymentType enum values

Revision ID: f2a1d59e94ef
Revises: 08e1703b528d
Create Date: 2025-08-13 19:29:32.791449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a1d59e94ef'
down_revision: Union[str, Sequence[str], None] = '08e1703b528d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create new enum type with all values
    op.execute("CREATE TYPE paymenttype_new AS ENUM ('payment', 'advance_payment', 'credit_application', 'refund')")

    # Update the column to use the new enum with explicit mapping
    op.execute("""
        ALTER TABLE payments
        ALTER COLUMN payment_type TYPE paymenttype_new
        USING CASE
            WHEN payment_type::text = 'PAYMENT' THEN 'payment'::paymenttype_new
            WHEN payment_type::text = 'ADVANCE_PAYMENT' THEN 'advance_payment'::paymenttype_new
            WHEN payment_type::text = 'CREDIT_APPLICATION' THEN 'credit_application'::paymenttype_new
            WHEN payment_type::text = 'REFUND' THEN 'refund'::paymenttype_new
            ELSE 'payment'::paymenttype_new
        END
    """)

    # Drop the old enum and rename the new one
    op.execute("DROP TYPE paymenttype")
    op.execute("ALTER TYPE paymenttype_new RENAME TO paymenttype")


def downgrade() -> None:
    """Downgrade schema."""
    # Create the old enum type
    op.execute("CREATE TYPE paymenttype_old AS ENUM ('advance_payment', 'credit_application', 'refund')")

    # Update existing 'payment' values to 'advance_payment' before conversion
    op.execute("UPDATE payments SET payment_type = 'advance_payment' WHERE payment_type = 'payment'")

    # Update the column to use the old enum
    op.execute("ALTER TABLE payments ALTER COLUMN payment_type TYPE paymenttype_old USING payment_type::text::paymenttype_old")

    # Drop the new enum and rename the old one
    op.execute("DROP TYPE paymenttype")
    op.execute("ALTER TYPE paymenttype_old RENAME TO paymenttype")
