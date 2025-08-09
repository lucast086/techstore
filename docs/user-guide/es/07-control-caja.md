# Control de Caja

## Índice
- [Introducción al Control de Caja](#introducción-al-control-de-caja)
- [Gestión de Caja Diaria](#gestión-de-caja-diaria)
- [Abrir Caja](#abrir-caja)
- [Cerrar Caja](#cerrar-caja)
- [Gestión de Gastos](#gestión-de-gastos)
- [Categorías de Gastos](#categorías-de-gastos)
- [Estados de Caja](#estados-de-caja)
- [Reconciliación y Control](#reconciliación-y-control)
- [Casos de Uso Comunes](#casos-de-uso-comunes)
- [Solución de Problemas](#solución-de-problemas)

---

## Introducción al Control de Caja

El **módulo de Control de Caja** gestiona el flujo de dinero diario de la tienda, desde la apertura matutina hasta el cierre nocturno, incluyendo el registro de gastos operativos.

### ¿Qué Puedo Hacer?
- ✅ **Abrir caja** diariamente con monto inicial
- ✅ **Registrar gastos** por categorías organizadas
- ✅ **Cerrar caja** con reconciliación automática
- ✅ **Gestionar categorías** de gastos (administradores)
- ✅ **Ver historial** de movimientos de caja
- ✅ **Consultar estados** de cajas anteriores

### Importancia del Control
**¿Por qué es crítico?**
- 💰 **Control exacto** de ingresos y egresos
- 📊 **Transparencia** en manejo de efectivo
- 🔍 **Trazabilidad** de todos los movimientos
- ⚖️ **Reconciliación** precisa al final del día
- 📈 **Datos confiables** para reportes financieros

### Acceso al Módulo
**Desde la barra de navegación:**
1. Haga clic en **"Caja"** en el menú superior
2. Seleccione la opción deseada del menú desplegable

---

## Gestión de Caja Diaria

### Flujo Diario de Caja
**Secuencia típica diaria:**

```
🌅 INICIO DEL DÍA
1. Abrir Caja con monto inicial
2. ✅ Sistema habilita ventas y operaciones

💼 DURANTE EL DÍA
3. Procesar ventas (ingresos automáticos)
4. Registrar gastos según ocurren
5. Monitorear estado de caja

🌙 FIN DEL DÍA
6. Cerrar Caja con conteo físico
7. Reconciliar diferencias
8. ✅ Sistema finaliza jornada
```

### Estados de Caja
**Posibles estados durante el día:**

- 🔴 **Cerrada**: No se pueden procesar ventas ni gastos
- 🟢 **Abierta**: Operaciones normales habilitadas
- 🟡 **En proceso de cierre**: Preparando cierre diario
- ✅ **Finalizada**: Día cerrado y reconciliado

---

## Abrir Caja

### Acceder a Apertura
📋 **Navegación:** Caja → Abrir Caja

### Cuándo Abrir Caja
**Momentos para apertura:**
- 🌅 **Inicio de jornada laboral** cada día
- 🔄 **Después de cerrar** caja del día anterior
- 🆕 **Primera vez** en el sistema
- 🔧 **Después de mantenimiento** del sistema

### Proceso de Apertura

```
[Captura de pantalla: Formulario de apertura de caja con campo de monto inicial y botón confirmar]
```

**Pasos para abrir:**
1. 📋 **Ingrese monto inicial** - dinero físico con que inicia
2. 📅 **Confirme fecha** (automática, día actual)
3. 👤 **Verifique usuario** (automático, su sesión)
4. 📋 **Haga clic** en "Abrir Caja"
5. ✅ **Sistema confirma** apertura exitosa

### Información Requerida

**Monto inicial obligatorio:**
- **¿Qué es?** Dinero en efectivo al inicio del día
- **¿Cuánto?** Cantidad que permite "dar vuelto" inicial
- **Típico**: Entre $50.000 y $200.000 según negocio
- **Formato**: Solo números (ej: 100000, no $100.000)

### Validaciones del Sistema
**El sistema verifica:**
- ⚠️ **Monto positivo** - no acepta cero o negativo
- ⚠️ **Caja no abierta** previamente el mismo día
- ⚠️ **Usuario autorizado** para apertura
- ⚠️ **Formato numérico** válido

### Después de Apertura
**Cambios en el sistema:**
- ✅ **Ventas habilitadas** - POS se activa
- ✅ **Registro de gastos** disponible
- ✅ **Indicador verde** en pantallas de venta
- ✅ **Dashboard actualizado** con estado "Abierta"

---

## Cerrar Caja

### Acceder a Cierre
📋 **Navegación:** Caja → Cerrar Caja

### Cuándo Cerrar Caja
**Momentos apropiados:**
- 🌙 **Final de jornada** laboral diaria
- 🔄 **Cambio de turno** principal
- 📊 **Para generar reportes** de período
- ⚠️ **Emergencias** o situaciones especiales

### Pre-requisitos para Cierre
**Antes de cerrar, asegúrese:**
- ✅ **Todas las ventas** del día están procesadas
- ✅ **Gastos registrados** completamente
- ✅ **Conteo físico** del dinero realizado
- ✅ **Sin transacciones** pendientes

### Proceso de Cierre

```
[Captura de pantalla: Formulario de cierre con resumen automático y campos de conteo físico]
```

### Información del Cierre

**Resumen automático mostrado:**
- **Monto apertura**: Dinero inicial del día
- **Total ventas**: Suma de todas las ventas en efectivo
- **Total gastos**: Suma de todos los gastos registrados
- **Saldo teórico**: Apertura + Ventas - Gastos
- **Diferencia**: Conteo físico vs. saldo teórico

**Información a ingresar:**
- **Conteo físico** - Dinero real contado en caja
- **Observaciones** - Notas sobre el día (opcional)

### Reconciliación Automática

**El sistema calcula automáticamente:**
```
Saldo Teórico = Monto Apertura + Ventas - Gastos
Diferencia = Conteo Físico - Saldo Teórico

• Diferencia = 0: ✅ Caja cuadrada perfectamente
• Diferencia > 0: 📈 Sobrante de dinero
• Diferencia < 0: 📉 Faltante de dinero
```

### Manejo de Diferencias
**Si hay diferencias:**
1. **Revise conteo físico** - cuente nuevamente
2. **Verifique gastos** - ¿falta algún registro?
3. **Confirme ventas** - ¿todas están registradas?
4. **Documente razón** en observaciones
5. **Proceda con cierre** - el sistema acepta diferencias

### Finalización del Cierre
**Al completar cierre:**
- ✅ **Caja marcada** como cerrada
- ✅ **Ventas deshabilitadas** hasta nueva apertura
- ✅ **Reporte generado** automáticamente
- ✅ **Historial actualizado** con datos del día

---

## Gestión de Gastos

### ¿Qué son los Gastos?
**Gastos son dinero que sale de caja por:**
- 🛒 **Compras** de inventario o insumos
- 🔧 **Servicios** públicos o técnicos
- 📱 **Pagos** a proveedores o empleados
- 🍽️ **Gastos operativos** del día a día

### Acceder a Gastos
📋 **Navegación:** Caja → Expenses

### Registrar Nuevo Gasto

**Formulario de gastos:**
```
[Captura de pantalla: Formulario con campos de categoría, descripción, monto y fecha]
```

**Información requerida:**
- **Categoría*** - Tipo de gasto (desplegable)
- **Descripción*** - Detalle específico del gasto
- **Monto*** - Cantidad de dinero gastado
- **Fecha** - Día del gasto (automático hoy)

### Proceso de Registro
1. 📋 **Seleccione categoría** apropiada del menú
2. 📋 **Escriba descripción** clara y específica
3. 📋 **Ingrese monto** exacto (solo números)
4. 📋 **Confirme fecha** (modifique si no es hoy)
5. 📋 **Haga clic** en "Guardar Gasto"
6. ✅ **Sistema registra** y actualiza caja

### Validaciones de Gastos
**El sistema verifica:**
- ⚠️ **Categoría seleccionada** válida
- ⚠️ **Monto positivo** y numérico
- ⚠️ **Descripción no vacía** (mínimo caracteres)
- ⚠️ **Caja abierta** para registrar gasto
- ⚠️ **Fondos suficientes** (advertencia si excede)

### Lista de Gastos
**Visualización de gastos registrados:**
- **Fecha y hora** del registro
- **Categoría** del gasto
- **Descripción** detallada
- **Monto** gastado
- **Usuario** que registró
- **Opciones** de edición (limitadas)

---

## Categorías de Gastos

### ¿Por qué Categorías?
**Beneficios de categorización:**
- 📊 **Reportes organizados** por tipo de gasto
- 📈 **Análisis de tendencias** de costos
- 🎯 **Presupuestación** más efectiva
- 🔍 **Búsqueda y filtrado** rápido

### Categorías Predeterminadas
**El sistema incluye categorías típicas:**
- **Servicios públicos** - Luz, agua, internet, teléfono
- **Inventario** - Compras de productos para reventa
- **Mantenimiento** - Reparaciones, limpieza, suministros
- **Transporte** - Gasolina, taxi, envíos
- **Alimentación** - Comidas, bebidas para empleados
- **Papelería** - Facturas, recibos, suministros oficina
- **Otros** - Gastos que no encajan en categorías

### Gestión de Categorías (Solo Administradores)

**Acceso:** Panel Administración → Categorías de Gastos

**Funciones administrativas:**
- ✅ **Crear** nuevas categorías específicas
- ✅ **Editar** nombres y descripciones
- ✅ **Organizar** por jerarquías
- ✅ **Desactivar** categorías obsoletas

**Proceso crear categoría:**
1. 📋 **Acceda** a gestión de categorías
2. 📋 **Clic** en "Nueva Categoría"
3. 📋 **Complete** nombre y descripción
4. 📋 **Guarde** categoría
5. ✅ **Disponible** inmediatamente para gastos

---

## Estados de Caja

### Consultar Estado Actual
**Información en tiempo real:**
- **Estado**: Abierta/Cerrada/Finalizada
- **Monto inicial**: Dinero de apertura
- **Ventas del día**: Total acumulado
- **Gastos del día**: Total registrado
- **Saldo teórico**: Cálculo automático
- **Última actividad**: Timestamp de último movimiento

### Historial de Cajas
📋 **Navegación:** Caja → Gestión de Caja

**Lista de períodos anteriores:**
- **Fecha** del período
- **Usuario** responsable
- **Monto apertura**
- **Total ventas** del período
- **Total gastos** del período
- **Estado final** (cuadrada/diferencia)
- **Acciones** (ver detalles, reportes)

### Ver Detalles de Período
**Al seleccionar día específico:**
```
[Captura de pantalla: Detalles de caja con resumen y lista de movimientos del día]
```

**Información detallada:**
- **Resumen financiero** completo
- **Lista de ventas** del período
- **Lista de gastos** registrados
- **Cálculos de reconciliación**
- **Observaciones** del cierre
- **Diferencias** encontradas

---

## Reconciliación y Control

### ¿Qué es Reconciliación?
**Proceso de verificación:**
- **Comparar** dinero físico vs. registros digitales
- **Identificar** diferencias y sus causas
- **Documentar** discrepancias encontradas
- **Tomar acciones** correctivas necesarias

### Tipos de Diferencias

**Sobrante de dinero (+):**
- 🤔 **Posibles causas**: Venta no registrada, error en vuelto, dinero olvidado
- ✅ **Acción**: Investigar origen, registrar venta faltante si aplica

**Faltante de dinero (-):**
- 🤔 **Posibles causas**: Gasto no registrado, error en cálculo, dinero retirado
- ✅ **Acción**: Revisar gastos, verificar registros, documentar diferencia

**Caja cuadrada (0):**
- ✅ **Ideal**: Registros digitales coinciden exactamente con físico
- 📊 **Indica**: Control preciso y registros completos

### Mejores Prácticas de Control

**Durante el día:**
- 📝 **Registre inmediatamente** todos los gastos
- 🧾 **Guarde recibos** de todas las compras
- 💰 **Mantenga organizado** el dinero físico
- 🔄 **Cuente periódicamente** efectivo disponible

**Al cerrar:**
- 🧮 **Cuente meticulosamente** todo el efectivo
- 📋 **Revise lista** de gastos del día
- 🔍 **Verifique** que ventas estén completas
- 📝 **Documente** cualquier irregularidad

---

## Casos de Uso Comunes

### Caso 1: Apertura Normal de Día
**Situación**: Lunes por la mañana, inicio de semana laboral

**Proceso:**
1. 🌅 **Llegue temprano** antes de atender clientes
2. 💰 **Cuente efectivo inicial** disponible
3. 📋 **Abra caja** con monto contado
4. ✅ **Verifique** que POS se active
5. 🚀 **Comience** a atender clientes normalmente

### Caso 2: Registro de Gasto Durante el Día
**Situación**: Necesita comprar almuerzo para empleados

**Proceso:**
1. 💰 **Saque dinero** de caja física
2. 🍽️ **Realice compra** del almuerzo
3. 🧾 **Guarde recibo** como comprobante
4. 📋 **Registre gasto** inmediatamente en sistema
5. 📝 **Categoría**: Alimentación, **Descripción**: "Almuerzo empleados día X"

### Caso 3: Cierre con Diferencia Menor
**Situación**: Al contar, hay $2.000 pesos de menos

**Proceso:**
1. 🧮 **Cuente nuevamente** para confirmar
2. 🔍 **Revise gastos** - ¿falta alguno por registrar?
3. 📋 **Ingrese conteo real** en sistema
4. 📝 **Documente** en observaciones: "Diferencia -$2.000, revisado sin encontrar causa"
5. ✅ **Complete cierre** - el sistema acepta la diferencia

### Caso 4: Gasto Grande Imprevisto
**Situación**: Reparación urgente de $100.000 en horario laboral

**Proceso:**
1. ⚠️ **Evalúe** si caja tiene fondos suficientes
2. 🔧 **Autorice** la reparación necesaria
3. 💰 **Retire dinero** de caja
4. 📋 **Registre inmediatamente** en categoría "Mantenimiento"
5. 📝 **Describa detalladamente**: "Reparación urgente [especificar qué]"

### Caso 5: Consulta de Período Anterior
**Situación**: Necesita revisar gastos de la semana pasada

**Proceso:**
1. 📋 **Vaya** a Gestión de Caja
2. 📅 **Identifique fecha** específica necesaria
3. 👁️ **Haga clic** en "Ver detalles" del día
4. 🔍 **Revise** lista completa de gastos
5. 📊 **Extraiga información** necesaria para reporte

---

## Solución de Problemas

### Problema: No Puedo Abrir Caja
**Posibles causas:**
- ❌ Caja ya abierta el mismo día
- ❌ Monto inicial inválido o negativo
- ❌ Sin permisos para apertura
- ❌ Problemas técnicos del sistema

**Soluciones:**
1. ✅ **Verifique** si caja ya está abierta hoy
2. ✅ **Confirme** que monto sea número positivo
3. ✅ **Contacte administrador** sobre permisos
4. ✅ **Recargue página** si hay errores técnicos

### Problema: Gasto No Se Registra
**Posibles causas:**
- ❌ Caja cerrada (no se permiten gastos)
- ❌ Categoría no seleccionada
- ❌ Monto o descripción vacíos
- ❌ Error de conectividad

**Soluciones:**
1. ✅ **Verifique** que caja esté abierta
2. ✅ **Seleccione** categoría válida del menú
3. ✅ **Complete** todos los campos obligatorios
4. ✅ **Intente** nuevamente después de verificar conectividad

### Problema: Diferencias Grandes en Cierre
**Posibles causas:**
- ❌ Ventas no registradas en sistema
- ❌ Gastos significativos no anotados
- ❌ Error en conteo físico
- ❌ Dinero retirado sin autorización

**Soluciones:**
1. ✅ **Recount** físico meticulosamente
2. ✅ **Revise** historial de ventas del día
3. ✅ **Verifique** todos los gastos registrados
4. ✅ **Documente** diferencia y contacte administrador
5. ✅ **No deje** caja sin cerrar - el sistema acepta diferencias

### Problema: No Aparecen Categorías de Gasto
**Posibles causas:**
- ❌ Problemas de carga del sistema
- ❌ Categorías desactivadas por administrador
- ❌ Error en base de datos

**Soluciones:**
1. ✅ **Recargue** la página completamente
2. ✅ **Contacte administrador** para verificar categorías
3. ✅ **Use categoría "Otros"** como temporal
4. ✅ **Reporte** problema técnico para solución

### Problema: Sistema No Calcula Saldo Correctamente
**Situación**: Los cálculos automáticos parecen incorrectos

**Soluciones:**
1. ✅ **Verifique** manualmente: Apertura + Ventas - Gastos
2. ✅ **Confirme** que todas las ventas estén incluidas
3. ✅ **Revise** que gastos sean del día correcto
4. ✅ **Documente** cálculo manual vs. sistema
5. ✅ **Reporte** discrepancia al soporte técnico

---

## Mejores Prácticas

### ✅ Para Apertura de Caja
- **Llegue temprano** para abrir antes de clientes
- **Use monto inicial** suficiente pero no excesivo
- **Mantenga rutina** diaria de horario de apertura
- **Verifique** que sistema confirme apertura exitosa

### ✅ Para Registro de Gastos
- **Registre inmediatamente** después de realizar gasto
- **Guarde recibos** físicos como respaldo
- **Use categorías** apropiadas y específicas
- **Describa claramente** para futura referencia

### ✅ Para Cierre de Caja
- **Planifique tiempo** suficiente para conteo cuidadoso
- **Organice dinero** antes de contar (por denominaciones)
- **Documente** diferencias sin importar el monto
- **No deje** caja sin cerrar al final del día

### ✅ Para Control Continuo
- **Mantenga** organizado el dinero físico durante el día
- **Cuente periódicamente** para detectar problemas temprano
- **Revise** registros digitales vs. físicos regularmente
- **Comunique** irregularidades inmediatamente

---

## Próximos Pasos

Una vez dominado el control de caja:

📖 **[Proceso de Ventas](05-proceso-ventas.md)** - Entienda cómo ventas afectan caja

📖 **[Gestión de Clientes](03-gestion-clientes.md)** - Administre cuentas corrientes relacionadas

📖 **[Sistema de Garantías](08-garantias.md)** - Gestione servicios post-venta

---

*¿Problemas con el control de caja? Consulte [Preguntas Frecuentes](11-preguntas-frecuentes.md) sección "Caja y Gastos" para más ayuda.*
