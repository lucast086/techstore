# TechStore Coding Standards

## Core Engineering Principles

### SOLID Principles
1. **Single Responsibility Principle (SRP)**
   - Each class/module should have one reason to change
   - Services handle business logic, repositories handle data access
   ```python
   # Good: Separated concerns
   class CustomerService:
       def create_customer(self, data: CustomerCreate) -> Customer:
           # Only business logic
           
   class CustomerRepository:
       def save(self, customer: Customer) -> Customer:
           # Only database operations
   ```

2. **Open/Closed Principle (OCP)**
   - Open for extension, closed for modification
   - Use abstract base classes and interfaces
   ```python
   from abc import ABC, abstractmethod
   
   class PaymentProcessor(ABC):
       @abstractmethod
       def process_payment(self, amount: Decimal) -> PaymentResult:
           pass
   ```

3. **Liskov Substitution Principle (LSP)**
   - Derived classes must be substitutable for base classes
   - Maintain consistent behavior in inheritance

4. **Interface Segregation Principle (ISP)**
   - Many specific interfaces better than one general interface
   - Don't force clients to depend on methods they don't use

5. **Dependency Inversion Principle (DIP)**
   - Depend on abstractions, not concretions
   - Use FastAPI's dependency injection system
   ```python
   def get_customer_service(
       repo: CustomerRepository = Depends(get_customer_repository)
   ) -> CustomerService:
       return CustomerService(repo)
   ```

### Design Patterns

#### Repository Pattern
```python
# Base repository interface
class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        pass
    
    @abstractmethod
    async def create(self, obj: T) -> T:
        pass
```

#### Service Layer Pattern
- All business logic in service classes
- Services orchestrate repositories and other services
- Keep controllers/routes thin

#### Factory Pattern
```python
class NotificationFactory:
    @staticmethod
    def create_notifier(type: str) -> Notifier:
        if type == "email":
            return EmailNotifier()
        elif type == "sms":
            return SMSNotifier()
```

## Python Code Style

### General Guidelines
- **Python Version**: 3.11+
- **Line Length**: 100 characters
- **Linting**: Ruff (replaces flake8, black, isort)
- **Type Hints**: Required throughout codebase
- **Pre-commit**: Configured for automatic checks
- **Docstrings**: Google style format required

### Google Docstring Format
```python
def calculate_customer_discount(customer: Customer, order_total: Decimal) -> Decimal:
    """Calculate discount for a customer based on their loyalty status.
    
    Args:
        customer: The customer object containing loyalty information.
        order_total: The total amount of the order before discount.
        
    Returns:
        The discount amount to be applied to the order.
        
    Raises:
        ValueError: If order_total is negative.
        CustomerNotFoundError: If customer doesn't exist.
        
    Example:
        >>> customer = Customer(loyalty_points=1000)
        >>> discount = calculate_customer_discount(customer, Decimal("100.00"))
        >>> print(discount)
        Decimal('10.00')
    """
    if order_total < 0:
        raise ValueError("Order total cannot be negative")
    
    # Business logic here
    return discount
```

### Class Docstrings
```python
class CustomerService:
    """Service for managing customer business logic.
    
    This service handles all customer-related operations including
    creation, updates, and business rule validation.
    
    Attributes:
        repository: The customer repository for data access.
        notification_service: Service for sending notifications.
        cache: Redis cache instance for performance optimization.
    """
    
    def __init__(self, repository: CustomerRepository):
        """Initialize the customer service.
        
        Args:
            repository: Repository instance for customer data access.
        """
        self.repository = repository
```

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --line-length=100]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, sqlalchemy]
        
  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        args: [--convention=google]
```

### Error Handling
```python
# Use custom exceptions with proper documentation
class CustomerNotFoundError(Exception):
    """Raised when a customer is not found in the database.
    
    Attributes:
        customer_id: The ID of the customer that was not found.
        message: Explanation of the error.
    """
    
    def __init__(self, customer_id: UUID, message: str = "Customer not found"):
        self.customer_id = customer_id
        self.message = message
        super().__init__(self.message)

# Handle errors at appropriate levels
try:
    customer = await customer_service.get(customer_id)
except CustomerNotFoundError:
    raise HTTPException(status_code=404, detail="Customer not found")
```

## Security Protocols

### Authentication & Authorization
1. **JWT Token Security**
   - Short-lived access tokens (15 minutes)
   - Refresh tokens with rotation
   - Secure storage (httpOnly cookies for web)
   ```python
   ACCESS_TOKEN_EXPIRE_MINUTES = 15
   REFRESH_TOKEN_EXPIRE_DAYS = 7
   ```

2. **Password Security**
   - Bcrypt with cost factor 12
   - Minimum requirements enforced
   - Password history to prevent reuse
   ```python
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
   ```

3. **Role-Based Access Control (RBAC)**
   ```python
   class RequireRole:
       """Dependency to require specific roles for endpoint access.
       
       Args:
           roles: List of roles that are allowed access.
       """
       
       def __init__(self, roles: List[str]):
           self.roles = roles
       
       def __call__(self, current_user: User = Depends(get_current_user)):
           if not any(role in current_user.roles for role in self.roles):
               raise HTTPException(status_code=403, detail="Insufficient permissions")
           return current_user
   ```

### API Security
1. **Input Validation**
   - Pydantic models for all inputs
   - SQL injection prevention via SQLAlchemy
   - XSS prevention in templates
   ```python
   class CustomerCreate(BaseModel):
       """Schema for creating a new customer.
       
       Attributes:
           name: Customer's full name.
           email: Valid email address.
           phone: Phone number with international format.
       """
       
       name: constr(min_length=1, max_length=100, strip_whitespace=True)
       email: EmailStr
       phone: constr(regex=r'^\+?1?\d{9,15}$')
   ```

2. **Rate Limiting**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   
   @limiter.limit("5/minute")
   async def create_customer(request: Request):
       """Create a new customer with rate limiting."""
       pass
   ```

