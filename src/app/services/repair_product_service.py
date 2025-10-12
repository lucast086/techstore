"""Service for managing repair products in the POS system."""

import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.product import Product

logger = logging.getLogger(__name__)

# Constants for repair service products
REPAIR_SERVICE_SKU = "REPAIR-SERVICE"
REPAIR_SERVICE_NAME = "Servicio de Reparación"
REPAIR_SERVICE_CATEGORY = "SERVICIOS"


class RepairProductService:
    """Service for handling repair products in POS."""

    def get_or_create_repair_product(self, db: Session) -> Product:
        """Get or create the repair service product.

        This product is used to represent repairs in the POS system.

        Args:
            db: Database session.

        Returns:
            The repair service product.
        """
        # Try to find existing repair service product
        product = db.query(Product).filter(Product.sku == REPAIR_SERVICE_SKU).first()

        if product:
            logger.debug(f"Found existing repair service product: {product.id}")
            return product

        # Get or create service category first
        from app.models.product import Category

        service_category = (
            db.query(Category).filter(Category.name == REPAIR_SERVICE_CATEGORY).first()
        )
        if not service_category:
            service_category = Category(
                name=REPAIR_SERVICE_CATEGORY,
                description="Categoría para servicios de reparación",
                is_active=True,
            )
            db.add(service_category)
            db.flush()

        # Create new repair service product
        product = Product(
            sku=REPAIR_SERVICE_SKU,
            name=REPAIR_SERVICE_NAME,
            description="Producto especial para servicios de reparación",
            category_id=service_category.id,
            brand="TECHSTORE",
            purchase_price=Decimal("0.00"),
            first_sale_price=Decimal("0.00"),  # Price will be overridden by repair cost
            second_sale_price=Decimal("0.00"),
            third_sale_price=Decimal("0.00"),
            current_stock=0,  # Service products don't have stock
            minimum_stock=0,
            barcode=REPAIR_SERVICE_SKU,
            is_active=True,
            is_service=True,  # Mark as service product
            created_by=1,  # System user
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        logger.info(f"Created repair service product: {product.id}")
        return product

    def format_repair_as_product(self, repair_data: dict) -> dict:
        """Format repair data as a product for POS cart.

        Args:
            repair_data: Repair information from prepare_for_sale.

        Returns:
            Dictionary formatted for POS cart item.
        """
        # Build description including device and problem
        description = f"Reparación #{repair_data['repair_number']}\n"
        description += f"{repair_data['device']} - {repair_data['device_type']}\n"
        description += (
            f"Problema: {repair_data['problem'][:100]}"  # Limit problem description
        )

        # Format cost breakdown
        cost_breakdown = []
        if repair_data.get("labor_cost", 0) > 0:
            cost_breakdown.append(f"Mano de obra: ${repair_data['labor_cost']:.2f}")
        if repair_data.get("parts_cost", 0) > 0:
            cost_breakdown.append(f"Repuestos: ${repair_data['parts_cost']:.2f}")

        return {
            "product_id": None,  # Will be set to repair service product ID
            "sku": f"REP-{repair_data['repair_number']}",
            "name": f"Reparación {repair_data['repair_number']}",
            "description": description,
            "category": REPAIR_SERVICE_CATEGORY,
            "brand": repair_data.get("device", ""),
            "quantity": 1,  # Always 1 for repairs
            "unit_price": repair_data["amount_due"],  # Use amount due after deposits
            "total_price": repair_data["amount_due"],
            "original_price": repair_data["total_cost"],  # Full price before deposits
            "discount_amount": repair_data[
                "total_deposits"
            ],  # Deposits shown as discount
            "is_repair": True,
            "repair_id": repair_data["repair_id"],
            "repair_number": repair_data["repair_number"],
            "customer_id": repair_data["customer_id"],
            "customer_name": repair_data["customer_name"],
            "cost_breakdown": "\n".join(cost_breakdown) if cost_breakdown else None,
            "deposits": repair_data.get("deposits", []),
            "total_deposits": repair_data["total_deposits"],
        }

    def can_add_to_cart(self, repair_data: dict) -> tuple[bool, Optional[str]]:
        """Check if repair can be added to POS cart.

        Args:
            repair_data: Repair information.

        Returns:
            Tuple of (can_add, error_message).
        """
        # Check if amount due is positive
        if repair_data["amount_due"] <= 0:
            return (
                False,
                f"La reparación {repair_data['repair_number']} ya está completamente pagada con señas",
            )

        # All checks passed
        return True, None


# Create singleton instance
repair_product_service = RepairProductService()
