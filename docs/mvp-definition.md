# TechStore MVP - Definición del Producto Mínimo Viable

## 🎯 Objetivo del MVP

Crear una versión funcional de TechStore que permita a un comercio técnico gestionar las **4 operaciones fundamentales**:
1. Gestionar clientes y cuentas corrientes
2. Realizar ventas de productos/servicios
3. Gestionar órdenes de reparación
4. Administrar inventario de productos

## 📦 Módulos del MVP

### 1. 👤 Módulo Cliente
**Funcionalidad principal**: Alta de clientes y gestión de cuenta corriente

#### Características:
- **Registro de clientes**: Datos básicos (nombre, teléfono, email, dirección)
- **Cuenta corriente**: Visualización de deuda/crédito actual
- **Historial de transacciones**: Lista de compras y pagos
- **Estado de cuenta**: Balance actual sin generación de comprobantes complejos

#### Entidades principales:
- `Cliente` (id, nombre, email, teléfono, dirección, fecha_creación)
- `MovimientoCuentaCorriente` (id, cliente_id, tipo, monto, descripción, fecha)

### 2. 💰 Módulo Venta
**Funcionalidad principal**: Generar ventas y asignarlas a cuenta corriente

#### Características:
- **Crear venta**: Seleccionar productos/servicios
- **Asignar cliente**: Vincular venta a cuenta corriente
- **Calcular totales**: Suma de productos + servicios
- **Registro en cuenta corriente**: Impacto automático en balance del cliente

#### Entidades principales:
- `Venta` (id, cliente_id, total, fecha, estado)
- `ItemVenta` (id, venta_id, producto_id, cantidad, precio_unitario)

### 3. 🔧 Módulo Reparación
**Funcionalidad principal**: Gestión básica de órdenes de trabajo

#### Características:
- **Recepción de reparación**: Datos del equipo y problema reportado
- **Diagnóstico**: Descripción del problema encontrado
- **Cotización**: Definir precio de la reparación
- **Status tracking**: Estados simples (Recibido → Diagnosticado → En Reparación → Listo → Entregado)

#### Entidades principales:
- `OrdenReparacion` (id, cliente_id, equipo, problema_reportado, diagnostico, precio, status, fecha_recepcion, fecha_entrega)

#### Estados del MVP:
1. **Recibido**: Equipo ingresó al taller
2. **Diagnosticado**: Se identificó el problema y se cotizó
3. **En Reparación**: Técnico trabajando en el equipo
4. **Listo**: Reparación completada, esperando retiro
5. **Entregado**: Cliente retiró el equipo

### 4. 📦 Módulo Productos
**Funcionalidad principal**: CRUD de productos con categorías y precios

#### Características:
- **Gestión de productos**: Crear, editar, eliminar productos
- **Categorización**: Organizar productos por tipo
- **Precios**: Precio de compra y precio de venta
- **Información básica**: Nombre, descripción, código/SKU

#### Entidades principales:
- `Categoria` (id, nombre, descripción)
- `Producto` (id, nombre, descripción, codigo_sku, categoria_id, precio_compra, precio_venta, fecha_creación)

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
- **Múltiples usuarios**: Un solo usuario administrador
- **Roles y permisos**: Sin sistema de roles
- **Backup automático**: Solo base de datos local
- **API externa**: Sin integraciones de terceros

## ✅ Criterios de Éxito del MVP

### Funcional
- [x] Un cliente puede ser registrado
- [x] Se puede crear una venta con productos
- [x] Se puede recibir una reparación y cambiar su estado
- [x] Se pueden gestionar productos básicos
- [x] La cuenta corriente refleja movimientos

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

**Semana 1-2**: Setup y Módulo Cliente + Productos
- Configuración proyecto FastAPI
- Base de datos y modelos
- CRUD básico clientes y productos

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