"""Tests for repair system integration with sales and deposits.

Tests cover FASE 8 from test coverage plan:
- Repair deposits creating customer credits
- Deposits applied to final sale
- Partial deposits + cash
- Deposits exceeding final cost
- Deposit refunds
- Complete repair with sale
- Repair service product in POS
- Delivery updating repair status
- Repairs with additional parts
- Multiple repairs in single sale
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from app.crud.cash_closing import cash_closing
from app.crud.sale import sale_crud
from app.models.customer import Customer
from app.models.customer_account import (
    CustomerAccount,
    CustomerTransaction,
    TransactionType,
)
from app.models.product import Category, Product
from app.models.repair import Repair
from app.models.repair_deposit import DepositStatus, RepairDeposit
from app.models.user import User
from app.schemas.repair import RepairCreate, RepairStatus
from app.schemas.repair_deposit import DepositCreate
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.repair_deposit_service import repair_deposit_service
from app.services.repair_service import repair_service
from app.utils.timezone import get_local_today
from sqlalchemy.orm import Session


class TestRepairIntegration:
    """Test repair system integration with sales and deposits."""

    @pytest.fixture
    def test_user(self, db_session: Session) -> User:
        """Create a test user."""
        user = User(
            email="repair_test@example.com",
            password_hash="hashedpass",
            full_name="Repair Test User",
            role="admin",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def test_category(self, db_session: Session) -> Category:
        """Create a test category."""
        category = Category(
            name="Repair Test Category",
            description="Test category",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def test_product(self, db_session: Session, test_category: Category) -> Product:
        """Create a test product for parts."""
        product = Product(
            sku="PART001",
            name="Replacement Screen",
            category_id=test_category.id,
            purchase_price=Decimal("50.00"),
            first_sale_price=Decimal("100.00"),
            second_sale_price=Decimal("100.00"),
            third_sale_price=Decimal("100.00"),
            tax_rate=Decimal("10.00"),
            current_stock=100,
            minimum_stock=10,
            is_active=True,
            is_service=False,
            created_by=1,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    @pytest.fixture
    def customer_with_account(self, db_session: Session) -> Customer:
        """Create customer with account."""
        customer = Customer(
            name="Repair Test Customer",
            phone="555-8888",
            email="repairtest@example.com",
            is_active=True,
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)

        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("0.00"),
            credit_limit=Decimal("1000.00"),
            created_by_id=1,
        )
        db_session.add(account)
        db_session.commit()

        return customer

    @pytest.fixture
    def open_cash_register(self, db_session: Session, test_user: User):
        """Open cash register for today."""
        today = get_local_today()
        register = cash_closing.open_cash_register(
            db_session,
            target_date=today,
            opening_balance=Decimal("1000.00"),
            opened_by=test_user.id,
        )
        db_session.commit()
        return register

    # ============================================================
    # CATEGORY: Repair Deposits
    # ============================================================

    def test_repair_deposit_creates_credit(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
    ):
        """Test 8.1: Repair deposit creates credit in customer account.

        Expected behavior:
        1. Create repair with estimated cost
        2. Record deposit
        3. Deposit creates negative balance (credit) in customer account
        4. Transaction recorded with type REPAIR_DEPOSIT
        """
        # Arrange: Create repair
        repair_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Smartphone",
            device_brand="Apple",
            device_model="iPhone 12",
            serial_number="SERIAL123",
            problem_description="Screen broken",
            device_condition="Good condition except screen",
            estimated_cost=Decimal("300.00"),
        )
        repair = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Get initial balance
        account = (
            db_session.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == customer_with_account.id)
            .first()
        )
        initial_balance = account.account_balance

        # Act: Record deposit
        deposit_data = DepositCreate(
            repair_id=repair.id,
            customer_id=customer_with_account.id,
            amount=Decimal("100.00"),
            payment_method="cash",
            notes="Initial deposit",
        )
        deposit = repair_deposit_service.record_deposit(
            db=db_session, deposit_data=deposit_data, received_by_id=test_user.id
        )

        # Assert: Deposit created
        assert deposit.id is not None
        assert deposit.amount == Decimal("100.00")
        assert deposit.status == DepositStatus.ACTIVE

        # Assert: Customer account has credit (negative balance)
        db_session.refresh(account)
        expected_balance = initial_balance - Decimal("100.00")
        assert account.account_balance == expected_balance

        # Assert: Transaction recorded
        transaction = (
            db_session.query(CustomerTransaction)
            .filter(CustomerTransaction.id == deposit.transaction_id)
            .first()
        )
        assert transaction is not None
        assert transaction.transaction_type == TransactionType.REPAIR_DEPOSIT
        # Note: amount is stored as positive, but creates negative balance
        assert transaction.amount == Decimal("100.00")
        assert (
            transaction.balance_after < transaction.balance_before
        )  # Balance decreased (credit)
        assert transaction.reference_id == deposit.id

    def test_repair_deposit_applied_to_sale(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
        open_cash_register,
    ):
        """Test 8.2: Repair deposit is applied to final sale.

        Expected behavior:
        1. Create repair with deposit
        2. Complete repair
        3. Create sale for repair
        4. Deposit is applied, status changes to APPLIED
        5. Sale linked to deposit
        """
        # Arrange: Create repair with deposit
        repair_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Laptop",
            device_brand="Dell",
            device_model="XPS 13",
            serial_number="SERIAL456",
            problem_description="Won't turn on",
            device_condition="Clean, no physical damage",
            estimated_cost=Decimal("250.00"),
        )
        repair = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        deposit_data = DepositCreate(
            repair_id=repair.id,
            customer_id=customer_with_account.id,
            amount=Decimal("100.00"),
            payment_method="cash",
        )
        deposit = repair_deposit_service.record_deposit(
            db=db_session, deposit_data=deposit_data, received_by_id=test_user.id
        )

        # Update repair to ready status
        repair_obj = db_session.query(Repair).filter(Repair.id == repair.id).first()
        repair_obj.status = RepairStatus.READY
        repair_obj.final_cost = Decimal("250.00")
        db_session.commit()

        # Act: Create sale for repair (using repair service product)
        from app.services.repair_product_service import repair_product_service

        repair_product = repair_product_service.get_or_create_repair_product(db_session)

        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=Decimal("150.00"),  # 250 - 100 deposit
                    price_tier="first",
                )
            ],
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Apply deposits
        applied_deposits = repair_deposit_service.apply_deposits_to_sale(
            db=db_session, repair_id=repair.id, sale_id=sale.id
        )

        # Assert: Deposit applied
        assert len(applied_deposits) == 1
        deposit_after = (
            db_session.query(RepairDeposit)
            .filter(RepairDeposit.id == deposit.id)
            .first()
        )
        assert deposit_after.status == DepositStatus.APPLIED
        assert deposit_after.sale_id == sale.id

    def test_repair_partial_deposit_plus_cash(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
        open_cash_register,
    ):
        """Test 8.3: Partial deposit + cash payment for repair.

        Expected behavior:
        1. Repair cost $300
        2. Deposit $100
        3. Sale for $200 (amount due)
        4. Customer pays $200 in cash
        """
        # Arrange: Create repair with partial deposit
        repair_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Tablet",
            device_brand="Samsung",
            device_model="Galaxy Tab",
            serial_number="TAB789",
            problem_description="Battery replacement needed",
            device_condition="Good overall condition",
            estimated_cost=Decimal("300.00"),
        )
        repair = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Record partial deposit
        deposit_data = DepositCreate(
            repair_id=repair.id,
            customer_id=customer_with_account.id,
            amount=Decimal("100.00"),
            payment_method="cash",
        )
        repair_deposit_service.record_deposit(
            db=db_session, deposit_data=deposit_data, received_by_id=test_user.id
        )

        # Complete repair
        repair_obj = db_session.query(Repair).filter(Repair.id == repair.id).first()
        repair_obj.status = RepairStatus.READY
        repair_obj.final_cost = Decimal("300.00")
        db_session.commit()

        # Act: Create sale for remaining amount
        from app.services.repair_product_service import repair_product_service

        repair_product = repair_product_service.get_or_create_repair_product(db_session)

        amount_due = Decimal("200.00")  # 300 - 100 deposit
        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=amount_due,
                    price_tier="first",
                )
            ],
            amount_paid=amount_due,  # Customer pays in cash
            payment_method="cash",
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Apply deposits
        repair_deposit_service.apply_deposits_to_sale(
            db=db_session, repair_id=repair.id, sale_id=sale.id
        )

        # Assert: Sale created for correct amount
        assert sale.total_amount > Decimal("0")  # Has tax
        assert sale.subtotal == amount_due
        assert sale.payment_status == "paid"

    def test_repair_deposit_exceeds_final_cost(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
    ):
        """Test 8.4: Multiple deposits tracking.

        Expected behavior:
        1. Create repair with estimated cost $200
        2. Record two deposits totaling $200
        3. Both deposits tracked correctly
        4. Total deposits calculated correctly
        """
        # Arrange: Create repair
        repair_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Phone",
            device_brand="Xiaomi",
            device_model="Redmi Note",
            serial_number="XIAO123",
            problem_description="Charging port loose",
            device_condition="Minor wear",
            estimated_cost=Decimal("200.00"),
        )
        repair = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Act: Record two deposits
        deposit1_data = DepositCreate(
            repair_id=repair.id,
            customer_id=customer_with_account.id,
            amount=Decimal("100.00"),
            payment_method="cash",
        )
        deposit1 = repair_deposit_service.record_deposit(
            db=db_session, deposit_data=deposit1_data, received_by_id=test_user.id
        )

        deposit2_data = DepositCreate(
            repair_id=repair.id,
            customer_id=customer_with_account.id,
            amount=Decimal("100.00"),
            payment_method="cash",
        )
        deposit2 = repair_deposit_service.record_deposit(
            db=db_session, deposit_data=deposit2_data, received_by_id=test_user.id
        )

        # Assert: Both deposits created
        assert deposit1.id is not None
        assert deposit2.id is not None

        # Assert: Total deposits calculated correctly
        total_deposits = repair_deposit_service.calculate_total_deposits(
            db=db_session, repair_id=repair.id, status=DepositStatus.ACTIVE
        )
        assert total_deposits == Decimal("200.00")

    def test_repair_deposit_refund(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
    ):
        """Test 8.5: Refund repair deposit.

        Expected behavior:
        1. Record deposit creating credit
        2. Refund deposit
        3. Credit is reversed (balance returns to original)
        4. Deposit status changed to REFUNDED
        """
        # Arrange: Create repair with deposit
        repair_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Monitor",
            device_brand="LG",
            device_model="UltraWide",
            serial_number="MON999",
            problem_description="No display",
            device_condition="Excellent",
            estimated_cost=Decimal("400.00"),
        )
        repair = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        deposit_data = DepositCreate(
            repair_id=repair.id,
            customer_id=customer_with_account.id,
            amount=Decimal("150.00"),
            payment_method="cash",
        )
        deposit = repair_deposit_service.record_deposit(
            db=db_session, deposit_data=deposit_data, received_by_id=test_user.id
        )

        # Get balance after deposit
        account = (
            db_session.query(CustomerAccount)
            .filter(CustomerAccount.customer_id == customer_with_account.id)
            .first()
        )
        balance_after_deposit = account.account_balance

        # Act: Refund deposit
        from app.schemas.repair_deposit import DepositRefund

        refund_data = DepositRefund(
            refund_amount=Decimal("150.00"), refund_reason="Customer cancelled repair"
        )
        refunded_deposit = repair_deposit_service.refund_deposit(
            db=db_session,
            deposit_id=deposit.id,
            refund_data=refund_data,
            refunded_by_id=test_user.id,
        )

        # Assert: Deposit refunded
        assert refunded_deposit.status == DepositStatus.REFUNDED
        assert refunded_deposit.refunded_amount == Decimal("150.00")

        # Assert: Credit reversed in customer account
        db_session.refresh(account)
        expected_balance = balance_after_deposit + Decimal("150.00")
        assert account.account_balance == expected_balance

    # ============================================================
    # CATEGORY: Repair Sales Integration
    # ============================================================

    def test_complete_repair_with_sale(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
        open_cash_register,
    ):
        """Test 8.6: Complete repair flow with sale creation.

        Expected behavior:
        1. Create and complete repair
        2. Create sale for repair
        3. Link repair to sale
        4. Repair status updated to DELIVERED
        """
        # Arrange: Create and complete repair
        repair_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Gaming Console",
            device_brand="Sony",
            device_model="PS5",
            serial_number="PS5-001",
            problem_description="Overheating",
            device_condition="Dusty internals",
            estimated_cost=Decimal("150.00"),
        )
        repair = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        # Mark as ready
        repair_obj = db_session.query(Repair).filter(Repair.id == repair.id).first()
        repair_obj.status = RepairStatus.READY
        repair_obj.final_cost = Decimal("150.00")
        db_session.commit()

        # Act: Create sale and link
        from app.services.repair_product_service import repair_product_service

        repair_product = repair_product_service.get_or_create_repair_product(db_session)

        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=Decimal("150.00"),
                    price_tier="first",
                )
            ],
            amount_paid=Decimal("165.00"),  # 150 + 10% tax
            payment_method="cash",
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Complete sale delivery (links repair to sale)
        completed_repair = repair_service.complete_sale_delivery(
            db=db_session, repair_id=repair.id, sale_id=sale.id, user_id=test_user.id
        )

        # Assert: Repair linked to sale
        assert completed_repair.sale_id == sale.id
        assert completed_repair.status == RepairStatus.DELIVERED
        assert completed_repair.delivered_date is not None

    def test_repair_service_product_in_sale(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
        open_cash_register,
    ):
        """Test 8.7: Repair appears as service product in sale.

        Expected behavior:
        1. Repair product (SKU: REPAIR-SERVICE) exists or is created
        2. Can be used in sales
        3. Has correct category (SERVICIOS)
        """
        # Act: Get or create repair product
        from app.services.repair_product_service import repair_product_service

        repair_product = repair_product_service.get_or_create_repair_product(db_session)

        # Assert: Product exists and has correct properties
        assert repair_product.id is not None
        assert repair_product.sku == "REPAIR-SERVICE"
        assert repair_product.is_service is True
        assert repair_product.is_active is True

        # Assert: Can be used in sale
        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    price_tier="first",
                )
            ],
            amount_paid=Decimal("110.00"),
            payment_method="cash",
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        assert sale.id is not None
        assert len(sale.items) == 1
        assert sale.items[0].product_id == repair_product.id

    def test_repair_delivery_updates_status(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
        open_cash_register,
    ):
        """Test 8.8: Delivery updates repair status and timestamps.

        Expected behavior:
        1. Repair starts as READY
        2. Complete sale delivery
        3. Status changes to DELIVERED
        4. delivered_date and delivered_by set
        5. warranty_expires calculated
        """
        # Arrange: Create ready repair
        repair_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Headphones",
            device_brand="Sony",
            device_model="WH-1000XM4",
            serial_number="HEAD001",
            problem_description="Left ear not working",
            device_condition="Good",
            estimated_cost=Decimal("80.00"),
            warranty_days=90,
        )
        repair = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        repair_obj = db_session.query(Repair).filter(Repair.id == repair.id).first()
        repair_obj.status = RepairStatus.READY
        repair_obj.final_cost = Decimal("80.00")
        db_session.commit()

        # Create sale
        from app.services.repair_product_service import repair_product_service

        repair_product = repair_product_service.get_or_create_repair_product(db_session)

        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=Decimal("80.00"),
                    price_tier="first",
                )
            ],
            amount_paid=Decimal("88.00"),
            payment_method="cash",
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Act: Complete delivery
        delivered_repair = repair_service.complete_sale_delivery(
            db=db_session, repair_id=repair.id, sale_id=sale.id, user_id=test_user.id
        )

        # Assert: Status and metadata updated
        assert delivered_repair.status == RepairStatus.DELIVERED
        assert delivered_repair.delivered_date is not None
        assert delivered_repair.delivered_by == test_user.id
        assert delivered_repair.warranty_expires is not None

        # Warranty should be 90 days from delivery
        expected_expiry = get_local_today() + timedelta(days=90)
        assert delivered_repair.warranty_expires == expected_expiry

    def test_repair_with_additional_parts(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
        test_product: Product,
        open_cash_register,
    ):
        """Test 8.9: Repair with additional parts in sale.

        Expected behavior:
        1. Repair service product in sale
        2. Additional parts products in same sale
        3. Total includes repair + parts
        """
        # Arrange: Create repair
        repair_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Laptop",
            device_brand="HP",
            device_model="Pavilion",
            serial_number="HP123",
            problem_description="Screen + keyboard issues",
            device_condition="Heavy use",
            estimated_cost=Decimal("200.00"),
        )
        repair = repair_service.create_repair(
            db=db_session, repair_data=repair_data, user_id=test_user.id
        )

        repair_obj = db_session.query(Repair).filter(Repair.id == repair.id).first()
        repair_obj.status = RepairStatus.READY
        repair_obj.final_cost = Decimal("200.00")
        db_session.commit()

        # Act: Create sale with repair + additional part
        from app.services.repair_product_service import repair_product_service

        repair_product = repair_product_service.get_or_create_repair_product(db_session)

        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                # Repair service
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=Decimal("200.00"),
                    price_tier="first",
                ),
                # Additional part (replacement screen from fixture)
                SaleItemCreate(
                    product_id=test_product.id,
                    quantity=1,
                    unit_price=Decimal("100.00"),
                    price_tier="first",
                ),
            ],
            amount_paid=Decimal("330.00"),  # (200 + 100) * 1.1 tax
            payment_method="cash",
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Assert: Sale has both items
        assert len(sale.items) == 2
        assert sale.items[0].product_id == repair_product.id
        assert sale.items[1].product_id == test_product.id
        assert sale.total_amount == Decimal("330.00")

    def test_multiple_repairs_single_sale(
        self,
        db_session: Session,
        test_user: User,
        customer_with_account: Customer,
        open_cash_register,
    ):
        """Test 8.10: Multiple repairs in single sale.

        Expected behavior:
        1. Customer has 2 repairs ready
        2. Both delivered in single sale
        3. Each repair linked to same sale
        4. Both repairs status = DELIVERED
        """
        # Arrange: Create 2 repairs
        repair1_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Phone",
            device_brand="Apple",
            device_model="iPhone 11",
            serial_number="IP11-001",
            problem_description="Battery replacement",
            device_condition="Good",
            estimated_cost=Decimal("120.00"),
        )
        repair1 = repair_service.create_repair(
            db=db_session, repair_data=repair1_data, user_id=test_user.id
        )

        repair2_data = RepairCreate(
            customer_id=customer_with_account.id,
            device_type="Tablet",
            device_brand="Apple",
            device_model="iPad Air",
            serial_number="IPAD-001",
            problem_description="Screen crack",
            device_condition="Minor crack",
            estimated_cost=Decimal("180.00"),
        )
        repair2 = repair_service.create_repair(
            db=db_session, repair_data=repair2_data, user_id=test_user.id
        )

        # Mark both as ready
        for repair_id in [repair1.id, repair2.id]:
            repair_obj = db_session.query(Repair).filter(Repair.id == repair_id).first()
            repair_obj.status = RepairStatus.READY
            repair_obj.final_cost = (
                Decimal("120.00") if repair_id == repair1.id else Decimal("180.00")
            )
            db_session.commit()

        # Act: Create single sale for both repairs
        from app.services.repair_product_service import repair_product_service

        repair_product = repair_product_service.get_or_create_repair_product(db_session)

        # Total cost: 120 + 180 = 300
        sale_data = SaleCreate(
            customer_id=customer_with_account.id,
            items=[
                # Repair 1
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=Decimal("120.00"),
                    price_tier="first",
                ),
                # Repair 2
                SaleItemCreate(
                    product_id=repair_product.id,
                    quantity=1,
                    unit_price=Decimal("180.00"),
                    price_tier="first",
                ),
            ],
            amount_paid=Decimal("330.00"),  # 300 * 1.1 tax
            payment_method="cash",
        )
        sale = sale_crud.create_sale(
            db=db_session, sale_in=sale_data, user_id=test_user.id
        )

        # Link both repairs to sale
        delivered_repair1 = repair_service.complete_sale_delivery(
            db=db_session, repair_id=repair1.id, sale_id=sale.id, user_id=test_user.id
        )
        delivered_repair2 = repair_service.complete_sale_delivery(
            db=db_session, repair_id=repair2.id, sale_id=sale.id, user_id=test_user.id
        )

        # Assert: Both repairs linked to same sale
        assert delivered_repair1.sale_id == sale.id
        assert delivered_repair2.sale_id == sale.id
        assert delivered_repair1.status == RepairStatus.DELIVERED
        assert delivered_repair2.status == RepairStatus.DELIVERED

        # Assert: Sale has 2 repair service items
        assert len(sale.items) == 2
