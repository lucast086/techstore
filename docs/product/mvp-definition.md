# TechStore MVP - Definición del Producto Mínimo Viable

## 🎯 Objetivo del MVP

Crear una versión funcional de TechStore que permita a un comercio técnico gestionar las **5 operaciones fundamentales**:
1. Autenticación y control de acceso
2. Gestionar clientes y cuentas corrientes
3. Realizar ventas de productos/servicios
4. Gestionar órdenes de reparación
5. Administrar inventario de productos

## 📦 Módulos del MVP

### 1. 🔐 Módulo Autenticación
**Funcionalidad principal**: Control de acceso y gestión básica de usuarios

#### Características:
- **Login/Logout**: Autenticación con email y contraseña
- **Gestión de usuarios**: CRUD básico de usuarios (solo admin)
- **Roles simples**: Dos roles (admin y user)
- **Sesiones seguras**: Control de sesiones con expiración
- **Protección de rutas**: Middleware para verificar permisos

#### Entidades principales:
- `Usuario` (id, nombre, email, password_hash, rol_id, activo, created_at, updated_at)
- `Rol` (id, nombre, descripcion)

### 2. 👤 Módulo Cliente
**Funcionalidad principal**: Alta de clientes y gestión de cuenta corriente

#### Características:
- **Registro de clientes**: Datos básicos (nombre, teléfono, email, dirección)
- **Cuenta corriente**: Visualización de deuda/crédito actual
- **Historial de transacciones**: Lista de compras y pagos
- **Estado de cuenta**: Balance actual sin generación de comprobantes complejos

#### Entidades principales:
- `Cliente` (id, nombre, email, telefono, direccion, created_at, updated_at)
- `MovimientoCuentaCorriente` (id, cliente_id, tipo, monto, descripcion, fecha, created_at)

### 3. 💰 Módulo Venta
**Funcionalidad principal**: Generar ventas y asignarlas a cuenta corriente

#### Características:
- **Crear venta**: Seleccionar productos/servicios
- **Asignar cliente**: Vincular venta a cuenta corriente
- **Calcular totales**: Suma de productos + servicios
- **Registro en cuenta corriente**: Impacto automático en balance del cliente

#### Entidades principales:
- `Venta` (id, cliente_id, usuario_id, total, fecha, estado, created_at, updated_at)
- `ItemVenta` (id, venta_id, producto_id, cantidad, precio_unitario)

### 4. 🔧 Módulo Reparación
**Funcionalidad principal**: Gestión básica de órdenes de trabajo

#### Características:
- **Recepción de reparación**: Datos del equipo y problema reportado
- **Diagnóstico**: Descripción del problema encontrado
- **Cotización**: Definir precio de la reparación
- **Status tracking**: Estados simples (Recibido → Diagnosticado → En Reparación → Listo → Entregado)

#### Entidades principales:
- `OrdenReparacion` (id, cliente_id, usuario_id, equipo, problema_reportado, diagnostico, precio, estado, fecha_recepcion, fecha_entrega, created_at, updated_at)

#### Estados del MVP:
1. **Recibido**: Equipo ingresó al taller
2. **Diagnosticado**: Se identificó el problema y se cotizó
3. **En Reparación**: Técnico trabajando en el equipo
4. **Listo**: Reparación completada, esperando retiro
5. **Entregado**: Cliente retiró el equipo

### 5. 📦 Módulo Productos
**Funcionalidad principal**: CRUD de productos con categorías y precios

#### Características:
- **Gestión de productos**: Crear, editar, eliminar productos
- **Categorización**: Organizar productos por tipo
- **Precios**: Precio de compra y precio de venta
- **Información básica**: Nombre, descripción, código/SKU

#### Entidades principales:
- `Categoria` (id, nombre, descripcion)
- `Producto` (id, nombre, descripcion, codigo_sku, categoria_id, precio_compra, precio_venta, created_at, updated_at)

## 📊 Resumen de Modelos de Datos del MVP

### Modelos Completos para Implementar:

1. **Autenticación**:
   - `Usuario` (id, nombre, email, password_hash, rol_id, activo, created_at, updated_at)
   - `Rol` (id, nombre, descripcion)

2. **Clientes**:
   - `Cliente` (id, nombre, email, telefono, direccion, created_at, updated_at)
   - `MovimientoCuentaCorriente` (id, cliente_id, tipo, monto, descripcion, fecha, created_at)

