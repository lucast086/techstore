# TechStore Architecture Guide

## Request Flow Pattern

### Unified Architecture
```
Browser → HTMX Endpoint ↘
                         Service Layer → Database
Mobile App → API Endpoint ↗
              ↓
         JSON Response

Browser receives: HTML Template
Mobile receives: JSON Response
```

### Key Principle: Service Layer as Single Source of Truth
- **ALL business logic lives in the Service Layer**
- **API endpoints are JSON adapters for the Service Layer**
- **HTMX endpoints are HTML adapters for the Service Layer**
- **Both endpoint types call the same services directly**

### Benefits of This Architecture:
1. **Single Source of Truth**: Business logic exists only in services
2. **No HTTP Overhead**: HTMX endpoints call services directly
3. **Simpler Testing**: Services can be tested in isolation
4. **Better Performance**: No internal HTTP calls
5. **Clearer Separation**: Each layer has a specific responsibility

## Authentication Pattern

TechStore follows a **Service-First Authentication** approach:

1. **All authentication logic lives in AuthService**
   - `AuthService.authenticate_user()` handles user verification
   - `AuthService.create_tokens()` generates JWT tokens
   - Both API and HTMX endpoints use the same service

2. **Token Storage by Client Type**:
   - **Web Browser**: Secure httpOnly cookies (set by HTMX endpoint)
   - **Mobile Apps**: Device secure storage (received from API endpoint)
   - **API Clients**: Client's choice (headers, etc.)

3. **Example Flows**:
   ```python
   # HTMX endpoint - Direct service call
   auth_service = AuthService(db)
   user = auth_service.authenticate_user(email, password)
   tokens = auth_service.create_tokens(user)
   response.set_cookie("access_token", tokens.access_token, httponly=True)

   # API endpoint - Same service, different response format
   auth_service = AuthService(db)
   user = auth_service.authenticate_user(email, password)
   tokens = auth_service.create_tokens(user)
   return tokens.model_dump()  # Returns JSON
   ```

This ensures consistency while avoiding unnecessary HTTP overhead.

## Implementation Standards

### Web Routes (HTMX) - Presentation Layer Only
Location: `app/web/`

```python
from fastapi import APIRouter, Depends, Request, Form
from app.dependencies import get_current_user
import httpx

router = APIRouter()

@router.post("/customers/new")
async def create_customer_htmx(
    request: Request,
    # Form data from HTMX
    name: str = Form(...),
    phone: str = Form(...),
    phone_secondary: str = Form(None),
    email: str = Form(None),
    address: str = Form(None),
    notes: str = Form(None),
    # Dependencies
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    HTMX endpoint - HTML adapter for CustomerService
    Calls service directly and returns HTML
    """
    # Log the operation
    logger.info(f"Creating customer via HTMX: {name}")

    # Prepare data for service
    customer_data = CustomerCreate(
        name=name,
        phone=phone,
        phone_secondary=phone_secondary,
        email=email,
        address=address,
        notes=notes
    )

    # Call service directly (Service-First approach)
    customer_service = CustomerService(db)
    try:
        customer = customer_service.create_customer(
            customer_data,
            created_by=current_user.id
        )
        logger.info(f"Customer created successfully: {customer.id}")

        # Return HTML partial with data
        return templates.TemplateResponse(
            "customers/partials/customer_row.html",
            {"request": request, "customer": customer}
        )
    except ValueError as e:
        logger.error(f"Error creating customer: {e}")
        # Handle validation errors
        return templates.TemplateResponse(
            "partials/error.html",
            {"request": request, "error": str(e)},
            status_code=400
        )
```

### API Routes (REST)
Location: `app/api/v1/`

```python
from fastapi import APIRouter, Depends
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/v1/customers")

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,  # Pydantic validation
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    API endpoint - JSON adapter for CustomerService
    Calls service directly and returns JSON
    """
    logger.info(f"Creating customer via API: {customer.name}")

    # Call service directly (same as HTMX endpoint)
    customer_service = CustomerService(db)
    try:
        new_customer = customer_service.create_customer(
            customer,
            created_by=current_user.id
        )
        logger.info(f"Customer created successfully: {new_customer.id}")
        return CustomerResponse.model_validate(new_customer)
    except ValueError as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=400, detail=str(e))
```

### Service Layer
Location: `app/services/`

