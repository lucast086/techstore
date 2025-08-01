"""Tests for invoice service."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.user import User
from app.services.invoice_service import invoice_service


class TestInvoiceService:
    """Test cases for InvoiceService."""

    @pytest.fixture
    def mock_sale(self):
        """Create a mock sale with items."""
        # Mock customer
        customer = MagicMock(spec=Customer)
        customer.name = "John Doe"
        customer.phone = "1234567890"
        customer.email = "john@example.com"
        customer.address = "123 Test St"

        # Mock user
        user = MagicMock(spec=User)
        user.full_name = "Test Cashier"

        # Mock products
        product1 = MagicMock(spec=Product)
        product1.name = "Test Product 1"
        product1.sku = "TEST001"

        product2 = MagicMock(spec=Product)
        product2.name = "Test Product 2"
        product2.sku = "TEST002"

        # Mock sale items
        item1 = MagicMock(spec=SaleItem)
        item1.product = product1
        item1.quantity = 2
        item1.unit_price = Decimal("50.00")
        item1.discount_percentage = Decimal("10.00")
        item1.discount_amount = Decimal("0.00")
        item1.total_price = Decimal("90.00")

        item2 = MagicMock(spec=SaleItem)
        item2.product = product2
        item2.quantity = 1
        item2.unit_price = Decimal("100.00")
        item2.discount_percentage = Decimal("0.00")
        item2.discount_amount = Decimal("5.00")
        item2.total_price = Decimal("95.00")

        # Mock sale
        sale = MagicMock(spec=Sale)
        sale.invoice_number = "INV-2024-00001"
        sale.customer = customer
        sale.user = user
        sale.sale_date = datetime(2024, 1, 15, 14, 30, 0)
        sale.subtotal = Decimal("200.00")
        sale.discount_amount = Decimal("15.00")
        sale.tax_amount = Decimal("29.60")
        sale.total_amount = Decimal("214.60")
        sale.payment_status = "paid"
        sale.payment_method = "cash"
        sale.amount_due = Decimal("0.00")
        sale.items = [item1, item2]
        sale.notes = "Test sale notes"

        return sale

    def test_generate_invoice_pdf(self, mock_sale):
        """Test PDF invoice generation."""
        pdf_bytes = invoice_service.generate_invoice_pdf(mock_sale)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDF files start with %PDF
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_invoice_pdf_walk_in_customer(self, mock_sale):
        """Test PDF invoice generation for walk-in customer."""
        mock_sale.customer = None

        pdf_bytes = invoice_service.generate_invoice_pdf(mock_sale)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_invoice_pdf_with_payment_notes(self, mock_sale):
        """Test PDF invoice generation with payment details in notes."""
        mock_sale.notes = "Amount received: $250.00\nTest notes\nMore notes"

        pdf_bytes = invoice_service.generate_invoice_pdf(mock_sale)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # Payment details should be filtered out from notes display

    def test_generate_invoice_pdf_pending_payment(self, mock_sale):
        """Test PDF invoice generation for pending payment."""
        mock_sale.payment_status = "pending"
        mock_sale.amount_due = Decimal("214.60")

        pdf_bytes = invoice_service.generate_invoice_pdf(mock_sale)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_invoice_pdf_partial_payment(self, mock_sale):
        """Test PDF invoice generation for partial payment."""
        mock_sale.payment_status = "partial"
        mock_sale.amount_due = Decimal("100.00")

        pdf_bytes = invoice_service.generate_invoice_pdf(mock_sale)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_credit_note(self, mock_sale):
        """Test credit note generation."""
        reason = "Customer return - defective product"

        pdf_bytes = invoice_service.generate_credit_note(mock_sale, reason)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_credit_note_partial_amount(self, mock_sale):
        """Test credit note generation with partial amount."""
        reason = "Partial refund - price adjustment"
        amount = Decimal("50.00")

        pdf_bytes = invoice_service.generate_credit_note(mock_sale, reason, amount)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_credit_note_no_customer(self, mock_sale):
        """Test credit note generation for walk-in customer."""
        mock_sale.customer = None
        reason = "Sale cancellation"

        pdf_bytes = invoice_service.generate_credit_note(mock_sale, reason)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_format_payment_status(self):
        """Test payment status formatting."""
        assert invoice_service._format_payment_status("paid") == "Paid"
        assert invoice_service._format_payment_status("partial") == "Partially Paid"
        assert invoice_service._format_payment_status("pending") == "Pending Payment"
        assert invoice_service._format_payment_status("unknown") == "Unknown"
