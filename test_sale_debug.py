"""Debug script to check sale and payment data."""

from decimal import Decimal

from app.database import SessionLocal
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.sale import Sale
from app.services.balance_service import balance_service

db = SessionLocal()

# Check a recent sale
recent_sale = (
    db.query(Sale).filter(Sale.customer_id.isnot(None)).order_by(Sale.id.desc()).first()
)
if recent_sale:
    print(f"Sale ID: {recent_sale.id}")
    print(f"Invoice: {recent_sale.invoice_number}")
    print(f"Customer ID: {recent_sale.customer_id}")
    print(f"Total Amount: ${recent_sale.total_amount}")
    print(f"Payment Status: {recent_sale.payment_status}")
    print(f"Payment Method: {recent_sale.payment_method}")

    # Check payments for this sale
    payments = db.query(Payment).filter(Payment.sale_id == recent_sale.id).all()
    print("\nPayments for this sale:")
    total_payments = Decimal("0")
    for p in payments:
        print(f"  - Payment {p.id}: ${p.amount}")
        total_payments += p.amount

    print(f"\nTotal payments for this sale: ${total_payments}")

    # Calculate amount_paid from property
    print(f"Calculated amount_paid (from property): ${recent_sale.amount_paid}")
    print(f"Calculated amount_due (from property): ${recent_sale.amount_due}")

    # Check customer balance
    if recent_sale.customer_id:
        customer = (
            db.query(Customer).filter(Customer.id == recent_sale.customer_id).first()
        )
        if customer:
            print(f"\nCustomer: {customer.name}")
            balance = balance_service.calculate_balance(db, customer.id)
            print(f"Customer Balance: ${balance}")

            # Get all sales for this customer
            all_sales = (
                db.query(Sale)
                .filter(Sale.customer_id == customer.id, Sale.is_voided.is_(False))
                .all()
            )

            total_sales_amount = sum(s.total_amount for s in all_sales)
            print(f"Total Sales for Customer: ${total_sales_amount}")

            # Get all payments for this customer
            all_payments = (
                db.query(Payment)
                .filter(Payment.customer_id == customer.id, Payment.voided.is_(False))
                .all()
            )

            total_payments_amount = sum(p.amount for p in all_payments)
            print(f"Total Payments by Customer: ${total_payments_amount}")

            print(f"\nExpected Balance: ${total_payments_amount - total_sales_amount}")
else:
    print("No sales found")

db.close()
