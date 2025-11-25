"""CRUD operations for sales management."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, case, desc, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.schemas.sale import SaleCreate
from app.utils.timezone import get_utc_now

logger = logging.getLogger(__name__)


class SaleCRUD:
    """CRUD operations for sales."""

    def generate_invoice_number(self, db: Session) -> str:
        """Generate unique invoice number."""
        current_year = get_utc_now().year

        # Get the last invoice number for current year
        last_sale = (
            db.query(Sale)
            .filter(Sale.invoice_number.like(f"INV-{current_year}-%"))
            .order_by(desc(Sale.id))
            .first()
        )

        if last_sale:
            # Extract number and increment
            last_number = int(last_sale.invoice_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"INV-{current_year}-{new_number:05d}"

    def create_sale(self, db: Session, *, sale_in: SaleCreate, user_id: int) -> Sale:
        """Create new sale with items and update inventory.

        If amount_paid is provided, delegates to SalesService for payment processing.
        """
        # If amount_paid is provided and greater than 0, use the service for integrated processing
        # This handles payment creation automatically
        if sale_in.amount_paid and sale_in.amount_paid > 0:
            from app.services.sales_service import sales_service

            return sales_service.process_sale_with_payment(db, sale_in, user_id)

        # Otherwise, use the original implementation
        return self._create_sale_internal(db, sale_in=sale_in, user_id=user_id)

    def _create_sale_internal(
        self, db: Session, *, sale_in: SaleCreate, user_id: int
    ) -> Sale:
        """Internal method to create sale without payment processing."""
        # Start transaction
        try:
            # BUSINESS RULE: All sales MUST have a customer
            # If no customer_id provided, default to walk-in customer (ID=1)
            # This ensures ALL sales and payments are tracked in the transaction system
            if not sale_in.customer_id:
                logger.warning(
                    "Sale created without customer_id, defaulting to walk-in customer (ID=1). "
                    "Frontend should always provide a customer_id."
                )
                sale_in.customer_id = 1

            # Check if sales are allowed (cash closing check)
            # Uses business day logic with 4 AM cutoff
            from app.services.cash_closing_service import cash_closing_service

            can_process, reason = cash_closing_service.check_can_process_sale(db=db)
            if not can_process:
                raise ValueError(reason)

            # Generate invoice number
            invoice_number = self.generate_invoice_number(db)

            # Calculate totals
            subtotal = Decimal("0")
            tax_amount = Decimal("0")

            # Validate products and calculate totals
            for item in sale_in.items:
                product = (
                    db.query(Product).filter(Product.id == item.product_id).first()
                )
                if not product:
                    raise ValueError(f"Product {item.product_id} not found")

                # Only check stock for physical products, not services
                if not product.is_service and product.current_stock < item.quantity:
                    raise ValueError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.current_stock}, Requested: {item.quantity}"
                    )

                # Calculate item total
                item_subtotal = item.unit_price * item.quantity
                item_discount = (
                    item_subtotal * item.discount_percentage / 100
                ) + item.discount_amount
                item_total = item_subtotal - item_discount

                subtotal += item_total

            # Apply sale-level discount first
            subtotal_after_discount = subtotal - sale_in.discount_amount

            # Calculate tax on final discounted amount
            for item in sale_in.items:
                product = (
                    db.query(Product).filter(Product.id == item.product_id).first()
                )
                # Calculate proportional tax for each item after sale discount
                item_subtotal = item.unit_price * item.quantity
                item_discount = (
                    item_subtotal * item.discount_percentage / 100
                ) + item.discount_amount
                item_total = item_subtotal - item_discount

                # Proportional discount allocation
                item_proportion = item_total / subtotal if subtotal > 0 else 0
                item_share_of_sale_discount = sale_in.discount_amount * item_proportion
                item_final_price = item_total - item_share_of_sale_discount

                tax_amount += item_final_price * product.tax_rate / 100

            total_amount = subtotal_after_discount + tax_amount

            # Determine payment status based on amount paid
            # If amount_paid is not specified, default to full payment for walk-in customers
            # and to the amount based on payment method for registered customers
            if sale_in.amount_paid is not None:
                amount_paid = sale_in.amount_paid
            else:
                # Default behavior when amount_paid is not specified:
                # For walk-in customers (no customer_id), assume full payment
                # For registered customers, the frontend should always specify amount_paid
                if not sale_in.customer_id:
                    amount_paid = total_amount  # Walk-in customers must pay in full
                else:
                    # For registered customers, amount_paid should always be specified
                    # If not specified, assume full payment to maintain backward compatibility
                    amount_paid = total_amount

            # Validate walk-in customers must pay in full
            if not sale_in.customer_id and amount_paid < total_amount:
                raise ValueError(
                    f"Walk-in customers must pay in full. "
                    f"Total: ${total_amount:.2f}, Paid: ${amount_paid:.2f}"
                )

            if amount_paid >= total_amount:
                payment_status = "paid"
            elif amount_paid > Decimal("0"):
                payment_status = "partial"
            else:
                payment_status = "pending"

            # Create sale
            sale = Sale(
                invoice_number=invoice_number,
                customer_id=sale_in.customer_id,
                user_id=user_id,
                subtotal=subtotal_after_discount,  # Store subtotal after global discount
                discount_amount=sale_in.discount_amount,
                tax_amount=tax_amount,
                total_amount=total_amount,
                payment_status=payment_status,
                payment_method=sale_in.payment_method,
                notes=sale_in.notes,
            )
            db.add(sale)
            db.flush()  # Get sale.id without committing

            # Create sale items and update inventory
            for item in sale_in.items:
                product = (
                    db.query(Product).filter(Product.id == item.product_id).first()
                )

                # Calculate item totals
                item_subtotal = item.unit_price * item.quantity
                item_discount = (
                    item_subtotal * item.discount_percentage / 100
                ) + item.discount_amount
                item_total = item_subtotal - item_discount

                # Create sale item
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    discount_percentage=item.discount_percentage,
                    discount_amount=item.discount_amount,
                    total_price=item_total,
                )
                db.add(sale_item)

                # Update inventory (only for physical products, not services)
                if not product.is_service:
                    product.current_stock -= item.quantity
                    db.add(product)

            # Update sale with actual paid amount
            sale.paid_amount = amount_paid

            # SIMPLIFIED: Only record the SALE transaction (creates debt)
            # Payment handling is now done in web/sales.py after sale creation
            # This follows the refactor plan: separate sale creation from payment processing
            if sale_in.customer_id:
                from app.services.customer_account_service import (
                    customer_account_service,
                )

                # ALWAYS record the sale as debt (SALE transaction)
                # Payments will be applied separately by the web endpoint
                try:
                    customer_account_service.record_sale(db, sale, user_id)
                    logger.info(
                        f"Recorded SALE transaction for {invoice_number}: "
                        f"${total_amount} debt for customer {sale_in.customer_id}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to record sale in account system: {e}")

                # Log debt amount
                if amount_paid < total_amount:
                    debt_amount = total_amount - amount_paid
                    logger.info(
                        f"Debt of ${debt_amount} remaining for customer {sale_in.customer_id} "
                        f"from sale {invoice_number}"
                    )

            db.commit()
            db.refresh(sale)

            # Load relationships
            sale = (
                db.query(Sale)
                .options(
                    joinedload(Sale.customer),
                    joinedload(Sale.user),
                    selectinload(Sale.items).joinedload(SaleItem.product),
                )
                .filter(Sale.id == sale.id)
                .first()
            )

            return sale

        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Database error: {str(e)}") from e
        except Exception:
            db.rollback()
            raise

    def get_with_details(self, db: Session, id: int) -> Optional[Sale]:
        """Get sale with all details."""
        return (
            db.query(Sale)
            .options(
                joinedload(Sale.customer),
                joinedload(Sale.user),
                selectinload(Sale.items).joinedload(SaleItem.product),
                selectinload(Sale.payments),
            )
            .filter(Sale.id == id)
            .first()
        )

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        payment_status: Optional[str] = None,
        payment_method: Optional[str] = None,
        is_voided: Optional[bool] = None,
    ) -> tuple[list[Sale], int]:
        """Get sales with filters and total count."""
        query = db.query(Sale).options(
            joinedload(Sale.customer),
            joinedload(Sale.user),
        )

        # Apply filters
        if customer_id:
            query = query.filter(Sale.customer_id == customer_id)
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
        if payment_status:
            query = query.filter(Sale.payment_status == payment_status)
        if payment_method:
            query = query.filter(Sale.payment_method == payment_method)
        if is_voided is not None:
            query = query.filter(Sale.is_voided == is_voided)

        # Get total count
        total = query.count()

        # Get paginated results
        sales = query.order_by(desc(Sale.sale_date)).offset(skip).limit(limit).all()

        return sales, total

    def search_products(
        self, db: Session, *, query: str, limit: int = 10
    ) -> list[Product]:
        """Search products for POS."""
        search_term = f"%{query}%"

        return (
            db.query(Product)
            .join(Product.category)
            .filter(
                and_(
                    Product.is_active.is_(True),
                    or_(
                        Product.name.ilike(search_term),
                        Product.sku.ilike(search_term),
                        Product.barcode.ilike(search_term),
                    ),
                )
            )
            .limit(limit)
            .all()
        )

    def void_sale(
        self, db: Session, *, sale_id: int, reason: str, user_id: int
    ) -> Sale:
        """Void a sale and restore inventory."""
        sale = self.get_with_details(db, sale_id)
        if not sale:
            raise ValueError("Sale not found")

        if sale.is_voided:
            raise ValueError("Sale is already voided")

        try:
            # Mark sale as voided
            sale.is_voided = True
            sale.void_reason = reason

            # Restore inventory
            for item in sale.items:
                product = item.product
                product.current_stock += item.quantity
                db.add(product)

            # If there were payments, void them
            for payment in sale.payments:
                payment.voided = True
                payment.void_reason = f"Sale {sale.invoice_number} voided"
                payment.voided_by_id = user_id
                payment.voided_at = get_utc_now()
                db.add(payment)

            # Reverse customer account balance if sale had a customer
            if sale.customer_id:
                from app.services.customer_account_service import (
                    customer_account_service,
                )

                # Create VOID_SALE transaction to reverse the debt
                customer_account_service.record_void_sale(
                    db=db, sale=sale, voided_by_id=user_id
                )

            # Update payment status
            sale.payment_status = "voided"

            db.add(sale)
            db.commit()
            db.refresh(sale)

            return sale

        except Exception:
            db.rollback()
            raise

    def get_sales_summary(
        self,
        db: Session,
        *,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Get sales summary statistics."""
        query = db.query(
            func.sum(Sale.total_amount).label("total_sales"),
            func.count(Sale.id).label("total_count"),
            func.sum(
                case(
                    (Sale.payment_method == "cash", Sale.total_amount),
                    else_=0,
                )
            ).label("cash_sales"),
            func.sum(
                case(
                    (Sale.payment_method == "credit", Sale.total_amount),
                    else_=0,
                )
            ).label("credit_sales"),
            func.sum(
                case(
                    (Sale.payment_method == "transfer", Sale.total_amount),
                    else_=0,
                )
            ).label("transfer_sales"),
            func.sum(
                case(
                    (Sale.payment_status == "pending", Sale.total_amount),
                    else_=0,
                )
            ).label("pending_amount"),
        ).filter(Sale.is_voided.is_(False))

        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)

        result = query.first()

        total_sales = result.total_sales or Decimal("0")
        total_count = result.total_count or 0

        return {
            "total_sales": total_sales,
            "total_count": total_count,
            "cash_sales": result.cash_sales or Decimal("0"),
            "credit_sales": result.credit_sales or Decimal("0"),
            "transfer_sales": result.transfer_sales or Decimal("0"),
            "pending_amount": result.pending_amount or Decimal("0"),
            "average_sale": total_sales / total_count
            if total_count > 0
            else Decimal("0"),
        }


sale_crud = SaleCRUD()
