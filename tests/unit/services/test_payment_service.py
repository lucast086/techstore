"""Unit tests for payment service."""

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from app.schemas.payment import PaymentCreate, PaymentMethodDetail
from app.services.payment_service import payment_service


class TestPaymentService:
    """Test payment service functionality."""

    def test_process_single_payment_method(self):
        """Test processing payment with single method."""
        db = Mock()
        customer_id = 1
        sale_id = 10
        user_id = 5

        payment_data = PaymentCreate(
            amount=Decimal("100.00"),
            payment_method="cash",
            reference_number=None,
            notes="Test payment",
        )

        # Mock the CRUD create method and balance service
        with patch("app.crud.payment.payment_crud.create") as mock_create, patch(
            "app.services.balance_service.balance_service.calculate_balance"
        ) as mock_balance, patch(
            "app.crud.sale.sale_crud.get_with_details"
        ) as mock_get_sale:
            mock_payment = Mock(
                id=1,
                receipt_number="PAY-2024-00001",
                amount=Decimal("100.00"),
                sale_id=sale_id,
            )
            mock_create.return_value = mock_payment
            mock_balance.return_value = Decimal("-150.00")  # Customer owes 150

            mock_sale = Mock(
                id=sale_id, total_amount=Decimal("100.00"), payments=[mock_payment]
            )
            mock_get_sale.return_value = mock_sale

            result = payment_service.process_payment(
                db=db,
                customer_id=customer_id,
                sale_id=sale_id,
                payment_data=payment_data,
                user_id=user_id,
            )

            assert result.id == 1
            assert result.receipt_number == "PAY-2024-00001"
            mock_create.assert_called_once()

    def test_process_mixed_payment_methods(self):
        """Test processing payment with multiple methods."""
        db = Mock()
        customer_id = 1
        sale_id = 10
        user_id = 5

        payment_methods = [
            PaymentMethodDetail(
                payment_method="cash", amount=Decimal("50.00"), reference_number=None
            ),
            PaymentMethodDetail(
                payment_method="transfer",
                amount=Decimal("50.00"),
                reference_number="REF123",
            ),
        ]

        with patch("app.crud.payment.payment_crud.create") as mock_create, patch(
            "app.services.balance_service.balance_service.calculate_balance"
        ) as mock_balance, patch(
            "app.crud.sale.sale_crud.get_with_details"
        ) as mock_get_sale:
            mock_payment = Mock(
                id=1, receipt_number="PAY-2024-00001", amount=Decimal("100.00")
            )
            mock_create.return_value = mock_payment
            mock_balance.return_value = Decimal("-150.00")  # Customer owes 150

            mock_sale = Mock(
                id=sale_id, total_amount=Decimal("100.00"), payments=[mock_payment]
            )
            mock_get_sale.return_value = mock_sale

            result = payment_service.process_mixed_payment(
                db=db,
                customer_id=customer_id,
                sale_id=sale_id,
                payment_methods=payment_methods,
                notes="Mixed payment test",
                user_id=user_id,
            )

            assert result.id == 1
            assert result.amount == Decimal("100.00")

    def test_validate_payment_amount_valid(self):
        """Test payment amount validation - valid case."""
        db = Mock()
        customer_id = 1
        payment_amount = Decimal("100.00")

        # Mock balance service
        with patch(
            "app.services.balance_service.balance_service.calculate_balance"
        ) as mock_balance:
            mock_balance.return_value = Decimal("-150.00")  # Customer owes 150

            # Should not raise exception
            payment_service.validate_payment_amount(
                db=db,
                customer_id=customer_id,
                payment_amount=payment_amount,
                allow_overpayment=False,
            )

    def test_validate_payment_amount_overpayment_not_allowed(self):
        """Test payment amount validation - overpayment not allowed."""
        db = Mock()
        customer_id = 1
        payment_amount = Decimal("200.00")

        # Mock balance service
        with patch(
            "app.services.balance_service.balance_service.calculate_balance"
        ) as mock_balance:
            mock_balance.return_value = Decimal("-150.00")  # Customer owes 150

            # Should raise exception
            with pytest.raises(ValueError, match="exceeds outstanding balance"):
                payment_service.validate_payment_amount(
                    db=db,
                    customer_id=customer_id,
                    payment_amount=payment_amount,
                    allow_overpayment=False,
                )

    def test_validate_payment_amount_overpayment_allowed(self):
        """Test payment amount validation - overpayment allowed."""
        db = Mock()
        customer_id = 1
        payment_amount = Decimal("200.00")

        # Mock balance service
        with patch(
            "app.services.balance_service.balance_service.calculate_balance"
        ) as mock_balance:
            mock_balance.return_value = Decimal("-150.00")  # Customer owes 150

            # Should not raise exception when overpayment is allowed
            payment_service.validate_payment_amount(
                db=db,
                customer_id=customer_id,
                payment_amount=payment_amount,
                allow_overpayment=True,
            )

    def test_validate_payment_amount_no_debt(self):
        """Test payment amount validation - no debt."""
        db = Mock()
        customer_id = 1
        payment_amount = Decimal("100.00")

        # Mock balance service
        with patch(
            "app.services.balance_service.balance_service.calculate_balance"
        ) as mock_balance:
            mock_balance.return_value = Decimal("0.00")  # No debt

            # Should raise exception
            with pytest.raises(ValueError, match="no outstanding balance"):
                payment_service.validate_payment_amount(
                    db=db,
                    customer_id=customer_id,
                    payment_amount=payment_amount,
                    allow_overpayment=False,
                )

    def test_generate_receipt_number(self):
        """Test receipt number generation."""
        db = Mock()

        with patch(
            "app.crud.payment.payment_crud.generate_receipt_number"
        ) as mock_generate:
            mock_generate.return_value = "PAY-2024-00001"

            result = payment_service.generate_receipt_number(db)

            assert result == "PAY-2024-00001"
            mock_generate.assert_called_once_with(db)

    def test_update_sale_payment_status_paid(self):
        """Test updating sale payment status to paid."""
        db = Mock()
        sale = Mock(
            id=1,
            total_amount=Decimal("100.00"),
            payments=[Mock(amount=Decimal("100.00"), voided=False)],
        )

        payment_service.update_sale_payment_status(db, sale)

        assert sale.payment_status == "paid"
        db.commit.assert_called_once()

    def test_update_sale_payment_status_partial(self):
        """Test updating sale payment status to partial."""
        db = Mock()
        sale = Mock(
            id=1,
            total_amount=Decimal("100.00"),
            payments=[Mock(amount=Decimal("50.00"), voided=False)],
        )

        payment_service.update_sale_payment_status(db, sale)

        assert sale.payment_status == "partial"
        db.commit.assert_called_once()

    def test_update_sale_payment_status_pending(self):
        """Test updating sale payment status to pending."""
        db = Mock()
        sale = Mock(id=1, total_amount=Decimal("100.00"), payments=[])

        payment_service.update_sale_payment_status(db, sale)

        assert sale.payment_status == "pending"
        db.commit.assert_called_once()
