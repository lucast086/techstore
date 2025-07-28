# STORY-028: Customer Model & Migration

## 📋 Story Details
- **Epic**: EPIC-002 (Customer Management)
- **Priority**: CRITICAL
- **Estimate**: 0.5 days
- **Status**: TODO
- **Type**: Technical Task

## 🎯 User Story
**As a** developer,  
**I want** to create the customer data model and database migration,  
**So that** we can store customer information in the database with proper structure and relationships

## ✅ Acceptance Criteria
1. [ ] Customer model created with all required fields
2. [ ] Database migration generated and runs successfully
3. [ ] Indexes added for search performance (name, phones)
4. [ ] Model includes soft delete functionality (is_active)
5. [ ] Relationship with User model (created_by) established
6. [ ] Timestamps (created_at, updated_at) auto-managed
7. [ ] Phone fields allow NULL for secondary phone
8. [ ] Model methods for common operations implemented
9. [ ] Unit tests for model functionality
10. [ ] Migration is reversible (down migration works)

## 🔧 Technical Details

### New Files to Create:
```
src/app/
├── models/
│   └── customer.py          # Customer model
├── schemas/
│   └── customer.py          # Customer Pydantic schemas
└── crud/
    └── customer.py          # Customer CRUD operations

alembic/versions/
└── xxx_create_customer_table.py  # Migration file
```

### Implementation Requirements:

1. **Customer Model** (`app/models/customer.py`):
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models import BaseModel

class Customer(BaseModel):
    __tablename__ = "customers"
    
    # Basic Information
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    phone_secondary = Column(String(20), nullable=True, index=True)
    email = Column(String(100), nullable=True, index=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User", backref="created_customers")
    
    # Indexes for search performance
    __table_args__ = (
        Index('idx_customer_search', 'name', 'phone', 'phone_secondary'),
        Index('idx_customer_active_name', 'is_active', 'name'),
    )
    
    def __repr__(self):
        return f"<Customer {self.name} - {self.phone}>"
    
    @property
    def display_phones(self):
        """Return formatted phone display"""
        phones = [self.phone]
        if self.phone_secondary:
            phones.append(self.phone_secondary)
        return " / ".join(phones)
    
    @property
    def search_string(self):
        """Concatenated string for search optimization"""
        parts = [self.name, self.phone]
        if self.phone_secondary:
            parts.append(self.phone_secondary)
        if self.email:
            parts.append(self.email)
        return " ".join(parts).lower()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "phone_secondary": self.phone_secondary,
            "email": self.email,
            "address": self.address,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by.full_name if self.created_by else None
        }
```

2. **Customer Schemas** (`app/schemas/customer.py`):
```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('phone', 'phone_secondary')
    def phone_format(cls, v):
        if v:
            # Remove common formatting characters
            cleaned = ''.join(filter(lambda x: x.isdigit() or x == '+', v))
            if len(cleaned) < 7:  # Minimum reasonable phone length
                raise ValueError('Phone number too short')
            return v.strip()
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class CustomerInDB(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]
    
    class Config:
        orm_mode = True

class CustomerResponse(CustomerInDB):
    created_by_name: Optional[str] = None
    balance: float = 0.0  # Will be calculated
    transaction_count: int = 0  # Will be calculated
    
class CustomerList(BaseModel):
    customers: list[CustomerResponse]
    total: int
    page: int
    per_page: int
    
class CustomerSearch(BaseModel):
    query: str = Field(..., min_length=1)
    include_inactive: bool = False
    limit: int = Field(20, ge=1, le=100)
```

3. **Customer CRUD Operations** (`app/crud/customer.py`):
```python
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

