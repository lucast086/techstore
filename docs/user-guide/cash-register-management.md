# Guía de Usuario: Gestión de Caja Registradora

## Introducción

El sistema de gestión de caja registradora es fundamental para mantener el control del flujo de efectivo en su negocio. Esta guía le explicará cómo usar todas las funcionalidades relacionadas con la caja.

## Conceptos Importantes

### Estados de la Caja

La caja registradora puede estar en tres estados:

1. **No Abierta**: No hay registro de caja para el día actual
2. **Abierta**: La caja está activa y puede registrar transacciones
3. **Cerrada/Finalizada**: La caja fue cerrada y no puede modificarse

### Reglas de Negocio

- **Solo una caja abierta**: No puede haber más de una caja abierta al mismo tiempo
- **Cierre obligatorio**: Debe cerrar la caja del día anterior antes de abrir una nueva
- **Validación de entregas**: No puede marcar reparaciones como entregadas sin caja abierta

## Operaciones Básicas

### 1. Abrir la Caja Diaria

#### Pasos:
1. Navegue a **Caja → Abrir Caja** en el menú principal
2. Verifique la fecha (debe ser la fecha actual)
3. El sistema sugiere un saldo inicial de **$10,000.00**
4. Puede modificar el monto si es necesario
5. Agregue notas opcionales
6. Haga clic en **Abrir Caja**

#### Consideraciones:
- Si existe una caja pendiente de días anteriores, el sistema le pedirá cerrarla primero
- El saldo inicial por defecto es configurable (actualmente $10,000.00)
- Solo usuarios con rol Admin o Manager pueden abrir caja

### 2. Cerrar la Caja Diaria

#### Pasos:
1. Navegue a **Caja → Cerrar Caja**
2. El sistema mostrará:
   - Saldo de apertura
   - Total de ventas del día
   - Total de gastos
   - Efectivo esperado
3. Cuente el efectivo físico en caja
4. Ingrese el monto contado en **Conteo de Efectivo**
5. El sistema calculará automáticamente la diferencia
6. Agregue notas si hay discrepancias
7. Haga clic en **Cerrar Caja**

#### Alertas de Diferencias:
- **Verde**: Diferencia menor a $100 (aceptable)
- **Amarillo**: Diferencia entre $100-$500 (requiere revisión)
- **Rojo**: Diferencia mayor a $500 (requiere investigación)

### 3. Finalizar el Cierre de Caja

#### Pasos:
1. Después de cerrar la caja, revise los totales
2. Si todo está correcto, haga clic en **Finalizar Cierre**
3. Una vez finalizado, el cierre no puede modificarse

#### Importante:
- Los cierres finalizados son inmutables
- Sirven como registro contable oficial
- Se recomienda imprimir el reporte antes de finalizar

## Validaciones del Sistema

### Entrega de Reparaciones

El sistema ahora valida que la caja esté abierta antes de permitir marcar una reparación como entregada.

#### Proceso Correcto:
1. Abra la caja del día
2. Navegue a la reparación
3. Cambie el estado a "Entregado"
4. El sistema permitirá la operación

#### Si la Caja No Está Abierta:
- Aparecerá un mensaje de error en rojo
- Mensaje: "La caja registradora debe estar abierta para entregar reparaciones"
- Solución: Abra la caja primero, luego intente nuevamente

### Procesamiento de Ventas

Similar a las reparaciones, las ventas requieren caja abierta:

#### Validación:
- No puede procesar ventas sin caja abierta
- El sistema redirigirá a la apertura de caja si intenta vender

## Casos Especiales

### Caja Olvidada del Día Anterior

**Situación**: Olvidó cerrar la caja del día 22 y ahora es día 23.

**Solución**:
1. El sistema detectará la caja pendiente
2. Mostrará alerta: "ATENCIÓN: Tiene una caja abierta del 22/08/2025"
3. Debe cerrar esa caja primero
4. El cierre mantendrá la fecha original (22)
5. Luego podrá abrir la caja del día actual (23)

### Múltiples Intentos de Apertura

**Situación**: Intenta abrir caja cuando ya hay una abierta.

**Resultado**:
- El sistema bloqueará la operación
- Mensaje: "Ya existe una caja abierta para hoy"
- Debe cerrar la caja actual antes de abrir otra

### Diferencias de Efectivo

**Situación**: El conteo físico no coincide con lo esperado.

**Pasos**:
1. Ingrese el monto real contado
2. El sistema calculará la diferencia
3. Agregue notas explicando la discrepancia
4. Puede cerrar con diferencia (se registra)
5. Revise el reporte para investigación posterior

