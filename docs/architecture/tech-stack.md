# TechStore Technology Stack

## Overview
TechStore is built with modern, production-ready technologies focusing on developer experience, performance, and maintainability. The stack emphasizes type safety, async operations, and clean architecture principles.

## Core Technologies

### Backend Framework
**FastAPI** (v0.104.1+)
- Modern, fast Python web framework
- Built-in OpenAPI/Swagger documentation
- Automatic request/response validation
- Native async/await support
- Dependency injection system
- Type hints throughout

### Language & Runtime
**Python 3.11+**
- Latest stable Python version
- Performance improvements over 3.10
- Better error messages
- Enhanced type hints
- Native asyncio optimizations

### Database
**PostgreSQL 15**
- ACID compliant relational database
- JSON/JSONB support for flexible data
- Full-text search capabilities
- Row-level security
- Excellent performance at scale

**SQLAlchemy 2.0+**
- Modern ORM with async support
- Type-safe queries
- Migration support via Alembic
- Connection pooling
- Lazy loading optimization

**Alembic**
- Database migration tool
- Version control for database schema
- Automatic migration generation
- Rollback capabilities

### Frontend
**HTMX**
- HTML-over-the-wire approach
- No JavaScript framework complexity
- Progressive enhancement
- Smaller bundle sizes
- Server-side rendering

**Jinja2 Templates**
- Server-side templating
- Fast rendering
- Template inheritance
- Auto-escaping for security
- Macros for reusability

**Tailwind CSS**
- Utility-first CSS framework
- No custom CSS needed
- Consistent design system
- Mobile-first responsive design
- Small production builds via PurgeCSS

### Authentication & Security
**python-jose**
- JWT token generation and validation
- RS256/HS256 algorithm support
- Token expiration handling

**passlib + bcrypt**
- Secure password hashing
- Cost factor 12 for bcrypt
- Future-proof with algorithm agility

### API & HTTP
**HTTPX**
- Async HTTP client
- Connection pooling
- Timeout handling
- HTTP/2 support
- Test client capabilities

**python-multipart**
- Form data parsing
- File upload handling
- Streaming support

### Development Tools

#### Code Quality
**Ruff**
- Fast Python linter (100x faster than flake8)
- Combines multiple tools (flake8, isort, etc.)
- Auto-fixing capabilities
- Extensive rule set

**Pre-commit**
- Git hooks for code quality
- Automatic formatting
- Prevents bad commits
- Team consistency

**MyPy** (via pre-commit)
- Static type checking
- Catches type errors early
- Improves code documentation
- IDE integration

#### Testing
**Pytest**
- Modern testing framework
- Fixtures for test data
- Parametrized tests
- Excellent error reporting

**pytest-asyncio**
- Async test support
- Event loop handling
- Async fixtures

**pytest-cov**
- Code coverage reporting
- Coverage thresholds
- HTML reports
- Integration with CI/CD

**Factory Boy**
- Test data generation
- Model factories
- Faker integration
- Relationship handling

### Infrastructure & Deployment

#### Containerization
**Docker**
- Consistent environments
- Multi-stage builds for optimization
- Docker Compose for local development
- Health checks

**DevContainer**
- VS Code integration
- Consistent development environment
- Pre-configured extensions
- Automatic port forwarding

#### Package Management
**Poetry**
- Modern dependency management
- Lock file for reproducibility
- Virtual environment handling
- Script definitions
- Dependency groups (dev/prod)

#### Environment Management
**python-dotenv**
- Environment variable loading
- .env file support
- Multiple environment support

**pydantic-settings**
- Type-safe configuration
- Environment variable validation
- Nested configuration support
- Secret management

### Production Dependencies

#### Performance
**uvicorn[standard]**
- ASGI server
- Production-ready with Gunicorn
- Auto-reload for development
- HTTP/2 support
- WebSocket support

**aiofiles**
- Async file operations
- Non-blocking I/O
- Static file serving
- Large file handling

#### Data Processing
**python-slugify**
- URL-safe string generation
- Unicode support
- Custom replacements
- SEO-friendly URLs

**email-validator**
- RFC-compliant email validation
- DNS checking optional
- International domain support

## Architecture Decisions

### Why FastAPI over Django/Flask?
- Native async support
- Automatic API documentation
- Type hints and validation
- Modern Python features
- Better performance
- Smaller footprint

### Why HTMX over React/Vue?
- Simpler architecture
- No build step required
- Progressive enhancement
- SEO-friendly
- Reduced complexity
- Faster initial development

### Why PostgreSQL over MySQL/MongoDB?
- ACID compliance for financial data
- Complex query support
- JSON capabilities when needed
- Better concurrent performance
- Extensions ecosystem

### Why Poetry over pip/pipenv?
- Better dependency resolution
- Cleaner pyproject.toml
- Built-in virtual env management
- Lock file for reproducibility
- Script management

## Version Policy

### Version Pinning Strategy
- **Production dependencies**: Use caret (^) for minor updates
- **Development dependencies**: Use caret (^) for flexibility
- **Security updates**: Apply immediately
- **Major versions**: Test thoroughly before upgrading

### Upgrade Schedule
- **Security patches**: Immediately
- **Bug fixes**: Weekly
- **Minor updates**: Monthly
- **Major updates**: Quarterly with testing

## Future Considerations

### Potential Additions
- **Redis**: For caching and sessions
- **Celery**: For background tasks
- **Sentry**: For error monitoring
- **Prometheus + Grafana**: For metrics
- **ElasticSearch**: For advanced search
- **MinIO**: For object storage

### Scaling Technologies
- **Kubernetes**: For container orchestration
- **API Gateway**: For microservices
- **Message Queue**: RabbitMQ or Kafka
- **CDN**: For static assets
- **Load Balancer**: For horizontal scaling

## Development Setup

### System Requirements
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (for non-devcontainer setup)
- VS Code (recommended)
- 8GB RAM minimum
- 10GB disk space

### Quick Start (Inside DevContainer)
```bash
# Dependencies are already installed via Poetry in the container

# Database is already running as a service in the container network
# Connection string: postgresql://postgres:postgres@db:5432/techstore_db

# Run migrations
poetry run alembic upgrade head

# Run development server
poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the shorter version from CLAUDE.md
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Quick Start (Outside DevContainer)
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Start PostgreSQL with Docker Compose
docker-compose up -d db

# Run migrations
poetry run alembic upgrade head

# Run development server
poetry run uvicorn src.app.main:app --reload
```

### Database Access
- **Inside DevContainer**: `db:5432` (container network)
- **Outside DevContainer**: `localhost:5432`
- **Username**: postgres
- **Password**: postgres
- **Database**: techstore_db

### IDE Setup
Recommended VS Code extensions (pre-installed in devcontainer):
- Python
- Pylance
- Ruff
- Docker
- PostgreSQL
- Tailwind CSS IntelliSense
- Better Jinja

### Testing Commands
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_api/test_customers.py

# Run tests in watch mode
poetry run pytest-watch
```