#!/usr/bin/env python3
"""
Find sales and payments that are NOT registered in customer_transactions.

This helps identify legacy data that needs to be migrated to the
CustomerAccount/CustomerTransaction system.
"""

import logging
import os
import sys
from decimal import Decimal
from pathlib import Path

os.environ["SQLALCHEMY_ECHO"] = "false"
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)

sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.customer import Customer
from app.models.customer_account import CustomerTransaction
from app.models.payment import Payment
from app.models.sale import Sale

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def find_missing_transactions(customer_id: int | None = None):
    """Find sales and payments without corresponding customer_transactions."""
    db = SessionLocal()

    try:
        logger.info("=" * 100)
        logger.info("MISSING TRANSACTIONS REPORT")
        logger.info("=" * 100)
        logger.info("")

        # Build customer filter
        customer_filter = []
        if customer_id:
            customer_filter.append(Sale.customer_id == customer_id)
            logger.info(f"Filtering for customer ID: {customer_id}")
            logger.info("")

        # Find sales without transactions
        logger.info("-" * 100)
        logger.info("SALES WITHOUT CUSTOMER_TRANSACTION")
        logger.info("-" * 100)

        # Get all sale IDs that have transactions
        sales_with_trans = (
            db.query(CustomerTransaction.reference_id)
            .filter(CustomerTransaction.reference_type == "sale")
            .subquery()
        )

        # Find sales not in that list
        missing_sales_query = (
            db.query(Sale, Customer)
            .join(Customer, Sale.customer_id == Customer.id)
            .filter(
                Sale.is_voided.is_(False),
                Sale.customer_id.isnot(None),
                ~Sale.id.in_(sales_with_trans),
            )
        )

        if customer_id:
            missing_sales_query = missing_sales_query.filter(
                Sale.customer_id == customer_id
            )

        missing_sales = missing_sales_query.order_by(Sale.sale_date.desc()).all()

        if missing_sales:
            logger.info(f"Found {len(missing_sales)} sales without transaction record:")
            logger.info("")
            logger.info(
                f"{'Sale ID':<10} {'Date':<12} {'Invoice':<15} {'Customer':<30} {'Amount':>15}"
            )
            logger.info("-" * 100)

            total_missing_sales = Decimal("0")
            for sale, customer in missing_sales:
                total_missing_sales += sale.total_amount
                logger.info(
                    f"{sale.id:<10} "
                    f"{sale.sale_date.strftime('%Y-%m-%d'):<12} "
                    f"{sale.invoice_number or 'N/A':<15} "
                    f"{customer.name[:29]:<30} "
                    f"${sale.total_amount:>13,.2f}"
                )

            logger.info("-" * 100)
            logger.info(f"{'TOTAL MISSING SALES:':<69} ${total_missing_sales:>13,.2f}")
        else:
            logger.info("No missing sales found.")

        logger.info("")

        # Find payments without transactions
        logger.info("-" * 100)
        logger.info("PAYMENTS WITHOUT CUSTOMER_TRANSACTION")
        logger.info("-" * 100)

        # Get all payment IDs that have transactions
        payments_with_trans = (
            db.query(CustomerTransaction.reference_id)
            .filter(CustomerTransaction.reference_type == "payment")
            .subquery()
        )

        # Find payments not in that list
        missing_payments_query = (
            db.query(Payment, Customer)
            .join(Customer, Payment.customer_id == Customer.id)
            .filter(
                Payment.voided.is_(False),
                Payment.customer_id.isnot(None),
                ~Payment.id.in_(payments_with_trans),
            )
        )

        if customer_id:
            missing_payments_query = missing_payments_query.filter(
                Payment.customer_id == customer_id
            )

        missing_payments = missing_payments_query.order_by(
            Payment.created_at.desc()
        ).all()

        if missing_payments:
            logger.info(
                f"Found {len(missing_payments)} payments without transaction record:"
            )
            logger.info("")
            logger.info(
                f"{'Pay ID':<10} {'Date':<12} {'Receipt':<15} {'Customer':<30} {'Amount':>15}"
            )
            logger.info("-" * 100)

            total_missing_payments = Decimal("0")
            for payment, customer in missing_payments:
                total_missing_payments += payment.amount
                pay_date = (
                    payment.created_at.strftime("%Y-%m-%d")
                    if payment.created_at
                    else "N/A"
                )
                logger.info(
                    f"{payment.id:<10} "
                    f"{pay_date:<12} "
                    f"{payment.receipt_number or 'N/A':<15} "
                    f"{customer.name[:29]:<30} "
                    f"${payment.amount:>13,.2f}"
                )

            logger.info("-" * 100)
            logger.info(
                f"{'TOTAL MISSING PAYMENTS:':<69} ${total_missing_payments:>13,.2f}"
            )
        else:
            logger.info("No missing payments found.")

        logger.info("")
        logger.info("=" * 100)
        logger.info("SUMMARY")
        logger.info("=" * 100)

        total_missing_sales = (
            sum(s.total_amount for s, _ in missing_sales)
            if missing_sales
            else Decimal("0")
        )
        total_missing_payments = (
            sum(p.amount for p, _ in missing_payments)
            if missing_payments
            else Decimal("0")
        )

        logger.info(
            f"Missing sales:    {len(missing_sales):>5} records, ${total_missing_sales:>15,.2f}"
        )
        logger.info(
            f"Missing payments: {len(missing_payments):>5} records, ${total_missing_payments:>15,.2f}"
        )
        logger.info(
            f"Net impact on balances:              ${total_missing_sales - total_missing_payments:>15,.2f}"
        )
        logger.info("")
        logger.info("NOTE: Net impact = Missing Sales - Missing Payments")
        logger.info("      Positive = Customers owe more than recorded")
        logger.info("      Negative = Customers have more credit than recorded")
        logger.info("=" * 100)

        return missing_sales, missing_payments

    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Find sales/payments missing from customer_transactions"
    )
    parser.add_argument(
        "--customer-id",
        type=int,
        help="Filter by specific customer ID",
    )
    args = parser.parse_args()

    try:
        find_missing_transactions(customer_id=args.customer_id)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
