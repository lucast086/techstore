"""Add customer accounts and transactions tables

Revision ID: add_customer_accounts
Revises: f2a1d59e94ef
Create Date: 2025-09-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_customer_accounts'
down_revision = 'f2a1d59e94ef'
branch_labels = None
depends_on = None


def upgrade():
    # Create transaction type enum (only if it doesn't exist)
    transaction_type = postgresql.ENUM(
        'sale', 'payment', 'credit_note', 'debit_note',
        'credit_application', 'opening_balance', 'adjustment',
        name='transactiontype',
        create_type=False
    )

    # Check if enum already exists
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transactiontype');"
    ))
    enum_exists = result.scalar()

    if not enum_exists:
        transaction_type.create(conn, checkfirst=True)

    # Create customer_accounts table
    op.create_table('customer_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('credit_limit', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('available_credit', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('account_balance', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('total_sales', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_payments', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_credit_notes', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_debit_notes', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('last_transaction_date', sa.DateTime(), nullable=True),
        sa.Column('last_payment_date', sa.DateTime(), nullable=True),
        sa.Column('transaction_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('blocked_until', sa.DateTime(), nullable=True),
        sa.Column('block_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_id')
    )
    op.create_index('idx_customer_account_activity', 'customer_accounts', ['last_transaction_date', 'is_active'], unique=False)
    op.create_index('idx_customer_account_balance', 'customer_accounts', ['account_balance', 'is_active'], unique=False)
    op.create_index(op.f('ix_customer_accounts_id'), 'customer_accounts', ['id'], unique=False)

    # Create customer_transactions table
    op.create_table('customer_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.Enum('sale', 'payment', 'credit_note', 'debit_note', 'credit_application', 'opening_balance', 'adjustment', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('balance_before', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('balance_after', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('transaction_date', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['account_id'], ['customer_accounts.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id', 'created_at', name='uq_transaction_immutable')
    )
    op.create_index('idx_customer_trans_date', 'customer_transactions', ['customer_id', 'transaction_date'], unique=False)
    op.create_index('idx_customer_trans_ref', 'customer_transactions', ['reference_type', 'reference_id'], unique=False)
    op.create_index('idx_customer_trans_type', 'customer_transactions', ['customer_id', 'transaction_type'], unique=False)
    op.create_index(op.f('ix_customer_transactions_customer_id'), 'customer_transactions', ['customer_id'], unique=False)
    op.create_index(op.f('ix_customer_transactions_id'), 'customer_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_customer_transactions_transaction_date'), 'customer_transactions', ['transaction_date'], unique=False)
    op.create_index(op.f('ix_customer_transactions_transaction_type'), 'customer_transactions', ['transaction_type'], unique=False)

    # Create trigger to update customer_accounts.updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';

        CREATE TRIGGER update_customer_accounts_updated_at BEFORE UPDATE
        ON customer_accounts FOR EACH ROW EXECUTE PROCEDURE
        update_updated_at_column();
    """)


def downgrade():
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_customer_accounts_updated_at ON customer_accounts;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop tables
    op.drop_index(op.f('ix_customer_transactions_transaction_type'), table_name='customer_transactions')
    op.drop_index(op.f('ix_customer_transactions_transaction_date'), table_name='customer_transactions')
    op.drop_index(op.f('ix_customer_transactions_id'), table_name='customer_transactions')
    op.drop_index(op.f('ix_customer_transactions_customer_id'), table_name='customer_transactions')
    op.drop_index('idx_customer_trans_type', table_name='customer_transactions')
    op.drop_index('idx_customer_trans_ref', table_name='customer_transactions')
    op.drop_index('idx_customer_trans_date', table_name='customer_transactions')
    op.drop_table('customer_transactions')

    op.drop_index(op.f('ix_customer_accounts_id'), table_name='customer_accounts')
    op.drop_index('idx_customer_account_balance', table_name='customer_accounts')
    op.drop_index('idx_customer_account_activity', table_name='customer_accounts')
    op.drop_table('customer_accounts')

    # Drop enum
    sa.Enum(name='transactiontype').drop(op.get_bind())
