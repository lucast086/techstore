# TechStore - Historias de Usuario

## 👤 Personas

### 🏪 **María (Administradora del Taller)**
- Dueña de un taller de reparación de celulares
- 45 años, maneja el negocio desde hace 10 años
- Conocimientos básicos de computación
- Necesita simplicidad y eficiencia

### 🔧 **Carlos (Técnico)**
- Técnico en reparación de dispositivos
- 28 años, 5 años de experiencia
- Maneja herramientas digitales básicas
- Se enfoca en reparaciones, no en administración

### 📱 **Ana (Cliente)**
- Profesional que usa mucho su celular
- 32 años, busca rapidez y transparencia
- Quiere estar informada del estado de su reparación
- Valora la comunicación clara

---

## 📦 Módulo Cliente

### Epic: Gestión de Clientes
*Como administradora del taller, necesito gestionar la información de mis clientes para tener un registro organizado y controlar las cuentas corrientes.*

#### 📝 Historia de Usuario #1: Registrar Cliente Nuevo
**Como** María (administradora)  
**Quiero** registrar un nuevo cliente en el sistema  
**Para** tener sus datos organizados y poder asignarle ventas y reparaciones

**Criterios de Aceptación:**
- [ ] Puedo ingresar nombre, teléfono, email y dirección
- [ ] El sistema valida que el email tenga formato correcto
- [ ] El sistema valida que el teléfono tenga formato válido
- [ ] No se permiten clientes duplicados (mismo email o teléfono)
- [ ] Al crear el cliente, su cuenta corriente inicia en $0
- [ ] El sistema me confirma que el cliente fue creado exitosamente

**Definición de Terminado:**
- Cliente se guarda en base de datos
- Se puede buscar al cliente después de creado
- Validaciones funcionan correctamente
- UI es intuitiva y responsive

---

#### 📝 Historia de Usuario #2: Buscar Cliente Existente  
**Como** María (administradora)  
**Quiero** buscar un cliente existente rápidamente  
**Para** acceder a su información y cuenta corriente

**Criterios de Aceptación:**
- [ ] Puedo buscar por nombre, teléfono o email
- [ ] La búsqueda funciona con texto parcial
- [ ] Los resultados se muestran en tiempo real mientras escribo
- [ ] Puedo ver nombre, teléfono y balance de cuenta corriente en los resultados
- [ ] Puedo seleccionar un cliente de los resultados

---

#### 📝 Historia de Usuario #3: Ver Cuenta Corriente
**Como** María (administradora)  
**Quiero** ver la cuenta corriente completa de un cliente  
**Para** saber cuánto debe o tiene a favor

**Criterios de Aceptación:**
- [ ] Veo el balance actual (positivo = debe, negativo = a favor)
- [ ] Veo historial de todos los movimientos (ventas, pagos, reparaciones)
- [ ] Cada movimiento muestra fecha, descripción y monto
- [ ] Los movimientos están ordenados por fecha (más reciente primero)
- [ ] Puedo distinguir visualmente entre débitos y créditos

---

## 💰 Módulo Venta

### Epic: Gestión de Ventas
*Como administradora, necesito registrar ventas de productos y servicios para generar ingresos y mantener actualizada la cuenta corriente del cliente.*

#### 📝 Historia de Usuario #4: Crear Venta de Productos
**Como** María (administradora)  
**Quiero** crear una venta seleccionando productos del inventario  
**Para** registrar la transacción y actualizar la cuenta del cliente

**Criterios de Aceptación:**
- [ ] Puedo seleccionar un cliente existente para la venta
- [ ] Puedo buscar y agregar productos desde el inventario
- [ ] Para cada producto puedo definir cantidad
- [ ] El sistema calcula automáticamente el subtotal por producto
- [ ] El sistema calcula el total general de la venta
- [ ] Puedo quitar productos de la venta antes de confirmar
- [ ] Al confirmar, la venta se registra en la cuenta corriente del cliente

---

#### 📝 Historia de Usuario #5: Venta Rápida (Sin Cliente)
**Como** María (administradora)  
**Quiero** realizar ventas rápidas sin asignar cliente específico  
**Para** atender ventas al mostrador de manera ágil

