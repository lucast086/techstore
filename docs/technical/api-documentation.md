# TechStore SaaS - API Documentation

## 📋 API Overview

TechStore SaaS implementa una arquitectura de capas clara donde los endpoints HTMX consumen los endpoints de API REST para renderizar HTML, mientras que las aplicaciones móviles y externas consumen directamente los endpoints de API.

### Flujo de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  HTMX Endpoints │───▶│  API Endpoints  │───▶│    Services     │
│   (HTML render) │    │  (JSON logic)   │    │ (Domain logic)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              ▲
                              │
                       ┌─────────────────┐
                       │   Mobile Apps   │
                       │  External APIs  │
                       └─────────────────┘
```

### Base URLs

- **REST API**: `/api/v1/` - Respuestas JSON para consumo programático
- **HTMX Web Interface**: `/htmx/` - Consume API y renderiza HTML
- **Main Web Pages**: `/` - Páginas completas del sitio web

### Content Types

- **API Endpoints**: `application/json`
- **HTMX Endpoints**: `text/html`
- **Static Assets**: `text/css`, `application/javascript`, etc.

## 🔍 Search API Endpoints

### Search Products API

Busca productos por nombre con filtrado opcional por categoría.

**Endpoint**: `GET /api/v1/search/products`

**Query Parameters**:
- `q` (required): Término de búsqueda para encontrar en nombres de productos
- `category` (optional): Filtrar por categoría de producto
- `limit` (optional): Máximo de resultados (1-50, default: 10)

**Response Schema**:
```json
{
  "results": [
    {
      "id": 1,
      "name": "iPhone 14 Pro",
      "category": "smartphone",
      "price": 999.99
    }
  ],
  "total": 1,
  "search_term": "iphone",
  "category": "smartphone",
  "message": "Search completed successfully"
}
```

**Example Requests**:
```bash
# Búsqueda básica
GET /api/v1/search/products?q=iphone

# Búsqueda con filtro de categoría
GET /api/v1/search/products?q=pro&category=smartphone&limit=5

# Búsqueda sin resultados
GET /api/v1/search/products?q=nonexistent
```

**Response Examples**:

*Búsqueda exitosa:*
```json
{
  "results": [
    {
      "id": 1,
      "name": "iPhone 14 Pro",
      "category": "smartphone",
      "price": 999.99
    },
    {
      "id": 3,
      "name": "MacBook Pro M2",
      "category": "laptop",
      "price": 1299.99
    }
  ],
  "total": 2,
  "search_term": "pro",
  "category": null,
  "message": "Search completed successfully"
}
```

*Sin resultados:*
```json
{
  "results": [],
  "total": 0,
  "search_term": "nonexistent",
  "category": null,
  "message": "No products found for 'nonexistent'"
}
```

*Término de búsqueda vacío:*
```json
{
  "results": [],
  "total": 0,
  "search_term": "",
  "category": null,
  "message": "Please enter a search term"
}
```

### Get Categories API

Recupera todas las categorías de productos disponibles.

**Endpoint**: `GET /api/v1/search/categories`

**Response Schema**:
```json
{
  "categories": ["audio", "laptop", "smartphone", "tablet"]
}
```

**Example Request**:
```bash
GET /api/v1/search/categories
```

**Response Example**:
```json
{
  "categories": [
    "audio",
    "laptop", 
    "smartphone",
    "tablet"
  ]
}
```

## 🌐 HTMX Web Interface

Los endpoints HTMX consumen los endpoints de API y convierten las respuestas JSON a HTML para actualizaciones dinámicas de página.

### Search Products HTMX

Endpoint HTMX que consume `/api/v1/search/products` y retorna fragmentos HTML.

**Endpoint**: `POST /htmx/search/products`

**Arquitectura**:
```
POST /htmx/search/products → GET /api/v1/search/products → SearchService → HTML Response
```

**Form Data**:
- `q` (required): Término de búsqueda
- `category` (optional): Filtro de categoría de producto

**Response**: Fragmento HTML con resultados de búsqueda

**HTMX Attributes**:
```html
<form hx-post="/htmx/search/products" hx-target="#search-results">
  <input name="q" placeholder="Search products...">
  <select name="category">
    <option value="">All Categories</option>
  </select>
