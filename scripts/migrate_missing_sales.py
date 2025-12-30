#!/usr/bin/env python3
"""
Migrate missing sales to customer_transactions.

This script finds sales that are not registered in customer_transactions
and creates the corresponding transaction records, updating the account balance.
"""

import logging
import os
import sys
from decimal import Decimal
from pathlib import Path

os.environ["SQLALCHEMY_ECHO"] = "false"
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)

sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.customer import Customer
from app.models.customer_account import (
    CustomerAccount,
    CustomerTransaction,
    TransactionType,
)
from app.models.sale import Sale

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def migrate_missing_sales(dry_run: bool = True):
    """Migrate sales without customer_transactions."""
    db = SessionLocal()

    try:
        logger.info("=" * 100)
        logger.info("MIGRATE MISSING SALES TO CUSTOMER_TRANSACTIONS")
        logger.info("=" * 100)
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        logger.info("")

        # Get all sale IDs that have transactions
        sales_with_trans = (
            db.query(CustomerTransaction.reference_id)
            .filter(CustomerTransaction.reference_type == "sale")
            .subquery()
        )

        # Find sales not in that list
        missing_sales = (
            db.query(Sale, Customer)
            .join(Customer, Sale.customer_id == Customer.id)
            .filter(
                Sale.is_voided.is_(False),
                Sale.customer_id.isnot(None),
                ~Sale.id.in_(select(sales_with_trans)),
            )
            .order_by(Sale.sale_date.asc())  # Process in chronological order
            .all()
        )

        if not missing_sales:
            logger.info("No missing sales found. Nothing to migrate.")
            return 0

        logger.info(f"Found {len(missing_sales)} sales to migrate:")
        logger.info("")

        migrated_count = 0
        total_amount = Decimal("0")

        # Track running balances per customer (for correct sequential calculation)
        running_balances = {}

        for sale, customer in missing_sales:
            # Get customer account
            account = (
                db.query(CustomerAccount)
                .filter(CustomerAccount.customer_id == customer.id)
                .first()
            )

            if not account:
                logger.warning(
                    f"  SKIP: Customer {customer.id} ({customer.name}) has no account"
                )
                continue

            # Use running balance if we've already processed this customer
            if customer.id in running_balances:
                balance_before = running_balances[customer.id]
            else:
                balance_before = account.account_balance

            # Sale increases debt (adds to positive balance)
            balance_after = balance_before + sale.total_amount

            # Update running balance for this customer
            running_balances[customer.id] = balance_after

            logger.info(
                f"  Sale {sale.id}: {customer.name[:25]:<25} "
                f"${sale.total_amount:>12,.2f}  "
                f"(Balance: ${balance_before:>12,.2f} -> ${balance_after:>12,.2f})"
            )

            if not dry_run:
                # Create the transaction record
                transaction = CustomerTransaction(
                    customer_id=customer.id,
                    account_id=account.id,
                    transaction_type=TransactionType.SALE,
                    amount=sale.total_amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    reference_type="sale",
                    reference_id=sale.id,
                    description=f"Sale - {sale.invoice_number}",
                    transaction_date=sale.sale_date,
                    created_by_id=sale.user_id or 1,  # Use sale's user or system user
                )
                db.add(transaction)

                # Update account balance
                account.account_balance = balance_after
                account.total_sales += sale.total_amount
                account.transaction_count += 1

            migrated_count += 1
            total_amount += sale.total_amount

        if not dry_run:
            db.commit()
            logger.info("")
            logger.info("Changes committed to database.")

        logger.info("")
        logger.info("=" * 100)
        logger.info("SUMMARY")
        logger.info("=" * 100)
        logger.info(f"Sales migrated: {migrated_count}")
        logger.info(f"Total amount:   ${total_amount:,.2f}")
        logger.info("")

        if dry_run:
            logger.info("This was a DRY RUN. No changes were made.")
            logger.info("Run with --live to apply changes.")
        else:
            logger.info("Migration completed successfully!")

        logger.info("=" * 100)

        return migrated_count

    except Exception as e:
        db.rollback()
        logger.error(f"Error during migration: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate missing sales to customer_transactions"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually perform migration (default is dry run)",
    )
    args = parser.parse_args()

    try:
        migrate_missing_sales(dry_run=not args.live)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
