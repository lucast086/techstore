"""Tests for repair service cash register validation."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from app.models.cash_closing import CashClosing
from app.models.customer import Customer
from app.models.repair import Repair
from app.models.user import User
from app.schemas.repair import RepairDeliver, RepairStatusUpdate
from app.services.repair_service import repair_service
from sqlalchemy.orm import Session


class TestRepairServiceCashValidation:
    """Test repair service cash register validation functionality."""

    def test_update_status_to_delivered_requires_open_cash(self, db_session: Session):
        """Test that updating status to delivered requires open cash register."""
        # Create test data
        customer = Customer(
            name="Test Customer", phone="555-0100", email="test@example.com"
        )
        db_session.add(customer)

        user = User(
            email="tech@example.com",
            full_name="Tech User",
            role="employee",
            password_hash="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        repair = Repair(
            repair_number="REP-2025-0001",
            customer_id=customer.id,
            device_type="smartphone",
            device_brand="Apple",
            device_model="iPhone 12",
            problem_description="Screen broken",
            status="completed",
            received_by=user.id,
            received_date=datetime.now(),
            final_cost=Decimal("150.00"),
        )
        db_session.add(repair)
        db_session.commit()

        # Test without open cash register
        status_update = RepairStatusUpdate(
            status="delivered", notes="Customer picked up device"
        )

        with pytest.raises(ValueError) as exc_info:
            repair_service.update_status(
                db=db_session,
                repair_id=repair.id,
                status_update=status_update,
                user_id=user.id,
            )

        assert "Cash register must be open" in str(exc_info.value)

        # Verify repair status hasn't changed
        db_session.refresh(repair)
        assert repair.status == "completed"

    def test_update_status_to_delivered_with_open_cash(self, db_session: Session):
        """Test that updating status to delivered works with open cash register."""
        # Create test data
        customer = Customer(
            name="Test Customer", phone="555-0100", email="test@example.com"
        )
        db_session.add(customer)

        user = User(
            email="tech@example.com",
            full_name="Tech User",
            role="employee",
            password_hash="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        # Create open cash register
        cash_register = CashClosing(
            closing_date=date.today(),
            opening_balance=Decimal("10000.00"),
            sales_total=Decimal("0.00"),
            expenses_total=Decimal("0.00"),
            cash_count=Decimal("10000.00"),
            expected_cash=Decimal("10000.00"),
            cash_difference=Decimal("0.00"),
            is_finalized=False,
            closed_by=user.id,
        )
        db_session.add(cash_register)

        repair = Repair(
            repair_number="REP-2025-0002",
            customer_id=customer.id,
            device_type="smartphone",
            device_brand="Samsung",
            device_model="Galaxy S21",
            problem_description="Battery issue",
            status="completed",
            received_by=user.id,
            received_date=datetime.now(),
            final_cost=Decimal("80.00"),
        )
        db_session.add(repair)
        db_session.commit()

        # Test with open cash register
        status_update = RepairStatusUpdate(
            status="delivered", notes="Customer picked up device"
        )

        result = repair_service.update_status(
            db=db_session,
            repair_id=repair.id,
            status_update=status_update,
            user_id=user.id,
        )

        assert result is not None
        assert result.status == "delivered"

        # Verify repair status changed
        db_session.refresh(repair)
        assert repair.status == "delivered"

    def test_deliver_repair_requires_open_cash(self, db_session: Session):
        """Test that deliver_repair method requires open cash register."""
        # Create test data
        customer = Customer(
            name="Test Customer", phone="555-0200", email="customer@example.com"
        )
        db_session.add(customer)

        user = User(
            email="staff@example.com",
            full_name="Staff User",
            role="employee",
            password_hash="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        repair = Repair(
            repair_number="REP-2025-0003",
            customer_id=customer.id,
            device_type="laptop",
            device_brand="Dell",
            device_model="XPS 13",
            problem_description="Keyboard not working",
            status="completed",
            received_by=user.id,
            received_date=datetime.now(),
            final_cost=Decimal("200.00"),
            labor_cost=Decimal("100.00"),
            parts_cost=Decimal("100.00"),
        )
        db_session.add(repair)
        db_session.commit()

        # Test without open cash register
        delivery = RepairDeliver(
            delivered_by=user.id,
            payment_received=Decimal("200.00"),
            notes="Paid in full",
        )

        with pytest.raises(ValueError) as exc_info:
            repair_service.deliver_repair(
                db=db_session, repair_id=repair.id, delivery=delivery
            )

        assert "Cash register must be open" in str(exc_info.value)

        # Verify repair hasn't been delivered
        db_session.refresh(repair)
        assert repair.status == "completed"
        assert repair.delivered_date is None

    def test_deliver_repair_with_open_cash(self, db_session: Session):
        """Test that deliver_repair works with open cash register."""
        # Create test data
        customer = Customer(
            name="Test Customer", phone="555-0300", email="customer2@example.com"
        )
        db_session.add(customer)

        user = User(
            email="manager@example.com",
            full_name="Manager User",
            role="manager",
            password_hash="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        # Create open cash register
        cash_register = CashClosing(
            closing_date=date.today(),
            opening_balance=Decimal("10000.00"),
            sales_total=Decimal("0.00"),
            expenses_total=Decimal("0.00"),
            cash_count=Decimal("10000.00"),
            expected_cash=Decimal("10000.00"),
            cash_difference=Decimal("0.00"),
            is_finalized=False,
            closed_by=user.id,
        )
        db_session.add(cash_register)

        repair = Repair(
            repair_number="REP-2025-0004",
            customer_id=customer.id,
            device_type="tablet",
            device_brand="Apple",
            device_model="iPad Pro",
            problem_description="Screen replacement",
            status="completed",
            received_by=user.id,
            received_date=datetime.now(),
            final_cost=Decimal("300.00"),
            labor_cost=Decimal("100.00"),
            parts_cost=Decimal("200.00"),
        )
        db_session.add(repair)
        db_session.commit()

        # Test with open cash register
        delivery = RepairDeliver(
            delivered_by=user.id,
            payment_received=Decimal("300.00"),
            notes="Customer paid in cash",
        )

        result = repair_service.deliver_repair(
            db=db_session, repair_id=repair.id, delivery=delivery
        )

        assert result is not None
        assert result.status == "delivered"

        # Verify repair has been delivered
        db_session.refresh(repair)
        assert repair.status == "delivered"
        assert repair.delivered_date is not None
        assert repair.delivered_by == user.id

    def test_other_status_changes_dont_require_cash(self, db_session: Session):
        """Test that other status changes don't require open cash register."""
        # Create test data
        customer = Customer(
            name="Test Customer", phone="555-0400", email="nocash@example.com"
        )
        db_session.add(customer)

        user = User(
            email="tech2@example.com",
            full_name="Tech User 2",
            role="employee",
            password_hash="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        repair = Repair(
            repair_number="REP-2025-0005",
            customer_id=customer.id,
            device_type="smartphone",
            device_brand="OnePlus",
            device_model="9 Pro",
            problem_description="Water damage",
            status="received",
            received_by=user.id,
            received_date=datetime.now(),
        )
        db_session.add(repair)
        db_session.commit()

        # No cash register open - but status changes to non-delivered should work

        # Change to diagnosing
        status_update = RepairStatusUpdate(
            status="diagnosing", notes="Starting diagnosis"
        )
        result = repair_service.update_status(
            db=db_session,
            repair_id=repair.id,
            status_update=status_update,
            user_id=user.id,
        )
        assert result is not None
        assert result.status == "diagnosing"

        # Change to in_progress
        status_update = RepairStatusUpdate(
            status="in_progress", notes="Repairing device"
        )
        result = repair_service.update_status(
            db=db_session,
            repair_id=repair.id,
            status_update=status_update,
            user_id=user.id,
        )
        assert result is not None
        assert result.status == "in_progress"

        # Change to completed
        status_update = RepairStatusUpdate(status="completed", notes="Repair finished")
        result = repair_service.update_status(
            db=db_session,
            repair_id=repair.id,
            status_update=status_update,
            user_id=user.id,
        )
        assert result is not None
        assert result.status == "completed"

    def test_cash_validation_with_previous_day_register(self, db_session: Session):
        """Test that validation fails if only previous day's cash register is open."""
        # Create test data
        customer = Customer(
            name="Test Customer", phone="555-0500", email="prevday@example.com"
        )
        db_session.add(customer)

        user = User(
            email="admin@example.com",
            full_name="Admin User",
            role="admin",
            password_hash="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        # Create cash register from yesterday (still open)
        yesterday = date.today() - timedelta(days=1)
        cash_register = CashClosing(
            closing_date=yesterday,
            opening_balance=Decimal("10000.00"),
            sales_total=Decimal("0.00"),
            expenses_total=Decimal("0.00"),
            cash_count=Decimal("10000.00"),
            expected_cash=Decimal("10000.00"),
            cash_difference=Decimal("0.00"),
            is_finalized=False,
            closed_by=user.id,
        )
        db_session.add(cash_register)

        repair = Repair(
            repair_number="REP-2025-0006",
            customer_id=customer.id,
            device_type="console",
            device_brand="Sony",
            device_model="PS5",
            problem_description="HDMI port issue",
            status="completed",
            received_by=user.id,
            received_date=datetime.now(),
            final_cost=Decimal("120.00"),
        )
        db_session.add(repair)
        db_session.commit()

        # Should fail because today's cash register is not open
        status_update = RepairStatusUpdate(status="delivered", notes="Ready for pickup")

        with pytest.raises(ValueError) as exc_info:
            repair_service.update_status(
                db=db_session,
                repair_id=repair.id,
                status_update=status_update,
                user_id=user.id,
            )

        assert "Cash register must be open" in str(exc_info.value)

    def test_cash_validation_integration_flow(self, db_session: Session):
        """Test complete flow: open cash -> deliver repair -> close cash."""
        # Create test data
        customer = Customer(
            name="Integration Customer",
            phone="555-0600",
            email="integration@example.com",
        )
        db_session.add(customer)

        user = User(
            email="complete@example.com",
            full_name="Complete User",
            role="admin",
            password_hash="hashed_password",
        )
        db_session.add(user)
        db_session.commit()

        repair = Repair(
            repair_number="REP-2025-0007",
            customer_id=customer.id,
            device_type="smartphone",
            device_brand="Google",
            device_model="Pixel 6",
            problem_description="Camera not working",
            status="completed",
            received_by=user.id,
            received_date=datetime.now(),
            final_cost=Decimal("175.00"),
        )
        db_session.add(repair)
        db_session.commit()

        # Step 1: Try to deliver without cash register - should fail
        delivery = RepairDeliver(
            delivered_by=user.id,
            payment_received=Decimal("175.00"),
            notes="Payment pending",
        )

        with pytest.raises(ValueError) as exc_info:
            repair_service.deliver_repair(
                db=db_session, repair_id=repair.id, delivery=delivery
            )
        assert "Cash register must be open" in str(exc_info.value)

        # Step 2: Open cash register
        cash_register = CashClosing(
            closing_date=date.today(),
            opening_balance=Decimal("10000.00"),
            sales_total=Decimal("0.00"),
            expenses_total=Decimal("0.00"),
            cash_count=Decimal("10000.00"),
            expected_cash=Decimal("10000.00"),
            cash_difference=Decimal("0.00"),
            is_finalized=False,
            closed_by=user.id,
        )
        db_session.add(cash_register)
        db_session.commit()

        # Step 3: Now delivery should work
        result = repair_service.deliver_repair(
            db=db_session, repair_id=repair.id, delivery=delivery
        )
        assert result is not None
        assert result.status == "delivered"

        # Step 4: Close cash register
        cash_register.is_finalized = True
        cash_register.cash_count = Decimal("10175.00")
        cash_register.sales_total = Decimal("175.00")
        cash_register.expenses_total = Decimal("0.00")
        cash_register.expected_cash = Decimal("10175.00")
        cash_register.cash_difference = Decimal("0.00")
        db_session.commit()

        # Step 5: Try to deliver another repair after closing - should fail
        repair2 = Repair(
            repair_number="REP-2025-0008",
            customer_id=customer.id,
            device_type="laptop",
            device_brand="HP",
            device_model="Pavilion",
            problem_description="Overheating",
            status="completed",
            received_by=user.id,
            received_date=datetime.now(),
            final_cost=Decimal("90.00"),
        )
        db_session.add(repair2)
        db_session.commit()

        delivery2 = RepairDeliver(
            delivered_by=user.id,
            payment_received=Decimal("90.00"),
            notes="Second repair",
        )

        with pytest.raises(ValueError) as exc_info:
            repair_service.deliver_repair(
                db=db_session, repair_id=repair2.id, delivery=delivery2
            )
        assert "Cash register must be open" in str(exc_info.value)
