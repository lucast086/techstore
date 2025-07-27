# TechStore SaaS - Project Architecture Documentation

## 📋 Overview

**TechStore SaaS** is a comprehensive business management system designed specifically for technology stores. It provides customer management, product inventory, sales processing, and repair order tracking through a modern web interface.

### Technology Stack

- **Backend Framework**: FastAPI + Python 3.11
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Frontend**: HTMX + Jinja2 Templates + Tailwind CSS
- **Development**: Poetry for dependency management, Ruff for linting
- **Testing**: Pytest with async support and coverage reporting
- **Deployment**: Docker containers on Railway platform
- **Development Environment**: Dev Containers with Docker Compose

### Development Tools

#### Poetry (Dependency Management)
- **Purpose**: Modern Python dependency management and packaging
- **Configuration**: `pyproject.toml` contains all project dependencies
- **Usage**: 
  - `poetry install` - Install dependencies
  - `poetry add <package>` - Add new dependency
  - `poetry run <command>` - Run commands in virtual environment

#### Alembic (Database Migrations)
- **Purpose**: Database schema version control and migrations
- **Configuration**: `alembic.ini` and `alembic/` directory
- **Usage**:
  - `poetry run alembic upgrade head` - Apply migrations
  - `poetry run alembic revision --autogenerate -m "description"` - Create new migration
  - `poetry run alembic history` - View migration history

#### Ruff (Code Quality)
- **Purpose**: Fast Python linter and formatter (replaces flake8, black, isort)
- **Configuration**: Settings in `pyproject.toml`
- **Features**:
  - Line length: 88 characters
  - Import sorting
  - Code style enforcement
  - Pre-commit hook integration
- **Usage**:
  - `poetry run ruff check .` - Check code quality
  - `poetry run ruff format .` - Format code

## 🏗️ Architecture Patterns

### 1. Layered Architecture

The application follows a 4-layer architecture pattern:

```
┌─────────────────────────────────────┐
│             Web Layer               │  ← HTMX templates & routes
│          (app/web/, templates/)     │
├─────────────────────────────────────┤
│             API Layer               │  ← REST endpoints  
│            (app/api/v1/)            │
├─────────────────────────────────────┤
│           Service Layer             │  ← Business logic
│          (app/services/)            │
├─────────────────────────────────────┤
│         Data Access Layer           │  ← Database operations
│      (app/crud/, app/models/)       │
└─────────────────────────────────────┘
```

### 2. Repository Pattern

Database operations are abstracted through CRUD classes that provide a consistent interface:

```python
class CRUDBase:
    def get(self, db: Session, id: int)
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100)
    def create(self, db: Session, obj_in: CreateSchemaType)
    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType)
    def remove(self, db: Session, id: int)
```

### 3. Schema-First Design

All data structures are defined using Pydantic schemas for automatic validation and serialization:

