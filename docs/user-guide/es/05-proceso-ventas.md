# Proceso de Ventas

## Índice
- [Introducción al Sistema de Ventas](#introducción-al-sistema-de-ventas)
- [Punto de Venta (POS)](#punto-de-venta-pos)
- [Crear Nueva Venta](#crear-nueva-venta)
- [Selección de Productos](#selección-de-productos)
- [Gestión del Carrito](#gestión-del-carrito)
- [Proceso de Checkout](#proceso-de-checkout)
- [Métodos de Pago](#métodos-de-pago)
- [Recibos y Facturas](#recibos-y-facturas)
- [Historial de Ventas](#historial-de-ventas)
- [Casos de Uso Comunes](#casos-de-uso-comunes)
- [Solución de Problemas](#solución-de-problemas)

---

## Introducción al Sistema de Ventas

El **módulo de Ventas** es donde se procesan todas las transacciones comerciales, desde ventas simples hasta operaciones complejas con múltiples productos y formas de pago.

### ¿Qué Puedo Hacer?
- ✅ **Procesar ventas** en tiempo real con el POS integrado
- ✅ **Buscar productos** rápidamente durante la venta
- ✅ **Gestionar múltiples items** en un solo carrito
- ✅ **Asignar ventas** a clientes específicos
- ✅ **Procesar pagos** con diferentes métodos
- ✅ **Generar recibos** e imprimir facturas
- ✅ **Ver historial** completo de todas las ventas

### Requisitos Previos
**Antes de realizar ventas:**
- ⚠️ **Caja debe estar abierta** - verificar estado en dashboard
- ✅ **Productos registrados** en el sistema
- ✅ **Clientes registrados** (opcional, pero recomendado)

### Acceso al Módulo
**Desde la barra de navegación:**
1. Haga clic en **"Ventas"** en el menú superior
2. Seleccione la opción deseada del menú desplegable

---

## Punto de Venta (POS)

### Acceder al POS
📋 **Navegación:** Ventas → Punto de Venta

### Verificación de Estado
**Al ingresar, el sistema verifica:**
- ✅ **Estado de caja** - debe estar abierta para procesar ventas
- 🟢 **Indicador verde**: "Cash Register is Open - Sales can be processed"
- 🔴 **Indicador rojo**: Si caja está cerrada, debe abrirla primero

```
[Captura de pantalla: Interfaz POS con indicador de estado de caja, secciones de búsqueda de productos, carrito y resumen]
```

### Diseño de la Interfaz
**La pantalla POS se divide en tres secciones principales:**

1. **Panel izquierdo (Productos y Carrito)**:
   - Búsqueda de productos
   - Lista del carrito de compras

2. **Panel derecho (Cliente y Totales)**:
   - Selección/búsqueda de cliente
   - Resumen de totales
   - Botones de acción

3. **Área superior**:
   - Estado de la caja
   - Navegación rápida

---

## Crear Nueva Venta

### Flujo General de Venta
**Proceso completo paso a paso:**

1. **Verificar estado de caja**
2. **Buscar/seleccionar cliente** (opcional)
3. **Agregar productos** al carrito
4. **Revisar totales**
5. **Procesar pago**
6. **Generar recibo**

### Iniciar Nueva Venta
**El POS siempre está listo para nueva venta:**
- **Carrito vacío** al ingresar
- **No hay cliente seleccionado** por defecto
- **Totales en $0**
- **Listo para agregar productos**

---

## Selección de Productos

### Búsqueda de Productos
**Campo de búsqueda inteligente:**
- **Ubicación**: Panel superior izquierdo
- **Placeholder**: "Search by name, SKU, or barcode..."
- **Búsqueda en tiempo real** mientras escribe

```
[Captura de pantalla: Campo de búsqueda con resultados desplegables mostrando productos con nombre, precio y botón agregar]
```

### Criterios de Búsqueda
**Puede buscar por:**
- **Nombre del producto** (completo o parcial)
- **Código SKU**
- **Código de barras** (si está registrado)

### Resultados de Búsqueda
**Para cada producto mostrado:**
- **Nombre** completo del producto
- **Precio de venta** actual
- **Código SKU**
- **Botón "Add"** para agregar al carrito

### Agregar Producto al Carrito
**Proceso:**
1. 🔍 **Escriba** nombre o código del producto
2. 📋 **Seleccione** producto de los resultados
3. 📋 **Haga clic** en botón "Add"
4. ✅ **Producto se agrega** al carrito automáticamente

### Tips de Búsqueda Efectiva
- **Use palabras clave**: "iPhone", "Samsung", "funda"
- **Códigos parciales**: "IP14" encuentra productos relacionados
- **Búsqueda por marca**: encuentra todos los productos de esa marca

---

## Gestión del Carrito

### Visualización del Carrito
**Ubicación**: Panel izquierdo inferior
**Información mostrada por item:**
- **Nombre** del producto
- **Precio unitario**
- **Cantidad** (con controles + y -)
- **Subtotal** del item
- **Botón eliminar** (X)

```
[Captura de pantalla: Lista del carrito con productos, cantidades, precios y controles de edición]
```

### Modificar Cantidades
**Para cambiar cantidad de un producto:**
1. **Botón "+"**: Aumenta cantidad en 1
2. **Botón "-"**: Disminuye cantidad en 1
3. **Eliminación automática**: Si cantidad llega a 0, se elimina del carrito

### Eliminar Productos
**Para quitar producto del carrito:**
- **Haga clic** en botón "X" rojo
- **Producto se elimina** inmediatamente
- **Totales se recalculan** automáticamente

### Carrito Vacío
**Cuando no hay productos:**
- **Mensaje**: "No items in cart"
- **Totales en $0**
- **Checkout deshabilitado**

---

## Proceso de Checkout

### Selección de Cliente
**Panel superior derecho:**
- **Campo de búsqueda** de cliente
- **Opción "General Customer"** por defecto
- **Resultados en tiempo real** al escribir

```
[Captura de pantalla: Sección de cliente con búsqueda y información del cliente seleccionado]
```

**Buscar cliente existente:**
1. 🔍 **Escriba** nombre o teléfono en campo de búsqueda
2. 📋 **Seleccione** cliente de los resultados
3. ✅ **Cliente se asigna** a la venta

**Cliente General (venta sin asignar):**
- **No requiere** selección de cliente
- **Venta directa** sin afectar cuenta corriente
- **Ideal para** ventas rápidas al mostrador

### Resumen de Totales
**Panel derecho inferior muestra:**
- **Subtotal**: Suma de todos los productos
- **Total**: Monto final a pagar (actualmente igual al subtotal)
- **Totales actualizados** automáticamente

### Botón Checkout
**Ubicación**: Panel derecho, botón azul grande
**Estados:**
- **Habilitado**: Cuando hay productos en carrito
- **Deshabilitado**: Cuando carrito está vacío
- **Texto**: "Checkout ($XX.XXX)"

---

## Métodos de Pago

### Pantalla de Pago
**Al hacer clic en Checkout se abre modal de pago:**

```
[Captura de pantalla: Modal de pago con opciones de método de pago y campos de monto]
```

### Métodos Disponibles
**Opciones de pago:**
- **Efectivo** - Pago en dinero físico
- **Transferencia** - Pago por transferencia bancaria
- **Tarjeta** - Pago con tarjeta de débito/crédito
- **Cuenta Corriente** - Agregar a deuda del cliente

### Proceso de Pago
1. **Seleccione** método de pago deseado
2. **Confirme** el monto (aparece automáticamente)
3. **Agregue observaciones** si es necesario
4. **Haga clic** en "Procesar Pago"
5. ✅ **Sistema procesa** y confirma venta

### Pago con Cuenta Corriente
**Características especiales:**
- **Solo disponible** si hay cliente asignado
- **Agrega monto** al saldo debido del cliente
- **No requiere** pago inmediato
- **Actualiza** cuenta corriente automáticamente

### Validaciones de Pago
**El sistema verifica:**
- ⚠️ **Monto positivo** y válido
- ⚠️ **Método seleccionado**
- ⚠️ **Cliente asignado** (si es pago a cuenta corriente)

---

## Recibos y Facturas

### Generación Automática
**Después del pago exitoso:**
- ✅ **Recibo generado** automáticamente
- ✅ **Número único** asignado a la venta
- ✅ **Información completa** registrada

### Información en Recibos
**Contenido del recibo:**
- **Datos de la tienda** (nombre, contacto)
- **Número de venta** único
- **Fecha y hora** de la transacción
- **Cliente** (si fue asignado)
- **Detalle de productos** con cantidades y precios
- **Totales** y método de pago
- **Empleado** que procesó la venta

### Acceso a Recibos
**Formas de obtener recibos:**
1. **Vista inmediata** después del pago
2. **Historial de ventas** → Ver detalles → Ver recibo
3. **Descarga PDF** para impresión
4. **Reimpresión** cuando sea necesario

### Facturación
**Para facturas oficiales:**
- **Funcionalidad disponible** en detalles de venta
- **Descarga PDF** con formato de factura
- **Información fiscal** completa
- **Válida para** efectos tributarios

---

## Historial de Ventas

### Acceder al Historial
📋 **Navegación:** Ventas → Historial de Ventas

### Información Mostrada
**Lista completa de ventas:**
- **Número de venta** único
- **Fecha y hora** de la transacción
- **Cliente** (nombre o "General")
- **Total** de la venta
- **Método de pago** utilizado
- **Estado** de la venta
- **Acciones** disponibles

```
[Captura de pantalla: Lista de historial de ventas con columnas de información y botones de acción]
```

### Filtros y Búsqueda
**Opciones de filtrado:**
- **Por fecha** (desde/hasta)
- **Por cliente** específico
- **Por método de pago**
- **Por monto** (rangos)

### Acciones por Venta
**Para cada venta puede:**
- 👁️ **Ver detalles** completos
- 🧾 **Ver recibo** generado
- 📄 **Descargar factura** en PDF
- ❌ **Anular venta** (con permisos)

### Ver Detalles de Venta
**Información completa incluye:**
- **Datos del cliente** y contacto
- **Lista detallada** de productos vendidos
- **Cálculos de totales** paso a paso
- **Información del pago** y método usado
- **Usuario** que procesó la venta
- **Timestamps** completos

---

## Casos de Uso Comunes

### Caso 1: Venta Simple al Mostrador
**Situación**: Cliente compra un producto, paga efectivo y se va

**Proceso:**
1. 📋 **No asigne cliente** (use "General Customer")
2. 🔍 **Busque y agregue** producto al carrito
3. 💰 **Seleccione "Efectivo"** como método de pago
4. 🧾 **Procese pago** y entregue recibo
5. ✅ **Venta completada** en menos de 2 minutos

### Caso 2: Venta a Cliente con Cuenta Corriente
**Situación**: Cliente habitual que "anota" sus compras

**Proceso:**
1. 🔍 **Busque y seleccione** al cliente
2. 🛒 **Agregue productos** al carrito
3. 💳 **Seleccione "Cuenta Corriente"** como pago
4. ✅ **Sistema actualiza** automáticamente deuda del cliente
5. 📊 **Cliente ve** nuevo balance en su cuenta

### Caso 3: Venta de Múltiples Productos
**Situación**: Cliente compra varios artículos diferentes

**Proceso:**
1. 🔍 **Busque primer producto** y agréguelo
2. 🔍 **Busque segundo producto** y agréguelo
3. 🔍 **Continue agregando** todos los productos
4. 📊 **Revise totales** en el carrito
5. 💰 **Procese pago** por el total completo

### Caso 4: Corrección Durante Venta
**Situación**: Se agregó producto equivocado o cantidad incorrecta

**Proceso:**
1. ❌ **Elimine producto** incorrecto con botón X
2. ➕➖ **Ajuste cantidades** con botones + y -
3. 🔍 **Agregue productos** correctos si es necesario
4. 📊 **Verifique totales** actualizados
5. 💰 **Continue con checkout** normal

### Caso 5: Consulta de Venta Anterior
**Situación**: Cliente pregunta por compra realizada días atrás

**Proceso:**
1. 📋 **Vaya a** Historial de Ventas
2. 🔍 **Filtre por cliente** específico
3. 📅 **Ajuste rango de fechas** si es necesario
4. 👁️ **Vea detalles** de la venta específica
5. 🧾 **Muestre información** al cliente o reimprima recibo

---

## Solución de Problemas

### Problema: No Puedo Procesar Ventas
**Posibles causas:**
- ❌ Caja cerrada o no abierta
- ❌ Sin productos en carrito
- ❌ Problemas de conectividad

**Soluciones:**
1. ✅ **Verifique** estado de caja (debe estar abierta)
2. ✅ **Agregue productos** al carrito antes de checkout
3. ✅ **Recargue página** si hay problemas técnicos
4. ✅ **Contacte administrador** si caja no se puede abrir

### Problema: Producto No Aparece en Búsqueda
**Posibles causas:**
- ❌ Producto no registrado en sistema
- ❌ Error en ortografía de búsqueda
- ❌ Producto con nombre muy diferente

**Soluciones:**
1. ✅ **Busque** con diferentes términos
2. ✅ **Revise** catálogo de productos
3. ✅ **Registre producto** si no existe
4. ✅ **Use código SKU** si lo conoce

### Problema: Error en Método de Pago
**Posibles causas:**
- ❌ Cliente no asignado para cuenta corriente
- ❌ Monto inválido
- ❌ Método no seleccionado

**Soluciones:**
1. ✅ **Seleccione cliente** antes de usar cuenta corriente
2. ✅ **Verifique** que monto sea positivo
3. ✅ **Seleccione método** antes de procesar
4. ✅ **Intente método alternativo** si uno falla

### Problema: Recibo No Se Genera
**Posibles causas:**
- ❌ Problemas de impresora (navegador)
- ❌ Bloqueador de ventanas emergentes
- ❌ Error en procesamiento de venta

**Soluciones:**
1. ✅ **Permita ventanas emergentes** en el navegador
2. ✅ **Vaya a historial** y reimprima desde allí
3. ✅ **Verifique** que venta se registró correctamente
4. ✅ **Use descarga PDF** como alternativa

### Problema: Totales Incorrectos
**Posibles causas:**
- ❌ Precios desactualizados en productos
- ❌ Cantidades incorrectas en carrito
- ❌ Error de cálculo en sistema

**Soluciones:**
1. ✅ **Revise** cantidades de cada producto
2. ✅ **Verifique** precios en catálogo
3. ✅ **Recalcule** manualmente para confirmar
4. ✅ **Reporte** discrepancias al administrador

---

## Mejores Prácticas

### ✅ Para Procesamiento Eficiente
- **Mantenga caja abierta** durante horario comercial
- **Busque productos** por términos cortos y claros
- **Verifique totales** antes de procesar pago
- **Asigne clientes** siempre que sea posible

### ✅ Para Control de Ventas
- **Registre ventas** inmediatamente después de realizada
- **Entregue recibos** a todos los clientes
- **Revise historial** periódicamente
- **Documente** ventas especiales o con descuentos

### ✅ Para Servicio al Cliente
- **Confirme productos** y cantidades con cliente
- **Informe totales** antes de procesar pago
- **Explique métodos de pago** disponibles
- **Ofrezca recibo** impreso o digital

---

## Próximos Pasos

Una vez dominado el proceso de ventas:

📖 **[Control de Caja](07-control-caja.md)** - Gestione ingresos y cierres diarios

📖 **[Gestión de Clientes](03-gestion-clientes.md)** - Administre cuentas corrientes generadas

📖 **[Gestión de Reparaciones](06-gestion-reparaciones.md)** - Procese servicios adicionales

---

*¿Problemas con el proceso de ventas? Consulte [Preguntas Frecuentes](11-preguntas-frecuentes.md) sección "Ventas" para más ayuda.*
