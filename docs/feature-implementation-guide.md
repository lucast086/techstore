# 🚀 Feature Implementation Guide - TechStore SaaS

Esta guía define el proceso paso a paso para implementar nuevas features siguiendo **Test-Driven Development (TDD)** y la arquitectura de 4 capas establecida.

## 🎯 **TDD + 4-Layer Architecture**

### **Principios Fundamentales:**
- **Red → Green → Refactor**: Escribir test que falle → Hacer que pase → Refactorizar
- **Outside-In Development**: Empezar por las capas externas (Web/API) hacia adentro (Service/Models)
- **Single Responsibility**: Cada capa tiene una responsabilidad específica
- **Dependency Injection**: Para facilitar testing y desacoplamiento

---

## 📋 **Proceso TDD por Feature**

### **Fase 1: Planificación y Casos de Prueba** 🧠

1. **Definir User Stories**
   ```
   Como [usuario] quiero [funcionalidad] para [beneficio]
   ```

2. **Identificar Casos de Prueba**
   - Happy path scenarios
   - Edge cases
   - Error scenarios
   - Validation scenarios

3. **Mapear a las 4 Capas**
   ```
   Web Layer (HTMX) → API Layer (JSON) → Service Layer → Model Layer
   ```

### **Fase 2: TDD Outside-In Implementation** 🔄

#### **Step 1: Web Layer Tests (TDD Red)**
```python
# tests/test_web/test_feature.py
def test_feature_web_endpoint():
    # Test que DEBE fallar inicialmente
    response = client.post("/htmx/feature", data={"param": "value"})
    assert response.status_code == 200
    assert "expected-content" in response.text
```

#### **Step 2: API Layer Tests (TDD Red)**
```python
# tests/test_api/test_feature.py
def test_feature_api_endpoint():
    # Test que DEBE fallar inicialmente
    response = client.post("/api/v1/feature", json={"param": "value"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

#### **Step 3: Service Layer Tests (TDD Red)**
```python
# tests/test_services/test_feature_service.py
def test_feature_service_logic():
    # Test que DEBE fallar inicialmente
    result = FeatureService.process_feature(param="value")
    assert result["success"] is True
    assert "data" in result
```

#### **Step 4: Model Tests (TDD Red)**
```python
# tests/test_models/test_feature_model.py
def test_feature_model_creation():
    # Test que DEBE fallar inicialmente
    feature = FeatureModel(name="test", value="data")
    assert feature.name == "test"
    assert feature.is_valid()
```

### **Fase 3: Implementation (TDD Green)** ✅

#### **Step 1: Models Implementation**
```python
# app/models/feature.py
from app.models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

class FeatureModel(BaseModel):
    __tablename__ = "features"
    
    name: Mapped[str] = mapped_column(nullable=False)
    # ... other fields
```

#### **Step 2: Schemas Implementation**
```python
# app/schemas/feature.py
from pydantic import BaseModel

class FeatureCreate(BaseModel):
    name: str
    # ... other fields

class FeatureResponse(BaseModel):
    id: int
    name: str
    # ... other fields
```

#### **Step 3: Service Implementation**
```python
# app/services/feature_service.py
class FeatureService:
    @classmethod
    def process_feature(cls, param: str) -> dict:
        # Pure business logic implementation
        # No HTTP, no HTML, no database calls
        pass
```

#### **Step 4: API Implementation**
```python
# app/api/v1/feature.py
from fastapi import APIRouter
from app.services.feature_service import FeatureService
from app.schemas.feature import FeatureResponse

@router.post("/feature", response_model=FeatureResponse)
async def create_feature_api(data: FeatureCreate):
    result = FeatureService.process_feature(data.param)
    return FeatureResponse(**result)
```

#### **Step 5: Web Implementation**
```python
# app/web/feature.py
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

@router.post("/feature", response_class=HTMLResponse)
async def create_feature_htmx(param: str = Form(...)):
    # Call internal API
    api_data = await call_internal_api(param)
    # Convert to HTML
    return render_feature_html(api_data)
```

### **Fase 4: Integration & Refactor** 🔧

1. **Run All Tests**: Verificar que todos los tests pasen
2. **Integration Testing**: Tests end-to-end
3. **Refactor**: Mejorar código manteniendo tests verdes
4. **Performance**: Optimizar si es necesario

---

## 📁 **Estructura de Archivos por Feature**

```
feature_name/
├── models/
│   └── feature.py              # SQLAlchemy model
├── schemas/
│   └── feature.py              # Pydantic schemas
├── services/
│   └── feature_service.py      # Business logic
├── api/v1/
│   └── feature.py              # JSON endpoints
├── web/
│   └── feature.py              # HTMX endpoints
├── crud/
│   └── feature.py              # Database operations
├── templates/
│   └── feature.html            # HTML templates
└── tests/
    ├── test_models/
    │   └── test_feature.py     # Model tests
    ├── test_services/
    │   └── test_feature_service.py  # Service tests
    ├── test_api/
    │   └── test_feature.py     # API tests
    └── test_web/
        └── test_feature_htmx.py # Web tests
