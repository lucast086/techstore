# Gestión de Productos

## Índice
- [Introducción al Módulo](#introducción-al-módulo)
- [Catálogo de Productos](#catálogo-de-productos)
- [Crear Nuevo Producto](#crear-nuevo-producto)
- [Buscar Productos](#buscar-productos)
- [Ver Detalles del Producto](#ver-detalles-del-producto)
- [Gestión de Categorías](#gestión-de-categorías)
- [Control de Inventario](#control-de-inventario)
- [Precios y Márgenes](#precios-y-márgenes)
- [Casos de Uso Comunes](#casos-de-uso-comunes)
- [Solución de Problemas](#solución-de-problemas)

---

## Introducción al Módulo

El **módulo de Productos** permite gestionar completamente el inventario de la tienda, desde el registro de nuevos productos hasta el control de precios y stock.

### ¿Qué Puedo Hacer?
- ✅ **Registrar** nuevos productos con información detallada
- ✅ **Organizar** productos por categorías
- ✅ **Controlar** precios de compra y venta
- ✅ **Buscar** productos rápidamente por nombre o código
- ✅ **Ver** detalles completos de cada producto
- ✅ **Gestionar** códigos SKU únicos

### Acceso al Módulo
**Desde la barra de navegación:**
1. Haga clic en **"Productos"** en el menú superior
2. Seleccione la opción deseada del menú desplegable

---

## Catálogo de Productos

### Acceder al Catálogo
📋 **Navegación:** Productos → Catálogo

### Información Mostrada
El catálogo muestra para cada producto:
- **Nombre** del producto
- **Categoría** asignada
- **Código SKU** único
- **Precio de venta** actual
- **Precio de compra**
- **Margen de ganancia** calculado automáticamente

```
[Captura de pantalla: Lista de productos con columnas de nombre, categoría, SKU, precio venta, precio compra, margen]
```

### Funciones Disponibles
**En cada producto puede:**
- 👁️ **Ver detalles** completos
- 🔍 **Usar en búsquedas** para ventas
- ✏️ **Editar información** (funcionalidad futura)

### Filtros y Ordenamiento
**Opciones de visualización:**
- **Filtrar por categoría** usando el menú desplegable
- **Ordenar por** nombre, precio o margen
- **Paginación** automática para catálogos grandes

---

## Crear Nuevo Producto

### Acceder al Formulario
📋 **Navegación:** Productos → Nuevo Producto

### Información Requerida

**Campos obligatorios (*):**
- **Nombre del producto*** - Descripción clara y específica
- **Precio de venta*** - Precio al público (solo números)
- **Precio de compra*** - Costo del producto para la tienda

**Campos opcionales:**
- **Descripción** - Información adicional del producto
- **Categoría** - Clasificación del producto
- **Código SKU** - Código único (se genera automáticamente si no se especifica)

```
[Captura de pantalla: Formulario de nuevo producto con campos de nombre, descripción, categoría, precios y SKU]
```

### Proceso de Registro
1. 📋 **Complete** el nombre descriptivo del producto
2. 📋 **Ingrese** los precios de compra y venta
3. 📋 **Seleccione** una categoría (opcional)
4. 📋 **Agregue** descripción adicional si es necesaria
5. 📋 **Haga clic** en "Guardar Producto"
6. ✅ **Confirme** que aparece mensaje de éxito

### Validaciones del Sistema
**El sistema verifica automáticamente:**
- ⚠️ **Precios válidos** - solo acepta números positivos
- ⚠️ **Precio de venta mayor** que precio de compra (recomendado)
- ⚠️ **Nombre único** - no permite productos con nombres idénticos
- ⚠️ **SKU único** - genera automáticamente si no se proporciona

### ✅ Buenas Prácticas
- **Use nombres descriptivos**: "iPhone 14 Pro 256GB Azul" mejor que "Celular"
- **Mantenga precios actualizados** según el mercado
- **Asigne categorías** para mejor organización
- **Include especificaciones** importantes en la descripción

### ❌ Errores Comunes
- Crear productos con nombres muy genéricos
- No verificar precios antes de guardar
- Olvidar asignar categoría apropiada
- No incluir información suficiente en descripción

---

## Buscar Productos

### Función de Búsqueda
La búsqueda de productos está disponible en:
- **Catálogo de productos** (filtrado)
- **Punto de venta** (selección para ventas)
- **Gestión de inventario**

### Campos de Búsqueda
**Puede buscar por:**
- **Nombre del producto** (completo o parcial)
- **Código SKU** (completo o parcial)
- **Descripción** (palabras clave)

### Cómo Buscar
1. 🔍 **Escriba** en el campo de búsqueda
2. 🔍 **Los resultados aparecen** automáticamente
3. 🔍 **Seleccione** el producto deseado

```
[Captura de pantalla: Campo de búsqueda de productos con resultados desplegables mostrando nombre, precio y SKU]
```

### Tips de Búsqueda Efectiva
- **Use palabras clave**: "iPhone", "Samsung", "funda"
- **Busque por marca**: encuentra todos los productos de esa marca
- **Use códigos parciales**: "IP14" puede encontrar "IP14-256-AZ"

---

## Ver Detalles del Producto

### Acceder a los Detalles
1. **Desde el catálogo**: Haga clic en el nombre del producto
2. **Desde búsquedas**: Seleccione "Ver detalles" en resultados

### Información Completa Mostrada
**Datos básicos:**
- Nombre completo del producto
- Descripción detallada
- Categoría asignada
- Código SKU único
- Fecha de creación en el sistema

**Información de precios:**
- **Precio de compra** actual
- **Precio de venta** al público
- **Margen de ganancia** (porcentaje y monto)
- **Historial de cambios** de precio (funcionalidad futura)

```
[Captura de pantalla: Página de detalles con información completa del producto, precios y estadísticas]
```

### Acciones Disponibles
**Desde la página de detalles puede:**
- ✏️ **Editar información** del producto (funcionalidad futura)
- 📊 **Ver estadísticas** de ventas (funcionalidad futura)
- 🛒 **Agregar a venta** directa desde POS

---

## Gestión de Categorías

### ¿Qué son las Categorías?
Las **categorías** ayudan a organizar los productos para:
- **Clasificación** lógica del inventario
- **Filtrado** rápido en búsquedas
- **Reportes** organizados por tipo de producto
- **Navegación** eficiente del catálogo

### Acceder a Categorías
📋 **Navegación:** Panel de Administración → Categorías
*(Solo disponible para administradores)*

### Categorías Predeterminadas
**El sistema incluye categorías básicas:**
- Teléfonos móviles
- Accesorios
- Fundas y protectores
- Componentes y repuestos
- Servicios

### Crear Nueva Categoría
**Proceso (solo administradores):**
1. 📋 **Acceda** al panel de administración
2. 📋 **Seleccione** "Categorías"
3. 📋 **Haga clic** en "Nueva Categoría"
4. 📋 **Complete** nombre y descripción
5. 📋 **Guarde** la nueva categoría

### Asignar Categoría a Producto
**Al crear o editar producto:**
1. 📋 **Seleccione** categoría del menú desplegable
2. 📋 **Si no existe** la categoría deseada, contacte al administrador
3. 📋 **Guarde** el producto con categoría asignada

---

## Control de Inventario

### Gestión de Stock Básica
**Estado actual del sistema:**
- ✅ **Registro** de productos disponibles
- ✅ **Información** de precios actualizada
- ✅ **Organización** por categorías
- 🔄 **Control de cantidades** (funcionalidad futura)

### Información Disponible
**Para cada producto puede ver:**
- Disponibilidad en el sistema
- Precios actuales
- Fecha de última modificación
- Categoría de clasificación

### Mejores Prácticas Actuales
**Para control manual de inventario:**
- **Mantenga** lista física paralela de cantidades
- **Actualice precios** regularmente en el sistema
- **Elimine** productos descontinuados (contacte administrador)
- **Revise** periódicamente información de productos

---

## Precios y Márgenes

### Gestión de Precios
**Información de precios incluye:**
- **Precio de compra**: Lo que cuesta obtener el producto
- **Precio de venta**: Lo que se cobra al cliente
- **Margen bruto**: Diferencia entre venta y compra

### Cálculo Automático de Márgenes
**El sistema calcula automáticamente:**
```
Margen en pesos = Precio de Venta - Precio de Compra
Margen en porcentaje = (Margen en pesos / Precio de Venta) × 100
```

**Ejemplo:**
- Precio de compra: $100.000
- Precio de venta: $150.000
- Margen: $50.000 (33.33%)

### Estrategias de Precios
**Recomendaciones generales:**
- **Margen mínimo**: 20-30% para cubrir gastos operativos
- **Margen típico**: 30-50% para productos estándar
- **Margen premium**: 50-100% para productos especializados

### Actualización de Precios
**Cuándo actualizar:**
- 📅 **Cambios de proveedor** en precios de compra
- 📅 **Fluctuaciones del mercado**
- 📅 **Estrategias comerciales** (ofertas, descuentos)
- 📅 **Revisión periódica** (mensual/trimestral)

---

## Casos de Uso Comunes

### Caso 1: Producto Nuevo en Inventario
**Situación**: Llega mercancía nueva a la tienda

**Proceso:**
1. 📋 **Registre** cada producto nuevo con información completa
2. 📋 **Calcule** precios de venta basados en márgenes deseados
3. 📋 **Asigne** categorías apropiadas
4. 📋 **Verifique** que información esté correcta
5. ✅ **Los productos** quedan disponibles para venta inmediatamente

### Caso 2: Actualización de Precios por Proveedor
**Situación**: Proveedor cambia precios de compra

**Proceso:**
1. 📋 **Identifique** productos afectados por categoría
2. 📋 **Actualice** precios de compra uno por uno
3. 📋 **Recalcule** precios de venta manteniendo margen deseado
4. 📋 **Verifique** que nuevos márgenes sean rentables

### Caso 3: Búsqueda Rápida para Venta
**Situación**: Cliente pregunta por producto específico

**Proceso:**
1. 🔍 **Use búsqueda** por nombre o características
2. 📊 **Verifique** disponibilidad y precio actual
3. 💰 **Informe** al cliente precio y características
4. 🛒 **Procese venta** si cliente acepta

### Caso 4: Organización de Catálogo
**Situación**: Catálogo desordenado con muchos productos

**Proceso:**
1. 📋 **Revise** productos sin categoría asignada
2. 📋 **Solicite** al administrador categorías adicionales si es necesario
3. 📋 **Asigne** categorías apropiadas a cada producto
4. 📋 **Verifique** que nombres sean descriptivos y únicos

---

## Solución de Problemas

### Problema: No Puede Crear Producto
**Posibles causas:**
- ❌ Nombre duplicado con producto existente
- ❌ Precios inválidos (negativos o no numéricos)
- ❌ Problemas de conectividad

**Soluciones:**
1. ✅ **Verifique** que el nombre sea único
2. ✅ **Confirme** que precios sean números positivos
3. ✅ **Revise** que precio de venta > precio de compra
4. ✅ **Recargue** la página e intente nuevamente

### Problema: Producto No Aparece en Búsquedas
**Posibles causas:**
- ❌ Nombre muy diferente al buscado
- ❌ Producto registrado con ortografía incorrecta
- ❌ Búsqueda con términos muy específicos

**Soluciones:**
1. ✅ **Busque** con términos más amplios
2. ✅ **Revise** ortografía en el catálogo
3. ✅ **Use** búsqueda por SKU si lo conoce
4. ✅ **Navegue** por categorías si es necesario

### Problema: Precios Incorrectos
**Posibles causas:**
- ❌ Error de digitación al crear producto
- ❌ Precios desactualizados
- ❌ Conversión incorrecta de moneda

**Soluciones:**
1. ✅ **Verifique** precios en detalles del producto
2. ✅ **Compare** con lista de precios física
3. ✅ **Contacte** administrador para correcciones
4. ✅ **Actualice** precios según información actual

### Problema: Categorías Insuficientes
**Situación**: Productos que no encajan en categorías existentes

**Soluciones:**
1. ✅ **Identifique** productos sin categoría apropiada
2. ✅ **Agrupe** productos similares que necesitan nueva categoría
3. ✅ **Contacte** administrador con propuesta de categorías
4. ✅ **Use** categoría temporal hasta obtener la específica

---

## Mejores Prácticas

### ✅ Para Registro de Productos
- **Use nombres descriptivos** que incluyan marca, modelo y características
- **Mantenga** información consistente en formato y estilo
- **Asigne categorías** apropiadas desde el registro inicial
- **Verifique** precios cuidadosamente antes de guardar

### ✅ Para Gestión de Precios
- **Revise precios** regularmente según mercado
- **Mantenga márgenes** rentables pero competitivos
- **Documente** cambios importantes de precios
- **Considere** estrategias por categoría de producto

### ✅ Para Organización del Catálogo
- **Use** nombres únicos y específicos
- **Mantenga** categorías organizadas y lógicas
- **Elimine** productos obsoletos (con ayuda del administrador)
- **Revise** periódicamente información desactualizada

---

## Próximos Pasos

Una vez dominada la gestión de productos:

📖 **[Proceso de Ventas](05-proceso-ventas.md)** - Aprenda a usar productos en el POS

📖 **[Gestión de Clientes](03-gestion-clientes.md)** - Conecte productos con clientes

📖 **[Control de Caja](07-control-caja.md)** - Gestione ingresos por ventas de productos

---

*¿Problemas con la gestión de productos? Consulte [Preguntas Frecuentes](11-preguntas-frecuentes.md) sección "Productos" para más ayuda.*
