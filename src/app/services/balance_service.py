"""Balance service for customer account calculations."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud.payment import payment_crud


class BalanceService:
    """Service for calculating customer balances from transactions."""

    def calculate_balance(self, db: Session, customer_id: int) -> Decimal:
        """Calculate current balance from all transactions.

        MVP: Simple calculation from sales (debt) and payments (credit).
        Positive balance = customer has credit
        Negative balance = customer owes money
        """
        # TODO: When Sale model exists
        # sales_total = db.query(func.sum(Sale.total)).filter(
        #     Sale.customer_id == customer_id,
        #     Sale.payment_method == "credit"
        # ).scalar() or Decimal("0")

        # Get total payments
        payments_total = payment_crud.get_customer_payment_total(db, customer_id)

        # MVP: Since we don't have sales yet, we'll simulate with a negative balance
        # In production, this would be: payments_total - sales_total
        sales_total = Decimal("0")

        return Decimal(str(payments_total)) - sales_total

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
        """Get transaction history with running balance.

        MVP: Return payments only until transaction models exist.
        """
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

        # TODO: When Sale model exists, add sales to transactions
        # sales = db.query(Sale).filter(
        #     Sale.customer_id == customer_id
        # ).all()
        #
        # for sale in sales:
        #     transactions.append({
        #         "date": sale.created_at,
        #         "type": "sale",
        #         "description": f"Sale #{sale.id}",
        #         "amount": -float(sale.total),  # Negative for debt
        #         "reference": f"sale_{sale.id}"
        #     })

        # Sort by date and calculate running balance
        transactions.sort(key=lambda x: x["date"], reverse=True)

        # Calculate running balance (newest to oldest)
        running_balance = Decimal("0")
        for transaction in transactions:
            running_balance += Decimal(str(transaction["amount"]))
            transaction["running_balance"] = float(running_balance)

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
        """Get list of customers with outstanding debt.

        MVP: Return empty list for now until sales exist.
        """
        # TODO: Implement when we can calculate balances with sales
        # This would query all customers and calculate their balances
        # filtering only those with negative balances
        return []

    def calculate_balance_before_payment(
        self, db: Session, customer_id: int, payment_id: int
    ) -> Decimal:
        """Calculate balance before a specific payment was made."""
        # Get all payments except the specified one
        payments = payment_crud.get_customer_payments(
            db, customer_id, include_voided=False
        )

        total = Decimal("0")
        for payment in payments:
            if payment.id != payment_id:
                total += payment.amount

        # TODO: When Sale model exists, subtract sales total
        # sales_total = db.query(func.sum(Sale.total)).filter(
        #     Sale.customer_id == customer_id,
        #     Sale.payment_method == "credit"
        # ).scalar() or Decimal("0")
        # return total - sales_total

        # MVP: Return negative to simulate debt
        return total - Decimal("1000")  # Simulated debt


balance_service = BalanceService()
