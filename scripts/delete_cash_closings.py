#!/usr/bin/env python3
"""Script to delete all cash closings from the database."""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.database import SessionLocal
from app.models.cash_closing import CashClosing


def delete_all_cash_closings():
    """Delete all cash closings from the database."""
    db = SessionLocal()
    try:
        # Count existing cash closings
        count = db.query(CashClosing).count()
        print(f"Found {count} cash closings to delete.")

        if count > 0:
            # Delete all cash closings
            db.query(CashClosing).delete()
            db.commit()
            print(f"Successfully deleted {count} cash closings.")
        else:
            print("No cash closings to delete.")

    except Exception as e:
        print(f"Error deleting cash closings: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    delete_all_cash_closings()
