# STORY-057: Repair Cost Management

## 📋 Story Details
- **Epic**: EPIC-005 (Repair Management)
- **Priority**: MEDIUM
- **Estimate**: 1.5 days
- **Status**: TODO

## 🎯 User Story
**As** María,
**I want** to manage repair pricing and costs,
**So that** repairs are profitable and consistently priced

## ✅ Acceptance Criteria
1. [ ] Parts cost catalog with suppliers
2. [ ] Labor rate configuration by repair type
3. [ ] Standard repair templates with pricing
4. [ ] Cost markup percentage settings
5. [ ] Margin calculation and reporting
6. [ ] Discount authorization levels
7. [ ] Price history tracking
8. [ ] Bulk price updates
9. [ ] Competitor price tracking
10. [ ] Profitability dashboard

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── models/
│   └── repair_pricing.py     # Pricing models
├── schemas/
│   └── pricing.py            # Pricing schemas
├── crud/
│   └── pricing.py            # Pricing operations
├── api/v1/
│   └── pricing.py            # Pricing endpoints
├── web/
│   └── pricing.py            # Pricing routes
├── templates/
│   └── pricing/
│       ├── catalog.html      # Parts catalog
│       ├── templates.html    # Repair templates
│       ├── settings.html     # Pricing settings
│       └── partials/
│           ├── part_form.html
│           └── margin_calculator.html
└── services/
    └── pricing_service.py    # Pricing logic
```

### Implementation Requirements:

1. **Pricing Models** (`app/models/repair_pricing.py`):
   - PartsCatalog with suppliers
   - RepairTemplate with standard costs
   - LaborRates by category
   - PriceHistory tracking

2. **Pricing Service** (`app/services/pricing_service.py`):
   - Calculate repair cost
   - Apply markup rules
   - Check discount authorization
   - Track margins
   - Suggest pricing

3. **API Endpoints** (`app/api/v1/pricing.py`):
   - GET /pricing/parts - Parts catalog
   - POST /pricing/parts - Add/update part
   - GET /pricing/templates - Repair templates
   - PUT /pricing/settings - Update settings
   - GET /pricing/margins - Margin report

4. **Web Routes** (`app/web/pricing.py`):
   - GET /pricing - Pricing dashboard
   - GET /pricing/catalog - Parts catalog
   - GET /pricing/templates - Templates
   - POST /pricing/calculate - Price calc

5. **Features**:
   - Import parts from CSV
   - Template categories
   - Seasonal pricing
   - Bundle discounts
   - Cost alerts

## 🧪 Testing Approach

### Unit Tests:
- Pricing calculations
- Markup application
- Discount validation
- Margin calculations

### Integration Tests:
- Template application
- Bulk updates
- History tracking

### UI Tests:
- Catalog management
- Calculator accuracy
- Settings updates

## 📦 Dependencies
- **Depends on**:
  - STORY-052 (Diagnose Repair)
- **Blocks**:
  - None

## 🎯 Definition of Done
- [ ] All acceptance criteria met
- [ ] Unit tests passing
- [ ] Pricing calculations accurate
- [ ] Templates working
- [ ] Margin tracking functional
- [ ] Import/export working
- [ ] Reports generating
- [ ] Code reviewed and approved
- [ ] Deployed to development environment

## 📝 Notes
- Consider supplier API integration
- Dynamic pricing based on demand
- Customer type pricing tiers
- Warranty cost inclusion

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-27 | 1.0 | Initial story creation | Sarah (PO) |
