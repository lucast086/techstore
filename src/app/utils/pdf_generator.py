"""PDF generator utility for statements and receipts."""

from datetime import datetime


def generate_statement_pdf(
    customer: dict, balance_info: dict, transactions: list[dict]
) -> bytes:
    """Generate a simple PDF statement.

    Note: This is a simplified HTML-based approach for MVP.
    In production, use reportlab or weasyprint for better PDF generation.

    Args:
        customer: Customer dictionary with details.
        balance_info: Balance summary information.
        transactions: List of transaction dictionaries.

    Returns:
        PDF bytes (currently returns HTML as bytes for MVP).
    """
    # Generate HTML content for the statement
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Account Statement - {customer['name']}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #333;
                padding-bottom: 20px;
            }}
            .company-name {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .statement-title {{
                font-size: 20px;
                margin-top: 10px;
            }}
            .section {{
                margin: 20px 0;
            }}
            .section-title {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #555;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .info-item {{
                margin: 5px 0;
            }}
            .label {{
                font-weight: bold;
                display: inline-block;
                width: 120px;
            }}
            .balance-box {{
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 5px;
                text-align: center;
                margin: 20px 0;
            }}
            .balance-amount {{
                font-size: 24px;
                font-weight: bold;
                color: {'#dc3545' if balance_info['has_debt'] else '#28a745' if balance_info['has_credit'] else '#333'};
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f5f5f5;
                font-weight: bold;
            }}
            .text-right {{
                text-align: right;
            }}
            .debit {{
                color: #dc3545;
            }}
            .credit {{
                color: #28a745;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            @media print {{
                body {{
                    margin: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="company-name">TechStore</div>
            <div>123 Main St, City | (555) 123-4567 | info@techstore.com</div>
            <div class="statement-title">ACCOUNT STATEMENT</div>
        </div>

        <div class="info-grid">
            <div class="section">
                <div class="section-title">Customer Information</div>
                <div class="info-item"><span class="label">Name:</span> {customer['name']}</div>
                <div class="info-item"><span class="label">Phone:</span> {customer['phone']}</div>
                {'<div class="info-item"><span class="label">Alt Phone:</span> ' + customer['phone_secondary'] + '</div>' if customer.get('phone_secondary') else ''}
                {'<div class="info-item"><span class="label">Email:</span> ' + customer['email'] + '</div>' if customer.get('email') else ''}
                {'<div class="info-item"><span class="label">Address:</span> ' + customer['address'] + '</div>' if customer.get('address') else ''}
            </div>

            <div class="section">
                <div class="section-title">Statement Details</div>
                <div class="info-item"><span class="label">Statement Date:</span> {datetime.now().strftime('%B %d, %Y')}</div>
                <div class="info-item"><span class="label">Customer Since:</span> {customer.get('created_at', 'N/A')}</div>
            </div>
        </div>

        <div class="balance-box">
            <div class="section-title">Current Balance</div>
            <div class="balance-amount">{balance_info['formatted']}</div>
        </div>

        <div class="section">
            <div class="section-title">Transaction History</div>
            """

    if transactions:
        html += """
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th class="text-right">Debit</th>
                        <th class="text-right">Credit</th>
                        <th class="text-right">Balance</th>
                    </tr>
                </thead>
                <tbody>
        """

        for trans in transactions:
            date_str = (
                trans["date"].strftime("%m/%d/%Y")
                if hasattr(trans["date"], "strftime")
                else trans["date"]
            )
            debit = (
                f'<span class="debit">${abs(trans["amount"]):,.2f}</span>'
                if trans["amount"] < 0
                else ""
            )
            credit = (
                f'<span class="credit">${trans["amount"]:,.2f}</span>'
                if trans["amount"] > 0
                else ""
            )
            balance = f'${abs(trans["running_balance"]):,.2f}'

            html += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td>{trans['description']}</td>
                        <td class="text-right">{debit}</td>
                        <td class="text-right">{credit}</td>
                        <td class="text-right">{balance}</td>
                    </tr>
            """

        html += f"""
                </tbody>
                <tfoot>
                    <tr style="border-top: 2px solid #333;">
                        <td colspan="4"><strong>Current Balance</strong></td>
                        <td class="text-right"><strong>${abs(balance_info['current_balance']):,.2f}</strong></td>
                    </tr>
                </tfoot>
            </table>
        """
    else:
        html += (
            '<p style="text-align: center; color: #666;">No transactions recorded.</p>'
        )

    html += (
        """
        </div>

        <div class="footer">
            <p>This statement is generated automatically and reflects all transactions up to the statement date.</p>
            <p>For questions about your account, please contact us.</p>
            <p>Generated on """
        + datetime.now().strftime("%B %d, %Y at %I:%M %p")
        + """</p>
        </div>
    </body>
    </html>
    """
    )

    # TODO: In production, use a proper PDF library
    # from weasyprint import HTML
    # pdf = HTML(string=html).write_pdf()
    # return pdf

    # For MVP, return HTML as bytes
    return html.encode("utf-8")
