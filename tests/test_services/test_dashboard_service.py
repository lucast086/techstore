"""Tests for DashboardService."""

from datetime import timedelta
from decimal import Decimal

import pytest
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.models.product import Category, Product
from app.models.repair import Repair
from app.models.sale import Sale
from app.models.user import User
from app.services.dashboard_service import (
    CUSTOMER_DEBT_ALERT_THRESHOLD,
    LOW_STOCK_ALERT_THRESHOLD,
    REPAIRS_RECEIVED_ALERT_THRESHOLD,
    dashboard_service,
)
from app.utils.timezone import get_local_now


class TestDashboardService:
    """Test class for DashboardService."""

    @pytest.fixture
    def test_user(self, db_session):
        """Create a test user for relationships."""
        from app.core.security import get_password_hash

        user = User(
            email="dashboard_test@example.com",
            password_hash=get_password_hash("test_password"),
            full_name="Dashboard Test User",
            role="admin",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def test_category(self, db_session):
        """Create a test category for products."""
        category = Category(
            name="Test Category",
            description="Category for dashboard tests",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def test_product_low_stock(self, db_session, test_user, test_category):
        """Create a product with low stock (current_stock <= minimum_stock, current_stock > 0)."""
        product = Product(
            sku="LOW-STOCK-001",
            name="Low Stock Product",
            description="Product with low stock for testing",
            category_id=test_category.id,
            purchase_price=Decimal("50.00"),
            first_sale_price=Decimal("100.00"),
            second_sale_price=Decimal("90.00"),
            third_sale_price=Decimal("85.00"),
            tax_rate=Decimal("0.00"),
            current_stock=3,
            minimum_stock=5,
            is_active=True,
            is_service=False,
            created_by=test_user.id,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    @pytest.fixture
    def test_product_out_of_stock(self, db_session, test_user, test_category):
        """Create a product with current_stock = 0."""
        product = Product(
            sku="OUT-STOCK-001",
            name="Out of Stock Product",
            description="Product out of stock for testing",
            category_id=test_category.id,
            purchase_price=Decimal("30.00"),
            first_sale_price=Decimal("60.00"),
            second_sale_price=Decimal("55.00"),
            third_sale_price=Decimal("50.00"),
            tax_rate=Decimal("0.00"),
            current_stock=0,
            minimum_stock=5,
            is_active=True,
            is_service=False,
            created_by=test_user.id,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    @pytest.fixture
    def test_product_normal_stock(self, db_session, test_user, test_category):
        """Create a product with normal stock levels."""
        product = Product(
            sku="NORMAL-STOCK-001",
            name="Normal Stock Product",
            description="Product with normal stock for testing",
            category_id=test_category.id,
            purchase_price=Decimal("40.00"),
            first_sale_price=Decimal("80.00"),
            second_sale_price=Decimal("75.00"),
            third_sale_price=Decimal("70.00"),
            tax_rate=Decimal("0.00"),
            current_stock=100,
            minimum_stock=10,
            is_active=True,
            is_service=False,
            created_by=test_user.id,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    @pytest.fixture
    def test_customer(self, db_session, test_user):
        """Create a test customer."""
        customer = Customer(
            name="Dashboard Test Customer",
            phone="5551234567",
            email="dashboard_customer@example.com",
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        return customer

    @pytest.fixture
    def test_customer_with_debt(self, db_session, test_user, test_customer):
        """Create a customer with a CustomerAccount with positive balance (debt)."""
        account = CustomerAccount(
            customer_id=test_customer.id,
            credit_limit=Decimal("1000.00"),
            available_credit=Decimal("0.00"),
            account_balance=Decimal("500.00"),
            total_sales=Decimal("500.00"),
            total_payments=Decimal("0.00"),
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        return account

    @pytest.fixture
    def test_repair_received(self, db_session, test_customer, test_user):
        """Create a repair with status='received'."""
        repair = Repair(
            repair_number="REP-DASH-00001",
            customer_id=test_customer.id,
            device_type="Phone",
            device_brand="Samsung",
            device_model="Galaxy S21",
            problem_description="Screen broken",
            status="received",
            received_by=test_user.id,
            warranty_days=30,
        )
        db_session.add(repair)
        db_session.commit()
        db_session.refresh(repair)
        return repair

    def test_count_repairs_received(self, db_session, test_repair_received):
        """Verify count of repairs with status='received'."""
        count = dashboard_service._count_repairs_received(db_session)

        assert count == 1

    def test_count_repairs_received_multiple(
        self, db_session, test_customer, test_user
    ):
        """Verify count of multiple repairs with status='received'."""
        for i in range(3):
            repair = Repair(
                repair_number=f"REP-DASH-{i:05d}",
                customer_id=test_customer.id,
                device_type="Phone",
                device_brand="Samsung",
                problem_description="Test problem",
                status="received",
                received_by=test_user.id,
                warranty_days=30,
            )
            db_session.add(repair)
        db_session.commit()

        count = dashboard_service._count_repairs_received(db_session)

        assert count == 3

    def test_count_repairs_received_excludes_other_statuses(
        self, db_session, test_customer, test_user
    ):
        """Verify that repairs with other statuses are not counted."""
        statuses = ["received", "diagnosing", "repairing", "completed", "delivered"]
        for i, status in enumerate(statuses):
            repair = Repair(
                repair_number=f"REP-STATUS-{i:05d}",
                customer_id=test_customer.id,
                device_type="Phone",
                device_brand="Samsung",
                problem_description="Test problem",
                status=status,
                received_by=test_user.id,
                warranty_days=30,
            )
            db_session.add(repair)
        db_session.commit()

        count = dashboard_service._count_repairs_received(db_session)

        assert count == 1

    def test_count_low_stock_products(
        self, db_session, test_product_low_stock, test_product_normal_stock
    ):
        """Verify count of low stock products."""
        count = dashboard_service._count_low_stock_products(db_session)

        assert count == 1

    def test_count_low_stock_products_excludes_out_of_stock(
        self, db_session, test_product_low_stock, test_product_out_of_stock
    ):
        """Verify that out of stock products are not counted as low stock."""
        count = dashboard_service._count_low_stock_products(db_session)

        assert count == 1

    def test_count_low_stock_excludes_services(
        self, db_session, test_user, test_category
    ):
        """Verify that service products are excluded from low stock count."""
        service_product = Product(
            sku="SERVICE-001",
            name="Service Product",
            description="Service with low stock setting",
            category_id=test_category.id,
            purchase_price=Decimal("0.00"),
            first_sale_price=Decimal("50.00"),
            second_sale_price=Decimal("50.00"),
            third_sale_price=Decimal("50.00"),
            tax_rate=Decimal("0.00"),
            current_stock=1,
            minimum_stock=10,
            is_active=True,
            is_service=True,
            created_by=test_user.id,
        )
        db_session.add(service_product)
        db_session.commit()

        count = dashboard_service._count_low_stock_products(db_session)

        assert count == 0

    def test_count_low_stock_excludes_inactive(
        self, db_session, test_user, test_category
    ):
        """Verify that inactive products are excluded from low stock count."""
        inactive_product = Product(
            sku="INACTIVE-001",
            name="Inactive Product",
            description="Inactive product with low stock",
            category_id=test_category.id,
            purchase_price=Decimal("10.00"),
            first_sale_price=Decimal("20.00"),
            second_sale_price=Decimal("18.00"),
            third_sale_price=Decimal("15.00"),
            tax_rate=Decimal("0.00"),
            current_stock=1,
            minimum_stock=10,
            is_active=False,
            is_service=False,
            created_by=test_user.id,
        )
        db_session.add(inactive_product)
        db_session.commit()

        count = dashboard_service._count_low_stock_products(db_session)

        assert count == 0

    def test_count_out_of_stock_products(
        self, db_session, test_product_out_of_stock, test_product_normal_stock
    ):
        """Verify count of out of stock products."""
        count = dashboard_service._count_out_of_stock_products(db_session)

        assert count == 1

    def test_count_out_of_stock_excludes_low_stock(
        self, db_session, test_product_out_of_stock, test_product_low_stock
    ):
        """Verify that low stock products are not counted as out of stock."""
        count = dashboard_service._count_out_of_stock_products(db_session)

        assert count == 1

    def test_count_out_of_stock_excludes_services(
        self, db_session, test_user, test_category
    ):
        """Verify that service products are excluded from out of stock count."""
        service_product = Product(
            sku="SERVICE-002",
            name="Service Out of Stock",
            description="Service with zero stock",
            category_id=test_category.id,
            purchase_price=Decimal("0.00"),
            first_sale_price=Decimal("50.00"),
            second_sale_price=Decimal("50.00"),
            third_sale_price=Decimal("50.00"),
            tax_rate=Decimal("0.00"),
            current_stock=0,
            minimum_stock=0,
            is_active=True,
            is_service=True,
            created_by=test_user.id,
        )
        db_session.add(service_product)
        db_session.commit()

        count = dashboard_service._count_out_of_stock_products(db_session)

        assert count == 0

    def test_count_out_of_stock_excludes_inactive(
        self, db_session, test_user, test_category
    ):
        """Verify that inactive products are excluded from out of stock count."""
        inactive_product = Product(
            sku="INACTIVE-002",
            name="Inactive Out of Stock",
            description="Inactive product with zero stock",
            category_id=test_category.id,
            purchase_price=Decimal("10.00"),
            first_sale_price=Decimal("20.00"),
            second_sale_price=Decimal("18.00"),
            third_sale_price=Decimal("15.00"),
            tax_rate=Decimal("0.00"),
            current_stock=0,
            minimum_stock=5,
            is_active=False,
            is_service=False,
            created_by=test_user.id,
        )
        db_session.add(inactive_product)
        db_session.commit()

        count = dashboard_service._count_out_of_stock_products(db_session)

        assert count == 0

    def test_sum_customer_debt(self, db_session, test_customer_with_debt):
        """Verify sum of positive balances."""
        total = dashboard_service._sum_customer_debt(db_session)

        assert total == Decimal("500.00")

    def test_sum_customer_debt_multiple_customers(self, db_session, test_user):
        """Verify sum of multiple customer debts."""
        customers_data = [
            ("Customer A", "5550001111", Decimal("100.00")),
            ("Customer B", "5550002222", Decimal("250.00")),
            ("Customer C", "5550003333", Decimal("150.00")),
        ]

        for name, phone, balance in customers_data:
            customer = Customer(
                name=name,
                phone=phone,
                is_active=True,
                created_by_id=test_user.id,
            )
            db_session.add(customer)
            db_session.flush()

            account = CustomerAccount(
                customer_id=customer.id,
                account_balance=balance,
                credit_limit=Decimal("1000.00"),
                is_active=True,
                created_by_id=test_user.id,
            )
            db_session.add(account)
        db_session.commit()

        total = dashboard_service._sum_customer_debt(db_session)

        assert total == Decimal("500.00")

    def test_sum_customer_debt_excludes_negative_balances(self, db_session, test_user):
        """Verify that negative balances (credits) are not included in debt sum."""
        customer = Customer(
            name="Credit Customer",
            phone="5559999999",
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(customer)
        db_session.flush()

        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("-200.00"),
            credit_limit=Decimal("1000.00"),
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()

        total = dashboard_service._sum_customer_debt(db_session)

        assert total == Decimal("0.00")

    def test_sum_customer_debt_excludes_zero_balances(self, db_session, test_user):
        """Verify that zero balances are not included in debt sum."""
        customer = Customer(
            name="Zero Balance Customer",
            phone="5558888888",
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(customer)
        db_session.flush()

        account = CustomerAccount(
            customer_id=customer.id,
            account_balance=Decimal("0.00"),
            credit_limit=Decimal("1000.00"),
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(account)
        db_session.commit()

        total = dashboard_service._sum_customer_debt(db_session)

        assert total == Decimal("0.00")

    def test_get_today_sales_total(self, db_session, test_user, test_customer):
        """Verify sum of today's sales."""
        sale = Sale(
            invoice_number="INV-DASH-001",
            customer_id=test_customer.id,
            user_id=test_user.id,
            sale_date=get_local_now(),
            subtotal=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
            payment_status="paid",
            payment_method="cash",
            is_voided=False,
        )
        db_session.add(sale)
        db_session.commit()

        total = dashboard_service._get_today_sales_total(db_session)

        assert total == Decimal("100.00")

    def test_get_today_sales_total_multiple_sales(
        self, db_session, test_user, test_customer
    ):
        """Verify sum of multiple today's sales."""
        for i in range(3):
            sale = Sale(
                invoice_number=f"INV-DASH-{i:03d}",
                customer_id=test_customer.id,
                user_id=test_user.id,
                sale_date=get_local_now(),
                subtotal=Decimal("100.00"),
                discount_amount=Decimal("0.00"),
                tax_amount=Decimal("0.00"),
                total_amount=Decimal("100.00"),
                payment_status="paid",
                payment_method="cash",
                is_voided=False,
            )
            db_session.add(sale)
        db_session.commit()

        total = dashboard_service._get_today_sales_total(db_session)

        assert total == Decimal("300.00")

    def test_get_today_sales_total_excludes_voided(
        self, db_session, test_user, test_customer
    ):
        """Verify that voided sales are excluded from today's total."""
        valid_sale = Sale(
            invoice_number="INV-VALID-001",
            customer_id=test_customer.id,
            user_id=test_user.id,
            sale_date=get_local_now(),
            subtotal=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
            payment_status="paid",
            payment_method="cash",
            is_voided=False,
        )
        db_session.add(valid_sale)

        voided_sale = Sale(
            invoice_number="INV-VOIDED-001",
            customer_id=test_customer.id,
            user_id=test_user.id,
            sale_date=get_local_now(),
            subtotal=Decimal("200.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("200.00"),
            payment_status="paid",
            payment_method="cash",
            is_voided=True,
            void_reason="Test void",
        )
        db_session.add(voided_sale)
        db_session.commit()

        total = dashboard_service._get_today_sales_total(db_session)

        assert total == Decimal("100.00")

    def test_get_today_sales_total_excludes_past_sales(
        self, db_session, test_user, test_customer
    ):
        """Verify that past sales are excluded from today's total."""
        today_sale = Sale(
            invoice_number="INV-TODAY-001",
            customer_id=test_customer.id,
            user_id=test_user.id,
            sale_date=get_local_now(),
            subtotal=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("100.00"),
            payment_status="paid",
            payment_method="cash",
            is_voided=False,
        )
        db_session.add(today_sale)

        yesterday_sale = Sale(
            invoice_number="INV-YESTERDAY-001",
            customer_id=test_customer.id,
            user_id=test_user.id,
            sale_date=get_local_now() - timedelta(days=1),
            subtotal=Decimal("500.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("500.00"),
            payment_status="paid",
            payment_method="cash",
            is_voided=False,
        )
        db_session.add(yesterday_sale)
        db_session.commit()

        total = dashboard_service._get_today_sales_total(db_session)

        assert total == Decimal("100.00")

    def test_get_today_sales_total_no_sales(self, db_session):
        """Verify that zero is returned when there are no sales."""
        total = dashboard_service._get_today_sales_total(db_session)

        assert total == Decimal("0.00")

    def test_get_dashboard_stats_returns_all_metrics(
        self,
        db_session,
        test_repair_received,
        test_product_low_stock,
        test_product_out_of_stock,
        test_customer_with_debt,
    ):
        """Verify the main method returns all expected keys."""
        stats = dashboard_service.get_dashboard_stats(db_session)

        expected_keys = [
            "repairs_received",
            "repairs_received_alert",
            "low_stock_count",
            "low_stock_alert",
            "out_of_stock_count",
            "customer_debt_total",
            "debt_alert",
            "today_sales_total",
        ]

        for key in expected_keys:
            assert key in stats, f"Missing key: {key}"

        assert stats["repairs_received"] == 1
        assert stats["low_stock_count"] == 1
        assert stats["out_of_stock_count"] == 1
        assert stats["customer_debt_total"] == Decimal("500.00")
        assert stats["today_sales_total"] == Decimal("0.00")

    def test_get_dashboard_stats_empty_database(self, db_session):
        """Verify dashboard stats with empty database."""
        stats = dashboard_service.get_dashboard_stats(db_session)

        assert stats["repairs_received"] == 0
        assert stats["repairs_received_alert"] is False
        assert stats["low_stock_count"] == 0
        assert stats["low_stock_alert"] is False
        assert stats["out_of_stock_count"] == 0
        assert stats["customer_debt_total"] == Decimal("0.00")
        assert stats["debt_alert"] is False
        assert stats["today_sales_total"] == Decimal("0.00")

    def test_alerts_triggered_when_thresholds_exceeded(
        self, db_session, test_customer, test_user, test_category
    ):
        """Verify alert flags are True when thresholds exceeded."""
        repairs_count = REPAIRS_RECEIVED_ALERT_THRESHOLD + 1
        for i in range(repairs_count):
            repair = Repair(
                repair_number=f"REP-ALERT-{i:05d}",
                customer_id=test_customer.id,
                device_type="Phone",
                device_brand="Samsung",
                problem_description="Test problem",
                status="received",
                received_by=test_user.id,
                warranty_days=30,
            )
            db_session.add(repair)

        low_stock_count = LOW_STOCK_ALERT_THRESHOLD + 1
        for i in range(low_stock_count):
            product = Product(
                sku=f"LOW-ALERT-{i:03d}",
                name=f"Low Stock Alert Product {i}",
                category_id=test_category.id,
                purchase_price=Decimal("10.00"),
                first_sale_price=Decimal("20.00"),
                second_sale_price=Decimal("18.00"),
                third_sale_price=Decimal("15.00"),
                tax_rate=Decimal("0.00"),
                current_stock=1,
                minimum_stock=10,
                is_active=True,
                is_service=False,
                created_by=test_user.id,
            )
            db_session.add(product)

        high_debt_customer = Customer(
            name="High Debt Customer",
            phone="5557777777",
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(high_debt_customer)
        db_session.flush()

        debt_amount = CUSTOMER_DEBT_ALERT_THRESHOLD + Decimal("1.00")
        high_debt_account = CustomerAccount(
            customer_id=high_debt_customer.id,
            account_balance=debt_amount,
            credit_limit=Decimal("10000000.00"),
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(high_debt_account)
        db_session.commit()

        stats = dashboard_service.get_dashboard_stats(db_session)

        assert stats["repairs_received"] == repairs_count
        assert stats["repairs_received_alert"] is True

        assert stats["low_stock_count"] == low_stock_count
        assert stats["low_stock_alert"] is True

        assert stats["customer_debt_total"] == debt_amount
        assert stats["debt_alert"] is True

    def test_alerts_not_triggered_at_threshold(
        self, db_session, test_customer, test_user, test_category
    ):
        """Verify alert flags are False when at exact threshold values."""
        repairs_count = REPAIRS_RECEIVED_ALERT_THRESHOLD
        for i in range(repairs_count):
            repair = Repair(
                repair_number=f"REP-THRESHOLD-{i:05d}",
                customer_id=test_customer.id,
                device_type="Phone",
                device_brand="Samsung",
                problem_description="Test problem",
                status="received",
                received_by=test_user.id,
                warranty_days=30,
            )
            db_session.add(repair)

        low_stock_count = LOW_STOCK_ALERT_THRESHOLD
        for i in range(low_stock_count):
            product = Product(
                sku=f"LOW-THRESHOLD-{i:03d}",
                name=f"Low Stock Threshold Product {i}",
                category_id=test_category.id,
                purchase_price=Decimal("10.00"),
                first_sale_price=Decimal("20.00"),
                second_sale_price=Decimal("18.00"),
                third_sale_price=Decimal("15.00"),
                tax_rate=Decimal("0.00"),
                current_stock=1,
                minimum_stock=10,
                is_active=True,
                is_service=False,
                created_by=test_user.id,
            )
            db_session.add(product)

        threshold_customer = Customer(
            name="Threshold Debt Customer",
            phone="5556666666",
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(threshold_customer)
        db_session.flush()

        debt_amount = CUSTOMER_DEBT_ALERT_THRESHOLD
        threshold_account = CustomerAccount(
            customer_id=threshold_customer.id,
            account_balance=debt_amount,
            credit_limit=Decimal("10000000.00"),
            is_active=True,
            created_by_id=test_user.id,
        )
        db_session.add(threshold_account)
        db_session.commit()

        stats = dashboard_service.get_dashboard_stats(db_session)

        assert stats["repairs_received"] == repairs_count
        assert stats["repairs_received_alert"] is False

        assert stats["low_stock_count"] == low_stock_count
        assert stats["low_stock_alert"] is False

        assert stats["customer_debt_total"] == debt_amount
        assert stats["debt_alert"] is False
