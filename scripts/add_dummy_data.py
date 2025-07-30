#!/usr/bin/env python3
"""Add dummy data for testing all functionalities."""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up environment
os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/techstore_db"
)


def main():
    """Main function to add dummy data."""
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.customer import Customer
    from app.models.user import User
    from app.schemas.customer import CustomerCreate
    from app.schemas.payment import PaymentCreate
    from app.services.customer import customer_service
    from app.crud.payment import payment_crud

    def create_dummy_customers(db: Session, admin_user: User):
        """Create dummy customers with various states."""
        print("\n📝 Creating dummy customers...")

        customers_data = [
            {
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john.doe@example.com",
                "address": "123 Main St, Anytown, USA",
                "notes": "VIP customer - always pays on time",
            },
            {
                "name": "Jane Smith",
                "phone": "+1234567891",
                "phone_secondary": "+1234567892",
                "email": "jane.smith@example.com",
                "address": "456 Oak Ave, Springfield, USA",
                "notes": "Prefers email communication",
            },
            {
                "name": "Bob Johnson",
                "phone": "+1234567893",
                "email": "bob.johnson@example.com",
                "notes": "New customer - referred by John Doe",
            },
            {
                "name": "Alice Williams",
                "phone": "+1234567894",
                "phone_secondary": "+1234567895",
                "address": "789 Pine Rd, Metropolis, USA",
                "notes": "Corporate account - NET 30 terms",
            },
            {
                "name": "Charlie Brown",
                "phone": "+1234567896",
                "email": "charlie.brown@example.com",
                "notes": "Student discount applicable",
            },
            {
                "name": "Diana Prince",
                "phone": "+1234567897",
                "email": "diana.prince@example.com",
                "address": "321 Wonder Way, Paradise Island",
                "notes": "Premium customer - priority service",
            },
            {
                "name": "Peter Parker",
                "phone": "+1234567898",
                "notes": "Freelance photographer - irregular income",
            },
            {
                "name": "Tony Stark",
                "phone": "+1234567899",
                "email": "tony.stark@starkindustries.com",
                "address": "10880 Malibu Point, Malibu, CA",
                "notes": "High-value customer - enterprise account",
            },
        ]

        customers = []
        for customer_data in customers_data:
            customer = customer_service.create_customer(
                db=db,
                customer_data=CustomerCreate(**customer_data),
                created_by_id=admin_user.id,
            )
            customers.append(customer)
            print(f"  ✅ Created customer: {customer.name}")

        return customers

    def create_initial_debts(db: Session, customers: list[Customer]):
        """
        Manually set initial account balances by directly inserting negative balance records.
        This simulates customers having existing debt without implementing sales.
        """
        print("\n📝 Setting initial customer debts...")

        # Initial debt amounts for testing
        debt_data = [
            (0, -430.00),  # John Doe owes $430
            (1, -1525.00),  # Jane Smith owes $1525
            (2, -120.00),  # Bob Johnson owes $120
            (3, -400.00),  # Alice Williams owes $400
            (4, -80.00),  # Charlie Brown owes $80
            (7, -15000.00),  # Tony Stark owes $15000
        ]

        for customer_index, debt_amount in debt_data:
            customer = customers[customer_index]
            # Update the account balance directly
            customer.account_balance = Decimal(str(debt_amount))
            db.commit()
            print(f"  ✅ Set initial debt for {customer.name}: ${abs(debt_amount):.2f}")

    def create_dummy_payments(db: Session, customers: list[Customer], admin_user: User):
        """Create dummy payments to create various balance scenarios."""
        print("\n💰 Creating dummy payments...")

        # Payments data: (customer_index, days_ago, amount, method, reference)
        payments_data = [
            # John Doe - partial payment (will still owe)
            (0, 10, 200.00, "cash", None),
            # Jane Smith - multiple partial payments (will still owe)
            (1, 35, 500.00, "transfer", "TRF-001"),
            (1, 15, 300.00, "card", "CARD-4532"),
            # Bob Johnson - overpayment (will have credit)
            (2, 5, 200.00, "cash", None),
            # Alice Williams - exact payment (zero balance)
            (3, 10, 400.00, "transfer", "TRF-002"),
            # Tony Stark - large partial payment
            (7, 15, 10000.00, "transfer", "WIRE-99887"),
        ]

        payments = []
        for customer_index, days_ago, amount, method, reference in payments_data:
            customer = customers[customer_index]
            payment_date = datetime.utcnow() - timedelta(days=days_ago)

            payment_data = PaymentCreate(
                customer_id=customer.id,
                amount=Decimal(str(amount)),
                payment_method=method,
                reference_number=reference,
                notes=f"Payment from {days_ago} days ago",
            )

            payment = payment_crud.create(
                db=db,
                customer_id=customer.id,
                payment=payment_data,
                received_by_id=admin_user.id,
            )

            # Update customer balance (payments increase balance)
            customer.account_balance += payment.amount

            # Update the created_at to simulate historical data
            payment.created_at = payment_date
            db.commit()

            payments.append(payment)
            print(
                f"  ✅ Created payment for {customer.name}: ${amount:.2f} via {method}"
            )

        return payments

    def display_final_balances(db: Session, customers: list[Customer]):
        """Display the final balance for each customer."""
        print("\n📊 Final Customer Balances:")
        print("-" * 60)

        for customer in customers:
            # Refresh to get updated balance
            db.refresh(customer)
            balance = customer.account_balance

            if balance < 0:
                status = f"Owes ${abs(balance):.2f} 🔴"
            elif balance > 0:
                status = f"Credit ${balance:.2f} 🟢"
            else:
                status = "Balanced $0.00 ✅"

            print(f"  {customer.name:<20} {status}")

    print("🚀 Starting dummy data creation...")

    # Get database session
    db = SessionLocal()

    try:
        # Get the admin user (ID 1)
        admin_user = db.query(User).filter(User.id == 1).first()
        if not admin_user:
            print("❌ Admin user not found. Please ensure the database is initialized.")
            return

        # Create dummy data
        customers = create_dummy_customers(db, admin_user)
        create_initial_debts(db, customers)
        payments = create_dummy_payments(db, customers, admin_user)

        # Display final balances
        display_final_balances(db, customers)

        print("\n✅ Dummy data creation completed successfully!")
        print("\n📋 Summary:")
        print(f"  - Created {len(customers)} customers")
        print(f"  - Created {len(payments)} payments")
        print("\n🎯 You can now test:")
        print("  - Customers with debt (John, Jane, Charlie, Tony)")
        print("  - Customers with credit (Bob)")
        print("  - Customers with zero balance (Alice)")
        print("  - Customers with no transactions (Diana, Peter)")

    except Exception as e:
        print(f"\n❌ Error creating dummy data: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
