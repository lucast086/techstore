# TechStore - TODO List

## 🎯 Estado Actual
- ✅ Documentación completa del proyecto
- ✅ Stack técnico definido (FastAPI + PostgreSQL + HTMX)
- ✅ Devcontainer configurado
- ✅ Git Flow script listo (version.sh)
- ✅ Dependencias definidas en pyproject.toml

---

## 📋 Próximos Pasos (Pre-Desarrollo)

### 🏗️ **Setup Inicial del Proyecto (Prioridad Alta)**

#### 1. Estructura Básica FastAPI
- [x] Crear `app/main.py` con FastAPI app inicial
- [x] Crear `app/__init__.py`
- [x] Crear `app/config.py` con settings y variables de entorno
- [x] Crear `app/database.py` con configuración SQLAlchemy
- [x] Crear `app/dependencies.py` con dependency injection básico

#### 2. Variables de Entorno
- [x] Crear `.env.template` con variables requeridas:
  ```
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/techstore_db
  SECRET_KEY=your-secret-key-here
  DEBUG=True
  ENVIRONMENT=development
  ```
- [ ] Crear `.env` real (no commitear)
- [x] Agregar `.env` a `.gitignore`

#### 3. Configuración Base de Datos
- [x] Inicializar Alembic: `alembic init alembic`
- [x] Configurar `alembic.ini` con DATABASE_URL
- [x] Crear `app/models/__init__.py`
- [ ] Crear `app/models/base.py` con base model class


#### 4. Testing Setup
- [x] Crear `tests/conftest.py` con configuración básica
- [x] Crear `tests/test_main.py` con test básico de health check
- [x] Verificar que `pytest` funciona

#### 5. Documentación Técnica
- [ ] Crear `README.md` con:
  - Descripción del proyecto
  - Instrucciones de setup local
  - Comandos básicos (run, test, migrate)
  - Estructura del proyecto
- [x] Actualizar `.gitignore` para FastAPI

---

## 🚀 **Desarrollo MVP - Fase 1**

### Módulo 1: Cliente (Semanas 1-2)

#### Sprint 1.1: Modelos y CRUD Básico
- [ ] **Historia #1**: Crear modelo Cliente
  - [ ] `app/models/cliente.py` con SQLAlchemy model
  - [ ] `app/schemas/cliente.py` con Pydantic schemas
  - [ ] `app/crud/cliente.py` con operaciones CRUD
  - [ ] Migración Alembic: `alembic revision --autogenerate -m "create cliente table"`
  - [ ] Tests unitarios para modelo y CRUD

#### Sprint 1.2: API Endpoints
- [ ] **Historia #1**: Registrar Cliente Nuevo
  - [ ] `app/api/v1/clientes.py` con endpoints FastAPI
  - [ ] POST `/api/v1/clientes/` - crear cliente
  - [ ] GET `/api/v1/clientes/{id}` - obtener cliente
  - [ ] Validaciones (email único, teléfono válido)
  - [ ] Tests de API endpoints

#### Sprint 1.3: Web Interface
- [ ] **Historia #2**: Buscar Cliente Existente
  - [ ] `app/templates/base.html` - template base
  - [ ] `app/templates/clientes/` - templates de cliente
  - [ ] `app/web/clientes.py` - web views con HTMX
  - [ ] GET `/clientes/` - lista de clientes
  - [ ] GET `/clientes/nuevo` - formulario crear cliente
  - [ ] POST `/clientes/` - procesar creación
  - [ ] Búsqueda en tiempo real con HTMX

#### Sprint 1.4: Cuenta Corriente
- [ ] **Historia #3**: Ver Cuenta Corriente
  - [ ] `app/models/cuenta_corriente.py` - modelo de movimientos
  - [ ] CRUD para movimientos de cuenta corriente
  - [ ] Vista de cuenta corriente del cliente
  - [ ] Cálculo de balance automático

### Módulo 2: Productos (Semanas 2-3)

#### Sprint 2.1: Gestión de Productos
- [ ] **Historia #12**: Crear Producto
  - [ ] `app/models/producto.py` y `app/models/categoria.py`
  - [ ] Schemas y CRUD para productos y categorías
  - [ ] Migración de base de datos
  - [ ] Tests unitarios

#### Sprint 2.2: Interface de Productos
- [ ] **Historia #13**: Gestionar Categorías
  - [ ] Templates para gestión de productos
  - [ ] CRUD completo via web interface
  - [ ] Búsqueda y filtros con HTMX
  - [ ] **Historia #14**: Buscar y Editar Productos

### Módulo 3: Ventas (Semanas 3-4)

