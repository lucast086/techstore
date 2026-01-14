"""Report service for generating PDF reports using ReportLab."""

import io
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

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

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating PDF reports.

    Uses ReportLab to generate professional PDF reports with consistent
    styling and branding for TechStore.
    """

    def __init__(self):
        """Initialize report service with default styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles for reports."""
        self.styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                spaceAfter=20,
                alignment=1,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="ReportSubtitle",
                parent=self.styles["Normal"],
                fontSize=12,
                textColor=colors.gray,
                alignment=1,
                spaceAfter=30,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
            )
        )

    def _create_header(self, title: str, subtitle: str | None = None) -> list:
        """Create report header elements.

        Args:
            title: Main title of the report.
            subtitle: Optional subtitle or date range.

        Returns:
            List of flowable elements for the header.
        """
        elements = []

        elements.append(Paragraph("TechStore", self.styles["ReportTitle"]))
        elements.append(Paragraph(title, self.styles["Heading1"]))

        if subtitle:
            elements.append(Paragraph(subtitle, self.styles["ReportSubtitle"]))

        generation_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(
            Paragraph(f"Generado: {generation_date}", self.styles["ReportSubtitle"])
        )

        elements.append(Spacer(1, 20))

        return elements

    def _create_table(
        self,
        data: list[list[Any]],
        col_widths: list[float] | None = None,
        header_bg_color: colors.Color = colors.HexColor("#1f2937"),
    ) -> Table:
        """Create a styled table.

        Args:
            data: List of rows, first row is header.
            col_widths: Optional column widths.
            header_bg_color: Background color for header row.

        Returns:
            Styled Table object.
        """
        table = Table(data, colWidths=col_widths)

        style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_bg_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f9fafb")],
                ),
            ]
        )

        table.setStyle(style)
        return table

    def _create_summary_table(self, data: dict[str, Any]) -> Table:
        """Create a key-value summary table.

        Args:
            data: Dictionary of label-value pairs.

        Returns:
            Styled Table object for summary display.
        """
        table_data = [[k, str(v)] for k, v in data.items()]
        table = Table(table_data, colWidths=[3 * inch, 2 * inch])

        style = TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.lightgrey),
                ("LINEBELOW", (0, -1), (-1, -1), 1, colors.gray),
            ]
        )

        table.setStyle(style)
        return table

    def _format_currency(self, value: Decimal | float) -> str:
        """Format a value as currency.

        Args:
            value: Numeric value to format.

        Returns:
            Formatted currency string.
        """
        return f"S/ {value:,.2f}"

    def _generate_pdf(self, elements: list) -> bytes:
        """Generate PDF from elements.

        Args:
            elements: List of flowable elements.

        Returns:
            PDF content as bytes.
        """
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        doc.build(elements)

        pdf_content = buffer.getvalue()
        buffer.close()

        return pdf_content


report_service = ReportService()
