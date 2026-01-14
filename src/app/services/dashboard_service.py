"""Dashboard service for aggregating business statistics and alerts."""

import logging
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer_account import CustomerAccount
from app.models.product import Product
from app.models.repair import Repair
from app.models.sale import Sale
from app.utils.timezone import get_local_today, local_date_to_utc_range

logger = logging.getLogger(__name__)

# =============================================================================
# ALERT THRESHOLDS - Modify these values to change when alerts are triggered
# =============================================================================
REPAIRS_RECEIVED_ALERT_THRESHOLD = 5  # Alert if repairs received > this value
LOW_STOCK_ALERT_THRESHOLD = 30  # Alert if low stock products > this value
CUSTOMER_DEBT_ALERT_THRESHOLD = Decimal("1500000")  # Alert if total debt > this value


class DashboardService:
    """Service for retrieving dashboard statistics and alerts.

    Provides aggregated metrics for the main dashboard including:
    - Repair counts by status
    - Inventory alerts (low stock, out of stock)
    - Customer debt totals
    - Daily sales totals
    """

    def get_dashboard_stats(self, db: Session) -> dict:
        """Get all dashboard statistics and alerts.

        Args:
            db: Database session.

        Returns:
            Dictionary containing:
            - repairs_received: Count of repairs with status="received"
            - repairs_received_alert: True if count > 5
            - low_stock_count: Count of products with low stock
            - low_stock_alert: True if count > 10
            - out_of_stock_count: Count of products with zero stock
            - customer_debt_total: Sum of positive account balances
            - debt_alert: True if total > 5000
            - today_sales_total: Sum of today's non-voided sales
        """
        logger.info("Fetching dashboard statistics")

        repairs_received = self._count_repairs_received(db)
        low_stock_count = self._count_low_stock_products(db)
        out_of_stock_count = self._count_out_of_stock_products(db)
        customer_debt_total = self._sum_customer_debt(db)
        today_sales_total = self._get_today_sales_total(db)

        stats = {
            "repairs_received": repairs_received,
            "repairs_received_alert": repairs_received
            > REPAIRS_RECEIVED_ALERT_THRESHOLD,
            "low_stock_count": low_stock_count,
            "low_stock_alert": low_stock_count > LOW_STOCK_ALERT_THRESHOLD,
            "out_of_stock_count": out_of_stock_count,
            "customer_debt_total": customer_debt_total,
            "debt_alert": customer_debt_total > CUSTOMER_DEBT_ALERT_THRESHOLD,
            "today_sales_total": today_sales_total,
        }

        logger.info(
            f"Dashboard stats: repairs_received={repairs_received}, "
            f"low_stock={low_stock_count}, out_of_stock={out_of_stock_count}, "
            f"debt=${customer_debt_total}, today_sales=${today_sales_total}"
        )

        return stats

    def _count_repairs_received(self, db: Session) -> int:
        """Count repairs with status='received'.

        Args:
            db: Database session.

        Returns:
            Count of repairs in received status.
        """
        count = (
            db.query(func.count(Repair.id)).filter(Repair.status == "received").scalar()
        )
        logger.debug(f"Repairs in received status: {count}")
        return count or 0

    def _count_low_stock_products(self, db: Session) -> int:
        """Count products with low stock levels.

        Criteria:
        - current_stock <= minimum_stock
        - current_stock > 0 (not completely out of stock)
        - is_active = True
        - is_service = False (only physical products)

        Args:
            db: Database session.

        Returns:
            Count of products with low stock.
        """
        count = (
            db.query(func.count(Product.id))
            .filter(
                Product.current_stock <= Product.minimum_stock,
                Product.current_stock > 0,
                Product.is_active == True,  # noqa: E712
                Product.is_service == False,  # noqa: E712
            )
            .scalar()
        )
        logger.debug(f"Products with low stock: {count}")
        return count or 0

    def _count_out_of_stock_products(self, db: Session) -> int:
        """Count products that are completely out of stock.

        Criteria:
        - current_stock = 0
        - is_active = True
        - is_service = False (only physical products)

        Args:
            db: Database session.

        Returns:
            Count of products out of stock.
        """
        count = (
            db.query(func.count(Product.id))
            .filter(
                Product.current_stock == 0,
                Product.is_active == True,  # noqa: E712
                Product.is_service == False,  # noqa: E712
            )
            .scalar()
        )
        logger.debug(f"Products out of stock: {count}")
        return count or 0

    def _sum_customer_debt(self, db: Session) -> Decimal:
        """Sum all positive customer account balances (debt owed to us).

        Args:
            db: Database session.

        Returns:
            Total customer debt amount.
        """
        total = (
            db.query(func.sum(CustomerAccount.account_balance))
            .filter(CustomerAccount.account_balance > 0)
            .scalar()
        )
        result = total or Decimal("0.00")
        logger.debug(f"Total customer debt: ${result}")
        return result

    def _get_today_sales_total(self, db: Session) -> Decimal:
        """Sum of total_amount from today's non-voided sales.

        Uses local timezone to determine "today" and converts to UTC range
        for correct database comparison.

        Args:
            db: Database session.

        Returns:
            Total sales amount for today.
        """
        today = get_local_today()
        utc_start, utc_end = local_date_to_utc_range(today)
        total = (
            db.query(func.sum(Sale.total_amount))
            .filter(
                Sale.sale_date >= utc_start,
                Sale.sale_date <= utc_end,
                Sale.is_voided == False,  # noqa: E712
            )
            .scalar()
        )
        result = total or Decimal("0.00")
        logger.debug(f"Today's sales total ({today}): ${result}")
        return result


dashboard_service = DashboardService()
