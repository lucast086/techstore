"""Unit tests for repair deposit service."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from app.models.repair_deposit import DepositStatus, PaymentMethod
from app.schemas.repair_deposit import DepositCreate
from app.services.repair_deposit_service import repair_deposit_service
from sqlalchemy.orm import Session


class TestRepairDepositService:
    """Test cases for repair deposit service."""

    def test_record_deposit_success(self):
        """Test successfully recording a deposit."""
        # Arrange
        db = MagicMock(spec=Session)
        deposit_data = DepositCreate(
            repair_id=1,
            customer_id=1,
            amount=Decimal("100.00"),
            payment_method=PaymentMethod.CASH,
            notes="Test deposit",
        )
        received_by_id = 1

        # Mock repair exists
        mock_repair = MagicMock()
        mock_repair.customer_id = 1
        mock_repair.repair_number = "REP001"

        # Mock deposit creation
        mock_deposit = MagicMock()
        mock_deposit.id = 1
        mock_deposit.receipt_number = "DEP000001"
        mock_deposit.amount = Decimal("100.00")
        mock_deposit.status = DepositStatus.ACTIVE
        mock_deposit.repair = mock_repair
        mock_deposit.customer = MagicMock(name="Test Customer")
        mock_deposit.received_by = MagicMock(full_name="Test User")
        mock_deposit.refunded_by = None
        mock_deposit.created_at = MagicMock()
        mock_deposit.updated_at = MagicMock()

        # Mock transaction
        mock_transaction = MagicMock()
        mock_transaction.id = 1

        from app.services import repair_deposit_service

        with patch.object(repair_deposit_service, "repair_crud") as mock_repair_crud:
            with patch.object(
                repair_deposit_service, "repair_deposit_crud"
            ) as mock_deposit_crud:
                with patch.object(
                    repair_deposit_service, "customer_account_service"
                ) as mock_account_service:
                    # Setup mocks
                    mock_repair_crud.get_repair.return_value = mock_repair
                    mock_deposit_crud.create_deposit.return_value = mock_deposit
                    mock_account_service.record_transaction.return_value = (
                        mock_transaction
                    )

                    # Act
                    result = repair_deposit_service.record_deposit(
                        db=db, deposit_data=deposit_data, received_by_id=received_by_id
                    )

                    # Assert
                    assert result is not None
                    assert result.receipt_number == "DEP000001"
                    assert result.amount == Decimal("100.00")
                    assert result.status == DepositStatus.ACTIVE

                    # Verify calls
                    mock_repair_crud.get_repair.assert_called_once_with(db, 1)
                    mock_deposit_crud.create_deposit.assert_called_once()
                    mock_account_service.record_transaction.assert_called_once()
                    db.commit.assert_called_once()

    def test_record_deposit_repair_not_found(self):
        """Test recording deposit when repair doesn't exist."""
        # Arrange
        db = MagicMock(spec=Session)
        deposit_data = DepositCreate(
            repair_id=999,
            customer_id=1,
            amount=Decimal("100.00"),
            payment_method=PaymentMethod.CASH,
            notes="Test deposit",
        )
        received_by_id = 1

        with patch("app.crud.repair.repair_crud") as mock_repair_crud:
            # Setup mock
            mock_repair_crud.get_repair.return_value = None

            # Act & Assert
            with pytest.raises(ValueError, match="Repair 999 not found"):
                repair_deposit_service.record_deposit(
                    db=db, deposit_data=deposit_data, received_by_id=received_by_id
                )

    def test_record_deposit_customer_mismatch(self):
        """Test recording deposit when customer doesn't match repair."""
        # Arrange
        db = MagicMock(spec=Session)
        deposit_data = DepositCreate(
            repair_id=1,
            customer_id=2,  # Different customer
            amount=Decimal("100.00"),
            payment_method=PaymentMethod.CASH,
            notes="Test deposit",
        )
        received_by_id = 1

        # Mock repair with different customer
        mock_repair = MagicMock()
        mock_repair.customer_id = 1  # Different from deposit_data.customer_id

        with patch("app.crud.repair.repair_crud") as mock_repair_crud:
            # Setup mock
            mock_repair_crud.get_repair.return_value = mock_repair

            # Act & Assert
            with pytest.raises(ValueError, match="Customer does not match repair"):
                repair_deposit_service.record_deposit(
                    db=db, deposit_data=deposit_data, received_by_id=received_by_id
                )

    def test_calculate_total_deposits(self):
        """Test calculating total deposits for a repair."""
        # Arrange
        db = MagicMock(spec=Session)
        repair_id = 1

        with patch("app.crud.repair_deposit.repair_deposit_crud") as mock_deposit_crud:
            # Setup mock
            mock_deposit_crud.calculate_total_deposits.return_value = Decimal("250.00")

            # Act
            result = repair_deposit_service.calculate_total_deposits(db, repair_id)

            # Assert
            assert result == Decimal("250.00")
            mock_deposit_crud.calculate_total_deposits.assert_called_once_with(
                db, repair_id, None
            )

    def test_refund_deposit_success(self):
        """Test successfully refunding a deposit."""
        # Arrange
        db = MagicMock(spec=Session)
        deposit_id = 1
        refunded_by_id = 1

        from app.schemas.repair_deposit import DepositRefund

        refund_data = DepositRefund(
            refund_amount=Decimal("50.00"), refund_reason="Customer request"
        )

        # Mock deposit
        mock_deposit = MagicMock()
        mock_deposit.id = 1
        mock_deposit.receipt_number = "DEP000001"
        mock_deposit.amount = Decimal("100.00")
        mock_deposit.customer_id = 1
        mock_deposit.repair = MagicMock(repair_number="REP001")
        mock_deposit.customer = MagicMock(name="Test Customer")
        mock_deposit.received_by = MagicMock(full_name="Test User")
        mock_deposit.refunded_by = MagicMock(full_name="Refund User")
        mock_deposit.status = DepositStatus.REFUNDED
        mock_deposit.refunded_amount = Decimal("50.00")
        mock_deposit.refund_date = MagicMock()
        mock_deposit.refund_reason = "Customer request"
        mock_deposit.created_at = MagicMock()
        mock_deposit.updated_at = MagicMock()

        # Mock transaction
        mock_transaction = MagicMock()
        mock_transaction.id = 2

        with patch("app.crud.repair_deposit.repair_deposit_crud") as mock_deposit_crud:
            with patch(
                "app.services.customer_account_service.customer_account_service"
            ) as mock_account_service:
                # Setup mocks
                mock_deposit_crud.get_deposit.return_value = mock_deposit
                mock_deposit_crud.refund_deposit.return_value = mock_deposit
                mock_account_service.record_transaction.return_value = mock_transaction

                # Act
                result = repair_deposit_service.refund_deposit(
                    db=db,
                    deposit_id=deposit_id,
                    refund_data=refund_data,
                    refunded_by_id=refunded_by_id,
                )

                # Assert
                assert result is not None
                assert result.receipt_number == "DEP000001"
                assert result.status == DepositStatus.REFUNDED
                assert result.refunded_amount == Decimal("50.00")

                # Verify calls
                mock_deposit_crud.get_deposit.assert_called_once_with(db, deposit_id)
                mock_deposit_crud.refund_deposit.assert_called_once()
                mock_account_service.record_transaction.assert_called_once()
                db.commit.assert_called_once()

    def test_refund_deposit_not_found(self):
        """Test refunding a deposit that doesn't exist."""
        # Arrange
        db = MagicMock(spec=Session)
        deposit_id = 999
        refunded_by_id = 1

        from app.schemas.repair_deposit import DepositRefund

        refund_data = DepositRefund(
            refund_amount=Decimal("50.00"), refund_reason="Customer request"
        )

        with patch("app.crud.repair_deposit.repair_deposit_crud") as mock_deposit_crud:
            # Setup mock
            mock_deposit_crud.get_deposit.return_value = None

            # Act & Assert
            with pytest.raises(ValueError, match="Deposit 999 not found"):
                repair_deposit_service.refund_deposit(
                    db=db,
                    deposit_id=deposit_id,
                    refund_data=refund_data,
                    refunded_by_id=refunded_by_id,
                )
