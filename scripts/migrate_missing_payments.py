#!/usr/bin/env python3
"""
Migrate missing payments to customer_transactions.

This script finds payments that are not registered in customer_transactions
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
from app.models.payment import Payment

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def migrate_missing_payments(dry_run: bool = True):
    """Migrate payments without customer_transactions."""
    db = SessionLocal()

    try:
        logger.info("=" * 100)
        logger.info("MIGRATE MISSING PAYMENTS TO CUSTOMER_TRANSACTIONS")
        logger.info("=" * 100)
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        logger.info("")

        # Get all payment IDs that have transactions
        payments_with_trans = (
            db.query(CustomerTransaction.reference_id)
            .filter(CustomerTransaction.reference_type == "payment")
            .subquery()
        )

        # Find payments not in that list
        missing_payments = (
            db.query(Payment, Customer)
            .join(Customer, Payment.customer_id == Customer.id)
            .filter(
                Payment.voided.is_(False),
                Payment.customer_id.isnot(None),
                ~Payment.id.in_(select(payments_with_trans)),
            )
            .order_by(Payment.created_at.asc())  # Process in chronological order
            .all()
        )

        if not missing_payments:
            logger.info("No missing payments found. Nothing to migrate.")
            return 0

        logger.info(f"Found {len(missing_payments)} payments to migrate:")
        logger.info("")

        migrated_count = 0
        total_amount = Decimal("0")

        # Track running balances per customer (for correct sequential calculation)
        running_balances = {}

        for payment, customer in missing_payments:
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

            # Payment reduces debt (subtracts from positive balance)
            balance_after = balance_before - payment.amount

            # Update running balance for this customer
            running_balances[customer.id] = balance_after

            logger.info(
                f"  Payment {payment.id}: {customer.name[:25]:<25} "
                f"${payment.amount:>12,.2f}  "
                f"(Balance: ${balance_before:>12,.2f} -> ${balance_after:>12,.2f})"
            )

            if not dry_run:
                # Create the transaction record
                transaction = CustomerTransaction(
                    customer_id=customer.id,
                    account_id=account.id,
                    transaction_type=TransactionType.PAYMENT,
                    amount=payment.amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    reference_type="payment",
                    reference_id=payment.id,
                    description=f"Payment - {payment.receipt_number}",
                    transaction_date=payment.created_at,
                    created_by_id=1,  # System user
                )
                db.add(transaction)

                # Update account balance
                account.account_balance = balance_after
                account.total_payments += payment.amount
                account.last_payment_date = payment.created_at
                account.transaction_count += 1

            migrated_count += 1
            total_amount += payment.amount

        if not dry_run:
            db.commit()
            logger.info("")
            logger.info("Changes committed to database.")

        logger.info("")
        logger.info("=" * 100)
        logger.info("SUMMARY")
        logger.info("=" * 100)
        logger.info(f"Payments migrated: {migrated_count}")
        logger.info(f"Total amount:      ${total_amount:,.2f}")
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
        description="Migrate missing payments to customer_transactions"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually perform migration (default is dry run)",
    )
    args = parser.parse_args()

    try:
        migrate_missing_payments(dry_run=not args.live)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