**Criterios de Aceptación:**
- [ ] Puedo crear una venta sin seleccionar cliente
- [ ] La venta se registra como "Cliente General" o "Mostrador"
- [ ] Sigue funcionando la selección de productos y cálculo de totales
- [ ] La venta se guarda en el sistema para reportes
- [ ] No afecta cuenta corriente (es venta directa)

---

#### 📝 Historia de Usuario #6: Ver Historial de Ventas
**Como** María (administradora)  
**Quiero** ver todas las ventas realizadas  
**Para** tener control de las transacciones del negocio

**Criterios de Aceptación:**
- [ ] Veo lista de todas las ventas ordenadas por fecha
- [ ] Para cada venta veo: cliente, total, fecha
- [ ] Puedo filtrar ventas por fecha (desde/hasta)
- [ ] Puedo filtrar ventas por cliente
- [ ] Puedo ver el detalle completo de una venta específica

---

## 🔧 Módulo Reparación

### Epic: Gestión de Órdenes de Trabajo
*Como administradora y técnico, necesitamos gestionar el ciclo completo de reparaciones desde la recepción hasta la entrega.*

#### 📝 Historia de Usuario #7: Recibir Reparación
**Como** María (administradora)  
**Quiero** registrar un equipo que llega para reparar  
**Para** crear una orden de trabajo y darle seguimiento

**Criterios de Aceptación:**
- [ ] Puedo seleccionar un cliente existente o crear uno nuevo
- [ ] Puedo ingresar descripción del equipo (marca, modelo, tipo)
- [ ] Puedo registrar el problema reportado por el cliente
- [ ] El sistema genera automáticamente un número de orden único
- [ ] La orden inicia en estado "Recibido"
- [ ] Puedo imprimir o mostrar el número de orden al cliente

---

#### 📝 Historia de Usuario #8: Diagnosticar Reparación
**Como** Carlos (técnico)  
**Quiero** registrar mi diagnóstico de la reparación  
**Para** definir qué trabajo realizar y cuánto cobrar

**Criterios de Aceptación:**
- [ ] Puedo ver órdenes en estado "Recibido"
- [ ] Puedo agregar descripción detallada del diagnóstico
- [ ] Puedo establecer precio de la reparación
- [ ] Puedo cambiar estado a "Diagnosticado"
- [ ] El precio se registra para facturar posteriormente

---

#### 📝 Historia de Usuario #9: Actualizar Estado de Reparación
**Como** Carlos (técnico)  
**Quiero** actualizar el estado de las reparaciones en proceso  
**Para** que la administración sepa el progreso

**Criterios de Aceptación:**
- [ ] Puedo cambiar estado entre: Recibido → Diagnosticado → En Reparación → Listo → Entregado
- [ ] Cada cambio de estado registra fecha y hora automáticamente
- [ ] Solo puedo avanzar al siguiente estado (no retroceder)
- [ ] Puedo agregar notas opcionales en cada cambio de estado

---

#### 📝 Historia de Usuario #10: Entregar Reparación
**Como** María (administradora)  
**Quiero** marcar una reparación como entregada  
**Para** finalizar la orden y cobrar al cliente

**Criterios de Aceptación:**
- [ ] Puedo ver órdenes en estado "Listo"
- [ ] Al marcar como "Entregado", el monto se registra en cuenta corriente del cliente
- [ ] La orden se marca como finalizada
- [ ] Puedo imprimir resumen de la reparación entregada

---

#### 📝 Historia de Usuario #11: Consultar Estado de Reparación
**Como** María (administradora)  
**Quiero** consultar rápidamente el estado de cualquier reparación  
**Para** informar a los clientes cuando pregunten

**Criterios de Aceptación:**
- [ ] Puedo buscar órdenes por número de orden
- [ ] Puedo buscar órdenes por cliente
- [ ] Veo estado actual, fecha de recepción y diagnóstico
- [ ] Veo historial completo de cambios de estado
- [ ] Puedo filtrar órdenes por estado

---

## 📦 Módulo Productos

### Epic: Gestión de Inventario
*Como administradora, necesito gestionar mi inventario de productos para poder venderlos y mantener control de stock.*

