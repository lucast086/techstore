# 🚀 Plan de Aceleración TechStore - MVP

## Contexto
Este documento describe el plan para acelerar el desarrollo del MVP de TechStore, enfocándose en implementar el sistema de permisos básico y realizar el primer deploy antes de continuar con las épicas de negocio.

**Fecha de creación**: 2025-07-29
**Estado del proyecto**: Autenticación completa, sin deploy en producción

## Estado Actual del Proyecto

### ✅ Completado
- **Autenticación completa**: JWT, login, roles básicos (admin/user)
- **Control de acceso web**: `require_web_role` funcionando en rutas HTMX
- **Usuario admin existente**: `admin@techstore.com` / `Admin123!`
- **Templates con verificación de roles**: Menú adaptativo según rol
- **Base de código limpia**: Stories #18-26 completadas

### ❌ Pendiente
- Deploy en producción
- Módulos de negocio (Customers, Products, Sales)
- Gestión de roles desde UI (futuro)

## Decisiones Técnicas Clave

1. **NO implementar middleware API de roles ahora**
   - La API solo es accedida por HTMX (con cookies)
   - Las rutas web ya tienen control de acceso
   - No hay API pública expuesta

2. **Deploy temprano en Railway**
   - Evitar "big bang" deployment
   - CI/CD activo desde el inicio
   - Feedback inmediato de producción

3. **Roles simples para MVP**
   - Solo admin/user por ahora
   - Sin permisos granulares
   - Gestión de roles será implementada en Story #22

---

## 📋 SPRINT 0: Deploy Inicial a Railway (2-3 horas)

### Objetivo
Tener la aplicación funcionando en producción antes de desarrollar features de negocio.

### Paso 1: Configurar Railway (30 min)
**Responsable**: DevOps Agent
1. Crear cuenta en Railway (si no existe)
2. Crear nuevo proyecto en Railway
3. Conectar repositorio GitHub (rama `main`)
4. Railway detectará automáticamente que es un proyecto Python

### Paso 2: Configurar Base de Datos PostgreSQL (20 min)
1. En Railway dashboard: Add Service → Database → PostgreSQL
2. Railway proveerá automáticamente `DATABASE_URL`
3. Anotar la URL de conexión para verificación

### Paso 3: Configurar Variables de Entorno (20 min)
En Railway Settings → Variables, agregar:
```env
JWT_SECRET_KEY=<generar-clave-segura-aqui>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8
JWT_REFRESH_EXPIRATION_DAYS=30
BCRYPT_ROUNDS=12
SECRET_KEY=<generar-otra-clave-segura>
ENVIRONMENT=production
```

### Paso 4: Verificar Configuración de Deploy (10 min)
Verificar que existan:
- `Procfile` o `railway.json` (para comandos de inicio)
- `requirements.txt` o `pyproject.toml` (Railway soporta Poetry)

Si no existe `Procfile`, crearlo:
```
web: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
```

### Paso 5: Deploy Inicial (20 min)
1. Push a rama `main`:
   ```bash
   git push origin main
   ```
2. Railway iniciará el deploy automático
3. Monitorear logs en Railway dashboard

### Paso 6: Ejecutar Migraciones en Producción (20 min)
**Opción A - Railway CLI**:
```bash
railway run poetry run alembic upgrade head
```

**Opción B - Railway Console**:
- Proyecto → Settings → Deploy → Run Command
- Ejecutar: `poetry run alembic upgrade head`

### Paso 7: Crear Usuario Admin en Producción (10 min)
```bash
railway run poetry run python scripts/seed_admin.py
```

### Paso 8: Verificación Final (20 min)
1. Acceder a la URL provista por Railway
2. Probar login con credenciales admin
3. Verificar acceso al panel de administración
4. Verificar logout
5. Confirmar operatividad completa

---

## 📋 SPRINT 1: Épicas Core del Negocio (5-7 días)

### Epic 1: Customer Management (2 días)
**Responsable**: Full-Stack Agent

**Stories en orden**:
1. STORY-028: Customer Model
2. STORY-029: Customer Registration
3. STORY-030: Customer Search
4. STORY-031: Customer Profile
5. STORY-032: Customer Account Balance

**Workflow**:
```bash
./scripts/version.sh feature start customer-management
# Desarrollo con TDD
./scripts/version.sh feature finish customer-management
```

### Epic 2: Product Management (1.5 días)
**Responsable**: Backend Dev Agent

**Features**:
- Product Model & Categories
- Product CRUD
- Product Search & Filters

### Epic 3: Sales Management (1.5 días)
**Responsable**: Full-Stack Agent

**Features core**:
- Sales Model
- Create Sale with Products
- Integration with Customer Balance
- Basic Sales Dashboard

---

## 🔄 Proceso de Desarrollo Continuo

### Para cada feature:
1. **Crear branch**: `./scripts/version.sh feature start [nombre]`
2. **Desarrollar con TDD** según `docs/feature-implementation-guide.md`
3. **Commits frecuentes** con mensajes descriptivos
4. **Push regular** para ver cambios en staging
5. **Finalizar feature**: `./scripts/version.sh feature finish [nombre]`
6. **Deploy automático** cuando se mergea a main

### Cambios en producción serán mínimos:
- **Nuevas tablas**: `railway run alembic upgrade head`
- **Variables**: Ya configuradas, no cambian
- **Código**: Deploy automático con git push
- **Sin downtime**: Railway maneja zero-downtime deploys

---

## 📊 Timeline Estimado

| Sprint | Duración | Entregables |
|--------|----------|-------------|
| Sprint 0 | 2-3 horas | App en producción con auth |
| Sprint 1 - Epic 1 | 2 días | Customer Management completo |
| Sprint 1 - Epic 2 | 1.5 días | Product Management completo |
| Sprint 1 - Epic 3 | 1.5 días | Sales básico funcional |
| **Total MVP** | **~1 semana** | **MVP funcional en producción** |

---

## 🎯 Beneficios del Plan

1. **Producción desde día 1**: Feedback inmediato del cliente
2. **Sin "integration hell"**: Deploys incrementales continuos
3. **CI/CD activo**: Cada feature se prueba en producción real
4. **Detección temprana**: Problemas de producción se ven inmediato
5. **Simplicidad**: Sin configuración adicional post-Sprint 0

---

## 📝 Notas Importantes

- El sistema de autorización actual es suficiente para el MVP
- No necesitamos API middleware hasta que expongamos API pública
- Los roles adicionales se agregarán vía UI (Story #22)
- Cada deploy es automático al mergear a main
- Railway maneja SSL, dominios y escalamiento automáticamente

---

## 🚀 Siguiente Paso

Ejecutar Sprint 0 con el DevOps Agent para configurar Railway y hacer el primer deploy.

```
*agent devops
```
