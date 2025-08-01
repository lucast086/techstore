# STORY-043: Invoice Management

## 📋 Story Details
- **Epic**: EPIC-004 (Sales Management)
- **Priority**: MEDIUM
- **Estimate**: 1.5 days
- **Status**: IN_PROGRESS

## 🎯 User Story
**As** María or Carlos,
**I want** to generate and manage invoices,
**So that** customers have proper documentation for their purchases

## ✅ Acceptance Criteria
1. [ ] Auto-generate PDF invoice after sale completion
2. [ ] Sequential invoice numbering (INV-YYYY-NNNNN)
3. [ ] Include company logo and details
4. [ ] Show all products, quantities, prices, taxes
5. [ ] Customer information clearly displayed
6. [ ] Email invoice to customer (if email provided)
7. [ ] WhatsApp invoice delivery option
8. [ ] Reprint invoices from sales history
9. [ ] Void invoice with reason and authorization
10. [ ] Generate credit notes for voided invoices

## 🔧 Technical Details

### Files to Update/Create:
```
src/app/
├── services/
│   └── invoice_service.py    # Invoice generation
├── templates/
│   └── invoices/
│       ├── invoice_pdf.html  # PDF template
│       └── credit_note.html  # Credit note template
├── utils/
│   └── pdf_generator.py      # PDF creation utility
└── static/
    └── images/
        └── company_logo.png   # Company branding
```

### Implementation Requirements:

1. **Invoice Service** (`app/services/invoice_service.py`):
   - Generate invoice number sequentially
   - Create invoice data model
   - Handle void process
   - Track invoice status

2. **PDF Generation** (`app/utils/pdf_generator.py`):
   - HTML to PDF conversion
   - Include styling and branding
   - Optimize for printing
   - Support a4 sizes

3. **API Updates** (`app/api/v1/sales.py`):
   - GET /sales/{id}/invoice - Get invoice PDF
   - POST /sales/{id}/void - Void invoice
   - POST /sales/{id}/send - Send via email/WhatsApp

4. **Web Updates** (`app/web/sales.py`):
   - Invoice preview modal
   - Void invoice form
   - Send invoice interface

5. **Database Updates**:
   - Add invoice_number to sales table
   - Add invoice_status field
   - Credit notes table

## 🧪 Testing Approach

### Unit Tests:
- Invoice number generation
- PDF creation
- Void logic validation

### Integration Tests:
- Invoice generation flow
- Email/WhatsApp delivery
- Credit note creation

### UI Tests:
- Invoice preview
- Send functionality
- Void process

## 📦 Dependencies
- **Depends on**:
  - STORY-040 (Create Sale)
  - STORY-041 (Sales History)
- **Blocks**:
  - STORY-044 (Refunds and Returns)

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing
- [ ] PDF generation working
- [ ] Invoice numbering sequential
- [ ] Email/WhatsApp delivery tested
- [ ] Void process with audit trail
- [ ] Print layout optimized
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Consider digital signature integration
- Tax compliance requirements vary by region
- Template should be customizable
- Store PDF copies for archival

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
