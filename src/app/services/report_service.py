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
from sqlalchemy.orm import Session

from app.models.customer_account import CustomerAccount
from app.models.product import Product
from app.models.repair import Repair
from app.models.sale import Sale
from app.utils.timezone import local_date_to_utc_range

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

    def generate_low_stock_report(self, db: Session) -> bytes:
        """Generate PDF report of products with low stock.

        Includes only active products (not services) where current_stock <= minimum_stock.
        Shows recommendation to buy (maximum_stock - current_stock).

        Args:
            db: Database session.

        Returns:
            PDF content as bytes.
        """
        logger.info("Generating low stock report")

        products = (
            db.query(Product)
            .filter(
                Product.is_active == True,  # noqa: E712
                Product.is_service == False,  # noqa: E712
                Product.current_stock <= Product.minimum_stock,
            )
            .order_by(Product.current_stock.asc())
            .all()
        )

        elements = self._create_header(
            title="Reporte de Inventario Bajo Stock",
            subtitle=f"Productos que requieren reposición ({len(products)} items)",
        )

        if not products:
            elements.append(
                Paragraph(
                    "No hay productos con stock bajo en este momento.",
                    self.styles["Normal"],
                )
            )
        else:
            table_data = [
                [
                    "SKU",
                    "Producto",
                    "Stock Actual",
                    "Stock Mín.",
                    "Stock Máx.",
                    "Rec. Compra",
                ]
            ]

            total_to_buy = 0
            for product in products:
                recommendation = (product.maximum_stock or 0) - product.current_stock
                if recommendation < 0:
                    recommendation = 0
                total_to_buy += recommendation

                table_data.append(
                    [
                        product.sku,
                        product.name[:35] + "..."
                        if len(product.name) > 35
                        else product.name,
                        str(product.current_stock),
                        str(product.minimum_stock),
                        str(product.maximum_stock or "-"),
                        str(recommendation) if recommendation > 0 else "-",
                    ]
                )

            col_widths = [
                1 * inch,
                2.5 * inch,
                0.9 * inch,
                0.9 * inch,
                0.9 * inch,
                1 * inch,
            ]
            table = self._create_table(table_data, col_widths)
            elements.append(table)

            elements.append(Spacer(1, 20))

            summary_data = {
                "Total de productos con stock bajo:": len(products),
                "Total de unidades a comprar:": total_to_buy,
            }
            summary_table = self._create_summary_table(summary_data)
            elements.append(summary_table)

        logger.info(f"Low stock report generated with {len(products)} products")
        return self._generate_pdf(elements)

    def generate_accounts_receivable_report(self, db: Session) -> bytes:
        """Generate PDF report of customers with outstanding debt.

        Lists customers with positive account balance (debt), their contact info,
        and associated pending invoices.

        Args:
            db: Database session.

        Returns:
            PDF content as bytes.
        """
        logger.info("Generating accounts receivable report")

        accounts = (
            db.query(CustomerAccount)
            .filter(CustomerAccount.account_balance > 0)
            .order_by(CustomerAccount.account_balance.desc())
            .all()
        )

        elements = self._create_header(
            title="Reporte de Cuentas por Cobrar",
            subtitle=f"Clientes con saldo pendiente ({len(accounts)} cuentas)",
        )

        if not accounts:
            elements.append(
                Paragraph(
                    "No hay clientes con saldo pendiente en este momento.",
                    self.styles["Normal"],
                )
            )
        else:
            table_data = [
                [
                    "Cliente",
                    "Teléfono",
                    "Saldo Pendiente",
                    "Última Actividad",
                    "Facturas Pendientes",
                ]
            ]

            total_debt = Decimal("0.00")
            for account in accounts:
                customer = account.customer
                if not customer:
                    continue

                total_debt += account.account_balance

                pending_sales = (
                    db.query(Sale.invoice_number)
                    .filter(
                        Sale.customer_id == customer.id,
                        Sale.payment_status.in_(["pending", "partial"]),
                        Sale.is_voided == False,  # noqa: E712
                    )
                    .all()
                )
                invoice_numbers = ", ".join([s.invoice_number for s in pending_sales])
                if len(invoice_numbers) > 25:
                    invoice_numbers = invoice_numbers[:22] + "..."

                last_activity = ""
                if account.last_transaction_date:
                    last_activity = account.last_transaction_date.strftime("%d/%m/%Y")

                table_data.append(
                    [
                        customer.name[:25] + "..."
                        if len(customer.name) > 25
                        else customer.name,
                        customer.phone,
                        self._format_currency(account.account_balance),
                        last_activity or "-",
                        invoice_numbers or "-",
                    ]
                )

            col_widths = [
                1.8 * inch,
                1.2 * inch,
                1.2 * inch,
                1 * inch,
                2 * inch,
            ]
            table = self._create_table(table_data, col_widths)
            elements.append(table)

            elements.append(Spacer(1, 20))

            summary_data = {
                "Total de clientes con deuda:": len(accounts),
                "Total por cobrar:": self._format_currency(total_debt),
            }
            summary_table = self._create_summary_table(summary_data)
            elements.append(summary_table)

        logger.info(
            f"Accounts receivable report generated with {len(accounts)} accounts"
        )
        return self._generate_pdf(elements)

    def generate_monthly_repairs_report(
        self, db: Session, year: int, month: int
    ) -> bytes:
        """Generate PDF report of repairs for a specific month.

        Includes all repairs received during the month, grouped by status,
        with totals and revenue summary.

        Args:
            db: Database session.
            year: Year to filter (e.g., 2024).
            month: Month to filter (1-12).

        Returns:
            PDF content as bytes.
        """
        from calendar import monthrange
        from datetime import date

        logger.info(f"Generating monthly repairs report for {year}-{month:02d}")

        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        utc_start, _ = local_date_to_utc_range(start_date)
        _, utc_end = local_date_to_utc_range(end_date)

        repairs = (
            db.query(Repair)
            .filter(
                Repair.received_date >= utc_start,
                Repair.received_date <= utc_end,
            )
            .order_by(Repair.received_date.asc())
            .all()
        )

        month_names = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre",
        }
        month_name = month_names.get(month, str(month))

        elements = self._create_header(
            title="Reporte de Reparaciones del Mes",
            subtitle=f"{month_name} {year} ({len(repairs)} reparaciones)",
        )

        if not repairs:
            elements.append(
                Paragraph(
                    "No hay reparaciones registradas en este período.",
                    self.styles["Normal"],
                )
            )
        else:
            table_data = [
                [
                    "N° Orden",
                    "Fecha",
                    "Cliente",
                    "Dispositivo",
                    "Estado",
                    "Costo Final",
                ]
            ]

            status_labels = {
                "received": "Recibido",
                "diagnosing": "En diagnóstico",
                "waiting_approval": "Esperando aprobación",
                "approved": "Aprobado",
                "repairing": "En reparación",
                "waiting_parts": "Esperando repuestos",
                "completed": "Completado",
                "delivered": "Entregado",
                "cancelled": "Cancelado",
            }

            status_counts: dict[str, int] = {}
            total_revenue = Decimal("0.00")

            for repair in repairs:
                status = repair.status
                status_counts[status] = status_counts.get(status, 0) + 1

                if repair.final_cost:
                    total_revenue += repair.final_cost

                device_info = f"{repair.device_brand}"
                if repair.device_model:
                    device_info += f" {repair.device_model}"
                if len(device_info) > 20:
                    device_info = device_info[:17] + "..."

                customer_name = repair.customer.name if repair.customer else "-"
                if len(customer_name) > 20:
                    customer_name = customer_name[:17] + "..."

                table_data.append(
                    [
                        repair.repair_number,
                        repair.received_date.strftime("%d/%m/%Y"),
                        customer_name,
                        device_info,
                        status_labels.get(status, status),
                        self._format_currency(repair.final_cost)
                        if repair.final_cost
                        else "-",
                    ]
                )

            col_widths = [
                1.1 * inch,
                0.9 * inch,
                1.5 * inch,
                1.5 * inch,
                1.3 * inch,
                1 * inch,
            ]
            table = self._create_table(table_data, col_widths)
            elements.append(table)

            elements.append(Spacer(1, 20))
            elements.append(
                Paragraph("Resumen por Estado", self.styles["SectionHeader"])
            )

            status_data = [["Estado", "Cantidad"]]
            for status, count in sorted(status_counts.items()):
                status_data.append([status_labels.get(status, status), str(count)])

            status_table = self._create_table(
                status_data,
                col_widths=[3 * inch, 1.5 * inch],
                header_bg_color=colors.HexColor("#374151"),
            )
            elements.append(status_table)

            elements.append(Spacer(1, 20))

            summary_data = {
                "Total de reparaciones:": len(repairs),
                "Ingresos por reparaciones:": self._format_currency(total_revenue),
            }
            summary_table = self._create_summary_table(summary_data)
            elements.append(summary_table)

        logger.info(f"Monthly repairs report generated with {len(repairs)} repairs")
        return self._generate_pdf(elements)


report_service = ReportService()
