#!/usr/bin/env python3
"""Seed script to create initial admin user."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker


def create_admin_user():
    """Create initial admin user for the system."""
    # Create sync engine
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)

    # Admin user data
    admin_email = "admin@techstore.com"
    admin_password = "Admin123!"

    with Session() as session:
        try:
            # Check if admin already exists
            existing_admin = session.execute(
                select(User).where(User.email == admin_email)
            ).scalar_one_or_none()

            if existing_admin:
                print(f"✓ Admin user already exists: {admin_email}")
                return

            # Create admin user
            admin = User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                full_name="System Administrator",
                role="admin",
                is_active=True,
            )

            session.add(admin)
            session.commit()

            print("✓ Admin user created successfully!")
            print(f"  Email: {admin.email}")
            print(f"  Password: {admin_password}")
            print(f"  Role: {admin.role}")
            print("\n⚠️  Please change the password after first login!")

        except Exception as e:
            print(f"✗ Error creating admin user: {e}")
            session.rollback()
            sys.exit(1)


if __name__ == "__main__":
    print("🚀 Creating initial admin user...")
    create_admin_user()
