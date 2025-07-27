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

## 🔐 Módulo Autenticación

### Epic: Autenticación y Control de Acceso
*Como administrador del sistema, necesito controlar quién puede acceder al sistema y qué puede hacer cada usuario para mantener la seguridad y organización del negocio.*

#### 📝 Historia de Usuario #18: Limpiar Base de Código
**Como** desarrollador del sistema  
**Quiero** eliminar todo el código de ejemplo y datos dummy  
**Para** tener una base limpia para implementar las funcionalidades reales

**Criterios de Aceptación:**
- [ ] Se eliminan todas las APIs de búsqueda de productos de ejemplo
- [ ] Se eliminan los datos DEMO_PRODUCTS del SearchService
- [ ] Se eliminan los schemas de SearchResponse y CategoryResponse
- [ ] Se eliminan las rutas web de búsqueda HTMX
- [ ] Se mantiene la estructura base: main.py, config.py, database.py, dependencies.py
- [ ] Se mantiene el template base.html como foundation para layouts
- [ ] El servidor FastAPI arranca sin errores después de la limpieza
- [ ] No quedan referencias a funcionalidades de ejemplo en el código

**Definición de Terminado:**
- Código de ejemplo completamente removido
- Servidor funciona sin errores
- Base limpia lista para nuevas funcionalidades
- Arquitectura de carpetas intacta

---

#### 📝 Historia de Usuario #19: Login en Página Principal
**Como** María (administradora) o Carlos (técnico)  
**Quiero** ver un formulario de login al entrar a la página principal  
**Para** poder autenticarme y acceder al sistema de manera segura

**Criterios de Aceptación:**
- [ ] Al acceder a la URL raíz ("/") aparece un formulario de login
- [ ] El formulario tiene campos para email/usuario y contraseña
- [ ] Los campos tienen validación visual (requeridos)
- [ ] Hay un botón "Iniciar Sesión" para enviar el formulario
- [ ] El diseño es responsive y funciona en dispositivos móviles
- [ ] Se muestra el logo/nombre de TechStore en la página
- [ ] Si ya hay una sesión activa, redirige directamente al dashboard

---

#### 📝 Historia de Usuario #20: Sistema de Autenticación
**Como** usuario del sistema  
**Quiero** que mis credenciales sean validadas correctamente  
**Para** acceder solo con permisos válidos y mantener mi sesión segura

**Criterios de Aceptación:**
- [ ] El sistema valida email y contraseña contra la base de datos
- [ ] Las contraseñas se almacenan encriptadas (no en texto plano)
- [ ] Se genera una sesión/token válido tras login exitoso
- [ ] Se muestra mensaje de error claro si las credenciales son incorrectas
- [ ] Las sesiones expiran después de un tiempo determinado
- [ ] Se previenen ataques de fuerza bruta (rate limiting)
- [ ] Logout invalida la sesión/token correctamente

---

#### 📝 Historia de Usuario #21: Panel de Administración
**Como** María (administradora)  
**Quiero** acceder a un panel de administración exclusivo  
**Para** gestionar usuarios y configuraciones del sistema

**Criterios de Aceptación:**
- [ ] Solo usuarios con rol "admin" pueden acceder al panel
- [ ] El panel está disponible en una ruta protegida (/admin)
- [ ] Si un usuario no-admin intenta acceder, se muestra error 403
- [ ] El panel tiene navegación hacia gestión de usuarios y roles
- [ ] Se muestra información del usuario logueado (nombre, rol)
- [ ] Hay opción para regresar al dashboard principal
- [ ] El diseño es consistente con el resto del sistema

---

#### 📝 Historia de Usuario #22: Gestión de Roles
**Como** María (administradora)  
**Quiero** crear y gestionar roles de usuario  
**Para** controlar qué permisos tiene cada tipo de usuario

**Criterios de Aceptación:**
- [ ] Puedo ver una lista de roles existentes (admin, user)
- [ ] Puedo crear nuevos roles con nombre y descripción
- [ ] Puedo editar roles existentes (nombre y descripción)
- [ ] No puedo eliminar roles que tienen usuarios asignados
- [ ] Cada rol muestra cuántos usuarios lo tienen asignado
- [ ] Los roles "admin" y "user" vienen pre-configurados en el sistema
- [ ] Solo administradores pueden gestionar roles

---

#### 📝 Historia de Usuario #23: Gestión de Usuarios
**Como** María (administradora)  
**Quiero** crear y gestionar usuarios del sistema  
**Para** controlar quién puede acceder y con qué permisos

**Criterios de Aceptación:**
- [ ] Puedo crear nuevos usuarios con: nombre, email, contraseña, rol
- [ ] Puedo ver lista de todos los usuarios con su información básica
- [ ] Puedo editar información de usuarios existentes
- [ ] Puedo cambiar el rol asignado a un usuario
- [ ] Puedo desactivar usuarios (sin eliminarlos)
- [ ] No puedo eliminar mi propio usuario administrador
- [ ] Las contraseñas se generan de forma segura
- [ ] Se valida que los emails sean únicos en el sistema

---

#### 📝 Historia de Usuario #24: Control de Acceso por Rol
**Como** usuario del sistema  
**Quiero** que el sistema restrinja mi acceso según mi rol  
**Para** mantener la seguridad y organización

**Criterios de Aceptación:**
- [ ] Usuarios con rol "admin" pueden acceder a todo el sistema
- [ ] Usuarios con rol "user" no pueden acceder al panel de administración
- [ ] Se verifica el rol en cada request a rutas protegidas
- [ ] Se muestran mensajes claros cuando no hay permisos
- [ ] El menú de navegación se adapta según el rol del usuario
- [ ] Los usuarios no pueden cambiar su propio rol
- [ ] Las restricciones funcionan tanto en API como en web interface

---

#### 📝 Historia de Usuario #25: Dashboard Personalizado
**Como** usuario logueado  
**Quiero** ver un dashboard adaptado a mi rol  
**Para** acceder rápidamente a las funciones que puedo usar

**Criterios de Aceptación:**
- [ ] Dashboard muestra bienvenida personalizada con nombre del usuario
- [ ] Administradores ven acceso al Panel de Administración
- [ ] Usuarios comunes NO ven el acceso al Panel de Administración
- [ ] Se muestra el rol actual del usuario claramente
- [ ] Hay botón de Logout visible en el dashboard
- [ ] El dashboard es la página por defecto después del login
- [ ] Se prepara estructura para agregar módulos futuros (placeholders)

---

#### 📝 Historia de Usuario #26: Logout Seguro
**Como** usuario logueado  
**Quiero** cerrar sesión de forma segura  
**Para** proteger mi cuenta cuando termino de usar el sistema

**Criterios de Aceptación:**
- [ ] Hay botón/enlace de "Cerrar Sesión" visible en dashboard
- [ ] Al hacer logout se invalida la sesión/token inmediatamente
- [ ] Después del logout redirije a la página de login
- [ ] No se puede acceder a páginas protegidas después del logout
- [ ] Se muestra confirmación de que la sesión se cerró correctamente
- [ ] El logout funciona desde cualquier página del sistema
- [ ] Se limpia cualquier información de sesión del navegador

---

## 📊 Métricas de Historias de Usuario

### Priorización para MVP
**PRIORIDAD MÁXIMA (Sprint 0 - Prerequisito):**
- Historia #18 (Limpiar base de código)
- Historias #19-#26 (Sistema de autenticación completo)

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