#### 📝 Historia de Usuario #12: Crear Producto
**Como** María (administradora)  
**Quiero** agregar un nuevo producto al inventario  
**Para** poder venderlo a los clientes

**Criterios de Aceptación:**
- [ ] Puedo ingresar nombre del producto
- [ ] Puedo agregar descripción detallada
- [ ] Puedo asignar una categoría existente
- [ ] Puedo definir precio de compra y precio de venta
- [ ] Puedo agregar código SKU único
- [ ] El producto aparece disponible para ventas inmediatamente

---

#### 📝 Historia de Usuario #13: Gestionar Categorías
**Como** María (administradora)  
**Quiero** organizar mis productos en categorías  
**Para** encontrarlos más fácilmente

**Criterios de Aceptación:**
- [ ] Puedo crear nuevas categorías
- [ ] Puedo editar nombres de categorías existentes
- [ ] Puedo ver cuántos productos tiene cada categoría
- [ ] No puedo eliminar categorías que tienen productos asignados

---

#### 📝 Historia de Usuario #14: Buscar y Editar Productos
**Como** María (administradora)  
**Quiero** buscar productos existentes y modificar su información  
**Para** mantener actualizado el inventario

**Criterios de Aceptación:**
- [ ] Puedo buscar productos por nombre o código SKU
- [ ] Puedo filtrar productos por categoría
- [ ] Puedo editar todos los campos del producto
- [ ] Puedo cambiar precios de compra y venta
- [ ] Los cambios se reflejan inmediatamente en ventas

---

#### 📝 Historia de Usuario #15: Ver Lista de Productos
**Como** María (administradora)  
**Quiero** ver todos mis productos organizadamente  
**Para** tener una visión general del inventario

**Criterios de Aceptación:**
- [ ] Veo lista de productos con nombre, categoría y precios
- [ ] Puedo ordenar por nombre, categoría o precio
- [ ] Puedo ver productos de una categoría específica
- [ ] Para cada producto veo margen de ganancia (venta - compra)

---

## 🔄 Historias Transversales

### Epic: Integración entre Módulos
*Como usuario del sistema, necesito que los módulos trabajen de manera integrada para tener una experiencia fluida.*

#### 📝 Historia de Usuario #16: Dashboard Principal
**Como** María (administradora)  
**Quiero** ver un resumen general del negocio al ingresar  
**Para** tener una vista rápida del estado actual

**Criterios de Aceptación:**
- [ ] Veo cantidad de órdenes por estado (Recibido, En Reparación, Listo)
- [ ] Veo total de ventas del día/semana
- [ ] Veo clientes con mayor deuda en cuenta corriente
- [ ] Veo órdenes que vencen pronto (fecha de entrega prometida)

---

#### 📝 Historia de Usuario #17: Navegación Intuitiva
**Como** cualquier usuario del sistema  
**Quiero** navegar fácilmente entre las diferentes secciones  
**Para** realizar mi trabajo de manera eficiente

**Criterios de Aceptación:**
- [ ] Menú principal siempre visible con acceso a los 4 módulos
- [ ] Breadcrumbs para saber dónde estoy
- [ ] Botones de acción principales siempre visibles
- [ ] Flujo lógico entre pantallas relacionadas
- [ ] Sistema responsive que funciona en tablet/móvil

---

## 📊 Métricas de Historias de Usuario

### Priorización para MVP
**Debe tener (Sprint 1-2):**
- Historias #1, #2, #3 (Cliente básico)
- Historia #12, #13 (Productos básicos)

**Debería tener (Sprint 3-4):**
- Historias #4, #7, #8, #9 (Venta y reparación core)
- Historia #17 (Navegación)

**Podría tener (Sprint 5-6):**
- Historias #5, #6, #10, #11 (Funcionalidades complementarias)
- Historias #14, #15, #16 (Mejoras de usabilidad)

### Criterios de Priorización
1. **Impacto en user journey core** (Alto/Medio/Bajo)
2. **Complejidad técnica** (Alta/Media/Baja)
3. **Dependencias** (Bloqueante/Independiente)
4. **Valor de negocio** (Crítico/Importante/Nice-to-have)