# TechStore - Arquitectura Técnica

## 🎯 Decisiones de Arquitectura

### Stack Tecnológico Seleccionado

**Backend**: FastAPI + Python 3.11  
**Base de Datos**: PostgreSQL 15  
**Frontend**: HTMX + Jinja2 Templates  
**Deploy**: Railway  
**Contenedores**: Docker + Dev Containers

## 🤔 Justificación de Decisiones Técnicas

### ¿Por qué FastAPI?

#### ✅ **Ventajas para TechStore:**
- **Performance**: Una de las frameworks más rápidas de Python
- **Productividad**: Menos código para misma funcionalidad vs Django
- **API-First**: Documentación automática con OpenAPI/Swagger
- **Type Safety**: Pydantic para validación automática
- **Async Support**: Preparado para escalabilidad futura
- **Learning Curve**: Más simple que Django para MVP rápido

#### 📊 **vs Alternativas:**
**vs Django:**
- ✅ Menos overhead para MVP simple
- ✅ API documentation automática
- ❌ Menos features built-in (admin, auth)
- ✅ Mejor para microservicios futuros

**vs Flask:**
- ✅ Type hints y validación automática
- ✅ Async nativo
- ✅ Documentación automática
- ✅ Mejor estructura para proyectos medianos

**vs Node.js/Express:**
- ✅ Team expertise en Python
- ✅ Ecosystem maduro para business logic
- ✅ Mejor para data processing (reportes, análisis)

---

### ¿Por qué PostgreSQL?

#### ✅ **Ventajas para TechStore:**
- **ACID Compliance**: Crítico para transacciones financieras
- **JSON Support**: Flexible para campos dinámicos (ej: configuraciones)
- **Escalabilidad**: Maneja growth de startup a empresa
- **Railway Support**: Primera clase en la plataforma
- **Rich Data Types**: Arrays, enums, etc. para business logic

#### 📊 **vs Alternativas:**
**vs MySQL:**
- ✅ Mejor soporte JSON
- ✅ Más features avanzadas
- ✅ Mejor para complex queries (reportes)

**vs SQLite:**
- ✅ Concurrencia real (múltiples usuarios)
- ✅ Escalabilidad para crecimiento
- ✅ Backup y replicación profesional

**vs MongoDB:**
- ✅ ACID transactions necesarias
- ✅ Relaciones complejas (cliente-venta-reparación)
- ✅ SQL familiar para reportes

---

### ¿Por qué HTMX?

#### ✅ **Ventajas para TechStore:**
- **Simplicidad**: No necesita JavaScript framework complejo
- **Server-Side Rendering**: SEO friendly, fast first load
- **Progressive Enhancement**: Funciona sin JS también
- **Small Bundle**: Menos dependencias que React/Vue
- **Python-First**: Desarrolladores backend pueden hacer frontend

#### 📊 **vs Alternativas:**
**vs React/Vue SPA:**
- ✅ Menor complejidad de desarrollo
- ✅ No necesita API separada
- ✅ SEO nativo
- ❌ Menos interactividad avanzada (pero suficiente para MVP)

**vs Server-Side rendering puro:**
- ✅ Mejor UX (no full page reloads)
- ✅ Componentes dinámicos
- ✅ Validación en tiempo real

**vs jQuery:**
- ✅ Paradigma más moderno
- ✅ Menos código boilerplate
- ✅ Mejor integración con forms

---

## 🏗️ Arquitectura del Sistema

### Estructura de Directorios

```
techstore/
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── database.py             # DB connection & session
│   │   ├── dependencies.py         # FastAPI dependencies
│   │   ├── config.py               # Settings & environment vars
│   │   │
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base model class
│   │   │   ├── cliente.py         # Customer model
│   │   │   ├── producto.py        # Product model
│   │   │   ├── venta.py           # Sale model
│   │   │   └── reparacion.py      # Repair order model
│   │   │
│   │   ├── schemas/               # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── cliente.py         # Customer schemas
│   │   │   ├── producto.py        # Product schemas
│   │   │   ├── venta.py           # Sale schemas
│   │   │   └── reparacion.py      # Repair schemas
│   │   │
│   │   ├── crud/                  # Database operations
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base CRUD operations
│   │   │   ├── cliente.py         # Customer CRUD
│   │   │   ├── producto.py        # Product CRUD
│   │   │   ├── venta.py           # Sale CRUD
│   │   │   └── reparacion.py      # Repair CRUD
│   │   │
│   │   ├── api/                   # API routes
│   │   │   ├── __init__.py
│   │   │   ├── deps.py            # API dependencies
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api.py         # API router
│   │   │       ├── clientes.py    # Customer endpoints
│   │   │       ├── productos.py   # Product endpoints
│   │   │       ├── ventas.py      # Sale endpoints
│   │   │       └── reparaciones.py # Repair endpoints
│   │   │
│   │   ├── web/                   # Web interface (HTMX)
│   │   │   ├── __init__.py
│   │   │   ├── deps.py            # Web dependencies  
│   │   │   ├── main.py            # Web router
│   │   │   ├── clientes.py        # Customer web views
│   │   │   ├── productos.py       # Product web views
│   │   │   ├── ventas.py          # Sale web views
│   │   │   ├── reparaciones.py    # Repair web views
│   │   │   └── dashboard.py       # Dashboard views
│   │   │
│   │   └── templates/             # Jinja2 templates
│   │       ├── base.html          # Base template
│   │       ├── dashboard.html     # Dashboard
│   │       ├── clientes/          # Customer templates
│   │       ├── productos/         # Product templates
│   │       ├── ventas/            # Sale templates
│   │       ├── reparaciones/      # Repair templates
│   │       └── components/        # Reusable components
│   │
│   └── static/                    # Static files
│       ├── css/
│       ├── js/
│       └── images/
│
├── alembic/                   # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Test configuration
│   ├── test_models/          # Model tests
│   ├── test_crud/            # CRUD tests
│   ├── test_api/             # API tests
│   └── test_web/             # Web interface tests
│
├── scripts/                  # Utility scripts
│   └── version.sh            # Git flow management
│
├── docs/                     # Documentation
│
├── .devcontainer/            # Development container
├── Dockerfile                # Production container
├── pyproject.toml            # Dependencies
└── alembic.ini               # Database migration config
```

