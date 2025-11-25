"""CRUD operations for Customer model."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerCRUD:
    """CRUD operations for Customer model."""

    def create(
        self, db: Session, customer: CustomerCreate, created_by_id: int
    ) -> Customer:
        """Create new customer.

        Args:
            db: Database session.
            customer: Customer data to create.
            created_by_id: ID of user creating the customer.

        Returns:
            Created customer instance.

        Raises:
            ValueError: If customer with phone already exists.
        """
        # Check for duplicate phone
        existing = (
            db.query(Customer)
            .filter(Customer.phone == customer.phone, Customer.is_active.is_(True))
            .first()
        )

        if existing:
            raise ValueError(f"Customer with phone {customer.phone} already exists")

        db_customer = Customer(**customer.model_dump(), created_by_id=created_by_id)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer

    def get(self, db: Session, customer_id: int) -> Customer | None:
        """Get customer by ID.

        Args:
            db: Database session.
            customer_id: Customer ID to retrieve.

        Returns:
            Customer instance if found, None otherwise.
        """
        return (
            db.query(Customer)
            .filter(Customer.id == customer_id, Customer.is_active.is_(True))
            .first()
        )

    def get_by_phone(self, db: Session, phone: str) -> Customer | None:
        """Get customer by phone number.

        Args:
            db: Database session.
            phone: Phone number to search.

        Returns:
            Customer instance if found, None otherwise.
        """
        return (
            db.query(Customer)
            .filter(
                or_(Customer.phone == phone, Customer.phone_secondary == phone),
                Customer.is_active.is_(True),
            )
            .first()
        )

    def search(
        self,
        db: Session,
        query: str,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Customer]:
        """Search customers by name or phone.

        Args:
            db: Database session.
            query: Search query string.
            include_inactive: Whether to include inactive customers.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of matching customers.
        """
        search_query = f"%{query}%"

        q = db.query(Customer)

        if not include_inactive:
            q = q.filter(Customer.is_active.is_(True))

        q = q.filter(
            or_(
                Customer.name.ilike(search_query),
                Customer.phone.like(search_query),
                Customer.phone_secondary.like(search_query),
                Customer.email.ilike(search_query),
            )
        )

        return q.offset(skip).limit(limit).all()

    def update(
        self, db: Session, customer_id: int, customer_update: CustomerUpdate
    ) -> Customer | None:
        """Update customer.

        Args:
            db: Database session.
            customer_id: ID of customer to update.
            customer_update: Updated customer data.

        Returns:
            Updated customer instance if found, None otherwise.

        Raises:
            ValueError: If phone number is already in use by another customer.
        """
        customer = self.get(db, customer_id)
        if not customer:
            return None

        update_data = customer_update.model_dump(exclude_unset=True)

        # Check phone uniqueness if updating
        if "phone" in update_data and update_data["phone"] != customer.phone:
            existing = (
                db.query(Customer)
                .filter(
                    Customer.phone == update_data["phone"],
                    Customer.id != customer_id,
                    Customer.is_active.is_(True),
                )
                .first()
            )
            if existing:
                raise ValueError(f"Phone {update_data['phone']} already in use")

        for field, value in update_data.items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)
        return customer

    def soft_delete(self, db: Session, customer_id: int) -> bool:
        """Soft delete customer (set is_active=False).

        Args:
            db: Database session.
            customer_id: ID of customer to delete.

        Returns:
            True if customer was deleted, False if not found.

        Raises:
            ValueError: If customer has non-zero balance.
        """
        customer = self.get(db, customer_id)
        if not customer:
            return False

        # Check if customer can be deleted based on balance
        from app.crud.customer_account import customer_account_crud

        account = customer_account_crud.get_by_customer_id(db, customer_id)
        if account and account.account_balance != 0:
            if account.has_debt:
                raise ValueError(
                    f"Cannot delete customer with outstanding debt: ${abs(account.account_balance):.2f}"
                )
            elif account.has_credit:
                raise ValueError(
                    f"Cannot delete customer with credit balance: ${abs(account.account_balance):.2f}"
                )

        customer.is_active = False
        db.commit()
        return True

    def count_active(self, db: Session) -> int:
        """Count active customers.

        Args:
            db: Database session.

        Returns:
            Number of active customers.
        """
        return (
            db.query(func.count(Customer.id))
            .filter(Customer.is_active.is_(True))
            .scalar()
        )

    def get_with_balance(self, db: Session, customer_id: int) -> dict | None:
        """Get customer with calculated balance.

        Args:
            db: Database session.
            customer_id: Customer ID to retrieve.

        Returns:
            Customer dict with balance info if found, None otherwise.
        """
        customer = self.get(db, customer_id)
        if not customer:
            return None

        from app.crud.customer_account import customer_account_crud

        # Get or create account
        account = customer_account_crud.get_or_create(db, customer_id, 1)  # System user
        db.commit()

        # Format balance info
        balance_info = {
            "current_balance": float(account.account_balance),
            "has_debt": account.has_debt,
            "has_credit": account.has_credit,
            "status": "debt"
            if account.has_debt
            else "credit"
            if account.has_credit
            else "clear",
            "formatted": f"${abs(account.account_balance):,.2f}",
        }

        return {**customer.to_dict(), **balance_info}

    def list_with_balances(
        self, db: Session, skip: int = 0, limit: int = 20
    ) -> list[dict]:
        """Get customers with their balances.

        Args:
            db: Database session.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of customer dicts with balance information.
        """
        from app.crud.customer_account import customer_account_crud

        customers = (
            db.query(Customer)
            .filter(Customer.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .all()
        )

        result = []
        for customer in customers:
            # Get or create account
            account = customer_account_crud.get_or_create(db, customer.id, 1)
            db.commit()

            # Format balance info
            balance_info = {
                "current_balance": float(account.account_balance),
                "has_debt": account.has_debt,
                "has_credit": account.has_credit,
                "status": "debt"
                if account.has_debt
                else "credit"
                if account.has_credit
                else "clear",
                "formatted": f"${abs(account.account_balance):,.2f}",
            }

            result.append({**customer.to_dict(), **balance_info})

        return result

    def get_customers_with_balance(self, db: Session) -> list[dict]:
        """Get all customers with their balance information.

        Args:
            db: Database session.

        Returns:
            List of customer dicts with balance information.
        """
        from app.crud.customer_account import customer_account_crud

        customers = (
            db.query(Customer)
            .filter(Customer.is_active.is_(True))
            .order_by(Customer.name)
            .all()
        )

        result = []
        for customer in customers:
            # Get or create account
            account = customer_account_crud.get_or_create(db, customer.id, 1)
            db.commit()

            # Build customer dict with all required fields for template
            customer_dict = customer.to_dict()
            customer_dict.update(
                {
                    "balance": float(account.account_balance),  # Template expects 'balance'
                    "current_balance": float(account.account_balance),
                    "sales_total": float(account.total_sales),
                    "payments_total": float(account.total_payments),
                    "has_debt": account.has_debt,
                    "has_credit": account.has_credit,
                    "status": "debt"
                    if account.has_debt
                    else "credit"
                    if account.has_credit
                    else "clear",
                    "formatted": f"${abs(account.account_balance):,.2f}",
                }
            )

            result.append(customer_dict)

        return result

    def get_customers_with_positive_balance(self, db: Session) -> list[dict]:
        """Get customers with outstanding debt.

        Returns customers who OWE money (positive balance).

        Args:
            db: Database session.

        Returns:
            List of customer dicts with outstanding debt.
        """
        from app.crud.customer_account import customer_account_crud

        customers = (
            db.query(Customer)
            .filter(Customer.is_active.is_(True))
            .order_by(Customer.name)
            .all()
        )

        result = []
        for customer in customers:
            # Get or create account
            account = customer_account_crud.get_or_create(db, customer.id, 1)
            db.commit()

            # Positive balance means customer owes money
            if account.has_debt:
                balance_info = {
                    "current_balance": float(account.account_balance),
                    "has_debt": account.has_debt,
                    "has_credit": account.has_credit,
                    "status": "debt",
                    "formatted": f"${abs(account.account_balance):,.2f}",
                }
                result.append({**customer.to_dict(), **balance_info})

        return result


customer_crud = CustomerCRUD()