#### Sprint 3.1: Sistema de Ventas
- [ ] **Historia #4**: Crear Venta de Productos
  - [ ] `app/models/venta.py` con items de venta
  - [ ] Lógica de negocio para ventas
  - [ ] Integración con cuenta corriente
  - [ ] Cálculos automáticos de totales

#### Sprint 3.2: Interface de Ventas
- [ ] Templates para crear ventas
- [ ] Selector de productos con HTMX
- [ ] Carrito de compras dinámico
- [ ] **Historia #5**: Venta Rápida (Sin Cliente)

### Módulo 4: Reparaciones (Semanas 4-5)

#### Sprint 4.1: Órdenes de Trabajo
- [ ] **Historia #7**: Recibir Reparación
  - [ ] `app/models/reparacion.py` con estados
  - [ ] Generación automática de número de orden
  - [ ] **Historia #8**: Diagnosticar Reparación

#### Sprint 4.2: Seguimiento de Reparaciones
- [ ] **Historia #9**: Actualizar Estado de Reparación
- [ ] **Historia #11**: Consultar Estado de Reparación
- [ ] Interface para técnicos y administradores
- [ ] **Historia #10**: Entregar Reparación

### Dashboard e Integración (Semana 5-6)

#### Sprint 5.1: Dashboard Principal
- [ ] **Historia #16**: Dashboard Principal
  - [ ] Métricas básicas del negocio
  - [ ] Órdenes pendientes y vencidas
  - [ ] Resumen de ventas
  - [ ] Clientes con mayor deuda

#### Sprint 5.2: Navigation y UX
- [ ] **Historia #17**: Navegación Intuitiva
  - [ ] Menú principal responsive
  - [ ] Breadcrumbs
  - [ ] Mobile-friendly interface
  - [ ] Testing en diferentes dispositivos

---

## 🚀 **Deploy y Testing (Semana 6)**

### Deploy en Railway
- [ ] Configurar variables de entorno en Railway
- [ ] Deploy automático desde main branch
- [ ] Configurar base de datos PostgreSQL
- [ ] Verificar que migraciones funcionen
- [ ] Health checks y monitoring básico

### Testing Integral
- [ ] Testing end-to-end de user journeys
- [ ] Performance testing básico
- [ ] Security testing básico
- [ ] Documentación de usuario final

### Preparación para Usuarios Piloto
- [ ] Crear usuario admin por defecto
- [ ] Datos de prueba básicos
- [ ] Guía de primeros pasos
- [ ] Contactar empresas piloto

---

## 📋 **Post-MVP Planning**

### Funcionalidades Futuras (Backlog)
- [ ] Sistema de notificaciones WhatsApp
- [ ] Portal del cliente
- [ ] Reportes avanzados
- [ ] Facturación fiscal (AFIP)
- [ ] Sistema multiusuario
- [ ] Mobile apps
- [ ] Integración con proveedores

### Mejoras Técnicas
- [ ] Implementar caching (Redis)
- [ ] Background jobs (Celery)
- [ ] Monitoring avanzado (Sentry)
- [ ] CI/CD pipeline completo
- [ ] Load testing
- [ ] Security audit

---

## 📝 **Notas de Desarrollo**

### Convenciones de Código
- Usar type hints en todo el código Python
- Seguir PEP 8 y configuración de ruff
- Tests unitarios para toda lógica de negocio
- Documentar APIs con docstrings
- Commits semánticos: `feat:`, `fix:`, `docs:`, etc.

### Git Flow
- `development` - rama principal de desarrollo
- `feature/nombre` - nuevas funcionalidades
- `release/version` - preparación de releases
- `hotfix/version` - fixes críticos
- `main` - solo código en producción

### Database
- Todas las migrations via Alembic
- Nunca hacer cambios manuales en producción
- Backup automático configurado
- Seeds para datos iniciales

---

## ✅ **Criterios de Done**

### Para cada Historia de Usuario:
- [ ] Código implementado y testeado
- [ ] Tests unitarios y de integración
- [ ] Documentación actualizada
- [ ] Code review completado
- [ ] Deploy en development funcionando

### Para cada Sprint:
- [ ] Demo funcionando end-to-end
- [ ] Performance aceptable (<2s response time)
- [ ] Sin bugs críticos conocidos
- [ ] Documentación técnica actualizada

### Para MVP completo:
- [ ] Todos los user journeys funcionando
- [ ] Deploy estable en Railway
- [ ] 3 empresas piloto onboarded
- [ ] Feedback inicial recopilado
- [ ] Plan para iteración siguiente

---

**📅 Timeline Objetivo: 6-8 semanas para MVP completo**

**🎯 Next Session: Comenzar con Setup Inicial del Proyecto**