#!/usr/bin/env python
"""
Clean database but keep essential data (clients, products, users).
This script removes all transactional data while preserving master data.
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


def clean_database():
    """Clean transactional data while keeping essential master data."""

    db = SessionLocal()

    try:
        logger.info("Starting database cleanup...")

        # Disable foreign key checks temporarily
        db.execute(text("SET session_replication_role = 'replica';"))

        # Define tables to clean
        tables_to_clean = [
            # Customer account transactions (must be first due to foreign keys)
            ("customer_transactions", "Customer transactions"),
            # Repair deposits
            ("repair_deposits", "Repair deposits"),
            # Payment-related
            ("payments", "Payments"),
            # Sale-related
            ("sale_items", "Sale items"),
            ("sales", "Sales"),
            # Repair-related (must clean history before repairs)
            ("repairstatushistorys", "Repair status history"),
            ("repairparts", "Repair parts"),
            ("repairphotos", "Repair photos"),
            ("repairs", "Repairs"),
            # Warranty-related (may not exist)
            ("warranties", "Warranties"),
            # Expense-related
            ("expenses", "Expenses"),
            # Cash closing
            ("cash_closings", "Cash closings"),
            # Inventory movements (may not exist)
            ("inventory_movements", "Inventory movements"),
            # Customer accounts (reset balances - must be last)
            ("customer_accounts", "Customer accounts"),
        ]

        # Clean each table
        for table_name, description in tables_to_clean:
            try:
                logger.info(f"Cleaning {description}...")
                result = db.execute(text(f"DELETE FROM {table_name};"))
                count = result.rowcount
                db.commit()
                logger.info(f"  ✓ Deleted {count} records from {table_name}")
            except Exception as e:
                if "does not exist" in str(e):
                    logger.info(f"  ⚠️  Table {table_name} does not exist, skipping...")
                else:
                    logger.warning(f"  ⚠️  Error cleaning {table_name}: {e}")
                db.rollback()

        # Reset sequences for cleaned tables
        logger.info("Resetting sequences for cleaned tables...")
        cleaned_sequences = [
            "payments_id_seq",
            "sales_id_seq",
            "sale_items_id_seq",
            "repairs_id_seq",
            "repairparts_id_seq",
            "repairphotos_id_seq",
            "repairstatushistorys_id_seq",
            "warranties_id_seq",
            "expenses_id_seq",
            "cash_closings_id_seq",
            "inventory_movements_id_seq",
            "customer_transactions_id_seq",
            "repair_deposits_id_seq",
        ]

        for seq in cleaned_sequences:
            try:
                db.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1;"))
                db.commit()
                logger.info(f"  ✓ Reset sequence: {seq}")
            except Exception as e:
                if "does not exist" in str(e):
                    logger.debug(f"  Sequence {seq} does not exist, skipping...")
                else:
                    logger.warning(f"  Could not reset sequence {seq}: {e}")
                db.rollback()

        # Fix sequences for preserved tables (in case they're out of sync)
        logger.info("Fixing sequences for preserved tables...")
        preserved_tables = [
            ("users", "users_id_seq"),
            ("customers", "customers_id_seq"),
            ("products", "products_id_seq"),
            ("categories", "categories_id_seq"),
            ("expense_categories", "expense_categories_id_seq"),
            ("suppliers", "suppliers_id_seq"),
            ("customer_accounts", "customer_accounts_id_seq"),
        ]

        for table_name, seq_name in preserved_tables:
            try:
                # Set sequence to MAX(id) from table, or 1 if empty
                result = db.execute(
                    text(
                        f"""
                    SELECT setval('{seq_name}',
                        COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                        true
                    )
                """
                    )
                )
                new_value = result.scalar()
                db.commit()
                logger.info(f"  ✓ Fixed sequence {seq_name} -> {new_value}")
            except Exception as e:
                if "does not exist" in str(e):
                    logger.debug(
                        f"  Table/sequence {table_name}/{seq_name} does not exist, skipping..."
                    )
                else:
                    logger.warning(f"  Could not fix sequence {seq_name}: {e}")
                db.rollback()

        # Clean orphaned records (records that reference deleted data)
        logger.info("Cleaning orphaned records...")

        orphan_cleanups = [
            (
                "repairstatushistorys",
                "DELETE FROM repairstatushistorys WHERE repair_id NOT IN (SELECT id FROM repairs)",
                "Orphaned repair status history",
            ),
            (
                "repairparts",
                "DELETE FROM repairparts WHERE repair_id NOT IN (SELECT id FROM repairs)",
                "Orphaned repair parts",
            ),
            (
                "repairphotos",
                "DELETE FROM repairphotos WHERE repair_id NOT IN (SELECT id FROM repairs)",
                "Orphaned repair photos",
            ),
            (
                "sale_items",
                "DELETE FROM sale_items WHERE sale_id NOT IN (SELECT id FROM sales)",
                "Orphaned sale items",
            ),
        ]

        for table_name, cleanup_sql, description in orphan_cleanups:
            try:
                result = db.execute(text(cleanup_sql))
                count = result.rowcount
                db.commit()
                if count > 0:
                    logger.info(f"  ✓ Removed {count} {description} records")
            except Exception as e:
                if "does not exist" in str(e):
                    logger.debug(
                        f"  Table {table_name} does not exist, skipping orphan cleanup..."
                    )
                else:
                    logger.warning(
                        f"  Could not clean orphaned records from {table_name}: {e}"
                    )
                db.rollback()

        # Re-enable foreign key checks
        db.execute(text("SET session_replication_role = 'origin';"))
        db.commit()

        logger.info("✅ Database cleanup completed successfully!")

        # Show what was preserved
        logger.info("\n📊 Preserved data summary:")

        # Count preserved records
        customers_count = (
            db.execute(text("SELECT COUNT(*) FROM customers;")).scalar() or 0
        )
        products_count = (
            db.execute(text("SELECT COUNT(*) FROM products;")).scalar() or 0
        )
        users_count = db.execute(text("SELECT COUNT(*) FROM users;")).scalar() or 0
        categories_count = (
            db.execute(text("SELECT COUNT(*) FROM categories;")).scalar() or 0
        )

        # Check if expense_categories exists
        try:
            expense_categories_count = (
                db.execute(text("SELECT COUNT(*) FROM expense_categories;")).scalar()
                or 0
            )
        except Exception:
            expense_categories_count = 0

        logger.info(f"  ✓ Customers: {customers_count}")
        logger.info(f"  ✓ Products: {products_count}")
        logger.info(f"  ✓ Users: {users_count}")
        logger.info(f"  ✓ Categories: {categories_count}")
        logger.info(f"  ✓ Expense Categories: {expense_categories_count}")

        # Show what was cleaned
        logger.info("\n🗑️  Cleaned data:")
        logger.info("  ✓ All sales and sale items")
        logger.info("  ✓ All payments")
        logger.info("  ✓ All repairs and repair items")
        logger.info("  ✓ All warranties")
        logger.info("  ✓ All expenses")
        logger.info("  ✓ All cash closings")
        logger.info("  ✓ All inventory movements")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error during cleanup: {e}")
        raise
    finally:
        db.close()


def confirm_cleanup():
    """Ask for user confirmation before cleaning."""
    print("\n" + "=" * 60)
    print("⚠️  DATABASE CLEANUP WARNING ⚠️")
    print("=" * 60)
    print("\nThis script will DELETE:")
    print("  • All sales and sale items")
    print("  • All payments")
    print("  • All repairs")
    print("  • All warranties")
    print("  • All expenses")
    print("  • All cash closings")
    print("  • All inventory movements")
    print("\nThis script will KEEP:")
    print("  • All customers")
    print("  • All products")
    print("  • All users")
    print("  • All categories")
    print("  • All expense categories")
    print("\n" + "=" * 60)

    response = input("\n⚠️  Are you sure you want to proceed? Type 'yes' to confirm: ")

    if response.lower() != "yes":
        print("❌ Cleanup cancelled.")
        return False

    return True


if __name__ == "__main__":
    # Check for --yes flag to skip confirmation
    skip_confirmation = "--yes" in sys.argv or "-y" in sys.argv

    if skip_confirmation or confirm_cleanup():
        try:
            clean_database()
        except Exception as e:
            logger.error(f"Failed to clean database: {e}")
            sys.exit(1)
    else:
        sys.exit(0)