```

---

## ✅ **TDD Checklist por Feature**

### **Pre-Implementation:**
- [ ] User stories definidas
- [ ] Test cases identificados
- [ ] Arquitectura de 4 capas mapeada

### **TDD Red Phase:**
- [ ] Web layer tests escritos (fallan)
- [ ] API layer tests escritos (fallan)
- [ ] Service layer tests escritos (fallan)
- [ ] Model tests escritos (fallan)

### **TDD Green Phase:**
- [ ] Models implementados (tests pasan)
- [ ] Schemas implementados
- [ ] Services implementados (tests pasan)
- [ ] API endpoints implementados (tests pasan)
- [ ] Web endpoints implementados (tests pasan)

### **TDD Refactor Phase:**
- [ ] Todos los tests pasan
- [ ] Código refactorizado
- [ ] Performance optimizada
- [ ] Documentación actualizada

### **Integration:**
- [ ] Database migration creada
- [ ] Routes registradas en main.py
- [ ] Templates creadas
- [ ] Manual testing realizado

---

## 🧪 **Testing Strategy**

### **Test Pyramid:**
```
    /\    End-to-End Tests (Few)
   /  \   
  /____\  Integration Tests (Some)
 /      \ 
/________\ Unit Tests (Many)
```

### **Test Types por Layer:**

**Model Tests:**
- Field validation
- Relationships
- Custom methods
- Database constraints

**Service Tests:**
- Business logic
- Edge cases
- Error handling
- Data transformations

**API Tests:**
- HTTP status codes
- JSON structure
- Request validation
- Error responses

**Web Tests:**
- HTML structure
- HTMX functionality
- Form handling
- UI interactions

---

## 🎯 **Example: Implementing "Cliente" Feature**

### **1. User Stories:**
```
Como administrador quiero registrar clientes para gestionar ventas
Como administrador quiero buscar clientes para ver su información
Como administrador quiero actualizar datos de clientes para mantenerlos actualizados
```

### **2. Test Cases:**
- Create client with valid data
- Search clients by name/email
- Update client information
- Handle validation errors
- Handle duplicate email

### **3. TDD Implementation:**
```bash
# Red: Write failing tests
tests/test_models/test_cliente.py
tests/test_services/test_cliente_service.py
tests/test_api/test_cliente.py
tests/test_web/test_cliente_htmx.py

# Green: Implement to make tests pass
app/models/cliente.py
app/schemas/cliente.py
app/services/cliente_service.py
app/api/v1/cliente.py
app/web/cliente.py

# Refactor: Improve while keeping tests green
```

---

## 📚 **Best Practices**

### **TDD Guidelines:**
- **Small steps**: Un test a la vez
- **Clear test names**: Describe what you're testing
- **Arrange-Act-Assert**: Estructura clara en tests
- **Mock external dependencies**: Base de datos, APIs, etc.

### **Code Quality:**
- **Type hints**: En todos los métodos y funciones
- **Docstrings**: Para módulos, clases y funciones públicas
- **Error handling**: Manejo explícito de errores
- **Validation**: En todas las capas apropiadas

### **Architecture:**
- **Single Source of Truth**: Business logic solo en Services
- **Separation of Concerns**: Cada capa una responsabilidad
- **Dependency Injection**: Para facilitar testing
- **No direct DB calls**: En Web/API layers

---

## 🚀 **Quick Start Template**

Para implementar una nueva feature rápidamente:

```bash
# 1. Create test files
touch tests/test_models/test_[feature].py
touch tests/test_services/test_[feature]_service.py
touch tests/test_api/test_[feature].py
touch tests/test_web/test_[feature]_htmx.py

# 2. Write failing tests for each layer

# 3. Create implementation files
touch app/models/[feature].py
touch app/schemas/[feature].py
touch app/services/[feature]_service.py
touch app/api/v1/[feature].py
touch app/web/[feature].py

# 4. Implement to make tests pass

# 5. Refactor and optimize
```

**Esta guía garantiza features bien tested, mantenibles y escalables siguiendo TDD y arquitectura limpia.**