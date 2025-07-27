# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development Setup
```bash
# Install dependencies
poetry install

# Run development server (in devcontainer)
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Run development server (outside devcontainer) 
poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
poetry run pytest

# Run linting and formatting
poetry run ruff check .
poetry run ruff format .

# Database migrations
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"
```

### Git Flow Management
```bash
# Initialize Git Flow structure
./scripts/version.sh init

# Feature development
./scripts/version.sh feature start feature-name
./scripts/version.sh feature finish feature-name

# Release management
./scripts/version.sh release start 1.0.0
./scripts/version.sh release finish 1.0.0

# Current version
./scripts/version.sh current
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_models/test_cliente.py
```

## Architecture Overview

**TechStore SaaS** is a FastAPI-based business management system built for tech stores, focusing on customer management, product inventory, sales, and repair orders.

### Technology Stack
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 15 
- **Frontend**: HTMX + Jinja2 Templates
- **Deployment**: Railway (Production), Docker (Development)

### Project Structure
Based on the planned architecture in `docs/tech-architecture.md`:

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Settings and environment configuration
├── database.py          # SQLAlchemy database connection
├── dependencies.py      # FastAPI dependency injection
├── models/             # SQLAlchemy models (cliente, producto, venta, reparacion)
├── schemas/            # Pydantic schemas for validation
├── crud/               # Database operation layer (Repository pattern)
├── api/v1/             # REST API endpoints
├── web/                # HTMX web interface routes
└── templates/          # Jinja2 HTML templates
```

### Key Design Patterns
- **Repository Pattern**: CRUD layer for database operations
- **Dependency Injection**: FastAPI dependencies for database sessions
- **Schema-First Design**: Pydantic models for validation and serialization

### Database
- Uses Alembic for migrations
- PostgreSQL with ACID compliance for financial transactions
- Models follow SQLAlchemy ORM patterns

## Development Guidelines

### Code Quality
- **Linting**: Configured with ruff (replaces flake8, black, isort)
- **Type Hints**: Required throughout codebase
- **Line Length**: 88 characters (configured in pyproject.toml)
- **Pre-commit Hooks**: Automatically run linting, formatting, and tests
- **Docstrings**: Add docstrings for modules, classes, and functions when required by linting
- **Comments**: NEVER add inline comments unless explicitly requested by the user

### Feature Implementation
- **ALWAYS follow TDD approach**: See `docs/feature-implementation-guide.md`
- **4-Layer Architecture**: Service → Schema → API → Web
- **Test-First Development**: Write tests before implementation
- **Outside-In Development**: Start with Web/API tests, work inward

### Session Workflow for Features
**In every session, follow this process:**
1. **Choose User Stories**: From `docs/user-stories.md` or write new ones
2. **Apply TDD Process**: Follow `docs/feature-implementation-guide.md` exactly
3. **Implementation Order**: 
   - Red Phase: Write failing tests (Web → API → Service → Model)
   - Green Phase: Implement to pass tests (Model → Service → API → Web)
   - Refactor Phase: Improve code while keeping tests green
4. **Always use TodoWrite**: Track progress through each phase
5. **Complete Features**: Don't leave half-implemented features

### Git Workflow
- **Main Branch**: `main` (production-ready code only)
- **Development Branch**: `development` (integration branch)
- **Feature Branches**: `feature/feature-name`
- **Release Branches**: `release/version-number`
- **Hotfix Branches**: `hotfix/version-number`

### Environment Configuration
- Uses `.env` files for local development
- Environment variables defined in `app/config.py` using Pydantic Settings
- Database URL: `postgresql://postgres:postgres@db:5432/techstore_db` (development)

### Development Environment
- **DevContainer**: Configured with docker-compose setup including PostgreSQL
- **VS Code**: Extensions and settings pre-configured for Python development
- **Port Forwarding**: 8000 (FastAPI), 5432 (PostgreSQL)

## Business Domain

This system manages four core entities for tech stores:

1. **Clientes (Customers)**: Customer management with account balances
2. **Productos (Products)**: Product catalog with categories and inventory
3. **Ventas (Sales)**: Sales transactions with customer account integration
4. **Reparaciones (Repairs)**: Repair order workflow with status tracking

### MVP Features (In Development)
- Customer registration and search
- Product catalog management
- Sales processing with customer accounts
- Repair order creation and status tracking
- Basic dashboard with business metrics

## Testing Strategy
- **Unit Tests**: All models and CRUD operations
- **Integration Tests**: API endpoints
- **Web Tests**: HTMX interface functionality
- **Test Database**: Separate test database configuration in conftest.py

## Deployment
- **Production**: Railway platform with automated deploys from main branch
- **Database**: Managed PostgreSQL on Railway
- **Environment**: Production environment variables configured in Railway dashboard