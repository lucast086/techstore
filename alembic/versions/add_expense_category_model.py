"""Add ExpenseCategory model

Revision ID: add_expense_category
Revises: 80d29f127897
Create Date: 2025-08-02 15:54:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_expense_category'
down_revision: Union[str, Sequence[str], None] = '80d29f127897'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create expense_categories table
    op.create_table(
        'expense_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_expense_categories_id'), 'expense_categories', ['id'], unique=False)

    # Insert default categories
    op.execute("""
        INSERT INTO expense_categories (name, description, is_active, created_at, updated_at)
        VALUES
            ('General', 'General expenses', true, NOW(), NOW()),
            ('Suppliers', 'Payments to suppliers', true, NOW(), NOW()),
            ('Utilities', 'Electricity, water, internet, etc.', true, NOW(), NOW()),
            ('Salaries', 'Employee salaries and benefits', true, NOW(), NOW()),
            ('Maintenance', 'Equipment and facility maintenance', true, NOW(), NOW()),
            ('Marketing', 'Advertising and marketing expenses', true, NOW(), NOW())
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_expense_categories_id'), table_name='expense_categories')
    op.drop_table('expense_categories')
