#!/usr/bin/env python3
"""Add only products to the database (assumes categories already exist)."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up environment
os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/techstore_db"
)


async def main():
    """Main function to add products."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.product import Category
    from app.schemas.product import ProductCreate
    from app.services.product_service import ProductService

    print("🚀 Starting products creation...")

    # Get database session
    db = SessionLocal()

    try:
        # Get the admin user (ID 1)
        admin_user = db.query(User).filter(User.id == 1).first()
        if not admin_user:
            print("❌ Admin user not found. Please ensure the database is initialized.")
            return

        # Initialize services
        product_service = ProductService(db)

        # Get categories by name
        categories = {}
        category_names = [
            "Desktop PCs",
            "Laptops",
            "Gaming PCs",
            "Processors",
            "Graphics Cards",
            "Motherboards",
            "Memory (RAM)",
            "Monitors",
            "Keyboards",
            "Mice",
            "SSDs",
            "HDDs",
        ]

        for name in category_names:
            category = db.query(Category).filter(Category.name == name).first()
            if category:
                categories[name] = category
            else:
                print(f"⚠️  Warning: Category '{name}' not found")

        print("\n📦 Creating products...")

        # Sample products
        products_data = [
            # Desktop PCs
            {
                "category": "Desktop PCs",
                "sku": "PC-DELL-001",
                "name": "Dell OptiPlex 3090",
                "description": "Business desktop with Intel Core i5",
                "brand": "Dell",
                "model": "OptiPlex 3090",
                "purchase_price": 450.00,
                "first_sale_price": 699.99,
                "second_sale_price": 679.99,
                "third_sale_price": 659.99,
                "current_stock": 15,
                "minimum_stock": 5,
                "maximum_stock": 30,
                "location": "A-01-01",
            },
            # Laptops
            {
                "category": "Laptops",
                "sku": "LAP-ASUS-001",
                "name": "ASUS VivoBook 15",
                "description": "15.6 inch FHD laptop",
                "brand": "ASUS",
                "model": "VivoBook 15",
                "purchase_price": 480.00,
                "first_sale_price": 749.99,
                "second_sale_price": 729.99,
                "third_sale_price": 699.99,
                "current_stock": 12,
                "minimum_stock": 5,
                "maximum_stock": 25,
                "location": "B-01-01",
            },
            # Processors
            {
                "category": "Processors",
                "sku": "CPU-INT-001",
                "name": "Intel Core i5-13600K",
                "description": "14-core processor",
                "brand": "Intel",
                "model": "i5-13600K",
                "purchase_price": 250.00,
                "first_sale_price": 349.99,
                "second_sale_price": 339.99,
                "third_sale_price": 329.99,
                "current_stock": 18,
                "minimum_stock": 10,
                "maximum_stock": 50,
                "location": "D-01-01",
            },
            # Graphics Cards
            {
                "category": "Graphics Cards",
                "sku": "GPU-NV-001",
                "name": "NVIDIA RTX 4060 Ti",
                "description": "8GB GDDR6 Graphics Card",
                "brand": "NVIDIA",
                "model": "RTX 4060 Ti",
                "purchase_price": 380.00,
                "first_sale_price": 499.99,
                "second_sale_price": 489.99,
                "third_sale_price": 479.99,
                "current_stock": 6,
                "minimum_stock": 5,
                "maximum_stock": 20,
                "location": "E-01-01",
            },
            # Monitors
            {
                "category": "Monitors",
                "sku": "MON-LG-001",
                "name": "LG 24 IPS Monitor",
                "description": "24 inch FHD IPS Display",
                "brand": "LG",
                "model": "24MK430H",
                "purchase_price": 120.00,
                "first_sale_price": 179.99,
                "second_sale_price": 169.99,
                "third_sale_price": 159.99,
                "current_stock": 22,
                "minimum_stock": 10,
                "maximum_stock": 40,
                "location": "H-01-01",
            },
            # SSDs
            {
                "category": "SSDs",
                "sku": "SSD-SAM-001",
                "name": "Samsung 980 1TB NVMe",
                "description": "1TB M.2 NVMe SSD",
                "brand": "Samsung",
                "model": "980 1TB",
                "purchase_price": 65.00,
                "first_sale_price": 89.99,
                "second_sale_price": 84.99,
                "third_sale_price": 79.99,
                "current_stock": 0,
                "minimum_stock": 20,
                "maximum_stock": 100,
                "location": "J-01-01",
            },
            # Low stock example
            {
                "category": "Memory (RAM)",
                "sku": "RAM-COR-001",
                "name": "Corsair Vengeance 16GB DDR5",
                "description": "16GB DDR5-5600 Memory Kit",
                "brand": "Corsair",
                "model": "Vengeance DDR5",
                "purchase_price": 75.00,
                "first_sale_price": 99.99,
                "second_sale_price": 94.99,
                "third_sale_price": 89.99,
                "current_stock": 3,
                "minimum_stock": 10,
                "maximum_stock": 50,
                "location": "G-01-01",
            },
        ]

        # Create products
        products = []
        for prod_data in products_data:
            category_name = prod_data.pop("category")
            category = categories.get(category_name)

            if not category:
                print(f"  ⚠️  Skipping product {prod_data['name']} - category not found")
                continue

            product_create = ProductCreate(category_id=category.id, **prod_data)

            product = await product_service.create_product(
                product_create, admin_user.id
            )
            products.append(product)

            # Determine stock status
            if product.current_stock == 0:
                status = "🔴 Out of Stock"
            elif product.current_stock < product.minimum_stock:
                status = "🟡 Low Stock"
            else:
                status = "🟢 In Stock"

            print(f"  ✅ Created product: {product.name} - {status}")

        print(f"\n✅ Successfully created {len(products)} products!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
