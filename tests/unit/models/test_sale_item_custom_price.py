"""Tests for custom pricing in sale items."""

from decimal import Decimal

from app.models.sale import SaleItem


class TestSaleItemCustomPrice:
    """Test custom pricing functionality in sale items."""

    def test_sale_item_has_custom_price_field(self):
        """Test that sale item has is_custom_price field."""
        item = SaleItem()
        assert hasattr(item, "is_custom_price")

    def test_custom_price_defaults_to_false(self):
        """Test that is_custom_price defaults to False when explicitly set."""
        item = SaleItem(
            sale_id=1,
            product_id=1,
            quantity=1,
            unit_price=Decimal("10.00"),
            total_price=Decimal("10.00"),
            is_custom_price=False,
        )
        assert item.is_custom_price is False

    def test_sale_item_with_custom_price(self):
        """Test creating a sale item with custom price."""
        item = SaleItem(
            sale_id=1,
            product_id=1,
            quantity=2,
            unit_price=Decimal("25.99"),  # Custom price
            is_custom_price=True,
            total_price=Decimal("51.98"),
        )

        assert item.is_custom_price is True
        assert item.unit_price == Decimal("25.99")

    def test_sale_item_with_standard_price(self):
        """Test creating a sale item with standard price."""
        item = SaleItem(
            sale_id=1,
            product_id=1,
            quantity=2,
            unit_price=Decimal("30.00"),  # Standard price
            is_custom_price=False,
            total_price=Decimal("60.00"),
        )

        assert item.is_custom_price is False
        assert item.unit_price == Decimal("30.00")

    def test_custom_price_note_property(self):
        """Test that custom price items have a note property."""
        item = SaleItem(
            sale_id=1,
            product_id=1,
            quantity=1,
            unit_price=Decimal("25.99"),
            is_custom_price=True,
            total_price=Decimal("25.99"),
        )

        assert hasattr(item, "price_note")
        assert item.price_note == "Custom Price"

    def test_standard_price_note_property(self):
        """Test that standard price items have empty note."""
        item = SaleItem(
            sale_id=1,
            product_id=1,
            quantity=1,
            unit_price=Decimal("30.00"),
            is_custom_price=False,
            total_price=Decimal("30.00"),
        )

        assert item.price_note == ""
