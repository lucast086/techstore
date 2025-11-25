"""Test partial cash payment creates proper debt."""

import logging
from decimal import Decimal

import pytest
from app.crud.customer_account import customer_account_crud
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.product import Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleItemCreate
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@pytest.fixture
def test_product(db_session: Session) -> Product:
    """Create a test product."""
    from app.models.product import Category

    # Create category
    category = Category(
        name="Electronics",
        description="Electronic items",
        is_active=True,
    )
    db_session.add(category)
    db_session.flush()

    # Create product
    product = Product(
        sku="TEST-001",
        name="Test Product",
        category_id=category.id,
        first_sale_price=Decimal("3000.00"),
        second_sale_price=Decimal("3000.00"),
        third_sale_price=Decimal("3000.00"),
        purchase_price=Decimal("2000.00"),
        current_stock=100,
        minimum_stock=0,
        tax_rate=Decimal("0.00"),
        is_service=False,
        is_active=True,
        created_by=1,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


def test_partial_cash_payment_records_debt(
    db_session: Session,
    test_customer: Customer,
    test_user: User,
    test_product: Product,
):
    """Test that partial cash payment correctly records debt to customer account.

    Scenario:
    - Product costs $3000
    - Customer pays $1000 cash
    - Expected: $2000 debt added to customer account
    """
    # Arrange: Open cash register
    from app.crud.cash_closing import cash_closing
    from app.utils.timezone import get_local_today

    cash_closing.open_cash_register(
        db=db_session,
        target_date=get_local_today(),
        opening_balance=Decimal("100.00"),
        opened_by=test_user.id,
    )

    # Get initial customer balance
    initial_account = customer_account_crud.get_or_create(
        db_session, test_customer.id, test_user.id
    )
    db_session.commit()
    initial_balance = initial_account.account_balance

    logger.info(f"Initial balance: ${initial_balance}")

    # Act: Create sale with partial payment
    sale_data = SaleCreate(
        customer_id=test_customer.id,
        payment_method="cash",
        discount_amount=Decimal("0.00"),
        amount_paid=Decimal("1000.00"),  # Partial payment
        notes="Test sale with partial payment",
        items=[
            SaleItemCreate(
                product_id=test_product.id,
                quantity=1,
                unit_price=Decimal("3000.00"),
                discount_percentage=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
            )
        ],
    )

    sale = sale_crud.create_sale(db=db_session, sale_in=sale_data, user_id=test_user.id)

    logger.info(f"Created sale {sale.invoice_number}")
    logger.info(f"Sale total: ${sale.total_amount}")
    logger.info(f"Sale paid_amount: ${sale.paid_amount}")
    logger.info(f"Sale payment_status: {sale.payment_status}")

    # Assert: Check that debt was recorded
    db_session.refresh(initial_account)
    final_balance = initial_account.account_balance

    # Get all transactions for this customer
    from app.models.customer_account import CustomerTransaction

    transactions = (
        db_session.query(CustomerTransaction)
        .filter(CustomerTransaction.customer_id == test_customer.id)
        .order_by(CustomerTransaction.transaction_date)
        .all()
    )

    logger.info(f"Final balance: ${final_balance}")
    logger.info(f"Balance change: ${final_balance - initial_balance}")
    logger.info(f"Number of transactions: {len(transactions)}")
    for i, txn in enumerate(transactions):
        logger.info(
            f"Transaction {i+1}: {txn.transaction_type} - "
            f"Amount: ${txn.amount}, "
            f"Balance: ${txn.balance_before} -> ${txn.balance_after}"
        )

    # Expected: $2000 debt added (positive balance)
    expected_debt = Decimal("2000.00")
    actual_balance_change = final_balance - initial_balance

    assert sale.total_amount == Decimal(
        "3000.00"
    ), f"Sale total should be $3000, got ${sale.total_amount}"
    assert sale.paid_amount == Decimal(
        "1000.00"
    ), f"Sale paid_amount should be $1000, got ${sale.paid_amount}"
    assert (
        sale.payment_status == "partial"
    ), f"Payment status should be 'partial', got '{sale.payment_status}'"
    assert actual_balance_change == expected_debt, (
        f"Expected ${expected_debt} debt added to account, "
        f"but balance only changed by ${actual_balance_change}"
    )
    assert initial_account.has_debt, "Customer should have debt after partial payment"


def test_full_cash_payment_no_debt(
    db_session: Session,
    test_customer: Customer,
    test_user: User,
    test_product: Product,
):
    """Test that full cash payment does NOT create debt transaction."""
    # Arrange: Open cash register
    from app.crud.cash_closing import cash_closing
    from app.utils.timezone import get_local_today

    cash_closing.open_cash_register(
        db=db_session,
        target_date=get_local_today(),
        opening_balance=Decimal("100.00"),
        opened_by=test_user.id,
    )

    # Get initial customer balance
    initial_account = customer_account_crud.get_or_create(
        db_session, test_customer.id, test_user.id
    )
    db_session.commit()
    initial_balance = initial_account.account_balance

    # Act: Create sale with full payment
    sale_data = SaleCreate(
        customer_id=test_customer.id,
        payment_method="cash",
        discount_amount=Decimal("0.00"),
        amount_paid=Decimal("3000.00"),  # Full payment
        notes="Test sale with full payment",
        items=[
            SaleItemCreate(
                product_id=test_product.id,
                quantity=1,
                unit_price=Decimal("3000.00"),
                discount_percentage=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
            )
        ],
    )

    _ = sale_crud.create_sale(db=db_session, sale_in=sale_data, user_id=test_user.id)

    # Assert: Check that NO debt was recorded (but payment WAS recorded)
    db_session.refresh(initial_account)
    final_balance = initial_account.account_balance

    # With full payment: +$3000 from sale, -$3000 from payment = $0 change
    assert final_balance == initial_balance, (
        f"Balance should not change with full payment. "
        f"Initial: ${initial_balance}, Final: ${final_balance}"
    )
