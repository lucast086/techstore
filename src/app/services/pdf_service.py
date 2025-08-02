"""PDF generation service for various documents."""

import io
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.cash_closing import CashClosing
from app.models.user import User

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF documents."""

    def generate_cash_closing_pdf(
        self, closing: CashClosing, user: Optional[User] = None
    ) -> bytes:
        """Generate PDF document for cash closing.

        Args:
            closing: CashClosing instance with all details.
            user: User who closed the register (optional if included in closing).

        Returns:
            PDF document as bytes.
        """
        logger.info(f"Generating PDF for cash closing {closing.id}")

        # Create PDF buffer
        buffer = io.BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Container for the 'Flowable' objects
        elements = []

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1d4ed8"),
            spaceAfter=30,
            alignment=1,  # Center
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#374151"),
            spaceAfter=12,
        )

        # Title
        elements.append(Paragraph("Daily Cash Closing Report", title_style))
        elements.append(Spacer(1, 12))

        # Store Information
        store_info = [
            ["TechStore SaaS"],
            [f"Date: {closing.closing_date.strftime('%B %d, %Y')}"],
            [f"Closing ID: #{closing.id}"],
        ]
        store_table = Table(store_info, colWidths=[6 * inch])
        store_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (0, 0), 14),
                    ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor("#374151")),
                ]
            )
        )
        elements.append(store_table)
        elements.append(Spacer(1, 20))

        # Financial Summary
        elements.append(Paragraph("Financial Summary", heading_style))

        financial_data = [
            ["Description", "Amount"],
            ["Opening Balance", f"${closing.opening_balance:.2f}"],
            ["Total Sales", f"${closing.sales_total:.2f}"],
            ["Total Expenses", f"-${closing.expenses_total:.2f}"],
            ["", ""],  # Empty row for separation
            ["Expected Cash", f"${closing.expected_cash:.2f}"],
            ["Actual Cash Count", f"${closing.cash_count:.2f}"],
            ["", ""],  # Empty row for separation
            ["Cash Difference", self._format_difference(closing.cash_difference)],
        ]

        financial_table = Table(financial_data, colWidths=[4 * inch, 2 * inch])
        financial_table.setStyle(
            TableStyle(
                [
                    # Header row
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    # Grid
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    # Special formatting for totals
                    ("FONTNAME", (0, 5), (-1, 6), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 5), (-1, 6), colors.HexColor("#f3f4f6")),
                    # Cash difference formatting
                    ("FONTNAME", (0, 8), (-1, 8), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 8), (-1, 8), 12),
                    (
                        "BACKGROUND",
                        (0, 8),
                        (-1, 8),
                        self._get_difference_color(closing.cash_difference),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 8),
                        (-1, 8),
                        self._get_difference_text_color(closing.cash_difference),
                    ),
                ]
            )
        )
        elements.append(financial_table)
        elements.append(Spacer(1, 20))

        # Closing Details
        elements.append(Paragraph("Closing Details", heading_style))

        # Get user name
        closer_name = (
            closing.user.name if closing.user else (user.name if user else "Unknown")
        )

        details_data = [
            ["Closed By:", closer_name],
            ["Closed At:", closing.closed_at.strftime("%I:%M %p")],
            ["Status:", "Finalized" if closing.is_finalized else "Draft"],
        ]

        details_table = Table(details_data, colWidths=[2 * inch, 4 * inch])
        details_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ]
            )
        )
        elements.append(details_table)
        elements.append(Spacer(1, 20))

        # Notes Section
        if closing.notes:
            elements.append(Paragraph("Notes", heading_style))
            notes_style = ParagraphStyle(
                "Notes",
                parent=styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#4b5563"),
                borderWidth=1,
                borderColor=colors.HexColor("#d1d5db"),
                borderPadding=10,
                backgroundColor=colors.HexColor("#f9fafb"),
            )
            elements.append(Paragraph(closing.notes, notes_style))
            elements.append(Spacer(1, 20))

        # Signature Section
        elements.append(Spacer(1, 40))

        signature_data = [
            ["_____________________________", "_____________________________"],
            ["Signature", "Date"],
        ]

        signature_table = Table(signature_data, colWidths=[3 * inch, 3 * inch])
        signature_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTSIZE", (0, 1), (-1, 1), 10),
                    ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#6b7280")),
                ]
            )
        )
        elements.append(signature_table)

        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#9ca3af"),
            alignment=1,  # Center
        )
        elements.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | TechStore SaaS",
                footer_style,
            )
        )

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"PDF generated successfully for closing {closing.id}")
        return pdf_bytes

    def _format_difference(self, difference: Decimal) -> str:
        """Format cash difference with appropriate sign and color."""
        if difference > 0:
            return f"+${difference:.2f}"
        elif difference < 0:
            return f"-${abs(difference):.2f}"
        else:
            return "$0.00"

    def _get_difference_color(self, difference: Decimal) -> colors.Color:
        """Get background color based on cash difference."""
        if difference > 0:
            return colors.HexColor("#dcfce7")  # Light green
        elif difference < 0:
            return colors.HexColor("#fee2e2")  # Light red
        else:
            return colors.HexColor("#f3f4f6")  # Light gray

    def _get_difference_text_color(self, difference: Decimal) -> colors.Color:
        """Get text color based on cash difference."""
        if difference > 0:
            return colors.HexColor("#16a34a")  # Green
        elif difference < 0:
            return colors.HexColor("#dc2626")  # Red
        else:
            return colors.HexColor("#374151")  # Gray


# Create service instance
pdf_service = PDFService()
