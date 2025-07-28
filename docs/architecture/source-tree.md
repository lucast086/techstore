# TechStore Source Tree

## Project Structure Overview

The TechStore project follows a clean architecture pattern with clear separation of concerns. The structure is designed for maintainability, testability, and scalability.

```
techstore/
├── .devcontainer/          # VS Code devcontainer configuration
│   ├── devcontainer.json   # Container settings and extensions
│   └── Dockerfile          # Development container image
│
├── .github/                # GitHub specific configurations
│   └── workflows/          # CI/CD pipelines
│
├── alembic/                # Database migrations
│   ├── versions/           # Migration files
│   ├── alembic.ini        # Alembic configuration
│   ├── env.py             # Migration environment setup
│   └── script.py.mako     # Migration template
│
├── docs/                   # Documentation
│   ├── architecture/       # Architecture documentation
│   │   ├── coding-standards.md
│   │   ├── tech-stack.md
│   │   └── source-tree.md
│   ├── design/            # Design documents
│   ├── stories/           # User stories and epics
│   │   ├── epic-001-authentication/
│   │   └── epic-002-customer-management/
│   └── technical/         # Technical guides
│       ├── architecture-guide.md
│       ├── implementation-guide.md
│       └── server-launch-guide.md
│
├── scripts/               # Utility scripts
│   ├── init_db.sh        # Database initialization
│   └── version.sh        # Git flow version management
│
├── src/                   # Source code
│   └── app/              # Main application package
│       ├── __init__.py
│       ├── main.py       # FastAPI app instance
│       ├── config.py     # Configuration management
│       ├── database.py   # Database connection
│       ├── dependencies.py # Dependency injection
│       │
│       ├── api/          # REST API endpoints
│       │   ├── __init__.py
│       │   └── v1/       # API version 1
│       │       ├── __init__.py
│       │       ├── health.py    # Health check endpoints
│       │       ├── auth.py      # Authentication endpoints
│       │       ├── customers.py # Customer CRUD
│       │       ├── products.py  # Product CRUD
│       │       ├── sales.py     # Sales endpoints
│       │       └── repairs.py   # Repair orders
│       │
│       ├── web/          # HTMX web routes
│       │   ├── __init__.py
│       │   ├── main.py   # Web router setup
│       │   ├── auth.py   # Authentication pages
│       │   ├── customers.py # Customer UI
│       │   ├── products.py  # Product UI
│       │   ├── sales.py     # Sales UI
│       │   └── repairs.py   # Repairs UI
│       │
│       ├── models/       # SQLAlchemy models
│       │   ├── __init__.py
│       │   ├── base.py   # Base model class
│       │   ├── user.py   # User/auth models
│       │   ├── customer.py # Customer model
│       │   ├── product.py  # Product model
│       │   ├── sale.py     # Sales model
│       │   └── repair.py   # Repair order model
│       │
│       ├── schemas/      # Pydantic schemas
│       │   ├── __init__.py
│       │   ├── auth.py   # Auth schemas
│       │   ├── customer.py # Customer DTOs
│       │   ├── product.py  # Product DTOs
│       │   ├── sale.py     # Sales DTOs
│       │   └── repair.py   # Repair DTOs
│       │
│       ├── crud/         # Database operations
│       │   ├── __init__.py
│       │   ├── base.py   # Base CRUD class
│       │   ├── user.py   # User operations
│       │   ├── customer.py # Customer operations
│       │   ├── product.py  # Product operations
│       │   ├── sale.py     # Sales operations
│       │   └── repair.py   # Repair operations
│       │
│       ├── services/     # Business logic
│       │   ├── __init__.py
│       │   ├── auth.py   # Authentication service
│       │   ├── customer.py # Customer service
│       │   ├── product.py  # Product service
│       │   ├── sale.py     # Sales service
│       │   └── repair.py   # Repair service
│       │
│       ├── static/       # Static assets
│       │   ├── css/      # Stylesheets
│       │   │   └── design-tokens.css
│       │   └── js/       # JavaScript
│       │       └── design-tokens.js
│       │
│       └── templates/    # Jinja2 templates
│           ├── base.html # Base layout
│           ├── auth/     # Auth templates
│           │   └── login.html
│           ├── components/ # Reusable components
│           ├── pages/    # Full page templates
│           └── partials/ # HTMX fragments
│
├── tests/                # Test suite
│   ├── __init__.py
│   ├── conftest.py      # Pytest configuration
│   ├── fixtures/        # Test data factories
│   ├── unit/           # Unit tests
│   │   ├── models/     # Model tests
│   │   ├── schemas/    # Schema tests
│   │   └── services/   # Service tests
│   ├── integration/    # Integration tests
│   │   ├── api/       # API endpoint tests
│   │   ├── crud/      # Database tests
│   │   └── web/       # Web route tests
│   └── e2e/           # End-to-end tests
│
├── .bmad-core/         # BMad agent configuration
│   └── core-config.yaml
│
├── .env.example        # Environment variables template
├── .gitignore         # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks
├── CLAUDE.md          # Claude AI instructions
├── docker-compose.yml # Docker services
├── Dockerfile         # Production image
├── pyproject.toml     # Poetry configuration
├── poetry.lock        # Locked dependencies
├── README.md          # Project documentation
└── tailwind.config.js # Tailwind CSS config
```

