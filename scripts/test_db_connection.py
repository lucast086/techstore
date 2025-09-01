#!/usr/bin/env python3
"""Test database connection for current environment."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Color codes for terminal output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def print_color(color, message):
    """Print colored message."""
    print(f"{color}{message}{NC}")


def test_connection():
    """Test database connection."""
    # Load environment variables
    load_dotenv()

    # Get database URL
    db_url = os.getenv("DATABASE_URL")
    environment = os.getenv("ENVIRONMENT", "unknown")

    if not db_url:
        print_color(RED, "❌ DATABASE_URL not found in environment variables")
        return False

    # Hide password in display
    display_url = db_url
    if "@" in db_url:
        parts = db_url.split("@")
        if "://" in parts[0]:
            protocol_and_creds = parts[0].split("://")
            display_url = f"{protocol_and_creds[0]}://***@{parts[1]}"

    print_color(BLUE, f"📍 Environment: {environment}")
    print_color(BLUE, f"🔗 Testing connection to: {display_url}")
    print()

    try:
        # Create engine and test connection
        engine = create_engine(db_url)

        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print_color(GREEN, "✅ Connection successful!")
            print_color(GREEN, f"   PostgreSQL version: {version}")

            # Get database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print_color(GREEN, f"   Database name: {db_name}")

            # Get table count
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """
                )
            )
            table_count = result.scalar()
            print_color(GREEN, f"   Tables in database: {table_count}")

            # Check if it's a TechStore database by looking for key tables
            result = conn.execute(
                text(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('users', 'customers', 'products', 'sales', 'repairs')
                ORDER BY table_name
            """
                )
            )

            techstore_tables = [row[0] for row in result]

            if techstore_tables:
                print_color(
                    GREEN, f"   TechStore tables found: {', '.join(techstore_tables)}"
                )
            else:
                print_color(
                    YELLOW,
                    "   ⚠️  No TechStore tables found - might be an empty database",
                )

            # Test write permissions (in a transaction that we'll rollback)
            try:
                conn.execute(text("BEGIN"))
                conn.execute(text("CREATE TEMP TABLE test_write (id INT)"))
                conn.execute(text("DROP TABLE test_write"))
                conn.execute(text("ROLLBACK"))
                print_color(GREEN, "   Write permissions: ✅")
            except Exception:
                print_color(YELLOW, "   Write permissions: ❌ (read-only)")

        return True

    except OperationalError as e:
        print_color(RED, "❌ Connection failed!")
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)

        # Provide helpful error messages
        if "password authentication failed" in error_msg:
            print_color(RED, "   Error: Invalid username or password")
        elif "could not connect to server" in error_msg:
            print_color(RED, "   Error: Cannot reach database server")
            print_color(YELLOW, "   Check that the host and port are correct")
        elif "database" in error_msg and "does not exist" in error_msg:
            print_color(RED, "   Error: Database does not exist")
        else:
            print_color(RED, f"   Error: {error_msg}")

        return False

    except Exception as e:
        print_color(RED, f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function."""
    print_color(BLUE, "🔍 Testing Database Connection")
    print_color(BLUE, "=" * 40)
    print()

    success = test_connection()

    print()
    print_color(BLUE, "=" * 40)

    if not success:
        print_color(YELLOW, "\nTroubleshooting tips:")
        print_color(YELLOW, "1. Check your .env file has the correct DATABASE_URL")
        print_color(YELLOW, "2. Ensure the database server is running")
        print_color(YELLOW, "3. Verify network connectivity to the database")
        print_color(YELLOW, "4. Confirm username and password are correct")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
