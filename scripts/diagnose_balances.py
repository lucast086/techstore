#!/usr/bin/env python3
"""
Diagnose customer balance discrepancies.

Compares balances from three sources:
1. CustomerAccount.account_balance (stored value)
2. Sum of CustomerTransactions (transaction ledger)
3. Direct calculation: Sales - Payments (source of truth)

This helps identify where discrepancies exist and their magnitude.
"""

import logging
import os
import sys
from decimal import Decimal
from pathlib import Path

# Disable SQLAlchemy echo
os.environ["SQLALCHEMY_ECHO"] = "false"

# Disable all SQLAlchemy logging
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.dialects").setLevel(logging.ERROR)

sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount, CustomerTransaction
from app.models.payment import Payment
from app.models.sale import Sale

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Create engine without echo
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def calculate_balance_from_sales_payments(db, customer_id: int) -> Decimal:
    """Calculate balance directly from sales and payments tables.

    Balance = Sales - Payments
    Positive = customer owes money
    Negative = customer has credit
    """
    total_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.customer_id == customer_id,
        Sale.is_voided.is_(False),
    ).scalar() or Decimal("0")

    total_payments = db.query(func.sum(Payment.amount)).filter(
        Payment.customer_id == customer_id,
        Payment.voided.is_(False),
    ).scalar() or Decimal("0")

    return Decimal(str(total_sales)) - Decimal(str(total_payments))


def get_last_transaction_balance(db, customer_id: int) -> Decimal | None:
    """Get balance from the last transaction in the ledger."""
    last_transaction = (
        db.query(CustomerTransaction)
        .filter(CustomerTransaction.customer_id == customer_id)
        .order_by(
            CustomerTransaction.transaction_date.desc(), CustomerTransaction.id.desc()
        )
        .first()
    )

    if last_transaction:
        return last_transaction.balance_after
    return None


def diagnose_balances(show_all: bool = False):
    """Compare balances from different sources and report discrepancies."""
    db = SessionLocal()

    try:
        logger.info("=" * 100)
        logger.info("CUSTOMER BALANCE DIAGNOSTIC REPORT")
        logger.info("=" * 100)
        logger.info("")

        # Get all customers with accounts
        customers_with_accounts = (
            db.query(Customer, CustomerAccount)
            .join(CustomerAccount, Customer.id == CustomerAccount.customer_id)
            .filter(Customer.is_active.is_(True))
            .order_by(Customer.name)
            .all()
        )

        logger.info(f"Total customers with accounts: {len(customers_with_accounts)}")
        logger.info("")

        discrepancies = []
        total_stored = Decimal("0")
        total_calculated = Decimal("0")

        for customer, account in customers_with_accounts:
            stored_balance = account.account_balance
            calculated_balance = calculate_balance_from_sales_payments(db, customer.id)
            ledger_balance = get_last_transaction_balance(db, customer.id)

            total_stored += stored_balance
            total_calculated += calculated_balance

            # Check for discrepancy (more than $0.01 difference)
            diff_stored_vs_calc = stored_balance - calculated_balance
            has_discrepancy = abs(diff_stored_vs_calc) > Decimal("0.01")

            if has_discrepancy or show_all:
                discrepancies.append(
                    {
                        "customer_id": customer.id,
                        "customer_name": customer.name,
                        "stored_balance": stored_balance,
                        "calculated_balance": calculated_balance,
                        "ledger_balance": ledger_balance,
                        "diff_stored_vs_calc": diff_stored_vs_calc,
                    }
                )

        # Report discrepancies
        if discrepancies:
            logger.info("-" * 100)
            logger.info("DISCREPANCIES FOUND" if not show_all else "ALL CUSTOMERS")
            logger.info("-" * 100)
            logger.info("")
            logger.info(
                f"{'ID':<6} {'Customer Name':<30} {'Stored':<15} {'Calculated':<15} {'Ledger':<15} {'Difference':<15}"
            )
            logger.info("-" * 100)

            for d in discrepancies:
                ledger_str = (
                    f"${d['ledger_balance']:,.2f}"
                    if d["ledger_balance"] is not None
                    else "N/A"
                )
                diff_str = f"${d['diff_stored_vs_calc']:,.2f}"

                # Mark significant discrepancies
                marker = (
                    " !!!" if abs(d["diff_stored_vs_calc"]) > Decimal("1000") else ""
                )

                logger.info(
                    f"{d['customer_id']:<6} "
                    f"{d['customer_name'][:29]:<30} "
                    f"${d['stored_balance']:>12,.2f} "
                    f"${d['calculated_balance']:>12,.2f} "
                    f"{ledger_str:>14} "
                    f"{diff_str:>14}{marker}"
                )

            logger.info("")
            logger.info("-" * 100)

        # Summary
        logger.info("")
        logger.info("=" * 100)
        logger.info("SUMMARY")
        logger.info("=" * 100)
        logger.info(f"Total customers analyzed: {len(customers_with_accounts)}")
        logger.info(
            f"Customers with discrepancies: {len([d for d in discrepancies if abs(d['diff_stored_vs_calc']) > Decimal('0.01')])}"
        )
        logger.info("")
        logger.info(f"Sum of STORED balances:     ${total_stored:>15,.2f}")
        logger.info(f"Sum of CALCULATED balances: ${total_calculated:>15,.2f}")
        logger.info(
            f"Total difference:           ${total_stored - total_calculated:>15,.2f}"
        )
        logger.info("")

        # Interpretation
        logger.info("INTERPRETATION:")
        logger.info("  - Stored balance: What CustomerAccount.account_balance says")
        logger.info("  - Calculated balance: Sales - Payments (source of truth)")
        logger.info("  - Ledger balance: Last CustomerTransaction.balance_after")
        logger.info("  - Positive balance = Customer OWES money")
        logger.info("  - Negative balance = Customer has CREDIT")
        logger.info("")
        logger.info("  If Stored != Calculated, the CustomerAccount is out of sync")
        logger.info("  with the actual sales/payments data.")
        logger.info("=" * 100)

        return discrepancies

    except Exception as e:
        logger.error(f"Error during diagnosis: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Diagnose customer balance discrepancies"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all customers, not just those with discrepancies",
    )
    args = parser.parse_args()

    try:
        diagnose_balances(show_all=args.all)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