### Patrones de Arquitectura

#### 🔹 **Repository Pattern (CRUD Layer)**
```python
# app/crud/base.py
class CRUDBase:
    def get(self, db: Session, id: int)
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100)
    def create(self, db: Session, obj_in: CreateSchemaType)
    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType)
    def remove(self, db: Session, id: int)
```

#### 🔹 **Dependency Injection**
```python
# app/dependencies.py
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoints
@router.get("/clientes/{cliente_id}")
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return crud.cliente.get(db=db, id=cliente_id)
```

#### 🔹 **Schema-First Design**
```python
# app/schemas/cliente.py
class ClienteBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    cuenta_corriente_balance: Decimal
    
    class Config:
        from_attributes = True
```

## 🌐 Arquitectura de Deployment

### Desarrollo Local
```yaml
# .devcontainer/docker-compose.yml
services:
  app:
    build: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/techstore_db
    depends_on:
      - db
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: techstore_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
```

### Producción (Railway)
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Non-root user setup
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -m appuser

# Install Poetry
RUN pip install poetry==1.7.1

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --only=main

# Copy application
COPY . .
RUN chown -R appuser:appuser /app

USER appuser

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔒 Consideraciones de Seguridad

### Autenticación y Autorización
```python
# MVP: Single user session-based auth
# Future: JWT tokens + role-based access

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    # MVP: Simple session validation
    # Future: JWT token validation
    pass
```

### Validación de Datos
```python
# Pydantic automatic validation
class VentaCreate(BaseModel):
    cliente_id: int = Field(..., gt=0)
    items: List[ItemVenta] = Field(..., min_items=1)
    total: Decimal = Field(..., gt=0, decimal_places=2)
```

### Variables de Entorno
```python
# app/config.py
class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"
```

## 📊 Performance y Escalabilidad

### Optimizaciones Planeadas

**Database:**
- Índices en campos de búsqueda frecuente
- Connection pooling con SQLAlchemy
- Read replicas para reportes (futuro)

**Caching:**
- Redis para sesiones (post-MVP)
- HTTP caching para static assets
- Query result caching para reportes

**Monitoring:**
- Logs estructurados con loguru
- Health checks para Railway
- Error tracking con Sentry (futuro)

## 🧪 Estrategia de Testing

### Niveles de Testing
```python
# tests/test_crud/test_cliente.py
def test_create_cliente(db: Session):
    cliente_data = {"nombre": "Test", "email": "test@example.com"}
    cliente = crud.cliente.create(db=db, obj_in=ClienteCreate(**cliente_data))
    assert cliente.nombre == "Test"

# tests/test_api/test_clientes.py  
def test_create_cliente_endpoint(client: TestClient):
    response = client.post("/api/v1/clientes/", json=cliente_data)
    assert response.status_code == 200

# tests/test_web/test_cliente_views.py
def test_cliente_list_view(client: TestClient):
    response = client.get("/clientes")
    assert "Lista de Clientes" in response.text
```

### CI/CD Pipeline
- **Pre-commit hooks**: ruff, black, pytest
- **Railway deploy**: Automatic on main branch push
- **Migration strategy**: Alembic automatic migrations

## 🔄 Evolución de la Arquitectura

### MVP → Post-MVP Evolution

**Current (MVP):**
- Monolith FastAPI app
- Single database
- Server-side rendering

**Near Future (6 months):**
- API + Web separation
- Background tasks (Celery)
- File storage (S3)

**Long Term (1+ years):**
- Microservices architecture
- Event-driven communication
- Multi-tenant database design
- Mobile API optimizations

Esta arquitectura está diseñada para ser **simple en el MVP** pero **escalable hacia el futuro**, permitiendo evolución incremental sin rewrites completos.