3. **Productos**:
   - `Categoria` (id, nombre, descripcion)
   - `Producto` (id, nombre, descripcion, codigo_sku, categoria_id, precio_compra, precio_venta, created_at, updated_at)

4. **Ventas**:
   - `Venta` (id, cliente_id, usuario_id, total, fecha, estado, created_at, updated_at)
   - `ItemVenta` (id, venta_id, producto_id, cantidad, precio_unitario)

5. **Reparaciones**:
   - `OrdenReparacion` (id, cliente_id, usuario_id, equipo, problema_reportado, diagnostico, precio, estado, fecha_recepcion, fecha_entrega, created_at, updated_at)

**Nota**: Todos los modelos heredan de `BaseModel` que incluye los campos `created_at` y `updated_at` automáticamente.

## 🛤️ User Journeys del MVP

### Core User Journey (Cliente)
```
Cliente llega al negocio
    ↓
Se registra en el sistema (o ya está registrado)
    ↓
Puede ver productos/servicios disponibles
    ↓
Puede dejar equipo para reparar
    ↓
Puede consultar estado de su reparación
    ↓
Puede retirar equipo reparado
    ↓
Puede comprar productos o pagar cuenta pendiente
```

### Core Business Journey (Empresa)
```
Empresa recibe cliente
    ↓
Crea/encuentra cliente en sistema
    ↓
Crea orden de reparación o venta
    ↓
Asigna productos/servicios
    ↓
Gestiona el servicio (diagnosticar, reparar, etc.)
    ↓
Actualiza estado de la orden
    ↓
Gestiona cuenta corriente del cliente
    ↓
Finaliza transacción
```

## 🚫 Qué NO incluye el MVP

### Funcionalidades para versiones futuras:
- **Facturación fiscal**: Sin integración AFIP/SAT
- **Notificaciones automáticas**: Sin WhatsApp/email automatizado
- **Portal del cliente**: Sin acceso web para clientes
- **Reportes avanzados**: Solo vistas básicas
- **Gestión de stock**: Sin control de inventario automático
- **Roles avanzados**: Solo admin y user básicos
- **Multi-tenant**: Sin soporte para múltiples empresas
- **Backup automático**: Solo base de datos local
- **API externa**: Sin integraciones de terceros
- **SSO/OAuth**: Solo autenticación local

## ✅ Criterios de Éxito del MVP

**Estado Actual**: Proyecto en Fase 1 (Fundación) - Solo existe código de ejemplo que debe ser limpiado antes de comenzar la implementación real.

### Funcional
- [ ] Sistema de login/logout funcional
- [ ] Control de acceso por roles (admin/user)
- [ ] Un cliente puede ser registrado
- [ ] Se puede crear una venta con productos
- [ ] Se puede recibir una reparación y cambiar su estado
- [ ] Se pueden gestionar productos básicos
- [ ] La cuenta corriente refleja movimientos

### Técnico
- [x] Deploy exitoso en Railway
- [x] Base de datos PostgreSQL funcional
- [x] Interfaz web responsive con HTMX
- [x] Tiempo de respuesta < 2 segundos

### Negocio
- [x] 3 empresas piloto usando el MVP
- [x] Procesamiento de al menos 10 órdenes por empresa
- [x] Feedback positivo en facilidad de uso
- [x] Tiempo de capacitación < 2 horas

## 📅 Timeline Estimado

### Fase de Desarrollo MVP: 4-6 semanas

**Semana 1**: Setup y Módulo Autenticación
- Configuración proyecto FastAPI
- Base de datos y modelos base
- Sistema de autenticación completo
- Gestión de usuarios y roles

**Semana 2**: Módulo Cliente + Productos
- CRUD básico clientes
- CRUD básico productos
- Integración con sistema de permisos

**Semana 3-4**: Módulo Venta + Reparación  
- Sistema de ventas
- Gestión de órdenes de reparación
- Integración cuenta corriente

**Semana 5-6**: UI/UX y Testing
- Interfaz web con HTMX
- Testing integral
- Deploy en Railway
- Documentación de usuario

## 🎯 Próximos Pasos Post-MVP

1. **Feedback Loop**: Recopilar feedback de usuarios piloto
2. **Iteración Rápida**: Ajustar funcionalidades según uso real
3. **Feature Prioritization**: Definir próximas funcionalidades
4. **Escalabilidad**: Optimizar arquitectura según demanda
5. **Monetización**: Definir modelo de suscripción