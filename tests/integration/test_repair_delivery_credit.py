"""Integration tests for repair delivery with customer credit."""

from datetime import date
from decimal import Decimal

import pytest
from app.crud.cash_closing import cash_closing
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.models.repair import Repair
from app.models.sale import Sale
from app.models.user import User
from app.schemas.repair import (
    RepairComplete,
    RepairCreate,
    RepairDeliver,
    RepairStatusUpdate,
)
from app.services.repair_service import repair_service
from sqlalchemy.orm import Session


@pytest.fixture
def test_customer(db_session: Session) -> Customer:
    """Create a test customer."""
    customer = Customer(
        name="Test Customer",
        phone="555-1234",
        email="test@example.com",
        address="123 Test St",
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    from app.core.security import get_password_hash

    user = User(
        email="user@test.com",
        password_hash=get_password_hash("test_password"),
        full_name="Test User",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def open_cash_register(db_session: Session, test_user: User):
    """Open cash register for testing."""
    cash_closing.open_cash_register(
        db=db_session,
        target_date=date.today(),
        opening_balance=Decimal("100.00"),
        opened_by=test_user.id,
    )


class TestRepairDeliveryWithCredit:
    """Test repair delivery with customer credit application."""

    def test_deliver_repair_with_no_credit(
        self,
        db_session: Session,
        test_customer: Customer,
        test_user: User,
        test_repair_service_product,
        open_cash_register,
    ):
        """Test delivering repair when customer has no credit."""
        # Create a repair
        repair_data = RepairCreate(
            customer_id=test_customer.id,
            device_type="phone",
            device_brand="Apple",
            device_model="iPhone 12",
            problem_description="Screen broken",
            device_condition="Good except screen",
            warranty_days=30,
        )

        repair_response = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Update status through the proper workflow: diagnosing -> approved -> repairing
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="diagnosing"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="approved"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="repairing"),
            user_id=test_user.id,
        )

        # Complete the repair with a cost
        completion = RepairComplete(
            final_cost=Decimal("150.00"),
            labor_cost=Decimal("50.00"),
            parts_cost=Decimal("100.00"),
            repair_notes="Screen replaced",
        )

        repair_service.complete_repair(
            db=db_session,
            repair_id=repair_response.id,
            completion=completion,
            user_id=test_user.id,
        )
        # Note: complete_repair automatically sets status to "ready"

        # Deliver the repair
        delivery = RepairDeliver(
            delivered_by=test_user.id,
            delivery_notes="Customer picked up device",
        )

        delivered_repair = repair_service.deliver_repair(
            db=db_session, repair_id=repair_response.id, delivery=delivery
        )

        # Verify repair is delivered
        assert delivered_repair.status == "delivered"
        assert delivered_repair.delivered_date is not None

        # Check that a sale was created
        repair = db_session.query(Repair).get(repair_response.id)
        assert repair.sale_id is not None

        sale = db_session.query(Sale).get(repair.sale_id)
        assert sale is not None
        assert sale.total_amount == Decimal("150.00")
        assert sale.customer_id == test_customer.id

    def test_deliver_repair_with_full_credit(
        self,
        db_session: Session,
        test_customer: Customer,
        test_user: User,
        test_repair_service_product,
        open_cash_register,
    ):
        """Test delivering repair when customer has sufficient credit to cover full cost."""
        # Give customer credit by creating a negative balance
        account = CustomerAccount(
            customer_id=test_customer.id,
            account_balance=Decimal("-200.00"),  # Customer has $200 credit
            available_credit=Decimal("200.00"),
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()

        # Create a repair
        repair_data = RepairCreate(
            customer_id=test_customer.id,
            device_type="laptop",
            device_brand="Dell",
            device_model="XPS 13",
            problem_description="Won't boot",
            device_condition="Good physical condition",
            warranty_days=30,
        )

        repair_response = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Update status through the proper workflow: diagnosing -> approved -> repairing
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="diagnosing"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="approved"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="repairing"),
            user_id=test_user.id,
        )

        # Complete the repair with a cost
        completion = RepairComplete(
            final_cost=Decimal("150.00"),
            labor_cost=Decimal("150.00"),
            parts_cost=Decimal("0.00"),
            repair_notes="Fixed boot issue",
        )

        repair_service.complete_repair(
            db=db_session,
            repair_id=repair_response.id,
            completion=completion,
            user_id=test_user.id,
        )
        # Note: complete_repair automatically sets status to "ready"

        # Deliver the repair
        delivery = RepairDeliver(
            delivered_by=test_user.id,
            delivery_notes="Device delivered with credit applied",
        )

        delivered_repair = repair_service.deliver_repair(
            db=db_session, repair_id=repair_response.id, delivery=delivery
        )

        # Verify repair is delivered
        assert delivered_repair.status == "delivered"

        # Check that a sale was created with credit applied
        repair = db_session.query(Repair).get(repair_response.id)
        assert repair.sale_id is not None

        sale = db_session.query(Sale).get(repair.sale_id)
        assert sale is not None
        assert sale.total_amount == Decimal("150.00")
        assert sale.paid_amount == Decimal("150.00")  # Fully paid with credit
        assert sale.payment_status == "paid"

        # Check customer account balance
        db_session.refresh(account)
        assert account.account_balance == Decimal(
            "-50.00"
        )  # $200 - $150 = $50 credit left
        assert account.available_credit == Decimal("50.00")

    def test_deliver_repair_with_partial_credit(
        self,
        db_session: Session,
        test_customer: Customer,
        test_user: User,
        test_repair_service_product,
        open_cash_register,
    ):
        """Test delivering repair when customer has partial credit."""
        # Give customer some credit
        account = CustomerAccount(
            customer_id=test_customer.id,
            account_balance=Decimal("-50.00"),  # Customer has $50 credit
            available_credit=Decimal("50.00"),
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()

        # Create a repair
        repair_data = RepairCreate(
            customer_id=test_customer.id,
            device_type="tablet",
            device_brand="Samsung",
            device_model="Tab S7",
            problem_description="Battery issue",
            device_condition="Good",
            warranty_days=30,
        )

        repair_response = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Update status through the proper workflow: diagnosing -> approved -> repairing
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="diagnosing"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="approved"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="repairing"),
            user_id=test_user.id,
        )

        # Complete the repair with a cost higher than available credit
        completion = RepairComplete(
            final_cost=Decimal("200.00"),
            labor_cost=Decimal("50.00"),
            parts_cost=Decimal("150.00"),
            repair_notes="Battery replaced",
        )

        repair_service.complete_repair(
            db=db_session,
            repair_id=repair_response.id,
            completion=completion,
            user_id=test_user.id,
        )
        # Note: complete_repair automatically sets status to "ready"

        # Deliver the repair
        delivery = RepairDeliver(
            delivered_by=test_user.id,
            delivery_notes="Device delivered with partial credit applied",
        )

        delivered_repair = repair_service.deliver_repair(
            db=db_session, repair_id=repair_response.id, delivery=delivery
        )

        # Verify repair is delivered
        assert delivered_repair.status == "delivered"

        # Check that a sale was created with partial credit
        repair = db_session.query(Repair).get(repair_response.id)
        assert repair.sale_id is not None

        sale = db_session.query(Sale).get(repair.sale_id)
        assert sale is not None
        assert sale.total_amount == Decimal("200.00")
        assert sale.paid_amount == Decimal("50.00")  # $50 credit applied
        assert sale.payment_status == "partial"  # Still owes $150

        # Check customer account balance
        db_session.refresh(account)
        assert account.account_balance == Decimal("0.00")  # Credit fully used
        assert account.available_credit == Decimal("0.00")

    def test_repair_included_in_cash_closing(
        self,
        db_session: Session,
        test_customer: Customer,
        test_user: User,
        test_repair_service_product,
        open_cash_register,
    ):
        """Test that delivered repairs are included in daily cash closing."""
        # Create and deliver a repair
        repair_data = RepairCreate(
            customer_id=test_customer.id,
            device_type="phone",
            device_brand="Samsung",
            device_model="Galaxy S21",
            problem_description="Charging port issue",
            device_condition="Good",
            warranty_days=30,
        )

        repair_response = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Update status through the proper workflow: diagnosing -> approved -> repairing
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="diagnosing"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="approved"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="repairing"),
            user_id=test_user.id,
        )

        # Complete the repair
        completion = RepairComplete(
            final_cost=Decimal("100.00"),
            labor_cost=Decimal("100.00"),
            repair_notes="Charging port fixed",
        )

        repair_service.complete_repair(
            db=db_session,
            repair_id=repair_response.id,
            completion=completion,
            user_id=test_user.id,
        )
        # Note: complete_repair automatically sets status to "ready"

        # Deliver the repair
        delivery = RepairDeliver(delivered_by=test_user.id)
        repair_service.deliver_repair(
            db=db_session, repair_id=repair_response.id, delivery=delivery
        )

        # Get daily summary
        summary = cash_closing.get_daily_summary(
            db=db_session, target_date=date.today()
        )

        # Verify repair is included in the sales total
        assert summary.total_sales >= Decimal("100.00")
        assert summary.sales_count >= 1
        assert summary.repairs_delivered_count >= 1
        assert summary.repairs_total >= Decimal("100.00")

    def test_cannot_deliver_repair_without_cash_register_open(
        self,
        db_session: Session,
        test_customer: Customer,
        test_user: User,
        test_repair_service_product,
    ):
        """Test that repair delivery fails when cash register is not open."""
        # Create a repair (without opening cash register)
        repair_data = RepairCreate(
            customer_id=test_customer.id,
            device_type="phone",
            device_brand="Apple",
            device_model="iPhone 13",
            problem_description="Screen issue",
            device_condition="Good",
            warranty_days=30,
        )

        repair_response = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Update status through the proper workflow: diagnosing -> approved -> repairing
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="diagnosing"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="approved"),
            user_id=test_user.id,
        )
        repair_service.update_status(
            db=db_session,
            repair_id=repair_response.id,
            status_update=RepairStatusUpdate(status="repairing"),
            user_id=test_user.id,
        )

        # Complete and mark as ready
        completion = RepairComplete(
            final_cost=Decimal("200.00"),
            labor_cost=Decimal("200.00"),
            repair_notes="Screen fixed",
        )

        repair_service.complete_repair(
            db=db_session,
            repair_id=repair_response.id,
            completion=completion,
            user_id=test_user.id,
        )
        # Note: complete_repair automatically sets status to "ready"

        # Try to deliver - should fail
        delivery = RepairDeliver(delivered_by=test_user.id)

        with pytest.raises(ValueError) as exc_info:
            repair_service.deliver_repair(
                db=db_session, repair_id=repair_response.id, delivery=delivery
            )

        assert "Cash register must be open" in str(exc_info.value)
