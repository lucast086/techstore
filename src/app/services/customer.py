"""Customer service with business logic."""

from __future__ import annotations

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud.customer import customer_crud
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.schemas.customer import CustomerCreate, CustomerUpdate

logger = logging.getLogger(__name__)


class CustomerService:
    """Business logic layer for customer operations.

    This service handles all customer-related business logic
    and is used by both API and HTMX endpoints.
    """

    def create_customer(
        self, db: Session, customer_data: CustomerCreate, created_by_id: int
    ) -> Customer:
        """Create a new customer with business validation.

        Args:
            db: Database session.
            customer_data: Customer creation data.
            created_by_id: ID of user creating the customer.

        Returns:
            Created customer instance.

        Raises:
            ValueError: If phone number already exists.
        """
        logger.info(f"Creating customer: {customer_data.name}")

        # Business rule: Check for duplicate phone
        existing = customer_crud.get_by_phone(db, customer_data.phone)
        if existing:
            logger.warning(f"Duplicate phone number: {customer_data.phone}")
            raise ValueError(
                f"Phone {customer_data.phone} already registered to {existing.name}"
            )

        # Create customer
        customer = customer_crud.create(
            db=db, customer=customer_data, created_by_id=created_by_id
        )

        # Create CustomerAccount with zero balance
        account = CustomerAccount(
            customer_id=customer.id,
            credit_limit=Decimal("0.00"),
            account_balance=Decimal("0.00"),
            created_by_id=created_by_id,
        )
        db.add(account)
        db.commit()
        db.refresh(customer)

        logger.info(f"Customer created successfully with account: {customer.id}")
        return customer

    def get_customer(self, db: Session, customer_id: int) -> Customer | None:
        """Get customer by ID.

        Args:
            db: Database session.
            customer_id: Customer ID.

        Returns:
            Customer if found, None otherwise.
        """
        return customer_crud.get(db, customer_id)

    def get_customer_by_phone(self, db: Session, phone: str) -> Customer | None:
        """Get customer by phone number.

        Args:
            db: Database session.
            phone: Phone number to search.

        Returns:
            Customer if found, None otherwise.
        """
        return customer_crud.get_by_phone(db, phone)

    def search_customers(
        self, db: Session, query: str, include_inactive: bool = False, limit: int = 20
    ) -> list[Customer]:
        """Search customers by name or phone.

        Args:
            db: Database session.
            query: Search query.
            include_inactive: Whether to include inactive customers.
            limit: Maximum results to return.

        Returns:
            List of matching customers.
        """
        logger.info(f"Searching customers: {query}")
        return customer_crud.search(
            db, query=query, include_inactive=include_inactive, limit=limit
        )

    def update_customer(
        self, db: Session, customer_id: int, customer_update: CustomerUpdate
    ) -> Customer | None:
        """Update customer information.

        Args:
            db: Database session.
            customer_id: Customer ID to update.
            customer_update: Update data.

        Returns:
            Updated customer if successful, None if not found.

        Raises:
            ValueError: If new phone number already exists.
        """
        logger.info(f"Updating customer: {customer_id}")

        # Get existing customer
        customer = customer_crud.get(db, customer_id)
        if not customer:
            logger.warning(f"Customer not found: {customer_id}")
            return None

        # Check if phone is being changed
        if customer_update.phone and customer_update.phone != customer.phone:
            existing = customer_crud.get_by_phone(db, customer_update.phone)
            if existing and existing.id != customer_id:
                raise ValueError(f"Phone {customer_update.phone} already in use")

        # Update customer
        updated = customer_crud.update(db, customer_id, customer_update)
        logger.info(f"Customer updated successfully: {customer_id}")
        return updated

    def delete_customer(self, db: Session, customer_id: int) -> bool:
        """Soft delete a customer.

        Args:
            db: Database session.
            customer_id: Customer ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        logger.info(f"Deleting customer: {customer_id}")

        # TODO: Check if customer has balance when transaction system is implemented
        # For now, just perform soft delete
        success = customer_crud.soft_delete(db, customer_id)

        if success:
            logger.info(f"Customer deleted successfully: {customer_id}")
        else:
            logger.warning(f"Customer not found for deletion: {customer_id}")

        return success

    def check_phone_availability(
        self, db: Session, phone: str, exclude_id: int | None = None
    ) -> dict:
        """Check if a phone number is available.

        Args:
            db: Database session.
            phone: Phone number to check.
            exclude_id: Customer ID to exclude from check.

        Returns:
            Dict with availability status and details.
        """
        existing = customer_crud.get_by_phone(db, phone)

        if existing and (not exclude_id or existing.id != exclude_id):
            return {
                "available": False,
                "message": f"Número de teléfono ya registrado a {existing.name}",
                "customer": {"id": existing.id, "name": existing.name},
            }

        return {"available": True}

    def get_customer_count(self, db: Session) -> int:
        """Get count of active customers.

        Args:
            db: Database session.

        Returns:
            Number of active customers.
        """
        return customer_crud.count_active(db)

    def get_customer_balance(self, db: Session, customer_id: int) -> float:
        """Calculate customer balance from transactions.

        Args:
            db: Database session.
            customer_id: Customer ID.

        Returns:
            Customer balance (positive = credit, negative = debt).
        """
        # TODO: Implement when transaction system is ready
        # For now, return 0
        return 0.0

    def get_customer_transaction_count(self, db: Session, customer_id: int) -> int:
        """Get count of customer transactions.

        Args:
            db: Database session.
            customer_id: Customer ID.

        Returns:
            Number of transactions.
        """
        # TODO: Implement when transaction system is ready
        # For now, return 0
        return 0


# Singleton instance
customer_service = CustomerService()
