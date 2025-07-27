# 🚀 Project Setup Guide - TechStore SaaS

Esta guía permite replicar exactamente el setup realizado para TechStore SaaS en otros proyectos.

## 📋 **Prerequisites**
- Python 3.11+
- Poetry for dependency management
- Docker + Docker Compose (for development)
- Git
- VS Code (recommended)

---

## 🔧 **Step-by-Step Setup**

### **Step 1: Project Structure**
```bash
mkdir techstore-saas
cd techstore-saas

# Create main directories
mkdir -p src/app/{api/v1,web,models,schemas,services,crud,templates}
mkdir -p tests/{test_api,test_web,test_services}
mkdir -p docs
mkdir -p scripts
mkdir -p .devcontainer
mkdir -p src/static/{css,js,images}
mkdir -p alembic

# Create __init__.py files
touch src/app/__init__.py
touch src/app/{api,web,models,schemas,services,crud}/__init__.py
touch tests/{test_api,test_web,test_services}/__init__.py
```

### **Step 2: Poetry + Dependencies**
```bash
# Initialize Poetry
poetry init

# Add main dependencies
poetry add fastapi uvicorn[standard] jinja2 python-multipart
poetry add sqlalchemy alembic psycopg2-binary
poetry add python-jose[cryptography] passlib[bcrypt]
poetry add python-dotenv pydantic-settings aiofiles
poetry add httpx python-slugify email-validator

# Add dev dependencies  
poetry add --group dev pytest pytest-asyncio pytest-cov
poetry add --group dev ruff pre-commit factory-boy coverage

# Install dependencies
poetry install
```

### **Step 3: Core Files**

**pyproject.toml configuration:**
```toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501", "B008"]

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = ["tests"]
```

**src/app/main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="Your App Name",
    description="Your app description", 
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/app/templates")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "API is running"}
```

**src/app/config.py:**
```python
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = Field(default="postgresql://postgres:postgres@db:5432/app_db")
    secret_key: str = Field(default="your-secret-key-here")
    debug: bool = Field(default=True)
    environment: str = Field(default="development")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

**src/app/database.py:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**src/app/dependencies.py:**
```python
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DatabaseDep = Depends(get_db)
```

### **Step 4: Environment Files**

**.env.template:**
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/your_app_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Application Settings
DEBUG=True
ENVIRONMENT=development

# CORS Origins (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

**.gitignore:**
```bash
# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
build/
dist/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# FastAPI
.ruff_cache/
```

### **Step 5: Alembic Setup**
```bash
# Initialize Alembic
poetry run alembic init alembic

# Edit alembic.ini - comment out sqlalchemy.url line
# Add: prepend_sys_path = src

# Edit alembic/env.py - add these imports:
```

**alembic/env.py additions:**
```python
from app.config import settings
from app.database import Base

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

### **Step 6: Testing Setup**

**tests/conftest.py:**
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

**tests/test_main.py:**
```python
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running"}
```

### **Step 7: Pre-commit Hooks**

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]
        args: [--max-line-length=100, --ignore=F841,D100,D103,D104,D415]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black, --line-length=100]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, css, scss, yaml]
```

```bash
# Install pre-commit hooks
poetry run pre-commit install
```

### **Step 8: VS Code Configuration**

**.vscode/settings.json:**
```json
{
  "python.linting.enabled": false,
  "python.formatting.provider": "none",
  
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },

  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.format.enable": true,
  "ruff.organizeImports": true,
  "ruff.nativeServer": true,

  "editor.formatOnSave": true,
  "editor.rulers": [88],

  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.analysis.extraPaths": ["${workspaceFolder}/src"]
}
```

### **Step 9: Documentation Structure**

**Create documentation files:**
```bash
touch docs/{tech-architecture.md,development-log.md,project-setup-guide.md}
touch docs/{architecture-examples.md,user-stories.md,mvp-definition.md}
```

### **Step 10: CLAUDE.md (for Claude Code)**

**CLAUDE.md:**
```markdown
# CLAUDE.md

## Essential Commands

### Development Setup
```bash
poetry install
poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
poetry run pytest
poetry run ruff check .
poetry run ruff format .
poetry run alembic upgrade head
```

## Architecture Overview
FastAPI-based application with 4-layer architecture:
- Service Layer: Business logic
- Schema Layer: Data contracts
- API Layer: REST endpoints (JSON)
- Web Layer: HTMX endpoints (HTML)

## Development Guidelines
- **Docstrings**: Add docstrings for modules, classes, and functions when required by linting
- **Comments**: NEVER add inline comments unless explicitly requested by the user
- **Testing**: Separate tests by layer (services/api/web)
- **Type Hints**: Required throughout codebase
```

---

## 🧪 **Verification Steps**

### **Test the setup:**
```bash
# 1. Install dependencies
poetry install

# 2. Run tests
poetry run pytest -v

# 3. Start development server
poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Test endpoints
curl http://localhost:8000/health
# Should return: {"status": "ok", "message": "API is running"}

# 5. Run linting
poetry run ruff check .
poetry run ruff format .

# 6. Test pre-commit
poetry run pre-commit run --all-files
```

### **Expected results:**
- ✅ All tests pass
- ✅ Server starts without errors  
- ✅ Health endpoint responds correctly
- ✅ Linting passes
- ✅ Pre-commit hooks work

---

## 📁 **Final Project Structure**

```
your-project/
├── src/app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── api/v1/
│   ├── web/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── crud/
│   └── templates/
├── tests/
│   ├── test_main.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_web/
│   └── test_services/
├── docs/
├── alembic/
├── .devcontainer/
├── scripts/
├── pyproject.toml
├── .env.template
├── .gitignore
├── .pre-commit-config.yaml
├── CLAUDE.md
└── README.md
```

## 🎯 **Next Steps**

After setup completion, see the **Feature Implementation Guide** (`docs/feature-implementation-guide.md`) for detailed TDD approach to implement new features using the 4-layer architecture.

This setup provides a solid, scalable foundation for any FastAPI + HTMX project.