```python
from sqlalchemy.orm import Session
from app.crud.customer import customer_crud
from app.models.customer import Customer

class CustomerService:
    """Business logic layer - used by both web and API routes"""

    def create(self, db: Session, name: str, phone: str,
               created_by_id: int, **kwargs) -> Customer:
        """
        Create customer with business rules
        Used by both HTMX and API endpoints
        """
        # Business logic here
        if self.is_duplicate_phone(db, phone):
            raise ValueError(f"Phone {phone} already registered")

        # Delegate to CRUD
        return customer_crud.create(
            db=db,
            name=name,
            phone=phone,
            created_by_id=created_by_id,
            **kwargs
        )

    def is_duplicate_phone(self, db: Session, phone: str) -> bool:
        """Check if phone already exists"""
        return customer_crud.get_by_phone(db, phone) is not None

customer_service = CustomerService()
```

### CRUD Layer
Location: `app/crud/`

```python
from sqlalchemy.orm import Session
from app.models.customer import Customer

class CustomerCRUD:
    """Database operations - no business logic"""

    def create(self, db: Session, **kwargs) -> Customer:
        """Simple database create"""
        customer = Customer(**kwargs)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    def get_by_phone(self, db: Session, phone: str) -> Optional[Customer]:
        """Simple database query"""
        return db.query(Customer).filter(
            Customer.phone == phone,
            Customer.is_active == True
        ).first()

customer_crud = CustomerCRUD()
```

## Dependency Injection Rules

### Always Use Dependencies For:
1. **Database Session**: `db: Session = Depends(get_db)`
2. **Current User**: `current_user: User = Depends(get_current_user)`
3. **Permissions**: `_: None = Depends(require_permission("customers.create"))`

### Why?
- **Testability**: Easy to mock in tests
- **Consistency**: Same pattern everywhere
- **Security**: Centralized auth checks
- **Flexibility**: Easy to swap implementations

## Testing Patterns

### Testing HTMX Endpoints
```python
def test_create_customer_htmx(client: TestClient, db: Session, mocker):
    """Test HTMX endpoint returns HTML"""
    # Mock the API call
    mock_customer = {
        "id": 1,
        "name": "Test Customer",
        "phone": "1234567890",
        "balance": 0.0
    }

    # Mock the API function call
    mocker.patch(
        "app.api.v1.customers.create_customer",
        return_value=mock_customer
    )

    response = client.post("/customers/new", data={
        "name": "Test Customer",
        "phone": "1234567890"
    })

    # Check HTML response
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Test Customer" in response.text
```

### Testing API Endpoints
```python
def test_create_customer_api(client: TestClient, db: Session):
    """Test API endpoint returns JSON"""
    response = client.post("/api/v1/customers/", json={
        "name": "Test Customer",
        "phone": "1234567890"
    })

    # Check JSON response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Customer"
    assert data["phone"] == "1234567890"
```

## File Organization

```
src/app/
├── api/v1/              # REST API endpoints (JSON)
│   ├── __init__.py
│   ├── auth.py
│   └── customers.py
├── web/                 # HTMX endpoints (HTML)
│   ├── __init__.py
│   ├── auth.py
│   └── customers.py
├── services/            # Business logic
│   ├── __init__.py
│   ├── auth_service.py
│   └── customer_service.py
├── crud/                # Database operations
│   ├── __init__.py
│   └── customer.py
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
└── dependencies.py      # Shared dependencies
```

## Key Principles

1. **API-First Design**:
   - ALL business logic in API endpoints
   - HTMX endpoints only transform JSON to HTML
   - API is the single source of truth
   - Mobile apps use same API

2. **Separation of Concerns**:
   - Web routes: Presentation only (Form → API → HTML)
   - API routes: Business logic (JSON in/out)
   - Services: Reusable business operations
   - CRUD: Pure database operations

3. **Dependency Injection Everywhere**:
   - All routes use DI for testability
   - Never hardcode dependencies
   - Use Depends() for all external resources

4. **Single Point of Change**:
   - Business logic changes → Update API only
   - All consumers (HTMX, mobile) get updates
   - No duplicate code between endpoints

5. **Error Handling**:
   - API returns structured JSON errors
   - HTMX converts to user-friendly HTML
   - Services raise domain exceptions

6. **Testing Strategy**:
   - Test API endpoints thoroughly
   - Mock API calls in HTMX tests
   - Services tested independently