3. **CORS Configuration**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.ALLOWED_ORIGINS,
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE"],
       allow_headers=["*"],
   )
   ```

### Data Security
1. **Encryption**
   - Sensitive data encrypted at rest
   - TLS 1.3 for data in transit
   - Use environment variables for secrets

2. **Audit Logging**
   ```python
   @dataclass
   class AuditLog:
       """Audit log entry for tracking user actions.
       
       Attributes:
           user_id: ID of the user performing the action.
           action: The action performed (e.g., 'CREATE', 'UPDATE').
           resource_type: Type of resource affected.
           resource_id: ID of the affected resource.
           timestamp: When the action occurred.
           ip_address: Client IP address.
           user_agent: Client user agent string.
       """
       
       user_id: UUID
       action: str
       resource_type: str
       resource_id: UUID
       timestamp: datetime
       ip_address: str
       user_agent: str
   ```

3. **Data Privacy**
   - PII masking in logs
   - Data retention policies
   - GDPR compliance helpers

## Testing Standards

### Test Structure
```
tests/
├── app/
│   ├── unit/           # Fast, isolated tests
│   ├── integration/    # Database/API tests
│   └── e2e/           # Full workflow tests
├── fixtures/          # Shared test data
└── conftest.py       # Pytest configuration
```

### Test Patterns
```python
async def test_create_customer():
    """Test customer creation endpoint.
    
    This test verifies that:
    - Valid customer data creates a new customer
    - Response contains correct customer information
    - Customer is persisted in database
    """
    # Arrange
    customer_data = CustomerCreateFactory.build()
    
    # Act
    response = await client.post("/api/v1/customers", json=customer_data.dict())
    
    # Assert
    assert response.status_code == 201
    assert response.json()["data"]["email"] == customer_data.email
```

### Test Coverage
- Minimum 80% overall coverage
- 100% coverage for critical paths:
  - Authentication/authorization
  - Payment processing
  - Data validation

## Database Standards

### Query Optimization
1. **Use indexes strategically**
   ```python
   class Customer(Base):
       """Customer database model.
       
       Attributes:
           id: Primary key UUID.
           email: Unique email address with index.
           phone: Phone number with index for search.
       """
       
       __tablename__ = "customers"
       
       email = Column(String, unique=True, index=True)
       phone = Column(String, index=True)
   ```

2. **Avoid N+1 queries**
   ```python
   # Use joinedload for eager loading
   customers = await db.query(Customer)\
       .options(joinedload(Customer.orders))\
       .all()
   ```

3. **Transaction Management**
   ```python
   async with db.begin():
       # All operations in transaction
       customer = await customer_repo.create(customer_data)
       await account_repo.create_for_customer(customer.id)
       # Auto-commit on success, rollback on exception
   ```

## Performance Standards

### Caching Strategy
```python
from functools import lru_cache
import redis

# In-memory caching for static data
@lru_cache(maxsize=128)
def get_product_categories():
    """Get all product categories with caching.
    
    Returns:
        List of category objects from cache or database.
    """
    return db.query(Category).all()

# Redis for distributed caching
async def get_customer_cached(customer_id: UUID) -> Optional[Customer]:
    """Get customer with Redis caching.
    
    Args:
        customer_id: The customer's unique identifier.
        
    Returns:
        Customer object if found, None otherwise.
    """
    cached = await redis.get(f"customer:{customer_id}")
    if cached:
        return Customer.parse_raw(cached)
    # Fetch from DB and cache
```

### Async Best Practices
```python
# Use asyncio.gather for parallel operations
customer, orders, payments = await asyncio.gather(
    customer_service.get(customer_id),
    order_service.list_by_customer(customer_id),
    payment_service.list_by_customer(customer_id)
)
```

## Monitoring & Observability

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "customer_created",
    customer_id=customer.id,
    email=customer.email,
    source="api"
)
```

### Metrics
```python
from prometheus_client import Counter, Histogram

request_count = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration')
```

### Health Checks
```python
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring.
    
    Returns:
        Dict containing service status and dependencies.
        
    Raises:
        HTTPException: 503 if service is unhealthy.
    """
    try:
        # Check database
        await db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")
```

## Additional Patterns to Consider

When implementing features, also consider these patterns where appropriate:
- **Strategy Pattern**: For interchangeable algorithms
- **Observer Pattern**: For event-driven architectures
- **Chain of Responsibility**: For request processing pipelines
- **Command Pattern**: For undo/redo functionality
- **Adapter Pattern**: For third-party integrations
- **Circuit Breaker**: For fault tolerance in external services
- **Event Sourcing**: For audit trails and complex state management
- **CQRS**: For separating read and write models in complex domains