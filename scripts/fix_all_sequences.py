#!/usr/bin/env python3
"""Fix all PostgreSQL sequences to match current max IDs.

This script fixes sequence values that get out of sync when:
- Data is inserted manually (bypassing ORM)
- Database is restored from backup
- Sequences are not properly updated after migrations

Usage:
    python scripts/fix_all_sequences.py
    # or
    poetry run python scripts/fix_all_sequences.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import SessionLocal
from app.config import settings


def fix_all_sequences():
    """Fix all table sequences to match their current max ID values."""

    # Get all tables with id sequences
    tables_with_sequences = [
        "users",
        "customers",
        "products",
        "categories",
        "repairs",
        "repairstatushistorys",
        "sales",
        "sale_items",
        "expenses",
        "expense_categories",
        "suppliers",
        "cash_closings",
        "customer_transactions",
        "customer_accounts",
        "warranties",
        "repair_deposits",
    ]

    db = SessionLocal()

    try:
        print("🔧 Fixing PostgreSQL sequences...\n")

        for table in tables_with_sequences:
            sequence_name = f"{table}_id_seq"

            # Fix the sequence
            query = text(
                f"""
                SELECT setval('{sequence_name}',
                    COALESCE((SELECT MAX(id) FROM {table}), 1),
                    true
                )
            """
            )

            try:
                result = db.execute(query)
                new_value = result.scalar()
                print(f"✅ {table:30} -> sequence set to {new_value}")
            except Exception as e:
                # Skip if table or sequence doesn't exist
                if "does not exist" in str(e):
                    print(f"⏭️  {table:30} -> table or sequence not found (skipping)")
                else:
                    print(f"❌ {table:30} -> error: {e}")

        db.commit()
        print("\n✨ All sequences fixed successfully!")

    except Exception as e:
        print(f"\n❌ Error fixing sequences: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}\n")
    fix_all_sequences()