class CustomerCRUD:
    def create(self, db: Session, customer: CustomerCreate, 
               created_by_id: int) -> Customer:
        """Create new customer"""
        # Check for duplicate phone
        existing = db.query(Customer).filter(
            Customer.phone == customer.phone,
            Customer.is_active == True
        ).first()
        
        if existing:
            raise ValueError(f"Customer with phone {customer.phone} already exists")
        
        db_customer = Customer(
            **customer.dict(),
            created_by_id=created_by_id
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    
    def get(self, db: Session, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        return db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.is_active == True
        ).first()
    
    def get_by_phone(self, db: Session, phone: str) -> Optional[Customer]:
        """Get customer by phone number"""
        return db.query(Customer).filter(
            or_(
                Customer.phone == phone,
                Customer.phone_secondary == phone
            ),
            Customer.is_active == True
        ).first()
    
    def search(self, db: Session, query: str, 
               include_inactive: bool = False,
               skip: int = 0, limit: int = 20) -> List[Customer]:
        """Search customers by name or phone"""
        search_query = f"%{query}%"
        
        q = db.query(Customer)
        
        if not include_inactive:
            q = q.filter(Customer.is_active == True)
        
        q = q.filter(
            or_(
                Customer.name.ilike(search_query),
                Customer.phone.like(search_query),
                Customer.phone_secondary.like(search_query),
                Customer.email.ilike(search_query)
            )
        )
        
        return q.offset(skip).limit(limit).all()
    
    def update(self, db: Session, customer_id: int, 
               customer_update: CustomerUpdate) -> Optional[Customer]:
        """Update customer"""
        customer = self.get(db, customer_id)
        if not customer:
            return None
        
        update_data = customer_update.dict(exclude_unset=True)
        
        # Check phone uniqueness if updating
        if 'phone' in update_data and update_data['phone'] != customer.phone:
            existing = db.query(Customer).filter(
                Customer.phone == update_data['phone'],
                Customer.id != customer_id,
                Customer.is_active == True
            ).first()
            if existing:
                raise ValueError(f"Phone {update_data['phone']} already in use")
        
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        return customer
    
    def soft_delete(self, db: Session, customer_id: int) -> bool:
        """Soft delete customer (set is_active=False)"""
        customer = self.get(db, customer_id)
        if not customer:
            return False
        
        # Check if customer has balance (will be implemented with transactions)
        # For now, just perform soft delete
        customer.is_active = False
        db.commit()
        return True
    
    def count_active(self, db: Session) -> int:
        """Count active customers"""
        return db.query(func.count(Customer.id)).filter(
            Customer.is_active == True
        ).scalar()

customer_crud = CustomerCRUD()
```

4. **Migration File** (generated by alembic):
```python
"""Create customer table

Revision ID: xxx
Revises: previous_migration
Create Date: 2024-01-27

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('phone_secondary', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_customers_phone', 'customers', ['phone'])
    op.create_index('idx_customers_phone_secondary', 'customers', ['phone_secondary'])
    op.create_index('idx_customers_email', 'customers', ['email'])
    op.create_index('idx_customers_active', 'customers', ['is_active'])
    op.create_index('idx_customer_search', 'customers', ['name', 'phone', 'phone_secondary'])
    op.create_index('idx_customer_active_name', 'customers', ['is_active', 'name'])

def downgrade():
    op.drop_index('idx_customer_active_name', table_name='customers')
    op.drop_index('idx_customer_search', table_name='customers')
    op.drop_index('idx_customers_active', table_name='customers')
    op.drop_index('idx_customers_email', table_name='customers')
    op.drop_index('idx_customers_phone_secondary', table_name='customers')
    op.drop_index('idx_customers_phone', table_name='customers')
    op.drop_table('customers')
```

## 📝 Definition of Done
- [ ] All acceptance criteria met
- [ ] Model can create, read, update, soft delete
- [ ] All indexes created and working
- [ ] Migration runs up and down successfully
- [ ] Unit tests pass with 100% coverage
- [ ] No duplicate phone numbers allowed
- [ ] Soft delete working correctly
- [ ] Model registered in `app/models/__init__.py`

## 🧪 Testing Approach

### Unit Tests (`tests/test_models/test_customer.py`):
```python
def test_create_customer():
    """Test customer creation"""
    
def test_duplicate_phone_prevented():
    """Test that duplicate phones are rejected"""
    
def test_soft_delete():
    """Test soft delete functionality"""
    
def test_search_by_phone():
    """Test searching by primary and secondary phone"""
    
def test_customer_relationships():
    """Test created_by relationship"""
```

### Migration Tests:
- Run migration up
- Verify table structure
- Run migration down
- Verify clean rollback

## 🔗 Dependencies
- **Depends on**: 
  - STORY-027 (Database Setup)
  - STORY-020 (Authentication System) - For User relationship
- **Blocks**: 
  - STORY-029 (Customer Registration)
  - STORY-030 (Customer Search)
  - STORY-031 (Customer Profile)
  - STORY-032 (Customer Account Balance)

## 📌 Notes
- No stored balance field - will be calculated from transactions
- Phone validation is minimal to allow flexibility
- Secondary phone is optional
- Search optimization via composite indexes
- Future: Add full-text search capabilities

## 📝 Dev Notes

### Migration Commands:
```bash
# Generate migration
poetry run alembic revision --autogenerate -m "Create customer table"

# Run migration
poetry run alembic upgrade head

# Rollback if needed
poetry run alembic downgrade -1
```

### Model Registration:
Add to `app/models/__init__.py`:
```python
from app.models.customer import Customer

__all__ = ["BaseModel", "Customer"]
```

### Testing the Model:
```python
# Quick test in Python shell
from app.database import SessionLocal
from app.models.customer import Customer
from app.crud.customer import customer_crud

db = SessionLocal()

# Create
customer_data = {
    "name": "Test Customer",
    "phone": "1234567890",
    "email": "test@example.com"
}
customer = customer_crud.create(db, customer_data, created_by_id=1)

# Search
results = customer_crud.search(db, "Test")

# Update
customer_crud.update(db, customer.id, {"notes": "VIP customer"})
```

### Performance Considerations:
- Composite index on name, phone, phone_secondary for search
- Separate index on is_active for filtering
- Consider partitioning if customer count > 1M

## 📊 Tasks / Subtasks

- [ ] **Create Customer Model** (AC: 1, 4, 5, 6)
  - [ ] Define SQLAlchemy model class
  - [ ] Add all required fields
  - [ ] Configure relationships
  - [ ] Add model methods

- [ ] **Create Pydantic Schemas** (AC: 1, 7)
  - [ ] Define base schema
  - [ ] Create CRUD schemas
  - [ ] Add validators
  - [ ] Define response schemas

- [ ] **Implement CRUD Operations** (AC: 8)
  - [ ] Create customer method
  - [ ] Search methods
  - [ ] Update method
  - [ ] Soft delete method

- [ ] **Generate Migration** (AC: 2, 3, 10)
  - [ ] Run alembic revision
  - [ ] Verify migration file
  - [ ] Add indexes
  - [ ] Test up/down migration

- [ ] **Write Unit Tests** (AC: 9)
  - [ ] Test model creation
  - [ ] Test validation
  - [ ] Test relationships
  - [ ] Test CRUD operations

- [ ] **Integration Tasks** (DoD)
  - [ ] Register model in __init__
  - [ ] Update database imports
  - [ ] Test with real database
  - [ ] Document model usage

## 🔄 Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2024-01-27 | 1.0 | Initial story creation | Tech Lead |

## 🤖 Dev Agent Record
*To be populated during implementation*

### Agent Model Used
*[Agent model and version]*

### Completion Notes
*[Implementation notes]*

### File List
*[List of created/modified files]*

## ✅ QA Results
*To be populated during QA review*