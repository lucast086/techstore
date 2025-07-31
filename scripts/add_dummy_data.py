#!/usr/bin/env python3
"""Add dummy data for testing all functionalities."""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up environment
os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/techstore_db"
)


def main():
    """Main function to add dummy data."""
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.customer import Customer
    from app.models.user import User
    from app.schemas.customer import CustomerCreate
    from app.schemas.payment import PaymentCreate
    from app.schemas.category import CategoryCreate
    from app.schemas.product import ProductCreate
    from app.services.customer import customer_service
    from app.services.category_service import EnhancedCategoryService
    from app.services.product_service import ProductService
    from app.crud.payment import payment_crud

    def create_dummy_customers(db: Session, admin_user: User):
        """Create dummy customers with various states."""
        print("\n📝 Creating dummy customers...")

        customers_data = [
            {
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john.doe@example.com",
                "address": "123 Main St, Anytown, USA",
                "notes": "VIP customer - always pays on time",
            },
            {
                "name": "Jane Smith",
                "phone": "+1234567891",
                "phone_secondary": "+1234567892",
                "email": "jane.smith@example.com",
                "address": "456 Oak Ave, Springfield, USA",
                "notes": "Prefers email communication",
            },
            {
                "name": "Bob Johnson",
                "phone": "+1234567893",
                "email": "bob.johnson@example.com",
                "notes": "New customer - referred by John Doe",
            },
            {
                "name": "Alice Williams",
                "phone": "+1234567894",
                "phone_secondary": "+1234567895",
                "address": "789 Pine Rd, Metropolis, USA",
                "notes": "Corporate account - NET 30 terms",
            },
            {
                "name": "Charlie Brown",
                "phone": "+1234567896",
                "email": "charlie.brown@example.com",
                "notes": "Student discount applicable",
            },
            {
                "name": "Diana Prince",
                "phone": "+1234567897",
                "email": "diana.prince@example.com",
                "address": "321 Wonder Way, Paradise Island",
                "notes": "Premium customer - priority service",
            },
            {
                "name": "Peter Parker",
                "phone": "+1234567898",
                "notes": "Freelance photographer - irregular income",
            },
            {
                "name": "Tony Stark",
                "phone": "+1234567899",
                "email": "tony.stark@starkindustries.com",
                "address": "10880 Malibu Point, Malibu, CA",
                "notes": "High-value customer - enterprise account",
            },
        ]

        customers = []
        for customer_data in customers_data:
            customer = customer_service.create_customer(
                db=db,
                customer_data=CustomerCreate(**customer_data),
                created_by_id=admin_user.id,
            )
            customers.append(customer)
            print(f"  ✅ Created customer: {customer.name}")

        return customers

    def create_initial_debts(db: Session, customers: list[Customer]):
        """
        Manually set initial account balances by directly inserting negative balance records.
        This simulates customers having existing debt without implementing sales.
        """
        print("\n📝 Setting initial customer debts...")

        # Initial debt amounts for testing
        debt_data = [
            (0, -430.00),  # John Doe owes $430
            (1, -1525.00),  # Jane Smith owes $1525
            (2, -120.00),  # Bob Johnson owes $120
            (3, -400.00),  # Alice Williams owes $400
            (4, -80.00),  # Charlie Brown owes $80
            (7, -15000.00),  # Tony Stark owes $15000
        ]

        for customer_index, debt_amount in debt_data:
            customer = customers[customer_index]
            # Update the account balance directly
            customer.account_balance = Decimal(str(debt_amount))
            db.commit()
            print(f"  ✅ Set initial debt for {customer.name}: ${abs(debt_amount):.2f}")

    def create_dummy_payments(db: Session, customers: list[Customer], admin_user: User):
        """Create dummy payments to create various balance scenarios."""
        print("\n💰 Creating dummy payments...")

        # Payments data: (customer_index, days_ago, amount, method, reference)
        payments_data = [
            # John Doe - partial payment (will still owe)
            (0, 10, 200.00, "cash", None),
            # Jane Smith - multiple partial payments (will still owe)
            (1, 35, 500.00, "transfer", "TRF-001"),
            (1, 15, 300.00, "card", "CARD-4532"),
            # Bob Johnson - overpayment (will have credit)
            (2, 5, 200.00, "cash", None),
            # Alice Williams - exact payment (zero balance)
            (3, 10, 400.00, "transfer", "TRF-002"),
            # Tony Stark - large partial payment
            (7, 15, 10000.00, "transfer", "WIRE-99887"),
        ]

        payments = []
        for customer_index, days_ago, amount, method, reference in payments_data:
            customer = customers[customer_index]
            payment_date = datetime.utcnow() - timedelta(days=days_ago)

            payment_data = PaymentCreate(
                customer_id=customer.id,
                amount=Decimal(str(amount)),
                payment_method=method,
                reference_number=reference,
                notes=f"Payment from {days_ago} days ago",
            )

            payment = payment_crud.create(
                db=db,
                customer_id=customer.id,
                payment=payment_data,
                received_by_id=admin_user.id,
            )

            # Update customer balance (payments increase balance)
            customer.account_balance += payment.amount

            # Update the created_at to simulate historical data
            payment.created_at = payment_date
            db.commit()

            payments.append(payment)
            print(
                f"  ✅ Created payment for {customer.name}: ${amount:.2f} via {method}"
            )

        return payments

    def display_final_balances(db: Session, customers: list[Customer]):
        """Display the final balance for each customer."""
        print("\n📊 Final Customer Balances:")
        print("-" * 60)

        for customer in customers:
            # Refresh to get updated balance
            db.refresh(customer)
            balance = customer.account_balance

            if balance < 0:
                status = f"Owes ${abs(balance):.2f} 🔴"
            elif balance > 0:
                status = f"Credit ${balance:.2f} 🟢"
            else:
                status = "Balanced $0.00 ✅"

            print(f"  {customer.name:<20} {status}")

    async def create_dummy_categories(db: Session, admin_user: User):
        """Create dummy product categories with hierarchy."""
        print("\n📂 Creating dummy categories...")

        category_service = EnhancedCategoryService(db)
        categories = {}

        # Root categories
        root_categories = [
            {
                "name": "Computers & Laptops",
                "description": "Desktop computers, laptops, and workstations",
                "icon": "💻",
                "display_order": 1,
            },
            {
                "name": "Components",
                "description": "Computer components and parts",
                "icon": "🔧",
                "display_order": 2,
            },
            {
                "name": "Peripherals",
                "description": "Computer peripherals and accessories",
                "icon": "⌨️",
                "display_order": 3,
            },
            {
                "name": "Networking",
                "description": "Networking equipment and accessories",
                "icon": "🌐",
                "display_order": 4,
            },
            {
                "name": "Storage",
                "description": "Storage devices and media",
                "icon": "💾",
                "display_order": 5,
            },
        ]

        # Create root categories
        for cat_data in root_categories:
            category = await category_service.create_category(
                CategoryCreate(**cat_data)
            )
            categories[category.name] = category
            print(f"  ✅ Created root category: {category.name}")

        # Subcategories
        subcategories = [
            # Computers & Laptops subcategories
            {
                "parent": "Computers & Laptops",
                "name": "Desktop PCs",
                "description": "Desktop computers for home and office",
                "display_order": 1,
            },
            {
                "parent": "Computers & Laptops",
                "name": "Laptops",
                "description": "Portable computers and notebooks",
                "display_order": 2,
            },
            {
                "parent": "Computers & Laptops",
                "name": "Gaming PCs",
                "description": "High-performance gaming computers",
                "display_order": 3,
            },
            # Components subcategories
            {
                "parent": "Components",
                "name": "Processors",
                "description": "CPUs from Intel and AMD",
                "display_order": 1,
            },
            {
                "parent": "Components",
                "name": "Graphics Cards",
                "description": "GPU cards for gaming and professional use",
                "display_order": 2,
            },
            {
                "parent": "Components",
                "name": "Motherboards",
                "description": "Motherboards for all platforms",
                "display_order": 3,
            },
            {
                "parent": "Components",
                "name": "Memory (RAM)",
                "description": "DDR4 and DDR5 memory modules",
                "display_order": 4,
            },
            {
                "parent": "Components",
                "name": "Power Supplies",
                "description": "PSUs for all system configurations",
                "display_order": 5,
            },
            # Peripherals subcategories
            {
                "parent": "Peripherals",
                "name": "Monitors",
                "description": "Computer monitors and displays",
                "display_order": 1,
            },
            {
                "parent": "Peripherals",
                "name": "Keyboards",
                "description": "Mechanical and membrane keyboards",
                "display_order": 2,
            },
            {
                "parent": "Peripherals",
                "name": "Mice",
                "description": "Gaming and productivity mice",
                "display_order": 3,
            },
            {
                "parent": "Peripherals",
                "name": "Speakers",
                "description": "Desktop speakers and sound systems",
                "display_order": 4,
            },
            # Storage subcategories
            {
                "parent": "Storage",
                "name": "SSDs",
                "description": "Solid state drives",
                "display_order": 1,
            },
            {
                "parent": "Storage",
                "name": "HDDs",
                "description": "Traditional hard disk drives",
                "display_order": 2,
            },
            {
                "parent": "Storage",
                "name": "External Storage",
                "description": "External drives and enclosures",
                "display_order": 3,
            },
        ]

        # Create subcategories
        for sub_data in subcategories:
            parent_name = sub_data.pop("parent")
            parent = categories[parent_name]
            sub_data["parent_id"] = parent.id

            category = await category_service.create_category(
                CategoryCreate(**sub_data)
            )
            categories[category.name] = category
            print(f"  ✅ Created subcategory: {category.name} under {parent_name}")

        return categories

    def create_dummy_products(db: Session, categories: dict, admin_user: User):
        """Create dummy products in various categories."""
        print("\n📦 Creating dummy products...")

        product_service = ProductService(db)
        products = []

        # Products data with real-world examples
        products_data = [
            # Desktop PCs
            {
                "category": "Desktop PCs",
                "sku": "PC-DELL-001",
                "name": "Dell OptiPlex 3090 Desktop",
                "description": "Business desktop with Intel Core i5, 8GB RAM, 256GB SSD",
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
            {
                "category": "Desktop PCs",
                "sku": "PC-HP-001",
                "name": "HP ProDesk 400 G7",
                "description": "Compact business PC with Intel Core i7, 16GB RAM, 512GB SSD",
                "brand": "HP",
                "model": "ProDesk 400 G7",
                "purchase_price": 650.00,
                "first_sale_price": 999.99,
                "second_sale_price": 979.99,
                "third_sale_price": 949.99,
                "current_stock": 8,
                "minimum_stock": 3,
                "maximum_stock": 20,
                "location": "A-01-02",
            },
            # Laptops
            {
                "category": "Laptops",
                "sku": "LAP-ASUS-001",
                "name": "ASUS VivoBook 15",
                "description": '15.6" FHD laptop with AMD Ryzen 5, 8GB RAM, 512GB SSD',
                "brand": "ASUS",
                "model": "VivoBook 15 X515EA",
                "purchase_price": 480.00,
                "first_sale_price": 749.99,
                "second_sale_price": 729.99,
                "third_sale_price": 699.99,
                "current_stock": 12,
                "minimum_stock": 5,
                "maximum_stock": 25,
                "location": "B-01-01",
            },
            {
                "category": "Laptops",
                "sku": "LAP-LEN-001",
                "name": "Lenovo ThinkPad E14",
                "description": '14" business laptop with Intel Core i5, 8GB RAM, 256GB SSD',
                "brand": "Lenovo",
                "model": "ThinkPad E14 Gen 4",
                "purchase_price": 580.00,
                "first_sale_price": 899.99,
                "second_sale_price": 879.99,
                "third_sale_price": 849.99,
                "current_stock": 2,
                "minimum_stock": 5,
                "maximum_stock": 20,
                "location": "B-01-02",
            },
            # Gaming PCs
            {
                "category": "Gaming PCs",
                "sku": "GAM-MSI-001",
                "name": "MSI Aegis Gaming Desktop",
                "description": "Gaming PC with RTX 4060, Intel i5-13400F, 16GB RAM, 1TB SSD",
                "brand": "MSI",
                "model": "Aegis RS 13",
                "purchase_price": 950.00,
                "first_sale_price": 1499.99,
                "second_sale_price": 1449.99,
                "third_sale_price": 1399.99,
                "current_stock": 0,
                "minimum_stock": 2,
                "maximum_stock": 10,
                "location": "C-01-01",
            },
            # Processors
            {
                "category": "Processors",
                "sku": "CPU-INT-001",
                "name": "Intel Core i5-13600K",
                "description": "14-core processor, 3.5GHz base, 5.1GHz boost, LGA1700",
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
            {
                "category": "Processors",
                "sku": "CPU-AMD-001",
                "name": "AMD Ryzen 7 5800X",
                "description": "8-core processor, 3.8GHz base, 4.7GHz boost, AM4",
                "brand": "AMD",
                "model": "Ryzen 7 5800X",
                "purchase_price": 220.00,
                "first_sale_price": 299.99,
                "second_sale_price": 289.99,
                "third_sale_price": 279.99,
                "current_stock": 25,
                "minimum_stock": 10,
                "maximum_stock": 50,
                "location": "D-01-02",
            },
            # Graphics Cards
            {
                "category": "Graphics Cards",
                "sku": "GPU-NV-001",
                "name": "NVIDIA RTX 4060 Ti",
                "description": "8GB GDDR6, PCIe 4.0, DLSS 3, Ray Tracing",
                "brand": "ASUS",
                "model": "TUF Gaming RTX 4060 Ti",
                "purchase_price": 380.00,
                "first_sale_price": 499.99,
                "second_sale_price": 489.99,
                "third_sale_price": 479.99,
                "current_stock": 6,
                "minimum_stock": 5,
                "maximum_stock": 20,
                "location": "E-01-01",
            },
            # Motherboards
            {
                "category": "Motherboards",
                "sku": "MB-ASUS-001",
                "name": "ASUS Prime B760M-A",
                "description": "LGA1700, DDR5, PCIe 4.0, M.2 slots",
                "brand": "ASUS",
                "model": "Prime B760M-A",
                "purchase_price": 110.00,
                "first_sale_price": 149.99,
                "second_sale_price": 144.99,
                "third_sale_price": 139.99,
                "current_stock": 30,
                "minimum_stock": 10,
                "maximum_stock": 50,
                "location": "F-01-01",
            },
            # Memory
            {
                "category": "Memory (RAM)",
                "sku": "RAM-COR-001",
                "name": "Corsair Vengeance 16GB DDR5",
                "description": "16GB (2x8GB) DDR5-5600 CL36",
                "brand": "Corsair",
                "model": "Vengeance DDR5",
                "purchase_price": 75.00,
                "first_sale_price": 99.99,
                "second_sale_price": 94.99,
                "third_sale_price": 89.99,
                "current_stock": 45,
                "minimum_stock": 20,
                "maximum_stock": 100,
                "location": "G-01-01",
            },
            # Monitors
            {
                "category": "Monitors",
                "sku": "MON-LG-001",
                "name": 'LG 24" IPS Monitor',
                "description": '24" FHD IPS, 75Hz, AMD FreeSync',
                "brand": "LG",
                "model": "24MK430H-B",
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
                "description": "1TB M.2 NVMe, PCIe 3.0, up to 3500MB/s",
                "brand": "Samsung",
                "model": "980 1TB",
                "purchase_price": 65.00,
                "first_sale_price": 89.99,
                "second_sale_price": 84.99,
                "third_sale_price": 79.99,
                "current_stock": 60,
                "minimum_stock": 20,
                "maximum_stock": 100,
                "location": "J-01-01",
                "barcode": "8801643021234",
            },
            # Keyboards
            {
                "category": "Keyboards",
                "sku": "KB-LOG-001",
                "name": "Logitech G213 Prodigy",
                "description": "RGB Gaming Keyboard, Membrane switches",
                "brand": "Logitech",
                "model": "G213 Prodigy",
                "purchase_price": 35.00,
                "first_sale_price": 59.99,
                "second_sale_price": 54.99,
                "third_sale_price": 49.99,
                "current_stock": 35,
                "minimum_stock": 15,
                "maximum_stock": 60,
                "location": "K-01-01",
            },
            # Mice
            {
                "category": "Mice",
                "sku": "MS-RAZ-001",
                "name": "Razer DeathAdder V3",
                "description": "Wireless gaming mouse, 30K DPI sensor",
                "brand": "Razer",
                "model": "DeathAdder V3",
                "purchase_price": 95.00,
                "first_sale_price": 149.99,
                "second_sale_price": 139.99,
                "third_sale_price": 129.99,
                "current_stock": 18,
                "minimum_stock": 10,
                "maximum_stock": 30,
                "location": "K-02-01",
            },
        ]

        # Create products
        for prod_data in products_data:
            category_name = prod_data.pop("category")
            category = categories[category_name]

            product_create = ProductCreate(
                category_id=category.id, created_by=admin_user.id, **prod_data
            )

            product = product_service.create_product(db, product_create)
            products.append(product)

            # Determine stock status for display
            if product.current_stock == 0:
                stock_status = "🔴 Out of Stock"
            elif product.current_stock < product.minimum_stock:
                stock_status = "🟡 Low Stock"
            elif (
                product.maximum_stock and product.current_stock > product.maximum_stock
            ):
                stock_status = "🟠 Overstock"
            else:
                stock_status = "🟢 In Stock"

            print(
                f"  ✅ Created product: {product.name} ({product.sku}) - {stock_status}"
            )

        return products

    print("🚀 Starting dummy data creation...")

    # Get database session
    db = SessionLocal()

    try:
        # Get the admin user (ID 1)
        admin_user = db.query(User).filter(User.id == 1).first()
        if not admin_user:
            print("❌ Admin user not found. Please ensure the database is initialized.")
            return

        # Create dummy data
        customers = create_dummy_customers(db, admin_user)
        create_initial_debts(db, customers)
        payments = create_dummy_payments(db, customers, admin_user)

        # Create categories and products
        import asyncio

        loop = asyncio.get_event_loop()
        categories = loop.run_until_complete(create_dummy_categories(db, admin_user))
        products = create_dummy_products(db, categories, admin_user)

        # Display final balances
        display_final_balances(db, customers)

        print("\n✅ Dummy data creation completed successfully!")
        print("\n📋 Summary:")
        print(f"  - Created {len(customers)} customers")
        print(f"  - Created {len(payments)} payments")
        print(f"  - Created {len(categories)} categories (with hierarchy)")
        print(f"  - Created {len(products)} products")
        print("\n🎯 You can now test:")
        print("  - Customers with debt (John, Jane, Charlie, Tony)")
        print("  - Customers with credit (Bob)")
        print("  - Customers with zero balance (Alice)")
        print("  - Customers with no transactions (Diana, Peter)")
        print("  - Product categories with hierarchical structure")
        print(
            "  - Products with various stock levels (in stock, low stock, out of stock)"
        )
        print("  - Product filtering and search functionality")

    except Exception as e:
        print(f"\n❌ Error creating dummy data: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
