"""Invoice service for generating and managing invoices."""

import logging
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from app.models.sale import Sale

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service for handling invoice generation and management."""

    def generate_invoice_pdf(self, sale: Sale) -> bytes:
        """Generate PDF invoice for a sale.

        Args:
            sale: Sale object to generate invoice for.

        Returns:
            PDF content as bytes.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Container for the 'Flowable' objects
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=30,
            alignment=1,  # Center alignment
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=12,
        )

        # Title
        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Company info
        company_info = [
            ["TechStore", f"Invoice #: {sale.invoice_number}"],
            ["123 Main Street", f"Date: {sale.sale_date.strftime('%Y-%m-%d')}"],
            ["City, State 12345", f"Time: {sale.sale_date.strftime('%H:%M')}"],
            ["Phone: (555) 123-4567", ""],
            ["Email: info@techstore.com", ""],
        ]

        company_table = Table(company_info, colWidths=[3 * inch, 3 * inch])
        company_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("FONTSIZE", (0, 0), (0, 0), 14),
                    ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor("#2c3e50")),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(company_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Customer info
        if sale.customer:
            elements.append(Paragraph("Bill To:", heading_style))
            customer_info = [
                [f"Customer: {sale.customer.name}"],
                [f"Phone: {sale.customer.phone}"],
            ]
            if sale.customer.email:
                customer_info.append([f"Email: {sale.customer.email}"])
            if sale.customer.address:
                customer_info.append([f"Address: {sale.customer.address}"])

            customer_table = Table(customer_info, colWidths=[6 * inch])
            customer_table.setStyle(
                TableStyle(
                    [
                        ("FONT", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            elements.append(customer_table)
        else:
            elements.append(Paragraph("Bill To: Walk-in Customer", heading_style))

        elements.append(Spacer(1, 0.3 * inch))

        # Items table
        items_data = [["Item", "SKU", "Qty", "Unit Price", "Discount", "Total"]]

        for item in sale.items:
            discount_text = ""
            if item.discount_percentage > 0:
                discount_text = f"{item.discount_percentage}%"
            elif item.discount_amount > 0:
                discount_text = f"${item.discount_amount}"

            items_data.append(
                [
                    item.product.name,
                    item.product.sku,
                    str(item.quantity),
                    f"${item.unit_price:.2f}",
                    discount_text,
                    f"${item.total_price:.2f}",
                ]
            )

        items_table = Table(
            items_data,
            colWidths=[
                2.5 * inch,
                1 * inch,
                0.7 * inch,
                1 * inch,
                0.8 * inch,
                1 * inch,
            ],
        )
        items_table.setStyle(
            TableStyle(
                [
                    # Header row
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    # Data rows
                    ("FONT", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("ALIGN", (2, 1), (2, -1), "CENTER"),  # Qty
                    ("ALIGN", (3, 1), (5, -1), "RIGHT"),  # Prices
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # Alternating row colors
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#ecf0f1")],
                    ),
                ]
            )
        )
        elements.append(items_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Totals
        totals_data = []
        totals_data.append(["Subtotal:", f"${sale.subtotal:.2f}"])
        if sale.discount_amount > 0:
            totals_data.append(["Discount:", f"-${sale.discount_amount:.2f}"])
        if sale.tax_amount > 0:
            totals_data.append(["Tax:", f"${sale.tax_amount:.2f}"])
        totals_data.append(["Total:", f"${sale.total_amount:.2f}"])

        totals_table = Table(totals_data, colWidths=[5 * inch, 1 * inch])
        totals_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONT", (0, 0), (-1, -2), "Helvetica"),
                    ("FONT", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
                    ("TEXTCOLOR", (1, 1), (1, 1), colors.red),  # Discount in red
                ]
            )
        )
        elements.append(totals_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Payment info
        payment_data = [
            [
                "Payment Method:",
                sale.payment_method.capitalize() if sale.payment_method else "N/A",
            ],
            ["Payment Status:", self._format_payment_status(sale.payment_status)],
        ]

        if sale.payment_status != "paid":
            payment_data.append(["Amount Due:", f"${sale.amount_due:.2f}"])

        payment_table = Table(payment_data, colWidths=[5 * inch, 1 * inch])
        payment_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONT", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                ]
            )
        )
        elements.append(payment_table)

        # Footer
        elements.append(Spacer(1, 0.5 * inch))
        footer_text = "Thank you for your business!"
        elements.append(Paragraph(footer_text, styles["Normal"]))

        if sale.notes:
            # Filter out payment details from notes
            display_notes = []
            for line in sale.notes.split("\n"):
                if not any(
                    prefix in line
                    for prefix in [
                        "Amount received:",
                        "Payment breakdown:",
                        "Reference:",
                    ]
                ):
                    if line.strip():
                        display_notes.append(line)

            if display_notes:
                elements.append(Spacer(1, 0.2 * inch))
                elements.append(Paragraph("Notes:", heading_style))
                elements.append(Paragraph("\n".join(display_notes), styles["Normal"]))

        # Build PDF
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _format_payment_status(self, status: str) -> str:
        """Format payment status for display."""
        status_map = {
            "paid": "Paid",
            "partial": "Partially Paid",
            "pending": "Pending Payment",
        }
        return status_map.get(status, status.capitalize())

    def generate_credit_note(
        self, sale: Sale, reason: str, amount: Optional[Decimal] = None
    ) -> bytes:
        """Generate credit note PDF for a voided or adjusted sale.

        Args:
            sale: Original sale to create credit note for.
            reason: Reason for the credit note.
            amount: Credit amount (if None, uses full sale amount).

        Returns:
            PDF content as bytes.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "CreditTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.red,
            spaceAfter=30,
            alignment=1,
        )

        elements.append(Paragraph("CREDIT NOTE", title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Credit note info
        credit_amount = amount or sale.total_amount
        credit_info = [
            ["Credit Note Date:", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Original Invoice:", sale.invoice_number],
            ["Original Date:", sale.sale_date.strftime("%Y-%m-%d")],
            ["Credit Amount:", f"${credit_amount:.2f}"],
            ["Reason:", reason],
        ]

        credit_table = Table(credit_info, colWidths=[2 * inch, 4 * inch])
        credit_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(credit_table)

        # Customer info
        if sale.customer:
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(Paragraph("Customer:", styles["Heading3"]))
            customer_text = f"{sale.customer.name}<br/>"
            if sale.customer.phone:
                customer_text += f"Phone: {sale.customer.phone}<br/>"
            elements.append(Paragraph(customer_text, styles["Normal"]))

        # Build PDF
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def email_invoice(self, db: Session, sale_id: int, recipient_email: str) -> bool:
        """Email invoice to customer.

        Args:
            db: Database session.
            sale_id: ID of sale to send invoice for.
            recipient_email: Email address to send to.

        Returns:
            True if sent successfully, False otherwise.
        """
        # TODO: Implement email functionality
        # This would integrate with an email service like SendGrid or AWS SES
        logger.info(
            f"Email invoice functionality not yet implemented for sale {sale_id}"
        )
        return False


invoice_service = InvoiceService()