## Directory Purposes

### `/src/app` - Application Core
The main application package containing all business logic, organized by layer:

- **api/**: RESTful API endpoints returning JSON
- **web/**: HTMX endpoints returning HTML fragments
- **models/**: Database models (SQLAlchemy ORM)
- **schemas/**: Data transfer objects (Pydantic)
- **crud/**: Database operations layer
- **services/**: Business logic layer
- **static/**: CSS, JavaScript, images
- **templates/**: Jinja2 HTML templates

### `/tests` - Test Suite
Comprehensive test coverage organized by type:

- **unit/**: Fast, isolated tests for individual components
- **integration/**: Tests with database/external dependencies
- **e2e/**: Full user workflow tests
- **fixtures/**: Shared test data and factories

### `/docs` - Documentation
All project documentation:

- **architecture/**: System design and standards
- **stories/**: User stories and requirements
- **technical/**: Implementation guides
- **design/**: UI/UX specifications

### `/alembic` - Database Migrations
Version-controlled database schema changes:

- **versions/**: Individual migration files
- **env.py**: Migration environment configuration

### `/scripts` - Utility Scripts
Helper scripts for development:

- **init_db.sh**: Database setup and seeding
- **version.sh**: Git flow automation

## File Naming Conventions

### Python Files
- **Models**: Singular noun (e.g., `customer.py`)
- **Schemas**: Match model names
- **Services**: Match domain names
- **Tests**: `test_<module_name>.py`

### Templates
- **Pages**: `<feature>_<action>.html` (e.g., `customer_list.html`)
- **Partials**: `_<component>.html` (e.g., `_customer_row.html`)
- **Components**: `<component>_component.html`

### Static Assets
- **CSS**: Feature-based organization
- **JS**: Minimal, HTMX-focused scripts
- **Images**: Organized by feature/component

## Import Structure

### Absolute Imports
```python
# Always use absolute imports from app root
from app.models.customer import Customer
from app.services.customer import CustomerService
from app.schemas.customer import CustomerCreate
```

### Layer Dependencies
```
Web/API → Services → CRUD → Models
    ↓         ↓        ↓       ↓
  Schemas   Schemas  Schemas  Base
```

## Configuration Files

### Root Configuration
- **pyproject.toml**: Project metadata and dependencies
- **poetry.lock**: Locked dependency versions
- **.env.example**: Environment variables template
- **docker-compose.yml**: Local services configuration

### Development Configuration
- **.pre-commit-config.yaml**: Code quality hooks
- **.gitignore**: Version control exclusions
- **CLAUDE.md**: AI assistant instructions
- **.devcontainer/**: VS Code container setup

### Production Configuration
- **Dockerfile**: Production container image
- **alembic.ini**: Migration configuration
- **tailwind.config.js**: CSS framework setup

## Best Practices

### Module Organization
1. One class/function per file for models and services
2. Group related functionality in CRUD/API modules
3. Keep templates close to their routes
4. Colocate tests with tested code structure

### Dependency Flow
1. Routes depend on services
2. Services depend on CRUD/repositories
3. CRUD depends on models
4. Everyone can depend on schemas

### File Size Guidelines
- Models: < 200 lines
- Services: < 300 lines
- Routes: < 100 lines per endpoint group
- Templates: < 150 lines (use partials)

### Naming Consistency
- Database tables: Plural, snake_case
- Model classes: Singular, PascalCase
- Route functions: Verb_noun pattern
- Service methods: Action-oriented names