"""Add Expense model

Revision ID: add_expense_model
Revises: add_expense_category
Create Date: 2025-08-02 16:15:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_expense_model'
down_revision: Union[str, Sequence[str], None] = 'add_expense_category'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create expenses table
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('receipt_number', sa.String(100), nullable=True),
        sa.Column('supplier_name', sa.String(200), nullable=True),
        sa.Column('receipt_file_path', sa.String(500), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('is_editable', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['expense_categories.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expenses_id'), 'expenses', ['id'], unique=False)
    op.create_index('ix_expenses_expense_date', 'expenses', ['expense_date'], unique=False)
    op.create_index('ix_expenses_category_id', 'expenses', ['category_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_expenses_category_id', table_name='expenses')
    op.drop_index('ix_expenses_expense_date', table_name='expenses')
    op.drop_index(op.f('ix_expenses_id'), table_name='expenses')
    op.drop_table('expenses')
