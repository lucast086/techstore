# Test Structure Analysis

## Expected Structure (from docs)
```
tests/
├── __init__.py
├── conftest.py      # Pytest configuration
├── fixtures/        # Test data factories
├── unit/           # Unit tests
│   ├── models/     # Model tests
│   ├── schemas/    # Schema tests
│   └── services/   # Service tests
├── integration/    # Integration tests
│   ├── api/       # API endpoint tests
│   ├── crud/      # Database tests
│   └── web/       # Web route tests
└── e2e/           # End-to-end tests
```

## Current Structure Issues

### 1. **Misplaced Tests in Root `tests/` Directory**
These should be moved to appropriate subdirectories:
- `tests/test_alembic_setup.py` → `tests/integration/` (database integration)
- `tests/test_api_sales.py` → `tests/integration/api/`
- `tests/test_database_setup.py` → `tests/integration/`
- `tests/test_health_endpoints.py` → `tests/integration/api/`
- `tests/test_main.py` → `tests/integration/`
- `tests/test_sales.py` → `tests/integration/api/` or `tests/unit/services/`

### 2. **Wrong Directory Names**
- `tests/test_api/` → should be `tests/integration/api/`
- `tests/test_core/` → should be `tests/unit/core/`
- `tests/test_crud/` → should be `tests/integration/crud/`
- `tests/test_models/` → should be `tests/unit/models/`
- `tests/test_services/` → should be `tests/unit/services/`
- `tests/test_web/` → should be `tests/integration/web/`

### 3. **Missing Directories**
- `tests/fixtures/` - for test data factories
- `tests/unit/schemas/` - for schema validation tests
- `tests/e2e/` - for end-to-end tests

### 4. **Correctly Placed Tests**
✅ Already in the right place:
- `tests/integration/api/test_api_customers.py`
- `tests/integration/web/test_products.py`
- `tests/integration/web/test_products_simple.py`
- `tests/integration/web/test_web_customers.py`
- `tests/unit/models/test_customer.py`
- `tests/unit/models/test_product.py`
- `tests/unit/services/test_invoice_service.py`

## Required Moves

### Integration Tests (with DB/external dependencies)
1. `tests/test_alembic_setup.py` → `tests/integration/test_alembic_setup.py`
2. `tests/test_database_setup.py` → `tests/integration/test_database_setup.py`
3. `tests/test_main.py` → `tests/integration/test_main.py`
4. `tests/test_api/` → `tests/integration/api/`
5. `tests/test_crud/` → `tests/integration/crud/`
6. `tests/test_web/` → `tests/integration/web/`
7. `tests/test_api_sales.py` → `tests/integration/api/test_api_sales.py`
8. `tests/test_health_endpoints.py` → `tests/integration/api/test_health_endpoints.py`
9. `tests/test_sales.py` → `tests/integration/api/test_sales.py`

### Unit Tests (no external dependencies)
1. `tests/test_core/` → `tests/unit/core/`
2. `tests/test_models/` → `tests/unit/models/`
3. `tests/test_services/` → `tests/unit/services/`

## Summary
The test structure needs significant reorganization to match the documented architecture. Most tests are in the wrong directories, with many in the root `tests/` folder that should be in subdirectories based on their type (unit vs integration).