</form>
```

**Proceso Interno**:
1. Recibe datos del formulario HTMX
2. Llama internamente a `GET /api/v1/search/products`
3. Procesa la respuesta JSON del API
4. Convierte los datos a HTML con iconos y estilos
5. Retorna el fragmento HTML para inserción en el DOM

**Response Examples**:

*Búsqueda exitosa:*
```html
<p class="text-success mb-2"><i class="fas fa-check"></i> Found 2 products</p>
<div class="result-item border-bottom py-2">
  <div class="d-flex align-items-center">
    <i class="fas fa-mobile-alt text-primary me-2"></i>
    <div class="flex-grow-1">
      <strong>iPhone 14 Pro</strong>
      <br><small class="text-muted">Smartphone • $999.99</small>
    </div>
  </div>
</div>
```

*Sin resultados:*
```html
<p class="text-warning"><i class="fas fa-exclamation-triangle"></i> No products found for 'xyz'</p>
```

*Búsqueda vacía:*
```html
<p class="text-muted"><i class="fas fa-search"></i> Enter a search term...</p>
```

### Get Categories HTMX

Endpoint HTMX que consume `/api/v1/search/categories` y retorna elementos HTML option.

**Endpoint**: `GET /htmx/search/categories`

**Arquitectura**:
```
GET /htmx/search/categories → GET /api/v1/search/categories → SearchService → HTML Options
```

**Response**: Elementos HTML option para dropdowns

**HTMX Usage**:
```html
<select hx-get="/htmx/search/categories" hx-trigger="load">
  <!-- Options cargadas dinámicamente -->
</select>
```

**Proceso Interno**:
1. Llama internamente a `GET /api/v1/search/categories`
2. Recibe array de categorías del API
3. Convierte a elementos `<option>` HTML
4. Retorna HTML para inserción en `<select>`

**Response Example**:
```html
<option value="">All Categories</option>
<option value="audio">Audio</option>
<option value="laptop">Laptop</option>
<option value="smartphone">Smartphone</option>
<option value="tablet">Tablet</option>
```

## 📊 Data Models

### Product Schema

Estructura de datos principal para productos usada en todos los endpoints.

```python
class ProductSchema(BaseModel):
    id: int                    # Identificador único del producto
    name: str                  # Nombre del producto
    category: str              # Categoría del producto
    price: float               # Precio del producto en USD
```

**Example**:
```json
{
  "id": 1,
  "name": "iPhone 14 Pro",
  "category": "smartphone", 
  "price": 999.99
}
```

### Search Response Schema

Formato de respuesta para operaciones de búsqueda.

```python
class SearchResponse(BaseModel):
    results: list[ProductSchema]  # Lista de productos coincidentes
    total: int                    # Número de resultados retornados
    search_term: str              # Término de búsqueda original
    category: str | None          # Filtro de categoría aplicado
    message: str                  # Mensaje de estado o error
```

### Category Response Schema

Formato de respuesta para listado de categorías.

```python
class CategoryResponse(BaseModel):
    categories: list[str]         # Lista de categorías disponibles
```

## 🏗️ Service Layer

### SearchService

Lógica de negocio principal para funcionalidad de búsqueda.

**Métodos**:

#### `search_products(search_term, category=None, max_results=10)`

Busca productos por término con filtrado opcional por categoría.

**Parameters**:
- `search_term` (str): Texto a buscar en nombres de productos
- `category` (str, optional): Filtro de categoría
- `max_results` (int): Número máximo de resultados (default: 10)

**Returns**: Diccionario con results, total, search_term, category, y message

**Lógica de Negocio**:
1. Valida término de búsqueda (no vacío)
2. Realiza coincidencia de nombres insensible a mayúsculas
3. Aplica filtro de categoría si se proporciona
4. Limita resultados a max_results
5. Retorna metadatos con resultados

#### `get_categories()`

Recupera todas las categorías de productos disponibles.

**Returns**: Lista ordenada de nombres de categorías únicos

## 🎨 UI Components

### Search Form

Formulario de búsqueda interactivo con mejora HTMX.

```html
<form hx-post="/htmx/search/products" 
      hx-target="#search-results"
      hx-trigger="submit, keyup delay:300ms from:input[name='q']">
  
  <div class="input-group mb-3">
    <input type="text" 
           name="q" 
           class="form-control" 
           placeholder="Search products...">
    
    <select name="category" 
            class="form-select"
            hx-get="/htmx/search/categories"
            hx-trigger="load">
      <!-- Options cargadas via HTMX -->
    </select>
    
    <button type="submit" class="btn btn-primary">
      <i class="fas fa-search"></i> Search
    </button>
  </div>
