#!/usr/bin/env python3
"""Reset database - delete all data except admin user."""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up environment
os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/techstore_db"
)


def main():
    """Main function to reset database."""
    from sqlalchemy import text
    from app.database import SessionLocal

    print("⚠️  WARNING: This will delete all data except the admin user!")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() != "yes":
        print("❌ Operation cancelled.")
        return

    db = SessionLocal()

    try:
        print("\n🗑️  Deleting data...")

        # Disable foreign key constraints temporarily
        db.execute(text("SET session_replication_role = 'replica';"))

        # Delete in order to respect foreign key constraints
        # (when re-enabled)
        tables_to_clear = [
            "product_suppliers",
            "product_images",
            "products",
            "categories",
            "payments",
            "customers",
            "password_reset_tokens",
            # Don't delete users - we want to keep the admin
        ]

        for table in tables_to_clear:
            try:
                result = db.execute(text(f"DELETE FROM {table}"))
                count = result.rowcount
                db.commit()
                print(f"  ✅ Deleted {count} records from {table}")
            except Exception as e:
                print(f"  ⚠️  Error deleting from {table}: {e}")
                db.rollback()

        # Re-enable foreign key constraints
        db.execute(text("SET session_replication_role = 'origin';"))
        db.commit()

        # Reset sequences for auto-increment IDs
        sequences_to_reset = [
            ("categories_id_seq", "categories"),
            ("products_id_seq", "products"),
            ("product_images_id_seq", "product_images"),
            ("product_suppliers_id_seq", "product_suppliers"),
            ("customers_id_seq", "customers"),
            ("payments_id_seq", "payments"),
        ]

        for seq_name, _ in sequences_to_reset:
            try:
                db.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH 1"))
                db.commit()
                print(f"  ✅ Reset sequence {seq_name}")
            except Exception as e:
                print(f"  ⚠️  Could not reset {seq_name}: {e}")
                db.rollback()

        print("\n✅ Database reset completed!")
        print("   - All data deleted except admin user")
        print("   - Sequences reset to start from 1")
        print("\n💡 You can now run scripts/add_dummy_data.py to populate test data")

    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