```python
class EntityBase(BaseModel):
    # Common fields
    
class EntityCreate(EntityBase):
    # Fields for creation
    
class EntityUpdate(EntityBase):
    # Fields for updates (optional)
    
class EntityResponse(EntityBase):
    # Fields for API responses
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## 📁 Project Structure

```
techstore/
├── src/app/                    # Application source code
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Settings and environment configuration
│   ├── database.py            # SQLAlchemy database connection
│   ├── dependencies.py        # FastAPI dependency injection
│   │
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   └── base.py           # Base model with common fields
│   │
│   ├── schemas/               # Pydantic validation schemas
│   │   ├── __init__.py
│   │   └── search.py         # Search functionality schemas
│   │
│   ├── crud/                  # Database operations (Repository pattern)
│   │   └── __init__.py
│   │
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   └── search_service.py # Search business logic
│   │
│   ├── api/v1/               # REST API endpoints
│   │   ├── __init__.py
│   │   └── search.py         # Search API endpoints
│   │
│   ├── web/                  # HTMX web interface
│   │   ├── __init__.py
│   │   ├── main.py          # Main web routes
│   │   └── search.py        # Search web routes
│   │
│   └── templates/            # Jinja2 HTML templates
│       ├── base.html        # Base template with HTMX setup
│       └── welcome.html     # Welcome page
│
├── src/static/               # Static assets
│   ├── css/style.css        # Custom styles
│   ├── js/                  # JavaScript files
│   └── images/              # Static images
│
├── tests/                    # Test suite
│   ├── conftest.py          # Test configuration and fixtures
│   ├── test_main.py         # Application entry point tests
│   ├── test_api/            # API endpoint tests
│   ├── test_crud/           # Database operation tests
│   ├── test_models/         # Model tests
│   ├── test_services/       # Service layer tests
│   └── test_web/            # Web interface tests
│
├── alembic/                  # Database migrations
│   ├── versions/            # Migration files
│   └── env.py              # Alembic configuration
│
├── docs/                     # Project documentation
├── scripts/                  # Utility scripts
│   └── version.sh           # Git flow management script
│
├── pyproject.toml           # Poetry dependencies and tool configuration
├── alembic.ini              # Database migration settings
├── Dockerfile               # Production container
└── CLAUDE.md               # Development guidelines
```

## 🔧 Core Components

### Database Configuration (`src/app/database.py`)

- SQLAlchemy engine with connection pooling
- Session management with dependency injection
- Declarative base for ORM models
- Debug mode SQL query logging

### Application Settings (`src/app/config.py`)

- Pydantic Settings for environment variable management
- Database URL configuration
- Security settings (secret keys, CORS)
- Pagination defaults
- Environment-specific configurations

### FastAPI Application (`src/app/main.py`)

- Application initialization with metadata
- CORS middleware configuration
- Static file serving
- Template engine setup
- Route registration (API + Web)
- Health check endpoint

### Dependency Injection (`src/app/dependencies.py`)

- Database session management
- Request-scoped dependencies
- Authentication dependencies (future)
- Common validation dependencies

## 🌐 API Design

### REST API Structure

- **Base URL**: `/api/v1/`
- **Content Type**: `application/json`
- **Response Format**: Consistent JSON with proper HTTP status codes
- **Error Handling**: Standardized error responses
- **Documentation**: Automatic OpenAPI/Swagger documentation

### Web Interface Structure

- **Base URL**: `/` for main pages, `/htmx/` for HTMX partials
- **Content Type**: `text/html`
- **Enhancement**: Progressive enhancement with HTMX
- **Accessibility**: Semantic HTML with proper ARIA attributes

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests**: Individual functions and classes
2. **Integration Tests**: Database operations and API endpoints
3. **Web Tests**: HTMX interface and user interactions
4. **End-to-End Tests**: Complete user workflows

### Test Configuration

- **Framework**: Pytest with async support
- **Database**: Separate test database with cleanup
- **Coverage**: HTML reports for coverage analysis
- **Fixtures**: Reusable test data factories
- **Mocking**: Dependency injection for service mocking

## 🚀 Deployment Architecture

### Development Environment

- **Container**: Dev Container with Docker Compose
- **Database**: PostgreSQL container
- **Hot Reload**: Uvicorn with auto-reload
- **Volume Mounting**: Live code editing

### Production Environment

- **Platform**: Railway cloud platform
- **Container**: Multi-stage Docker build
- **Database**: Managed PostgreSQL
- **Process Management**: Uvicorn with production settings
- **Security**: Non-root user, environment variables

## 🔒 Security Considerations

### Data Validation

- **Input Sanitization**: Pydantic automatic validation
- **SQL Injection**: SQLAlchemy ORM protection
- **XSS Protection**: Jinja2 template auto-escaping

### Authentication (Planned)

- **Session-based**: For web interface
- **JWT Tokens**: For API access
- **Role-based Access**: User permissions system

### Environment Security

- **Secret Management**: Environment variables
- **CORS Configuration**: Restricted origins
- **HTTPS Enforcement**: Production TLS termination

## 📊 Performance Considerations

### Database Optimization

- **Connection Pooling**: SQLAlchemy pool management
- **Query Optimization**: Lazy loading and eager loading strategies
- **Indexing**: Strategic database indexes
- **Migration Management**: Alembic for schema changes

### Application Performance

- **Async Support**: FastAPI async capabilities
- **Caching Strategy**: (Future) Redis for session storage
- **Static Assets**: Optimized CSS/JS serving
- **Compression**: (Future) Response compression

## 🔄 Development Workflow

### Git Flow

- **Main Branch**: `main` (production-ready)
- **Development Branch**: `development` (integration)
- **Feature Branches**: `feature/feature-name`
- **Release Management**: Automated with version scripts

### Code Quality

- **Linting**: Ruff for code style and errors
- **Formatting**: Ruff for consistent formatting
- **Type Checking**: Python type hints throughout
- **Pre-commit Hooks**: Automated quality checks

### Testing Workflow

- **Test-Driven Development**: Red-Green-Refactor cycle
- **Continuous Integration**: Automated test runs
- **Coverage Requirements**: Minimum coverage thresholds
- **Test Database**: Isolated test environment

## 🎯 Business Domain

### Core Entities

1. **Clientes (Customers)**
   - Customer information and contact details
   - Account balance and credit management
   - Purchase history and preferences

2. **Productos (Products)**
   - Product catalog with categories
   - Inventory management and stock levels
   - Pricing and supplier information

3. **Ventas (Sales)**
   - Sales transaction processing
   - Customer account integration
   - Payment method handling

4. **Reparaciones (Repairs)**
   - Repair order workflow
   - Status tracking and updates
   - Technician assignment and parts management

### MVP Feature Set

- Customer registration and search
- Product catalog management
- Sales processing with customer accounts
- Repair order creation and tracking
- Basic dashboard with business metrics
- Responsive web interface with HTMX

This architecture provides a solid foundation for rapid development while maintaining scalability and code quality standards.