</form>

<div id="search-results">
  <!-- Resultados cargados aquí via HTMX -->
</div>
```

### Category Icons

Las categorías de productos se muestran con iconos de Font Awesome:

- **Smartphone**: `fas fa-mobile-alt`
- **Laptop**: `fas fa-laptop`
- **Tablet**: `fas fa-tablet-alt`
- **Audio**: `fas fa-headphones`
- **Default**: `fas fa-box`

## 🔄 Architecture Benefits

### Separación de Responsabilidades

**API Endpoints**:
- Contienen toda la lógica de negocio
- Validan datos de entrada
- Retornan respuestas JSON estructuradas
- Son consumibles por múltiples clientes

**HTMX Endpoints**:
- Se enfocan únicamente en renderizado HTML
- Consumen APIs internas como cualquier cliente externo
- Convierten JSON a HTML con estilos apropiados
- Manejan interacciones específicas del navegador

**Services**:
- Lógica de dominio pura
- Independientes de la capa de presentación
- Reutilizables por diferentes endpoints
- Fáciles de testear en aislamiento

### Escalabilidad

```
┌─────────────────┐
│   Mobile App    │──┐
└─────────────────┘  │
                     │
┌─────────────────┐  │    ┌─────────────────┐    ┌─────────────────┐
│  HTMX Frontend  │──┼───▶│  API Endpoints  │───▶│    Services     │
└─────────────────┘  │    └─────────────────┘    └─────────────────┘
                     │
┌─────────────────┐  │
│  External API   │──┘
└─────────────────┘
```

### Beneficios para el Futuro

1. **Mobile Apps**: Pueden consumir directamente los API endpoints
2. **External Integrations**: APIs listos para terceros
3. **Microservices**: Services pueden extraerse fácilmente
4. **Testing**: Cada capa puede testearse independientemente
5. **Caching**: APIs pueden cachearse para múltiples clientes
6. **Rate Limiting**: Aplicable a nivel de API para todos los consumidores

## 🧪 Testing Strategy

### API Testing

```python
def test_search_products_api(client):
    response = client.get("/api/v1/search/products?q=iphone")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert "iphone" in data["results"][0]["name"].lower()

def test_search_empty_term(client):
    response = client.get("/api/v1/search/products?q=")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert "enter a search term" in data["message"].lower()
```

### HTMX Testing

```python
def test_search_htmx_calls_api(client, mock_api):
    # Mock del API endpoint interno
    mock_api.return_value = {
        "results": [{"id": 1, "name": "iPhone", "category": "smartphone", "price": 999}],
        "total": 1,
        "message": "Success"
    }
    
    response = client.post("/htmx/search/products", data={"q": "iphone"})
    assert response.status_code == 200
    assert "iPhone" in response.text
    assert "fas fa-mobile-alt" in response.text
    mock_api.assert_called_once()

def test_search_htmx_empty(client):
    response = client.post("/htmx/search/products", data={"q": ""})
    assert response.status_code == 200
    assert "Enter a search term" in response.text
```

### Service Testing

```python
def test_search_service():
    result = SearchService.search_products("iphone")
    assert result["total"] > 0
    assert all("iphone" in p["name"].lower() for p in result["results"])

def test_category_filter():
    result = SearchService.search_products("pro", category="smartphone")
    assert all(p["category"] == "smartphone" for p in result["results"])
```

## 🚀 Future API Extensions

### Planned Enhancements

1. **Authentication**: JWT-based authentication para API access
2. **Pagination**: Cursor-based pagination para large result sets  
3. **Sorting**: Múltiples opciones de ordenamiento (price, name, relevance)
4. **Advanced Filtering**: Filtros avanzados (price range, availability, etc.)
5. **Full-text Search**: Integración con Elasticsearch para mejor búsqueda
6. **Rate Limiting**: API rate limiting y throttling
7. **API Versioning**: Estrategia de versionado para backward compatibility

### Performance Optimizations

1. **Caching**: Redis caching para búsquedas frecuentes
2. **Database**: Reemplazar demo data con queries reales de base de datos
3. **Indexing**: Índices de base de datos para búsqueda rápida
4. **Compression**: Compresión de respuestas para large result sets
5. **CDN**: Entrega de static assets via CDN

Esta arquitectura asegura que los API endpoints sean el punto central de la lógica de negocio, mientras que los endpoints HTMX se mantienen como una capa de presentación pura que consume los APIs internamente.