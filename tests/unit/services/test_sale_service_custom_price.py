"""Tests for custom pricing in sale service."""

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from app.schemas.sale import SaleItemCreate
from app.services.sale_service import SaleService


class TestSaleServiceCustomPrice:
    """Test custom pricing functionality in sale service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SaleService()
        self.db = Mock()

    def test_add_item_with_custom_price(self):
        """Test adding an item to sale with custom price."""
        # Mock product
        mock_product = Mock(
            id=1, name="Test Product", selling_price=Decimal("30.00"), stock=10
        )

        item_data = SaleItemCreate(
            product_id=1,
            quantity=2,
            unit_price=Decimal("25.99"),  # Custom price different from product price
            is_custom_price=True,
        )

        with patch("app.crud.product.product.get") as mock_get_product:
            mock_get_product.return_value = mock_product

            result = self.service.add_sale_item(self.db, sale_id=1, item_data=item_data)

            # Verify custom price was used
            assert result.unit_price == Decimal("25.99")
            assert result.is_custom_price is True
            assert result.total_price == Decimal("51.98")  # 25.99 * 2

    def test_add_item_with_standard_price(self):
        """Test adding an item to sale with standard price."""
        # Mock product
        mock_product = Mock(
            id=1, name="Test Product", selling_price=Decimal("30.00"), stock=10
        )

        item_data = SaleItemCreate(
            product_id=1,
            quantity=2,
            is_custom_price=False,  # Using standard price
        )

        with patch("app.crud.product.product.get") as mock_get_product:
            mock_get_product.return_value = mock_product

            result = self.service.add_sale_item(self.db, sale_id=1, item_data=item_data)

            # Verify standard price was used
            assert result.unit_price == Decimal("30.00")
            assert result.is_custom_price is False
            assert result.total_price == Decimal("60.00")  # 30.00 * 2

    def test_validate_custom_price_minimum(self):
        """Test that custom price cannot be negative."""
        item_data = SaleItemCreate(
            product_id=1,
            quantity=1,
            unit_price=Decimal("-10.00"),  # Negative price
            is_custom_price=True,
        )

        with pytest.raises(ValueError, match="Custom price cannot be negative"):
            self.service.validate_custom_price(item_data)

    def test_validate_custom_price_maximum(self):
        """Test that custom price has reasonable maximum."""
        item_data = SaleItemCreate(
            product_id=1,
            quantity=1,
            unit_price=Decimal("1000000.00"),  # Unreasonably high
            is_custom_price=True,
        )

        with pytest.raises(ValueError, match="Custom price exceeds maximum allowed"):
            self.service.validate_custom_price(item_data)

    def test_custom_price_in_receipt(self):
        """Test that custom price is indicated in receipt."""
        mock_sale = Mock(
            id=1,
            invoice_number="INV-001",
            items=[
                Mock(
                    product=Mock(name="Product 1"),
                    quantity=1,
                    unit_price=Decimal("25.99"),
                    is_custom_price=True,
                    total_price=Decimal("25.99"),
                ),
                Mock(
                    product=Mock(name="Product 2"),
                    quantity=2,
                    unit_price=Decimal("30.00"),
                    is_custom_price=False,
                    total_price=Decimal("60.00"),
                ),
            ],
        )

        receipt = self.service.generate_receipt_data(mock_sale)

        # Verify custom price is marked in receipt
        assert receipt["items"][0]["is_custom_price"] is True
        assert receipt["items"][0]["price_note"] == "Custom Price"
        assert receipt["items"][1]["is_custom_price"] is False
        assert receipt["items"][1]["price_note"] == ""
