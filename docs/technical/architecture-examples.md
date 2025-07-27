# 🏗️ Architecture Examples - TechStore SaaS

Este documento muestra ejemplos concretos de la arquitectura implementada en TechStore SaaS.

## 📋 **Estructura de Directorios**

```
src/app/
├── main.py                 # FastAPI app + router registration
├── config.py               # Settings con Pydantic
├── database.py             # SQLAlchemy setup
├── dependencies.py         # FastAPI dependency injection
│
├── services/               # 🧠 Business Logic Layer
│   ├── __init__.py
│   └── search_service.py   # Pure business logic
│
├── schemas/                # 📝 Pydantic Schemas  
│   ├── __init__.py
│   └── search.py           # Request/Response models
│
├── api/v1/                 # 🔗 API Layer (JSON)
│   ├── __init__.py
│   └── search.py           # REST endpoints
│
├── web/                    # 🌐 Web Layer (HTMX)
│   ├── __init__.py
│   └── search.py           # HTML endpoints
│
├── crud/                   # 💾 Database Layer
│   └── __init__.py
│
├── models/                 # 🗃️ SQLAlchemy Models
│   └── __init__.py
│
└── templates/              # 📄 Jinja2 Templates
    └── welcome.html
```

## 🔄 **Flujo de Datos**

### **Producción:**
```
HTMX Request → Web Endpoint → HTTP Call → API Endpoint → Service → Data
                     ↓                        ↓           ↓
                   HTML                     JSON    Business Logic
```

### **Testing:**
```
Test Client → Web Endpoint → DI Fallback → Service → Mock Data
                     ↓                        ↓
                   HTML                Business Logic
```

## 📁 **Ejemplo: Search Feature**

### **1. Service Layer (Business Logic)**
```python
# app/services/search_service.py
class SearchService:
    @classmethod
    def search_products(cls, search_term: str) -> Dict:
        # Pure business logic - no HTTP, no HTML
        results = [product for product in cls.DEMO_PRODUCTS 
                  if search_term.lower() in product["name"].lower()]
        return {"results": results, "total": len(results)}
```

### **2. Schemas Layer (Data Contracts)**
```python
# app/schemas/search.py
class ProductSchema(BaseModel):
    id: int
    name: str
    category: str
    price: float

class SearchResponse(BaseModel):
    results: List[ProductSchema]
    total: int
    search_term: str
```

### **3. API Layer (JSON Endpoints)**
```python
# app/api/v1/search.py
@router.get("/products", response_model=SearchResponse)
async def search_products_api(q: str = Query(...)):
    result = SearchService.search_products(search_term=q)
    return SearchResponse(**result)
```

### **4. Web Layer (HTMX Endpoints)**
```python
# app/web/search.py
@router.post("/products", response_class=HTMLResponse)
async def search_products_htmx(search_term: str = Form(...)):
    # Calls internal API
    api_data = await call_internal_api(search_term)
    
    # Converts JSON to HTML
    html = render_products_html(api_data)
    return html
```

## 🧪 **Testing Strategy**

### **Tests por Layer:**
```
tests/
├── test_services/          # Business logic tests
│   └── test_search_service.py
├── test_api/              # JSON API tests  
│   └── test_search.py
└── test_web/              # HTML/HTMX tests
    └── test_search_htmx.py
```

### **Ejemplos de Tests:**

**Service Tests:**
```python
def test_search_service():
    result = SearchService.search_products("iphone")
    assert result["total"] == 1
    assert result["results"][0]["name"] == "iPhone 14 Pro"
```

**API Tests:**
```python
def test_search_api():
    response = client.get("/api/v1/search/products?q=iphone")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
```

**Web Tests:**
```python
def test_search_htmx():
    response = client.post("/htmx/search/products", data={"q": "iphone"})
    assert response.status_code == 200
    assert "iPhone 14 Pro" in response.text
    assert "<div" in response.text  # HTML structure
```

## 🔧 **Dependency Injection**

### **Setup:**
```python
# app/dependencies.py
def get_search_service() -> SearchService:
    return SearchService

# app/web/search.py
async def search_htmx(
    search_service: SearchService = Depends(get_search_service)
):
    # Uses injected service
```

### **Testing Override:**
```python
# tests/conftest.py
def get_mock_service():
    return MockSearchService()

# Override for testing
app.dependency_overrides[get_search_service] = get_mock_service
```

## ✅ **Best Practices Implementadas**

### **1. Separation of Concerns**
- **Services**: Solo business logic
- **APIs**: Solo JSON serialization
- **Web**: Solo HTML rendering
- **Schemas**: Solo data contracts

### **2. Single Source of Truth**
- Business logic vive solo en Services
- APIs y Web consumen mismo Service
- Schemas centralizados

### **3. Testeable**
- Cada layer se testea independientemente
- DI permite mocking fácil
- Sin HTTP calls reales en tests

### **4. Escalable**
- Agregar mobile: usa APIs existentes
- Agregar admin: usa Services existentes
- Cambiar DB: solo afecta Services

## 🚀 **Pasos para Nueva Feature**

1. **Service**: Implementar business logic
2. **Schema**: Definir data contracts  
3. **API**: Crear JSON endpoints
4. **Web**: Crear HTMX endpoints
5. **Tests**: Testear cada layer
6. **Templates**: Crear HTML si necesario

Esta arquitectura está lista para escalar desde MVP hasta aplicación enterprise.