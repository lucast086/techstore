# Configuración del Sistema

## Índice
- [Introducción a la Configuración](#introducción-a-la-configuración)
- [Panel de Administración](#panel-de-administración)
- [Gestión de Usuarios](#gestión-de-usuarios)
- [Roles y Permisos](#roles-y-permisos)
- [Gestión de Categorías](#gestión-de-categorías)
- [Configuración de Gastos](#configuración-de-gastos)
- [Configuración General](#configuración-general)
- [Seguridad y Acceso](#seguridad-y-acceso)
- [Mantenimiento](#mantenimiento)

---

## Introducción a la Configuración

La **Configuración del Sistema** permite a los administradores personalizar TechStore según las necesidades específicas de su negocio.

### ¿Quién Puede Configurar?
- 👤 **Solo usuarios administradores** tienen acceso completo
- 🔒 **Empleados regulares** no ven opciones de configuración
- ⚠️ **Cambios requieren** permisos especiales del sistema

### Áreas de Configuración
- **Usuarios y roles** - Quién puede acceder y qué puede hacer
- **Categorías** - Organización de productos y gastos
- **Políticas de negocio** - Reglas y procedimientos
- **Seguridad** - Control de acceso y sesiones

### Acceso a Configuración
📋 **Navegación:**
- Panel de Administración → Configuración
- O menú usuario → Panel de Administración

---

## Panel de Administración

### Acceso al Panel
**Solo para administradores:**
1. **Haga clic** en su nombre de usuario (esquina superior derecha)
2. **Seleccione** "Panel de Administración"
3. **Acceda** al dashboard administrativo

```
[Captura de pantalla: Panel de administración con opciones de gestión de usuarios, categorías, configuración]
```

### Funciones Disponibles
**Módulos principales:**
- 👥 **Gestión de Usuarios** - Crear, editar, desactivar usuarios
- 🏷️ **Categorías** - Gestionar productos y gastos
- ⚙️ **Configuración** - Ajustes generales del sistema
- 📊 **Estadísticas** - Métricas de uso del sistema
- 🔍 **Auditoría** - Registros de actividad

### Navegación del Panel
**Interfaz administrativa:**
- **Menú lateral** con todas las opciones
- **Dashboard** con información resumida
- **Breadcrumbs** para ubicación actual
- **Enlaces rápidos** a funciones frecuentes

---

## Gestión de Usuarios

### Lista de Usuarios
📋 **Panel Admin → Usuarios**

**Información mostrada:**
- **Nombre** completo del usuario
- **Email** de acceso
- **Rol asignado** (Admin, Usuario)
- **Estado** (Activo, Inactivo)
- **Última conexión**
- **Acciones** disponibles

### Crear Nuevo Usuario
**Proceso:**
1. 📋 **Haga clic** en "Nuevo Usuario"
2. 📋 **Complete** información requerida:
   - **Nombre completo***
   - **Email*** (será su usuario de acceso)
   - **Contraseña temporal***
   - **Rol*** (Administrador o Usuario)
3. 📋 **Guarde** usuario
4. ✅ **Informe credenciales** al nuevo usuario

### Editar Usuario Existente
**Información modificable:**
- **Nombre** del usuario
- **Email** de acceso (con precaución)
- **Rol asignado**
- **Estado** (Activo/Inactivo)
- **Resetear contraseña**

### Desactivar Usuarios
**Para empleados que ya no trabajan:**
1. 📋 **Seleccione** usuario en lista
2. 📋 **Cambie estado** a "Inactivo"
3. ✅ **Usuario no podrá** acceder más al sistema
4. 📊 **Historial se mantiene** para auditoría

---

## Roles y Permisos

### Roles Predefinidos

#### 👑 **Administrador**
**Permisos completos:**
- ✅ **Gestión de usuarios** y roles
- ✅ **Configuración** del sistema
- ✅ **Todas las operaciones** comerciales
- ✅ **Reportes** y estadísticas completas
- ✅ **Panel de administración** completo

#### 👤 **Usuario**
**Permisos operativos:**
- ✅ **Operaciones diarias** (ventas, reparaciones, caja)
- ✅ **Gestión de clientes** y productos
- ✅ **Consultas** y reportes básicos
- ❌ **NO configuración** del sistema
- ❌ **NO gestión** de usuarios

### Asignación de Roles
**Al crear o editar usuario:**
1. **Seleccione rol** apropiado del menú desplegable
2. **Considere responsabilidades** del empleado
3. **Use "Usuario"** para mayoría de empleados
4. **Reserve "Administrador"** para supervisores

### Cambiar Roles
**Modificación de permisos:**
- **Puede cambiar** roles en cualquier momento
- **Cambios surten efecto** inmediatamente
- **Usuario debe** reiniciar sesión para ver cambios
- **Documente** cambios importantes

---

## Gestión de Categorías

### Categorías de Productos
📋 **Panel Admin → Categorías → Productos**

**Gestión completa:**
- **Ver** todas las categorías existentes
- **Crear** nuevas categorías según necesidades
- **Editar** nombres y descripciones
- **Organizar** en jerarquías si es necesario
- **Desactivar** categorías obsoletas

### Categorías de Gastos
📋 **Panel Admin → Categorías → Gastos**

**Organización de gastos:**
- **Servicios públicos** - Luz, agua, internet
- **Inventario** - Compras de productos
- **Mantenimiento** - Reparaciones, limpieza
- **Transporte** - Gasolina, envíos
- **Otros** - Gastos varios

### Crear Nueva Categoría
**Proceso:**
1. 📋 **Seleccione** tipo (Producto o Gasto)
2. 📋 **Complete** información:
   - **Nombre*** de la categoría
   - **Descripción** detallada
   - **Categoría padre** (si aplica)
3. 📋 **Guarde** categoría
4. ✅ **Disponible** inmediatamente para uso

### Mejores Prácticas
- **Use nombres** claros y específicos
- **Evite duplicar** categorías existentes
- **Organice jerárquicamente** cuando sea lógico
- **Revise periódicamente** uso y relevancia

---

## Configuración de Gastos

### Políticas de Gastos
**Configuración disponible:**
- **Categorías obligatorias** - Requiere categorización
- **Límites por usuario** - Montos máximos sin aprobación
- **Validaciones** - Campos requeridos para registro
- **Reportes automáticos** - Frecuencia de resúmenes

### Aprobaciones de Gastos
**Control de autorización:**
- **Gastos menores** - Aprobación automática
- **Gastos mayores** - Requieren autorización
- **Categorías sensibles** - Siempre requieren aprobación
- **Límites personalizados** por usuario o categoría

---

## Configuración General

### Información de la Tienda
**Datos básicos:**
- **Nombre comercial** de la tienda
- **Dirección** y datos de contacto
- **Información fiscal** (NIT, régimen)
- **Logo** para documentos (futuro)

### Configuración de Operaciones
**Políticas operativas:**
- **Horarios** de operación
- **Moneda** de trabajo (COP por defecto)
- **Formato** de números de orden
- **Términos** de garantías por defecto

### Configuración de Reportes
**Personalización de reportes:**
- **Período fiscal** de la empresa
- **Frecuencia** de reportes automáticos
- **Destinatarios** de reportes por email
- **Formatos** preferidos de exportación

---

## Seguridad y Acceso

### Políticas de Contraseñas
**Configuración actual:**
- **Longitud mínima** requerida
- **Complejidad** (mayúsculas, números, símbolos)
- **Expiración** automática de contraseñas
- **Historial** - no repetir contraseñas recientes

### Configuración de Sesiones
**Gestión de acceso:**
- **Tiempo de expiración** por inactividad
- **Sesiones simultáneas** permitidas por usuario
- **Cierre automático** por seguridad
- **Registro** de inicios de sesión

### Auditoría de Acciones
**Registro de actividad:**
- **Inicios de sesión** con fecha/hora
- **Acciones críticas** (cambios de precios, etc.)
- **Errores** y intentos fallidos
- **Cambios** en configuración

---

## Mantenimiento

### Respaldos del Sistema
**Política actual:**
- **Respaldos automáticos** diarios
- **Retención** de respaldos por 30 días
- **Verificación** de integridad semanal
- **Restauración** bajo demanda

### Actualizaciones
**Gestión de versiones:**
- **Actualizaciones automáticas** de seguridad
- **Notificaciones** de nuevas funcionalidades
- **Programación** de actualizaciones mayores
- **Pruebas** en ambiente controlado

### Monitoreo del Sistema
**Supervisión continua:**
- **Rendimiento** de la aplicación
- **Disponibilidad** del servicio
- **Capacidad** de almacenamiento
- **Alertas** por problemas críticos

### Soporte Técnico
**Canales de ayuda:**
- **Documentación** integrada en sistema
- **Contacto directo** con soporte
- **Registro** de tickets de soporte
- **Base de conocimiento** actualizada

---

## Mejores Prácticas de Administración

### ✅ Para Gestión de Usuarios
- **Cree usuarios** solo cuando sea necesario
- **Use rol "Usuario"** para mayoría de empleados
- **Revise permisos** periódicamente
- **Desactive usuarios** inactivos promptamente

### ✅ Para Configuración de Categorías
- **Mantenga estructura** lógica y simple
- **Evite** exceso de categorías que complique uso
- **Revise uso** de categorías regularmente
- **Capacite** empleados sobre categorización correcta

### ✅ Para Seguridad
- **Cambie contraseñas** predeterminadas inmediatamente
- **Revise accesos** de usuarios periódicamente
- **Monitoree** intentos de acceso fallidos
- **Mantenga** información de contacto actualizada

### ✅ Para Mantenimiento
- **Verifique respaldos** regulares del sistema
- **Pruebe restauración** de datos periódicamente
- **Mantenga** documentación de configuraciones
- **Planifique** actualizaciones con anticipación

---

## Contacto para Configuración Avanzada

### ¿Necesita Más Configuración?
**Para casos especiales contacte:**
- **Administrador** principal del sistema
- **Soporte técnico** para configuraciones complejas
- **Proveedor** para personalizaciones específicas

### Configuraciones No Disponibles en UI
**Requieren soporte técnico:**
- **Integración** con sistemas externos
- **Personalización** de documentos PDF
- **Configuración** de correo electrónico
- **Ajustes** avanzados de base de datos

---

*¿Necesita configurar algo específico? Consulte [Preguntas Frecuentes](11-preguntas-frecuentes.md) sección "Configuración" o contacte al administrador del sistema.*
