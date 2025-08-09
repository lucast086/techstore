# Gestión de Reparaciones

## Índice
- [Introducción al Sistema de Reparaciones](#introducción-al-sistema-de-reparaciones)
- [Lista de Reparaciones](#lista-de-reparaciones)
- [Recibir Nueva Reparación](#recibir-nueva-reparación)
- [Estados de Reparación](#estados-de-reparación)
- [Proceso de Diagnóstico](#proceso-de-diagnóstico)
- [Seguimiento y Actualizaciones](#seguimiento-y-actualizaciones)
- [Entrega al Cliente](#entrega-al-cliente)
- [Consultas y Reportes](#consultas-y-reportes)
- [Casos de Uso Comunes](#casos-de-uso-comunes)
- [Solución de Problemas](#solución-de-problemas)

---

## Introducción al Sistema de Reparaciones

El **módulo de Reparaciones** gestiona completamente el ciclo de vida de los servicios técnicos, desde que el cliente trae el equipo hasta que lo retira reparado.

### ¿Qué Puedo Hacer?
- ✅ **Recibir equipos** con información completa del problema
- ✅ **Asignar números únicos** a cada orden de trabajo
- ✅ **Gestionar estados** del proceso de reparación
- ✅ **Registrar diagnósticos** y presupuestos
- ✅ **Seguir progreso** de cada reparación
- ✅ **Entregar equipos** y generar garantías
- ✅ **Consultar historial** y estados actuales

### Flujo General del Proceso
```
📥 RECEPCIÓN
Cliente trae equipo → Registro en sistema → Número de orden generado

🔍 DIAGNÓSTICO
Técnico evalúa → Presupuesto → Aprobación del cliente

🔧 REPARACIÓN
Trabajo técnico → Pruebas → Preparación para entrega

📦 ENTREGA
Notificación al cliente → Pago → Entrega → Garantía activada
```

### Acceso al Módulo
**Desde la barra de navegación:**
1. Haga clic en **"Reparaciones"** en el menú superior
2. Seleccione la opción deseada del menú desplegable

---

## Lista de Reparaciones

### Acceder a la Lista
📋 **Navegación:** Reparaciones → Lista de Reparaciones

### Información Mostrada
La lista completa incluye para cada reparación:
- **Número de orden** único generado automáticamente
- **Cliente** propietario del equipo
- **Equipo/dispositivo** y modelo si disponible
- **Estado actual** del proceso
- **Fecha de recepción**
- **Técnico asignado** (si aplica)
- **Acciones** disponibles según estado

```
[Captura de pantalla: Lista de reparaciones con columnas de orden, cliente, equipo, estado, fecha, acciones]
```

### Estados Visuales
**Códigos de color por estado:**
- 🔵 **Recibido**: Azul - Equipo recién ingresado
- 🟡 **En Diagnóstico**: Amarillo - Evaluación técnica
- 🟠 **Presupuestado**: Naranja - Esperando aprobación
- 🔧 **En Reparación**: Verde - Trabajo en progreso
- ✅ **Listo**: Verde brillante - Terminado, listo para entrega
- 📦 **Entregado**: Gris - Completado y retirado

### Filtros y Búsqueda
**Opciones de filtrado:**
- **Por estado** específico
- **Por cliente** (nombre o teléfono)
- **Por fecha** de recepción
- **Por técnico** asignado
- **Solo pendientes** (excluye entregadas)

---

## Recibir Nueva Reparación

### Acceder al Formulario
📋 **Navegación:** Reparaciones → Nueva Reparación

### Información del Cliente
**Búsqueda de cliente existente:**
1. 🔍 **Use campo de búsqueda** por nombre o teléfono
2. 📋 **Seleccione cliente** de los resultados
3. ✅ **Información se completa** automáticamente

**Cliente nuevo:**
1. 📋 **Deje búsqueda vacía** si no existe el cliente
2. 📋 **Complete formulario** con datos del cliente
3. ✅ **Sistema crea** cliente y reparación simultáneamente

### Información del Equipo
**Campos requeridos:**
- **Tipo de dispositivo*** - Celular, tablet, computador, etc.
- **Marca** - Samsung, iPhone, Huawei, etc.
- **Modelo** - Específico si se conoce
- **Problema reportado*** - Descripción del cliente

```
[Captura de pantalla: Formulario de nueva reparación con secciones de cliente y equipo]
```

**Información adicional:**
- **Estado físico** - Condición visual del equipo
- **Accesorios incluidos** - Cargador, audífonos, funda
- **Observaciones** - Notas adicionales importantes

### Proceso de Registro
1. 📋 **Busque o registre** información del cliente
2. 📋 **Complete** descripción detallada del equipo
3. 📋 **Documente problema** reportado por el cliente
4. 📋 **Agregue observaciones** relevantes
5. 📋 **Haga clic** en "Crear Reparación"
6. ✅ **Sistema genera** número de orden único
7. 🧾 **Entregue comprobante** al cliente con número de orden

### Validaciones del Sistema
**El sistema verifica:**
- ⚠️ **Información mínima** del cliente (nombre, teléfono)
- ⚠️ **Descripción del equipo** no vacía
- ⚠️ **Problema reportado** claramente documentado
- ⚠️ **Formato válido** de datos de contacto

### Después del Registro
**Información generada:**
- ✅ **Número de orden único** (ej: REP-2024-001234)
- ✅ **Estado inicial**: "Recibido"
- ✅ **Fecha y hora** de recepción automática
- ✅ **Usuario responsable** de la recepción
- ✅ **Cliente puede consultar** estado con el número

---

## Estados de Reparación

### Ciclo de Estados
**Flujo normal de una reparación:**
```
📥 Recibido → 🔍 En Diagnóstico → 💰 Presupuestado →
🔧 En Reparación → ✅ Listo → 📦 Entregado
```

### Descripción de Cada Estado

#### 📥 **Recibido**
- **¿Qué significa?** Equipo recién ingresado al taller
- **¿Quién lo maneja?** Personal de recepción
- **¿Qué sigue?** Técnico debe revisar y cambiar a "En Diagnóstico"
- **Cliente ve**: "Su equipo ha sido recibido y está en cola para diagnóstico"

#### 🔍 **En Diagnóstico**
- **¿Qué significa?** Técnico está evaluando el problema
- **¿Quién lo maneja?** Técnico especializado
- **¿Qué sigue?** Determinar costo y cambiar a "Presupuestado"
- **Cliente ve**: "Nuestro técnico está evaluando su equipo"

#### 💰 **Presupuestado**
- **¿Qué significa?** Diagnóstico completo, esperando aprobación del cliente
- **¿Quién lo maneja?** Personal de atención al cliente
- **¿Qué sigue?** Cliente aprueba presupuesto, pasa a "En Reparación"
- **Cliente ve**: "Diagnóstico listo, esperamos su aprobación para proceder"

#### 🔧 **En Reparación**
- **¿Qué significa?** Trabajo técnico en progreso
- **¿Quién lo maneja?** Técnico especializado
- **¿Qué sigue?** Completar reparación y cambiar a "Listo"
- **Cliente ve**: "Su equipo está siendo reparado"

#### ✅ **Listo**
- **¿Qué significa?** Reparación terminada, equipo listo para recoger
- **¿Quién lo maneja?** Personal de entrega
- **¿Qué sigue?** Cliente viene a recoger, pasa a "Entregado"
- **Cliente ve**: "Su equipo está listo para recoger"

#### 📦 **Entregado**
- **¿Qué significa?** Cliente retiró el equipo satisfactoriamente
- **¿Quién lo maneja?** Personal de entrega
- **¿Qué sigue?** Proceso completado, solo seguimiento de garantía
- **Cliente ve**: "Reparación completada y entregada"

### Cambiar Estados
**Proceso para actualizar estado:**
1. 📋 **Acceda** a detalles de la reparación
2. 📋 **Haga clic** en "Cambiar Estado"
3. 📋 **Seleccione** nuevo estado apropiado
4. 📋 **Agregue observaciones** del cambio
5. 📋 **Confirme** el cambio
6. ✅ **Sistema registra** fecha, hora y usuario del cambio

---

## Proceso de Diagnóstico

### Acceder al Diagnóstico
📋 **Desde lista de reparaciones:**
1. Seleccione reparación en estado "En Diagnóstico"
2. Haga clic en "Gestionar Diagnóstico"

### Formulario de Diagnóstico
**Información a completar:**

```
[Captura de pantalla: Formulario de diagnóstico con campos de problema técnico, solución propuesta, costo]
```

**Campos principales:**
- **Problema técnico identificado*** - Diagnóstico específico del técnico
- **Solución propuesta*** - Qué trabajo se realizará
- **Costo de reparación*** - Precio total del servicio
- **Tiempo estimado** - Días aproximados para completar
- **Repuestos necesarios** - Lista de componentes requeridos
- **Observaciones técnicas** - Notas adicionales del técnico

### Información para el Cliente
**El sistema genera automáticamente:**
- **Resumen del diagnóstico** en lenguaje comprensible
- **Presupuesto total** desglosado
- **Tiempo estimado** de reparación
- **Garantía aplicable** al trabajo

### Aprobar Diagnóstico
**Proceso con el cliente:**
1. 📞 **Contacte al cliente** con el diagnóstico
2. 📋 **Explique problema** y solución propuesta
3. 💰 **Informe costo** y tiempo estimado
4. ✅ **Cliente aprueba**: Cambiar estado a "En Reparación"
5. ❌ **Cliente rechaza**: Cambiar estado a "Listo" (para retirar sin reparar)

### Casos Especiales
**Diagnóstico: "No se puede reparar"**
- 📋 **Documente razones** técnicas específicas
- 💰 **Establezca costo $0** si no hay cargo por diagnóstico
- 📞 **Comunique al cliente** la situación
- ✅ **Cambie estado** a "Listo" para retiro del equipo

**Diagnóstico: "No requiere reparación"**
- 📋 **Documente** que no se encontró problema
- 🧹 **Puede incluir** limpieza o configuración realizada
- 💰 **Establezca costo** según política de la tienda
- ✅ **Proceda** normalmente con aprobación del cliente

---

## Seguimiento y Actualizaciones

### Ver Detalles Completos
**Información disponible en cada reparación:**

```
[Captura de pantalla: Página de detalles con información completa de la reparación]
```

**Sección de información básica:**
- Número de orden y fecha de recepción
- Datos completos del cliente
- Descripción del equipo y problema
- Estado actual y historial de cambios
- Usuario responsable actual

**Sección técnica:**
- Diagnóstico detallado (si disponible)
- Presupuesto y costos
- Tiempo estimado y transcurrido
- Observaciones técnicas
- Repuestos utilizados

### Historial de Cambios
**Para cada cambio de estado se registra:**
- 📅 **Fecha y hora exacta** del cambio
- 👤 **Usuario** que realizó el cambio
- 📝 **Estado anterior** y **estado nuevo**
- 💬 **Observaciones** agregadas
- ⏱️ **Tiempo transcurrido** en cada estado

### Agregar Observaciones
**Durante el proceso puede:**
1. 📋 **Agregar notas** sobre el progreso
2. 📋 **Documentar complicaciones** encontradas
3. 📋 **Registrar comunicación** con el cliente
4. 📋 **Notar cambios** en alcance o costo
5. ✅ **Observaciones quedan** en historial permanente

### Comunicación con Cliente
**Información disponible para compartir:**
- **Estado actual** en lenguaje comprensible
- **Tiempo transcurrido** desde recepción
- **Progreso estimado** hasta completar
- **Cualquier cambio** en costo o tiempo original
- **Fecha estimada** de finalización

---

## Entrega al Cliente

### Proceso de Entrega
**Cuando reparación está "Lista":**

1. **Verificación previa:**
   - ✅ **Confirme** que trabajo está completado
   - ✅ **Pruebe** funcionamiento del equipo
   - ✅ **Prepare** accesorios devueltos
   - ✅ **Verifique** costo final vs. presupuesto

2. **Contacto con cliente:**
   - 📞 **Llame** para notificar que está listo
   - 📅 **Coordine** horario de recogida
   - 💰 **Confirme** forma de pago preferida
   - 🧾 **Informe** documentos necesarios

3. **Proceso de entrega:**
   - 👤 **Identifique** al cliente (documento, nombre completo)
   - 🔍 **Muestre** funcionamiento del equipo reparado
   - 📋 **Explique** trabajo realizado
   - 💰 **Procese pago** del servicio
   - 📝 **Genere recibo** y garantía
   - ✅ **Cambie estado** a "Entregado"

### Pago del Servicio
**Opciones de pago:**
- 💵 **Efectivo** - Pago inmediato en caja
- 💳 **Transferencia** - Comprobante requerido
- 💳 **Tarjeta** - Proceso según terminal disponible
- 📋 **Cuenta corriente** - Se agrega a deuda del cliente

### Garantía de Reparación
**El sistema automáticamente:**
- ✅ **Genera garantía** con términos estándar
- 📅 **Establece período** de cobertura
- 📋 **Registra** trabajo cubierto por garantía
- 🧾 **Incluye** información en recibo de entrega

### Recibo de Entrega
**Documento generado incluye:**
- **Información del cliente** y contacto
- **Número de orden** de la reparación
- **Descripción del equipo** reparado
- **Trabajo realizado** y repuestos usados
- **Costo total** y método de pago
- **Términos de garantía** aplicables
- **Fecha de entrega** y responsable

---

## Consultas y Reportes

### Consulta Rápida por Cliente
**Para atención telefónica:**
1. 🔍 **Busque cliente** en lista de reparaciones
2. 📋 **Filtre** por cliente específico
3. 👁️ **Vea** todas sus reparaciones (activas e históricas)
4. 📞 **Informe estado** y progreso actual

### Consulta por Número de Orden
**Cuando cliente tiene número:**
1. 🔍 **Use búsqueda** por número específico
2. 👁️ **Acceda** directamente a detalles
3. 📋 **Revise** estado e historial actual
4. 📞 **Proporcione** información actualizada

### Reportes de Productividad
**Información disponible:**
- **Reparaciones por estado** (cuántas en cada fase)
- **Tiempo promedio** por tipo de reparación
- **Técnico más productivo** por período
- **Ingresos generados** por reparaciones
- **Cliente más frecuente** en servicios

### Seguimiento de Garantías
**Control de garantías activas:**
- **Garantías vigentes** por expirar
- **Reclamaciones** registradas
- **Costo de garantías** para el negocio
- **Tipos de problema** más comunes en garantía

---

## Casos de Uso Comunes

### Caso 1: Cliente Trae Celular con Pantalla Rota
**Situación**: iPhone con pantalla dañada, cliente conocido

**Proceso completo:**
1. 📋 **Busque cliente** existente en sistema
2. 📋 **Complete formulario** - Tipo: iPhone, Problema: Pantalla rota
3. 🧾 **Entregue número** de orden al cliente
4. 🔍 **Técnico evalúa** - Estado: "En Diagnóstico"
5. 💰 **Presupueste** $150.000 por cambio de pantalla
6. 📞 **Cliente aprueba** - Estado: "En Reparación"
7. 🔧 **Realizar cambio** de pantalla
8. ✅ **Pruebas completadas** - Estado: "Listo"
9. 📞 **Llamar cliente** para recoger
10. 💰 **Cliente paga** y retira - Estado: "Entregado"

### Caso 2: Reparación que No se Puede Completar
**Situación**: Tablet con daño en placa madre irreparable

**Proceso:**
1. 📋 **Recepción normal** del equipo
2. 🔍 **Diagnóstico técnico** - daño severo en circuitería
3. 📋 **Documente** "No se puede reparar - daño en placa madre"
4. 💰 **Establezca costo $0** (o según política de diagnóstico)
5. 📞 **Contacte cliente** explicando situación
6. ✅ **Estado "Listo"** para retiro sin costo
7. 📦 **Entrega equipo** sin reparar al cliente

### Caso 3: Cliente Consulta Estado por Teléfono
**Situación**: Cliente llama preguntando por su reparación después de 3 días

**Proceso:**
1. 🔍 **Busque** por nombre o teléfono del cliente
2. 👁️ **Identifique** reparación activa
3. 📋 **Revise estado** actual - "En Reparación"
4. 📅 **Consulte** fecha de recepción y tiempo transcurrido
5. 📞 **Informe**: "Su equipo está siendo reparado, estimamos 2 días más"
6. 📝 **Agregue observación** "Cliente consultó por teléfono"

### Caso 4: Reparación con Complicaciones
**Situación**: Durante reparación se encuentra problema adicional

**Proceso:**
1. 🔧 **Técnico encuentra** problema no detectado inicialmente
2. 📋 **Agregue observación** detallada del nuevo problema
3. 💰 **Calcule** costo adicional necesario
4. 📞 **Contacte cliente** explicando situación
5. ✅ **Cliente aprueba** costo adicional - continuar
6. ❌ **Cliente rechaza** - completar solo trabajo original
7. 📝 **Documente** decisión del cliente en observaciones

### Caso 5: Entrega con Garantía Inmediata
**Situación**: Cliente reporta problema 2 días después de retirar equipo

**Proceso:**
1. 🔍 **Verifique** garantía activa en sistema
2. 📋 **Confirme** problema está cubierto por garantía
3. 📥 **Reciba equipo** nuevamente sin costo
4. 📝 **Referencie** reparación original en observaciones
5. 🔧 **Corrija problema** bajo garantía
6. 📦 **Entregue** sin costo adicional al cliente

---

## Solución de Problemas

### Problema: No Puedo Crear Nueva Reparación
**Posibles causas:**
- ❌ Información del cliente incompleta
- ❌ Descripción del problema muy corta
- ❌ Conexión de red intermitente

**Soluciones:**
1. ✅ **Complete** todos los campos obligatorios (*)
2. ✅ **Agregue** descripción detallada del problema
3. ✅ **Verifique** conexión y recargue página
4. ✅ **Intente** nuevamente después de verificar datos

### Problema: No Puedo Cambiar Estado de Reparación
**Posibles causas:**
- ❌ Sin permisos para cambiar estados
- ❌ Estado seleccionado no válido para flujo
- ❌ Información faltante requerida

**Soluciones:**
1. ✅ **Contacte administrador** sobre permisos
2. ✅ **Siga secuencia** correcta de estados
3. ✅ **Complete diagnóstico** antes de pasar a "En Reparación"
4. ✅ **Agregue observaciones** explicando el cambio

### Problema: Cliente Dice que Nunca Trajo el Equipo
**Situación**: Discrepancia entre registros y memoria del cliente

**Proceso:**
1. ✅ **Verifique** información del cliente en sistema
2. ✅ **Confirme** número de orden con cliente
3. ✅ **Revise** fecha y hora de recepción
4. ✅ **Consulte** historial de cambios de estado
5. ✅ **Documente** la consulta en observaciones
6. ✅ **Escale** a supervisor si persiste discrepancia

### Problema: Reparación Tomó Más Tiempo del Estimado
**Situación**: Cliente reclama por demora

**Proceso:**
1. ✅ **Revise** historial de estados y tiempos
2. ✅ **Identifique** dónde ocurrió la demora
3. ✅ **Documente** razones en observaciones
4. ✅ **Comunique** transparentemente al cliente
5. ✅ **Ofrezca** compensación si política lo permite
6. ✅ **Aprenda** para mejorar estimaciones futuras

### Problema: No Encuentro una Reparación Específica
**Posibles causas:**
- ❌ Número de orden incorrecto
- ❌ Búsqueda con criterios muy específicos
- ❌ Reparación registrada con cliente diferente

**Soluciones:**
1. ✅ **Verifique** número de orden cuidadosamente
2. ✅ **Busque** por nombre del cliente
3. ✅ **Use** filtros de fecha si conoce período
4. ✅ **Revise** reparaciones "Entregadas" si es antigua
5. ✅ **Contacte administrador** si definitivamente no aparece

---

## Mejores Prácticas

### ✅ Para Recepción de Equipos
- **Documente todo** detalladamente en el momento de recepción
- **Tome fotos** del estado físico si hay daños visibles
- **Confirme información** del cliente verbalmente
- **Entregue siempre** comprobante con número de orden
- **Explique proceso** y tiempos estimados al cliente

### ✅ Para Gestión de Estados
- **Actualice estados** tan pronto como cambie la situación real
- **Agregue observaciones** significativas en cada cambio
- **Mantenga comunicación** con cliente en estados críticos
- **No salte estados** sin justificación documentada
- **Use tiempos** realistas en estimaciones

### ✅ Para Comunicación con Clientes
- **Sea proactivo** en comunicar demoras o complicaciones
- **Use lenguaje** comprensible para explicar problemas técnicos
- **Confirme** costos adicionales antes de proceder
- **Documente** todas las conversaciones importantes
- **Mantenga** expectativas realistas sobre tiempos

### ✅ Para Organización del Trabajo
- **Priorice** reparaciones por fecha de recepción
- **Identifique** físicamente equipos con número de orden
- **Mantenga** área de trabajo organizada por estados
- **Revise** diariamente reparaciones pendientes
- **Planifique** carga de trabajo según capacidad

---

## Próximos Pasos

Una vez dominada la gestión de reparaciones:

📖 **[Sistema de Garantías](08-garantias.md)** - Gestione garantías generadas por reparaciones

📖 **[Gestión de Clientes](03-gestion-clientes.md)** - Administre relación con clientes de servicios

📖 **[Control de Caja](07-control-caja.md)** - Gestione ingresos por servicios técnicos

---

*¿Problemas con la gestión de reparaciones? Consulte [Preguntas Frecuentes](11-preguntas-frecuentes.md) sección "Reparaciones" para más ayuda.*
