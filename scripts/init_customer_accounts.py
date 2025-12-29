#!/usr/bin/env python3
"""
Initialize CustomerAccount for all customers that don't have one.

This script should be run once to create accounts for legacy customers
that existed before the CustomerAccount system was implemented.
"""

import sys
from decimal import Decimal
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import logging

from sqlalchemy import text

from app.database import SessionLocal
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_customer_accounts(dry_run: bool = True):
    """Initialize CustomerAccount for customers without one.

    Args:
        dry_run: If True, only show what would be done without making changes.
    """
    db = SessionLocal()

    try:
        logger.info("=" * 80)
        logger.info("CUSTOMER ACCOUNT INITIALIZATION")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        logger.info("")

        # Find customers without accounts using LEFT JOIN
        customers_without_account = (
            db.query(Customer)
            .outerjoin(CustomerAccount, Customer.id == CustomerAccount.customer_id)
            .filter(
                Customer.is_active.is_(True),
                CustomerAccount.id.is_(None),
            )
            .all()
        )

        total_customers = (
            db.query(Customer).filter(Customer.is_active.is_(True)).count()
        )
        customers_with_account = total_customers - len(customers_without_account)

        logger.info(f"Total active customers: {total_customers}")
        logger.info(f"Customers WITH account: {customers_with_account}")
        logger.info(f"Customers WITHOUT account: {len(customers_without_account)}")
        logger.info("")

        if not customers_without_account:
            logger.info("All customers already have accounts. Nothing to do.")
            return 0

        # Get system user ID (usually 1)
        system_user_id = db.execute(
            text("SELECT id FROM users ORDER BY id LIMIT 1")
        ).scalar()

        if not system_user_id:
            logger.error("No users found in database. Cannot create accounts.")
            return -1

        logger.info(f"Using user ID {system_user_id} as creator for new accounts")
        logger.info("")

        if dry_run:
            logger.info("DRY RUN - The following accounts would be created:")
            for customer in customers_without_account:
                logger.info(f"  - Customer {customer.id}: {customer.name}")
            logger.info("")
            logger.info(
                f"Total: {len(customers_without_account)} accounts would be created"
            )
            logger.info("")
            logger.info("Run with --live to actually create the accounts")
            return len(customers_without_account)

        # Create accounts
        logger.info("Creating accounts...")
        created_count = 0

        for customer in customers_without_account:
            account = CustomerAccount(
                customer_id=customer.id,
                credit_limit=Decimal("0.00"),
                account_balance=Decimal("0.00"),
                total_sales=Decimal("0.00"),
                total_payments=Decimal("0.00"),
                created_by_id=system_user_id,
            )
            db.add(account)
            created_count += 1
            logger.info(
                f"  Created account for customer {customer.id}: {customer.name}"
            )

        db.commit()
        logger.info("")
        logger.info(f"Successfully created {created_count} accounts")

        return created_count

    except Exception as e:
        db.rollback()
        logger.error(f"Error during initialization: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize CustomerAccount for legacy customers"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually create accounts (default is dry run)",
    )
    args = parser.parse_args()

    try:
        result = init_customer_accounts(dry_run=not args.live)
        if result >= 0:
            logger.info("=" * 80)
            logger.info("DONE")
            logger.info("=" * 80)
        sys.exit(0 if result >= 0 else 1)
    except Exception as e:
        logger.error(f"Failed: {e}")
        sys.exit(1)
