"""Test cash closing with customer credit balance and repair scenarios."""

from datetime import date, datetime, time
from decimal import Decimal

import pytest
from app.crud.cash_closing import cash_closing
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.models.payment import Payment
from app.models.repair import Repair
from app.models.sale import Sale
from app.utils.timezone import local_to_utc
from sqlalchemy.orm import Session


class TestCashClosingCreditScenario:
    """Test cash closing with customer credit balance scenarios."""

    @pytest.fixture
    def customer_with_credit(self, db_session: Session, test_user) -> Customer:
        """Create a customer with positive credit balance."""
        customer = Customer(
            name="Test Customer",
            phone="1234567890",
            email="test@example.com",
        )
        db_session.add(customer)
        db_session.flush()

        # Create customer account with credit
        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("-30000.00"),  # Negative means customer has credit
            available_credit=Decimal("30000.00"),
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(customer)
        return customer

    def test_repair_payment_with_customer_credit(
        self, db_session: Session, test_user, customer_with_credit
    ):
        """Test cash closing when customer with credit pays for repair.

        Scenario:
        1. Customer has $30,000 credit balance (saldo a favor)
        2. Repair created for $50,000
        3. Customer pays full $50,000 for repair
        4. This creates an overpayment situation
        """
        # Customer with credit is provided by fixture

        # Setup test date
        test_date = date.today()
        # Create datetime with local timezone and convert to UTC
        local_datetime = datetime.combine(test_date, time(12, 0))  # noon local time
        utc_datetime = local_to_utc(local_datetime)

        # Step 1: Verify customer has credit balance
        assert customer_with_credit.account.account_balance == Decimal("-30000.00")

        # Step 2: Create completed repair for $50,000
        repair = Repair(
            customer_id=customer_with_credit.id,
            repair_number=f"REP-{test_date.strftime('%Y%m%d')}-001",
            device_type="Laptop",
            device_brand="Dell",
            device_model="XPS",
            serial_number="12345",
            problem_description="Screen broken",
            status="completed",
            final_cost=Decimal("50000.00"),
            received_by=test_user.id,
            received_date=utc_datetime,
            completed_date=utc_datetime,
        )
        db_session.add(repair)
        db_session.commit()
        db_session.refresh(repair)

        # Step 3: Create sale to invoice the repair (this is how repairs are paid)
        sale = Sale(
            invoice_number=f"INV-{test_date.strftime('%Y%m%d')}-001",
            customer_id=customer_with_credit.id,
            subtotal=Decimal("50000.00"),
            total_amount=Decimal("50000.00"),
            paid_amount=Decimal("50000.00"),
            payment_method="cash",
            user_id=test_user.id,
            sale_date=utc_datetime,
        )
        db_session.add(sale)
        db_session.commit()
        db_session.refresh(sale)

        # Link repair to sale
        repair.sale_id = sale.id

        # Update customer balance (should now have even more credit)
        # Customer had -30000 credit, paid 50000 cash, so new balance is -80000
        customer_with_credit.account.account_balance = Decimal("-80000.00")
        customer_with_credit.account.available_credit = Decimal("80000.00")

        db_session.commit()

        # Step 4: Get daily summary for cash closing
        daily_summary = cash_closing.get_daily_summary(
            db_session, target_date=test_date
        )

        # Print debug information
        print("Daily Summary:")
        print(f"  Total Sales: {daily_summary.total_sales}")
        print(f"  Sales Count: {daily_summary.sales_count}")
        print(f"  Repairs Total: {daily_summary.repairs_total}")
        print(f"  Repairs Delivered Count: {daily_summary.repairs_delivered_count}")

        # Assertions
        # The sale should be properly reflected in daily summary
        # Total sales should be $50,000 (the repair was invoiced as a sale)
        assert daily_summary.total_sales == Decimal(
            "50000.00"
        ), f"Total sales should be 50000, got: {daily_summary.total_sales}"

        # Sales count should be 1
        assert (
            daily_summary.sales_count == 1
        ), f"Sales count should be 1, got: {daily_summary.sales_count}"

    def test_sale_with_overpayment(
        self, db_session: Session, customer_with_credit: Customer, test_user
    ):
        """Test cash closing when customer overpays for a sale.

        Scenario:
        1. Customer has $30,000 credit balance
        2. Makes a purchase of $10,000
        3. Pays $31,000 (covering the purchase and using all credit)
        """
        test_date = date.today()
        # Create datetime with local timezone and convert to UTC
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        # Create a sale
        sale = Sale(
            invoice_number=f"INV-{test_date.strftime('%Y%m%d')}-002",
            customer_id=customer_with_credit.id,
            subtotal=Decimal("10000.00"),
            total_amount=Decimal("10000.00"),
            paid_amount=Decimal("0.00"),
            payment_method="account_credit",
            user_id=test_user.id,
            sale_date=utc_datetime,
        )
        db_session.add(sale)
        db_session.commit()
        db_session.refresh(sale)

        # Customer pays $31,000
        payment = Payment(
            customer_id=customer_with_credit.id,
            sale_id=sale.id,
            amount=Decimal("31000.00"),
            payment_method="cash",
            receipt_number=f"REC-{test_date.strftime('%Y%m%d')}-001",
            received_by_id=test_user.id,
        )
        db_session.add(payment)

        # Update sale paid amount
        sale.paid_amount = Decimal("31000.00")

        # Update customer balance
        # Had -30000 credit, made 10000 purchase, paid 31000
        # New balance: -30000 + 10000 - 31000 = -51000
        customer_with_credit.account.account_balance = Decimal("-51000.00")
        customer_with_credit.account.available_credit = Decimal("51000.00")

        db_session.commit()

        # Get daily summary
        daily_summary = cash_closing.get_daily_summary(
            db_session, target_date=test_date
        )

        print("\nSale Overpayment Summary:")
        print(f"  Total Sales: {daily_summary.total_sales}")
        print(f"  Sales Count: {daily_summary.sales_count}")

        # Total sales should be $10,000 (the sale amount)
        assert daily_summary.total_sales == Decimal(
            "10000.00"
        ), f"Total sales should be 10000, got: {daily_summary.total_sales}"

        # Sales count should be 1
        assert (
            daily_summary.sales_count == 1
        ), f"Sales count should be 1, got: {daily_summary.sales_count}"

    def test_verify_repairs_in_cash_closing(self, db_session: Session, test_user):
        """Verify that repairs are properly included in cash closing calculations."""
        test_date = date.today()
        # Create datetime with local timezone and convert to UTC
        local_datetime = datetime.combine(test_date, time(12, 0))
        utc_datetime = local_to_utc(local_datetime)

        # Create a customer
        customer = Customer(
            name="Repair Customer",
            phone="9876543210",
            email="repair@example.com",
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)

        # Create a completed repair
        repair = Repair(
            customer_id=customer.id,
            repair_number=f"REP-{test_date.strftime('%Y%m%d')}-002",
            device_type="Phone",
            device_brand="Samsung",
            device_model="Galaxy",
            serial_number="ABC123",
            problem_description="Battery issue",
            final_cost=Decimal("15000.00"),
            status="completed",
            received_by=test_user.id,
            received_date=utc_datetime,
            completed_date=utc_datetime,
        )
        db_session.add(repair)
        db_session.commit()
        db_session.refresh(repair)

        # Create sale to invoice the repair (paid in cash)
        sale = Sale(
            invoice_number=f"INV-{test_date.strftime('%Y%m%d')}-003",
            customer_id=customer.id,
            subtotal=Decimal("15000.00"),
            total_amount=Decimal("15000.00"),
            paid_amount=Decimal("15000.00"),
            payment_method="cash",
            user_id=test_user.id,
            sale_date=utc_datetime,
        )
        db_session.add(sale)
        db_session.commit()
        db_session.refresh(sale)

        # Link repair to sale
        repair.sale_id = sale.id
        db_session.commit()

        # Get daily summary
        daily_summary = cash_closing.get_daily_summary(
            db_session, target_date=test_date
        )

        print("\nRepair Cash Closing Summary:")
        print(f"  Total Sales: {daily_summary.total_sales}")
        print(f"  Sales Count: {daily_summary.sales_count}")
        print(f"  Repairs Total: {daily_summary.repairs_total}")
        print(f"  Repairs Delivered Count: {daily_summary.repairs_delivered_count}")

        # Check if repair payments are included through sales
        # Repairs are invoiced as sales, so they should appear in total_sales
        assert (
            daily_summary.total_sales == Decimal("15000.00")
        ), f"Total sales should be 15000 (repair invoiced as sale), got: {daily_summary.total_sales}"

        # Sales count should be 1
        assert (
            daily_summary.sales_count == 1
        ), f"Sales count should be 1, got: {daily_summary.sales_count}"
