#!/usr/bin/env python3
"""Script to create or update the REPAIR-SERVICE product for repair deliveries."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from decimal import Decimal

from app.database import SessionLocal
from app.models.product import Category, Product
from app.models.user import User


def create_repair_service_product():
    """Create or update the REPAIR-SERVICE product."""
    db = SessionLocal()
    try:
        # Check if product already exists
        existing_product = (
            db.query(Product).filter(Product.sku == "REPAIR-SERVICE").first()
        )

        if existing_product:
            print(f"✓ Repair service product already exists: {existing_product.name}")
            print(f"  SKU: {existing_product.sku}")
            print(f"  is_service: {existing_product.is_service}")
            return

        # Find or create Services category
        services_category = (
            db.query(Category).filter(Category.name == "Services").first()
        )

        if not services_category:
            print("Creating 'Services' category...")
            services_category = Category(
                name="Services",
                description="Service products (non-physical items)",
                is_active=True,
                display_order=999,
            )
            db.add(services_category)
            db.flush()
            print(f"✓ Created category: {services_category.name}")

        # Get first admin user to set as creator
        admin_user = (
            db.query(User).filter(User.role == "admin", User.is_active == True).first()
        )

        if not admin_user:
            print(
                "ERROR: No active admin user found. Please create an admin user first."
            )
            return

        # Create repair service product
        print("Creating REPAIR-SERVICE product...")
        repair_service = Product(
            sku="REPAIR-SERVICE",
            name="Repair Service",
            description="Service product for repair deliveries - price set per repair",
            category_id=services_category.id,
            purchase_price=Decimal("0.00"),
            first_sale_price=Decimal("0.00"),
            second_sale_price=Decimal("0.00"),
            third_sale_price=Decimal("0.00"),
            tax_rate=Decimal("0.00"),
            current_stock=0,
            minimum_stock=0,
            is_active=True,
            is_service=True,  # This is key - marks it as a service
            created_by=admin_user.id,
        )

        db.add(repair_service)
        db.commit()

        print("✓ Successfully created product:")
        print(f"  Name: {repair_service.name}")
        print(f"  SKU: {repair_service.sku}")
        print(f"  Category: {services_category.name}")
        print(f"  is_service: {repair_service.is_service}")
        print("\n✓ Ready to use for repair deliveries!")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Creating REPAIR-SERVICE product for repair deliveries")
    print("=" * 60)
    create_repair_service_product()