## Reportes y Consultas

### Ver Historial de Cierres

1. Navegue a **Caja → Historial**
2. Vea lista de cierres por fecha
3. Haga clic en una fecha para ver detalles

### Información Disponible:
- Fecha y hora de apertura/cierre
- Usuario que operó
- Totales de ventas y gastos
- Diferencias de efectivo
- Notas y observaciones

### Imprimir Reporte de Cierre

1. Abra el detalle del cierre
2. Haga clic en **Imprimir Reporte**
3. Se abrirá vista de impresión
4. Use Ctrl+P para imprimir

## Permisos y Roles

### Roles con Acceso:
- **Admin**: Acceso completo
- **Manager**: Acceso completo
- **Employee**: Sin acceso a gestión de caja

### Operaciones por Rol:

| Operación | Admin | Manager | Employee |
|-----------|-------|---------|----------|
| Abrir Caja | ✓ | ✓ | ✗ |
| Cerrar Caja | ✓ | ✓ | ✗ |
| Finalizar Cierre | ✓ | ✓ | ✗ |
| Ver Reportes | ✓ | ✓ | ✗ |
| Modificar Config | ✓ | ✗ | ✗ |

## Solución de Problemas

### Error: "La caja debe estar abierta"

**Causas**:
- No se abrió la caja del día
- La caja fue cerrada prematuramente

**Solución**:
1. Vaya a Caja → Abrir Caja
2. Abra la caja del día actual
3. Intente la operación nuevamente

### Error: "Existe una caja pendiente"

**Causas**:
- Caja de día anterior no cerrada

**Solución**:
1. Cierre la caja pendiente
2. Abra la nueva caja

### Diferencias Frecuentes

**Causas Comunes**:
- Pagos no registrados
- Gastos no documentados
- Errores de cambio
- Retiros no autorizados

**Prevención**:
- Registre todas las transacciones
- Mantenga recibos
- Haga arqueos parciales
- Limite acceso al efectivo

## Mejores Prácticas

### Apertura Diaria
1. Abra la caja primera hora del día
2. Verifique el efectivo inicial
3. Documente cualquier discrepancia inicial

### Durante el Día
1. Registre todas las transacciones inmediatamente
2. Guarde todos los comprobantes
3. Haga arqueos parciales si maneja mucho efectivo

### Cierre Diario
1. Cierre la caja antes de salir
2. Cuente el efectivo con cuidado
3. Documente cualquier diferencia
4. Finalice solo después de verificar
5. Imprima y archive el reporte

### Seguridad
1. No comparta credenciales
2. Cierre sesión al terminar
3. Guarde efectivo en lugar seguro
4. Reporte anomalías inmediatamente

## Configuración del Sistema

### Valores Configurables (Futuro Panel Admin):

1. **Saldo de Apertura Por Defecto**
   - Actual: $10,000.00
   - Modificable según necesidades del negocio

2. **Umbral de Diferencia Aceptable**
   - Actual: $100.00
   - Define qué diferencias son normales

3. **Requisito de Caja para Operaciones**
   - Ventas: Requerido
   - Entregas: Requerido
   - Configurable por tipo de operación

## Integración con Otros Módulos

### Ventas
- Todas las ventas se reflejan en el total diario
- Los pagos en efectivo afectan el conteo esperado
- Los créditos no afectan el efectivo

### Reparaciones
- Las entregas requieren caja abierta
- Los pagos de reparaciones se suman al efectivo
- Los anticipos se registran como ingresos

### Gastos
- Se restan del efectivo esperado
- Requieren documentación de respaldo
- Afectan el balance final

## Preguntas Frecuentes

**P: ¿Puedo modificar un cierre finalizado?**
R: No, los cierres finalizados son inmutables por seguridad contable.

**P: ¿Qué pasa si olvido cerrar la caja?**
R: Debe cerrarla antes de abrir la siguiente, mantendrá la fecha original.

**P: ¿Puedo tener múltiples cajas abiertas?**
R: No, el sistema permite solo una caja abierta a la vez.

**P: ¿Cómo cambio el saldo inicial por defecto?**
R: Actualmente es fijo en $10,000. Próximamente será configurable desde el panel admin.

**P: ¿Qué hago si hay una diferencia grande?**
R: Documente en las notas, cierre la caja e investigue. Puede requerir auditoría.

## Contacto y Soporte

Para problemas técnicos o preguntas adicionales:
- Contacte al administrador del sistema
- Revise los logs del sistema para errores
- Consulte la documentación técnica para detalles avanzados
