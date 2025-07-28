# TechStore Architecture Guide

## Request Flow Pattern

### Unified Architecture
```
Browser → HTMX Endpoint → API Endpoint → Service Layer → Database
              ↓               ↓
         HTML Template    JSON Response
                         (reusable for any client)

Mobile App → API Endpoint → Service Layer → Database
                  ↓
             JSON Response
```

### Key Principle: API-First Design
- **ALL business logic goes through API endpoints**
- **HTMX endpoints are thin presentation layers**
- **API endpoints are the single source of truth**
- **Services contain reusable business logic**

### Benefits of This Architecture:
1. **Single Source of Truth**: Change business logic in one place (API)
2. **Future-Proof**: Mobile app can use same API endpoints
3. **Testable**: API endpoints can be tested independently
4. **Maintainable**: Clear separation of concerns
5. **Scalable**: API can be deployed separately if needed

## Authentication Pattern

TechStore follows an **API-First Authentication** approach (see ADR-004):

1. **All authentication logic flows through API endpoints**
   - `/api/v1/auth/login` returns JWT tokens as JSON
   - Web endpoints call API endpoints and handle web-specific concerns

2. **Token Storage by Client Type**:
   - **Web Browser**: Secure httpOnly cookies
   - **Mobile Apps**: Device secure storage (Keychain/Keystore)
   - **API Clients**: Client's choice (headers, etc.)

3. **Example Flow**:
   ```python
   # Web endpoint calls API
   api_response = await client.post("/api/v1/auth/login", json=credentials)
   tokens = api_response.json()
   
   # Web endpoint handles cookies
   response.set_cookie("access_token", tokens["access_token"], httponly=True)
   ```

This ensures consistency across all client types and maintains a single source of truth for authentication logic.

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
    current_user: User = Depends(get_current_user)
):
    """
    HTMX endpoint - thin presentation layer
    Calls API endpoint and returns HTML
    """
    # Prepare data for API
    customer_data = {
        "name": name,
        "phone": phone,
        "phone_secondary": phone_secondary,
        "email": email,
        "address": address,
        "notes": notes
    }
    
    # Call API endpoint via HTTP (API-First approach)
    # See ADR-004 for authentication pattern details
    async with httpx.AsyncClient(base_url=str(request.base_url)) as client:
        # Forward auth token from cookies
        headers = {"Authorization": f"Bearer {request.cookies.get('access_token')}"}
        
        response = await client.post(
            "/api/v1/customers",
            json=customer_data,
            headers=headers
        )
        
        if response.status_code == 201:
            customer = response.json()
            # Return HTML partial with data
            return templates.TemplateResponse(
                "customers/partials/customer_row.html",
                {"request": request, "customer": customer}
            )
        else:
            # Handle errors
            error = response.json().get("detail", "An error occurred")
            return templates.TemplateResponse(
                "partials/error.html",
                {"request": request, "error": error},
                status_code=response.status_code
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
    REST API endpoint - returns JSON
    Uses same service layer as web routes
    """
    return customer_service.create(
        db=db,
        **customer.dict(),
        created_by_id=current_user.id
    )
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