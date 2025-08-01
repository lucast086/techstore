"""Balance service for customer account calculations."""

from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.payment import payment_crud
from app.models.sale import Sale


class BalanceService:
    """Service for calculating customer balances from transactions."""

    def calculate_balance(self, db: Session, customer_id: int) -> Decimal:
        """Calculate current balance from all transactions.

        Balance = Payments - Credit Sales
        Positive balance = customer has credit
        Negative balance = customer owes money
        """
        # Get total credit sales (only unpaid or partially paid credit sales)
        credit_sales_total = db.query(func.sum(Sale.total_amount)).filter(
            Sale.customer_id == customer_id,
            Sale.payment_method == "credit",
            Sale.is_voided.is_(False),
        ).scalar() or Decimal("0")

        # Get total payments
        payments_total = payment_crud.get_customer_payment_total(db, customer_id)

        # Balance = Payments - Credit Sales
        # If customer bought $200 on credit and paid $50: 50 - 200 = -150 (owes $150)
        return Decimal(str(payments_total)) - Decimal(str(credit_sales_total))

    def get_balance_summary(self, db: Session, customer_id: int) -> dict:
        """Get balance with summary information."""
        balance = self.calculate_balance(db, customer_id)

        return {
            "current_balance": float(balance),
            "has_debt": balance < 0,
            "has_credit": balance > 0,
            "status": "debt" if balance < 0 else "credit" if balance > 0 else "clear",
            "formatted": self.format_balance(balance),
        }

    def format_balance(self, balance: Decimal) -> str:
        """Format balance for display."""
        if balance < 0:
            return f"Owes ${abs(balance):,.2f}"
        elif balance > 0:
            return f"Credit ${balance:,.2f}"
        else:
            return "$0.00"

    def get_transaction_history(
        self, db: Session, customer_id: int, limit: int | None = None
    ) -> list[dict]:
        """Get transaction history with running balance."""
        transactions = []

        # Get all payments
        payments = payment_crud.get_customer_payments(
            db, customer_id, include_voided=False
        )

        for payment in payments:
            transactions.append(
                {
                    "date": payment.created_at,
                    "type": "payment",
                    "description": f"Payment - {payment.receipt_number}",
                    "amount": float(payment.amount),  # Positive for credit
                    "reference": f"payment_{payment.id}",
                    "payment_method": payment.payment_method,
                    "reference_number": payment.reference_number,
                }
            )

        # Get all credit sales
        sales = (
            db.query(Sale)
            .filter(
                Sale.customer_id == customer_id,
                Sale.payment_method == "credit",
                Sale.is_voided.is_(False),
            )
            .all()
        )

        for sale in sales:
            transactions.append(
                {
                    "date": sale.sale_date,
                    "type": "sale",
                    "description": f"Credit Sale - {sale.invoice_number}",
                    "amount": -float(sale.total_amount),  # Negative for debt
                    "reference": f"sale_{sale.id}",
                    "payment_method": "credit",
                    "reference_number": sale.invoice_number,
                }
            )

        # Sort by date and calculate running balance
        transactions.sort(key=lambda x: x["date"], reverse=True)

        # Calculate running balance (newest to oldest)
        running_balance = self.calculate_balance(db, customer_id)
        for i, transaction in enumerate(transactions):
            transaction["running_balance"] = float(running_balance)
            if i < len(transactions) - 1:
                # Reverse the effect of this transaction for the next iteration
                running_balance -= Decimal(str(transaction["amount"]))

        if limit:
            transactions = transactions[:limit]

        return transactions

    def can_delete_customer(self, db: Session, customer_id: int) -> tuple[bool, str]:
        """Check if customer can be deleted based on balance."""
        balance = self.calculate_balance(db, customer_id)

        if balance != 0:
            return (
                False,
                f"Customer has non-zero balance: {self.format_balance(balance)}",
            )

        return True, "Customer can be deleted"

    def get_customers_with_debt(
        self, db: Session, limit: int | None = None
    ) -> list[dict]:
        """Get list of customers with outstanding debt."""
        from app.models.customer import Customer

        # Get all customers with credit sales
        customers_with_sales = (
            db.query(Customer)
            .join(Sale, Customer.id == Sale.customer_id)
            .filter(
                Sale.payment_method == "credit",
                Sale.is_voided.is_(False),
                Customer.is_active.is_(True),
            )
            .distinct()
            .all()
        )

        customers_with_debt = []

        for customer in customers_with_sales:
            balance = self.calculate_balance(db, customer.id)
            if balance < 0:  # Customer owes money
                customers_with_debt.append(
                    {
                        "customer": customer,
                        "balance": balance,
                        "formatted_balance": self.format_balance(balance),
                    }
                )

        # Sort by debt amount (most debt first)
        customers_with_debt.sort(key=lambda x: x["balance"])

        if limit:
            customers_with_debt = customers_with_debt[:limit]

        return customers_with_debt

    def calculate_balance_before_payment(
        self, db: Session, customer_id: int, payment_id: int
    ) -> Decimal:
        """Calculate balance before a specific payment was made."""
        # Get all payments except the specified one
        payments = payment_crud.get_customer_payments(
            db, customer_id, include_voided=False
        )

        payments_total = Decimal("0")
        for payment in payments:
            if payment.id != payment_id:
                payments_total += payment.amount

        # Get total credit sales
        credit_sales_total = db.query(func.sum(Sale.total_amount)).filter(
            Sale.customer_id == customer_id,
            Sale.payment_method == "credit",
            Sale.is_voided.is_(False),
        ).scalar() or Decimal("0")

        # Balance before payment = Other Payments - Credit Sales
        return payments_total - Decimal(str(credit_sales_total))


balance_service = BalanceService()
