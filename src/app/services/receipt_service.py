"""Receipt service for generating payment receipts."""

from app.utils.timezone import get_local_now


class ReceiptService:
    """Service for generating receipts."""

    def __init__(self):
        """Initialize receipt service with company information."""
        self.company_info = {
            "name": "TechStore",
            "address": "123 Main St, City",
            "phone": "(555) 123-4567",
            "email": "info@techstore.com",
        }

    def generate_payment_receipt_html(self, data: dict) -> str:
        """Generate payment receipt HTML.

        Args:
            data: Dictionary containing payment, balance, and company information.

        Returns:
            HTML string for the receipt.
        """
        # Add company info and timestamp
        data["company"] = self.company_info
        data["generated_at"] = get_local_now()

        # Format the receipt HTML
        payment = data["payment"]
        balance_before = data.get("balance_before", 0)
        balance_after = data.get("balance_after", 0)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Payment Receipt - {payment.receipt_number}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }}
                .receipt-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    border: 1px solid #ddd;
                    padding: 30px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .company-name {{
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .receipt-title {{
                    font-size: 20px;
                    margin: 20px 0;
                    text-transform: uppercase;
                }}
                .info-section {{
                    margin: 20px 0;
                }}
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    margin: 8px 0;
                }}
                .label {{
                    font-weight: bold;
                }}
                .amount-section {{
                    margin: 30px 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }}
                .amount-large {{
                    font-size: 24px;
                    font-weight: bold;
                    text-align: center;
                    color: #28a745;
                }}
                .balance-section {{
                    margin: 20px 0;
                    padding: 15px;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                }}
                .paid-in-full {{
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                    color: #28a745;
                    margin: 20px 0;
                    padding: 15px;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                }}
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
                @media print {{
                    body {{
                        margin: 0;
                        padding: 10px;
                    }}
                    .receipt-container {{
                        border: none;
                        padding: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="receipt-container">
                <div class="header">
                    <div class="company-name">{self.company_info['name']}</div>
                    <div>{self.company_info['address']}</div>
                    <div>{self.company_info['phone']} | {self.company_info['email']}</div>
                    <div class="receipt-title">Payment Receipt</div>
                </div>

                <div class="info-section">
                    <div class="info-row">
                        <span class="label">Receipt Number:</span>
                        <span>{payment.receipt_number}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Date:</span>
                        <span>{payment.created_at.strftime('%B %d, %Y %I:%M %p')}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Customer:</span>
                        <span>{payment.customer.name}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Phone:</span>
                        <span>{payment.customer.phone}</span>
                    </div>
                </div>

                <div class="amount-section">
                    <div class="amount-large">${payment.amount:.2f}</div>
                    <div style="text-align: center; margin-top: 10px;">
                        Payment Method: {payment.payment_method.upper()}
                    </div>
                    {f'<div style="text-align: center; margin-top: 5px;">Reference: {payment.reference_number}</div>' if payment.reference_number else ''}
                </div>

                <div class="balance-section">
                    <div class="info-row">
                        <span class="label">Balance Before Payment:</span>
                        <span>${abs(balance_before):.2f} {"(Owed)" if balance_before < 0 else "(Credit)"}</span>
                    </div>
                    <div class="info-row">
                        <span class="label">Payment Amount:</span>
                        <span>${payment.amount:.2f}</span>
                    </div>
                    <div class="info-row" style="border-top: 1px solid #dee2e6; padding-top: 8px; margin-top: 8px;">
                        <span class="label">Balance After Payment:</span>
                        <span>${abs(balance_after):.2f} {"(Owed)" if balance_after < 0 else "(Credit)" if balance_after > 0 else ""}</span>
                    </div>
                </div>

                {'<div class="paid-in-full">✓ ACCOUNT PAID IN FULL</div>' if balance_after == 0 else ''}

                {f'<div class="info-section"><strong>Notes:</strong><br>{payment.notes}</div>' if payment.notes else ''}

                <div class="info-section" style="margin-top: 30px;">
                    <div class="info-row">
                        <span class="label">Received By:</span>
                        <span>{payment.received_by.full_name if payment.received_by else 'System'}</span>
                    </div>
                </div>

                <div class="footer">
                    <p>Thank you for your payment!</p>
                    <p>This is a computer-generated receipt. No signature required.</p>
                    <p>Generated on {get_local_now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def generate_payment_receipt_pdf(self, data: dict) -> bytes:
        """Generate payment receipt PDF.

        Note: This is a simplified version. In production, you would use
        a proper PDF library like reportlab or weasyprint.

        Args:
            data: Dictionary containing payment and balance information.

        Returns:
            PDF bytes (placeholder for now).
        """
        # For MVP, we'll return the HTML and let the browser handle PDF generation
        # In production, use reportlab or weasyprint to generate actual PDF
        html = self.generate_payment_receipt_html(data)

        # TODO: Implement actual PDF generation
        # from weasyprint import HTML
        # pdf = HTML(string=html).write_pdf()
        # return pdf

        # For now, return HTML as bytes
        return html.encode("utf-8")


receipt_service = ReceiptService()
