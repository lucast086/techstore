#!/usr/bin/env python3
"""
Analyze production database content without deleting anything.
This script shows what data exists and what would be cleaned.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_database():
    """Analyze database content without making any changes."""

    db = SessionLocal()

    try:
        logger.info("=" * 80)
        logger.info("PRODUCTION DATABASE ANALYSIS")
        logger.info("=" * 80)
        logger.info("")

        # Tables that will be CLEANED
        tables_to_clean = [
            ("customer_transactions", "Customer transactions"),
            ("repair_deposits", "Repair deposits"),
            ("payments", "Payments"),
            ("sale_items", "Sale items"),
            ("sales", "Sales"),
            ("repairstatushistorys", "Repair status history"),
            ("repairparts", "Repair parts"),
            ("repairphotos", "Repair photos"),
            ("repairs", "Repairs"),
            ("warranties", "Warranties"),
            ("expenses", "Expenses"),
            ("cash_closings", "Cash closings"),
            ("inventory_movements", "Inventory movements"),
            ("customer_accounts", "Customer accounts"),
        ]

        logger.info("🗑️  Data that WILL BE DELETED:")
        logger.info("")
        total_to_delete = 0

        for table_name, description in tables_to_clean:
            try:
                count = (
                    db.execute(text(f"SELECT COUNT(*) FROM {table_name};")).scalar()
                    or 0
                )
                total_to_delete += count
                if count > 0:
                    logger.info(f"  - {description:30s}: {count:,} records")
                db.commit()  # Commit after each successful query
            except Exception as e:
                db.rollback()  # Rollback on error to continue
                if "does not exist" in str(e):
                    logger.info(f"  - {description:30s}: Table does not exist")
                else:
                    logger.warning(f"  - {description:30s}: Error - {e}")

        logger.info("")
        logger.info(f"  TOTAL TO DELETE: {total_to_delete:,} records")
        logger.info("")

        # Tables that will be PRESERVED
        logger.info("=" * 80)
        logger.info("✅ Data that will be PRESERVED:")
        logger.info("")

        preserved_tables = [
            ("customers", "Customers"),
            ("products", "Products"),
            ("categories", "Product categories"),
            ("users", "Users"),
            ("suppliers", "Suppliers"),
            ("expense_categories", "Expense categories"),
        ]

        total_preserved = 0
        for table_name, description in preserved_tables:
            try:
                count = (
                    db.execute(text(f"SELECT COUNT(*) FROM {table_name};")).scalar()
                    or 0
                )
                total_preserved += count
                logger.info(f"  - {description:30s}: {count:,} records")
                db.commit()  # Commit after each successful query
            except Exception as e:
                db.rollback()  # Rollback on error to continue
                if "does not exist" in str(e):
                    logger.info(f"  - {description:30s}: Table does not exist")
                else:
                    logger.warning(f"  - {description:30s}: Error - {e}")

        logger.info("")
        logger.info(f"  TOTAL PRESERVED: {total_preserved:,} records")
        logger.info("")
        logger.info("=" * 80)

        return total_to_delete, total_preserved

    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        total_delete, total_preserve = analyze_database()
        print("")
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Records to DELETE:   {total_delete:,}")
        print(f"Records to PRESERVE: {total_preserve:,}")
        print("=" * 80)
    except Exception as e:
        logger.error(f"Failed to analyze database: {e}")
        sys.exit(1)
