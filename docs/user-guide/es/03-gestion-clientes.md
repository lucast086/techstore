# Gestión de Clientes

## Índice
- [Introducción al Módulo](#introducción-al-módulo)
- [Lista de Clientes](#lista-de-clientes)
- [Registrar Nuevo Cliente](#registrar-nuevo-cliente)
- [Buscar Clientes](#buscar-clientes)
- [Ver Detalles del Cliente](#ver-detalles-del-cliente)
- [Cuentas Corrientes](#cuentas-corrientes)
- [Estado de Cuenta](#estado-de-cuenta)
- [Gestión de Pagos](#gestión-de-pagos)
- [Casos de Uso Comunes](#casos-de-uso-comunes)
- [Solución de Problemas](#solución-de-problemas)

---

## Introducción al Módulo

El **módulo de Clientes** es el corazón del sistema TechStore, donde se administra toda la información de los clientes y sus cuentas corrientes.

### ¿Qué Puedo Hacer?
- ✅ **Registrar** nuevos clientes con información completa
- ✅ **Buscar** clientes rápidamente por nombre, teléfono o email
- ✅ **Ver historial** completo de transacciones
- ✅ **Gestionar cuentas corrientes** (debe/haber)
- ✅ **Generar** estados de cuenta detallados
- ✅ **Registrar pagos** y ajustar balances

### Acceso al Módulo
**Desde la barra de navegación:**
1. Haga clic en **"Clientes"** en el menú superior
2. Seleccione la opción deseada del menú desplegable

---

## Lista de Clientes

### Acceder a la Lista
📋 **Navegación:** Clientes → Lista de Clientes

### Información Mostrada
La lista muestra para cada cliente:
- **Nombre completo** del cliente
- **Teléfono** de contacto principal
- **Email** registrado
- **Balance actual** (positivo = debe, negativo = a favor)
- **Fecha** de registro en el sistema

```
[Captura de pantalla: Tabla de clientes con columnas: Nombre, Teléfono, Email, Balance, Fecha Registro, Acciones]
```

### Funciones Disponibles
**En cada fila de cliente puede:**
- 👁️ **Ver detalles** completos del cliente
- 📋 **Ver estado de cuenta** con historial de movimientos
- 🔍 **Acceso rápido** a información de contacto

### Paginación
- **Navegación automática** cuando hay muchos clientes
- **20 clientes por página** por defecto
- **Números de página** en la parte inferior

---

## Registrar Nuevo Cliente

### Acceder al Formulario
📋 **Navegación:** Clientes → Nuevo Cliente

### Información Requerida

**Campos obligatorios (*):**
- **Nombre completo*** - Nombre y apellidos del cliente
- **Teléfono principal*** - Número de contacto (formato: +573001234567)

**Campos opcionales:**
- **Email** - Correo electrónico para comunicaciones
- **Dirección** - Dirección física del cliente

```
[Captura de pantalla: Formulario de nuevo cliente con campos de nombre, teléfono, email y dirección]
```

### Proceso de Registro
1. 📋 **Complete** los campos obligatorios
2. 📋 **Agregue** información opcional si está disponible
3. 📋 **Haga clic** en "Guardar Cliente"
4. ✅ **Confirme** que aparece mensaje de éxito

### Validaciones del Sistema
**El sistema verifica automáticamente:**
- ⚠️ **Formato de teléfono** válido
- ⚠️ **Formato de email** correcto (si se proporciona)
- ⚠️ **Duplicados** - no permite teléfonos o emails repetidos

### ✅ Buenas Prácticas
- **Siempre complete** el nombre completo para identificación clara
- **Use formato internacional** para teléfonos: +573001234567
- **Solicite email** para futuras comunicaciones automáticas
- **Verifique información** con el cliente antes de guardar

### ❌ Errores Comunes
- No verificar si el cliente ya existe antes de crear uno nuevo
- Escribir teléfonos sin el código del país
- No confirmar la ortografía del nombre con el cliente

---

## Buscar Clientes

### Función de Búsqueda Inteligente
El sistema incluye **búsqueda en tiempo real** disponible en múltiples pantallas:
- Lista de clientes
- Punto de venta
- Registro de pagos
- Cualquier lugar que requiera seleccionar cliente

### Campos de Búsqueda
**Puede buscar por:**
- **Nombre completo** (completo o parcial)
- **Número de teléfono** (completo o parcial)
- **Dirección de email** (completo o parcial)

### Cómo Buscar
1. 🔍 **Escriba** en el campo de búsqueda
2. 🔍 **Los resultados aparecen** automáticamente mientras escribe
3. 🔍 **Seleccione** el cliente deseado de los resultados

```
[Captura de pantalla: Campo de búsqueda con lista desplegable mostrando resultados en tiempo real]
```

### Tips de Búsqueda Efectiva
**Para mejores resultados:**
- **Use nombres parciales**: "Juan" encuentra "Juan Pérez", "Juan Carlos", etc.
- **Use números parciales**: "300" encuentra todos los teléfonos que contengan "300"
- **Sin mayúsculas necesarias**: el sistema ignora mayúsculas/minúsculas

### Resultados de Búsqueda
**Información mostrada en resultados:**
- **Nombre completo** del cliente
- **Teléfono** principal
- **Balance actual** de cuenta corriente
- **Indicador visual** del estado financiero

---

## Ver Detalles del Cliente

### Acceder a los Detalles
**Desde cualquier lista:**
1. Haga clic en el **nombre del cliente** o botón "Ver"
2. Se abre la **página de detalles** completos

### Información Completa Mostrada
**Datos personales:**
- Nombre completo
- Teléfono principal
- Email (si registrado)
- Dirección (si registrada)
- Fecha de registro en el sistema

**Información financiera:**
- **Balance actual** de cuenta corriente
- **Total histórico** de compras
- **Total histórico** de pagos
- **Número de transacciones** realizadas

```
[Captura de pantalla: Página de detalles con información personal y resumen financiero del cliente]
```

### Acciones Disponibles
**Desde la página de detalles puede:**
- 📊 **Ver estado de cuenta** completo
- 💰 **Registrar pago** nuevo
- 📄 **Generar reporte** de actividad del cliente
- ✏️ **Editar información** (funcionalidad futura)

---

## Cuentas Corrientes

### ¿Qué son las Cuentas Corrientes?
Las **cuentas corrientes** registran automáticamente todas las transacciones del cliente:
- ➕ **Débitos**: Ventas y reparaciones (aumentan el saldo que debe)
- ➖ **Créditos**: Pagos y devoluciones (disminuyen el saldo que debe)

### Interpretación del Balance
**Balance positivo (+)**: Cliente **debe** dinero a la tienda
```
Ejemplo: +$50.000 = Cliente debe cincuenta mil pesos
```

**Balance negativo (-)**: Cliente tiene dinero **a favor** en la tienda
```
Ejemplo: -$25.000 = Cliente tiene veinticinco mil pesos a favor
```

**Balance cero (0)**: Cliente está **al día** sin deudas ni créditos

### Movimientos Automáticos
**El sistema registra automáticamente:**
- ✅ **Ventas realizadas** (aumentan deuda)
- ✅ **Reparaciones entregadas** (aumentan deuda)
- ✅ **Pagos recibidos** (disminuyen deuda)
- ✅ **Devoluciones aprobadas** (disminuyen deuda)

### Control Manual
**También puede registrar manualmente:**
- Pagos recibidos fuera del sistema
- Ajustes por descuentos especiales
- Correcciones por errores previos

---

## Estado de Cuenta

### Generar Estado de Cuenta
📋 **Navegación:**
1. Vaya a detalles del cliente
2. Haga clic en **"Ver Estado de Cuenta"**

### Información del Estado de Cuenta
**Resumen superior:**
- **Nombre y datos** del cliente
- **Balance actual** destacado
- **Período** de consulta
- **Totales** de débitos y créditos

**Detalle de movimientos:**
- **Fecha** de cada transacción
- **Tipo** de movimiento (venta, reparación, pago)
- **Descripción** detallada
- **Monto** con signo (+ débito, - crédito)
- **Balance** acumulado después de cada movimiento

```
[Captura de pantalla: Estado de cuenta mostrando tabla de movimientos con columnas de fecha, descripción, débito, crédito y balance]
```

### Filtros Disponibles
**Puede filtrar por:**
- **Fecha desde** y **fecha hasta**
- **Tipo de movimiento** (todos, ventas, pagos, reparaciones)
- **Solo pendientes** o **todos los movimientos**

### Acciones en Estado de Cuenta
**Funciones disponibles:**
- 🖨️ **Imprimir** estado de cuenta
- 📱 **Enviar por WhatsApp** (si cliente tiene teléfono)
- 💰 **Registrar pago** directo desde la pantalla

---

## Gestión de Pagos

### Registrar Nuevo Pago
**Desde el estado de cuenta:**
1. Haga clic en **"Registrar Pago"**
2. **Complete** el formulario de pago
3. **Confirme** el registro

**Información requerida para pago:**
- **Monto del pago** (número positivo)
- **Método de pago** (efectivo, transferencia, etc.)
- **Fecha del pago** (por defecto hoy)
- **Observaciones** opcionales

### Validaciones de Pago
**El sistema verifica:**
- ⚠️ **Monto positivo** - no acepta valores negativos o cero
- ⚠️ **Monto razonable** - no exceda deudas grandes sin confirmación
- ⚠️ **Fecha válida** - no acepta fechas futuras

### Efecto en la Cuenta Corriente
**Al registrar un pago:**
1. **Se reduce** el balance debido del cliente
2. **Se genera** recibo automático
3. **Se actualiza** el historial inmediatamente
4. **Se refleja** en reportes de caja

---

## Casos de Uso Comunes

### Caso 1: Cliente Nuevo en Tienda
**Situación**: Llega un cliente que nunca ha venido

**Proceso:**
1. 📋 **Registre** al cliente con nombre y teléfono
2. 🛒 **Procese** la venta normalmente
3. ✅ **El sistema** vincula automáticamente la venta al cliente
4. 📊 **El cliente** queda registrado para futuras visitas

### Caso 2: Cliente Habitual sin Pago Inmediato
**Situación**: Cliente conocido que quiere "anotar" la compra

**Proceso:**
1. 🔍 **Busque** al cliente existente
2. 🛒 **Realice** la venta normalmente
3. 💳 **Seleccione** "Cuenta Corriente" como método de pago
4. ✅ **El sistema** registra la deuda automáticamente

### Caso 3: Cliente Paga Deuda Acumulada
**Situación**: Cliente viene solo a pagar lo que debe

**Proceso:**
1. 🔍 **Busque** al cliente
2. 👁️ **Vea** su estado de cuenta y balance actual
3. 💰 **Registre** el pago completo o parcial
4. 🧾 **Entregue** recibo del pago realizado

### Caso 4: Consulta de Deuda por Teléfono
**Situación**: Cliente llama preguntando cuánto debe

**Proceso:**
1. 🔍 **Busque** al cliente por nombre o teléfono
2. 👁️ **Abra** sus detalles
3. 📊 **Consulte** el balance actual
4. 📞 **Informe** al cliente el monto exacto

---

## Solución de Problemas

### Problema: No Encuentra el Cliente
**Posibles causas:**
- ❌ Cliente no está registrado aún
- ❌ Búsqueda con información incorrecta
- ❌ Cliente registrado con datos diferentes

**Soluciones:**
1. ✅ **Busque** con diferentes términos (nombre parcial, teléfono)
2. ✅ **Verifique** la ortografía del nombre
3. ✅ **Pregunte** al cliente por datos alternativos
4. ✅ **Si no existe**, regístrelo como cliente nuevo

### Problema: Balance Incorrecto
**Posibles causas:**
- ❌ Pago no registrado en el sistema
- ❌ Venta duplicada
- ❌ Error en monto de transacción anterior

**Soluciones:**
1. ✅ **Revise** el estado de cuenta completo
2. ✅ **Identifique** el movimiento incorrecto
3. ✅ **Contacte** al administrador para ajustes
4. ✅ **Documente** el error para corrección

### Problema: No Puede Registrar Pago
**Posibles causas:**
- ❌ Monto inválido (negativo o cero)
- ❌ Fecha incorrecta
- ❌ Problemas de conectividad

**Soluciones:**
1. ✅ **Verifique** que el monto sea positivo
2. ✅ **Use fecha actual** o anterior válida
3. ✅ **Recargue** la página e intente nuevamente
4. ✅ **Contacte** soporte técnico si persiste

### Problema: Cliente Duplicado
**Situación**: Mismo cliente con dos registros

**Prevención:**
- ✅ **Siempre busque** antes de crear cliente nuevo
- ✅ **Use información exacta** para evitar duplicados
- ✅ **Confirme identidad** con teléfono o documento

**Si ya existe duplicado:**
1. ✅ **Identifique** cuál registro tiene más información
2. ✅ **Use siempre** el mismo registro para futuras transacciones
3. ✅ **Contacte** administrador para consolidar registros

---

## Mejores Prácticas

### ✅ Para Registro de Clientes
- **Solicite información completa** desde la primera visita
- **Confirme ortografía** del nombre con el cliente
- **Use formato consistente** para teléfonos (+57...)
- **Actualice información** cuando el cliente lo indique

### ✅ Para Manejo de Cuentas Corrientes
- **Revise balances** antes de nuevas ventas
- **Informe al cliente** su saldo cuando pague
- **Registre pagos** inmediatamente cuando los reciba
- **Mantenga comunicación** sobre deudas pendientes

### ✅ Para Búsquedas Eficientes
- **Use términos parciales** para búsquedas amplias
- **Combine criterios** (nombre + teléfono) si es necesario
- **Actualice datos** cuando encuentre información incorrecta

---

## Próximos Pasos

Una vez dominada la gestión de clientes:

📖 **[Gestión de Productos](04-gestion-productos.md)** - Aprenda a manejar el inventario

📖 **[Proceso de Ventas](05-proceso-ventas.md)** - Conecte clientes con ventas

📖 **[Control de Caja](07-control-caja.md)** - Gestione pagos y cierres diarios

---

*¿Problemas con la gestión de clientes? Consulte [Preguntas Frecuentes](11-preguntas-frecuentes.md) sección "Clientes" para más ayuda.*
