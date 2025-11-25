"""Simple test to verify credit payment functionality."""

from decimal import Decimal

from app.crud.sale import sale_crud
from app.schemas.sale import SaleCreate, SaleItemCreate
from sqlalchemy.orm import Session


def test_credit_payment_working(db_session: Session, test_user, test_customer):
    """Test that credit payment now works correctly."""
    # First, give customer some credit by creating a payment
    from app.models.payment import Payment, PaymentType
    from app.services.customer_account_service import CustomerAccountService

    # Create advance payment to give customer credit
    advance_payment = Payment(
        customer_id=test_customer.id,
        amount=Decimal("500.00"),
        payment_method="cash",
        payment_type=PaymentType.advance_payment.value,
        receipt_number="ADV-001",
        received_by_id=test_user.id,
        notes="Advance payment for credit",
    )
    db_session.add(advance_payment)
    db_session.flush()

    # Record the advance payment in account system
    account_service = CustomerAccountService()
    account_service.record_payment(db_session, advance_payment, test_user.id)

    # Check initial balance (should be -500, negative means credit)
    account = account_service.get_or_create_account(
        db_session, test_customer.id, test_user.id
    )
    print(f"Initial balance after advance payment: {account.account_balance}")
    assert account.account_balance == Decimal("-500.00")

    # Create a product for testing
    from app.models.product import Category as ProductCategory
    from app.models.product import Product

    category = ProductCategory(name="Test Category")
    db_session.add(category)
    db_session.flush()

    product = Product(
        sku="TEST001",
        name="Test Product",
        category_id=category.id,
        purchase_price=Decimal("50.00"),
        first_sale_price=Decimal("100.00"),
        second_sale_price=Decimal("100.00"),
        third_sale_price=Decimal("100.00"),
        current_stock=10,
        tax_rate=Decimal("10.00"),
        created_by=test_user.id,
    )
    db_session.add(product)
    db_session.flush()

    # Open cash register for today
    from app.services.cash_closing_service import cash_closing_service
    from app.utils.timezone import get_local_today

    cash_closing_service.open_cash_register(
        db=db_session,
        user_id=test_user.id,
        opening_balance=Decimal("100.00"),
        opening_date=get_local_today(),
    )

    # Create sale using credit
    sale_data = SaleCreate(
        customer_id=test_customer.id,
        payment_method="account_credit",
        discount_amount=Decimal("0.00"),
        notes="Credit payment test",
        items=[
            SaleItemCreate(
                product_id=product.id,
                quantity=1,
                unit_price=Decimal("200.00"),  # $200 + 10% tax = $220
                discount_percentage=Decimal("0.00"),
                discount_amount=Decimal("0.00"),
            )
        ],
        amount_paid=Decimal("220.00"),
    )

    # Create the sale
    sale = sale_crud.create_sale(db=db_session, sale_in=sale_data, user_id=test_user.id)

    # Verify sale
    assert sale.total_amount == Decimal("220.00")
    assert sale.payment_status == "paid"
    assert sale.payment_method == "account_credit"

    # Check final balance
    # Should be: -$500 (credit) + $220 (sale) = -$280 (remaining credit)
    db_session.refresh(account)
    print(f"Final balance after sale: {account.account_balance}")
    assert account.account_balance == Decimal("-280.00")

    print("✓ Credit payment working correctly!")
    print("  - Customer had $500 credit")
    print("  - Used $220 for purchase")
    print("  - Remaining credit: $280")
