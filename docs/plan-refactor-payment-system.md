# Plan: Refactorizar el Sistema de Pagos con Crédito

## Objetivo
Simplificar el flujo de ventas y pagos para que sea más robusto, fácil de mantener y maneje correctamente todos los escenarios (efectivo, crédito, mixto).

## Problema Actual
- Lógica compleja y duplicada entre `crud/sale.py` y `web/sales.py`
- Manejo especial inconsistente para `account_credit`
- Pagos mixtos no funcionan correctamente
- Código difícil de seguir y mantener

## Solución: Separar Responsabilidades

### Fase 1: Refactorizar `crud/sale.py`
1. **Simplificar creación de venta**:
   - Eliminar toda lógica especial para `account_credit`
   - Siempre registrar la venta completa en customer_account (crear deuda)
   - NO crear payments automáticamente
   - Solo manejar items, inventario y registro contable de la venta

2. **Resultado**: `create_sale()` solo crea la venta y registra la deuda

### Fase 2: Centralizar lógica de pagos en `web/sales.py`
1. **Después de crear la venta**, aplicar pagos según el tipo:
   - **Efectivo**: Crear Payment + registrar en balance
   - **Crédito total**: Usar crédito existente (NO crear Payment)
   - **Mixto**: Crear Payment por efectivo + usar crédito

2. **Validaciones previas**:
   - Verificar crédito disponible antes de crear la venta
   - Rechazar si no hay suficiente crédito para la parte correspondiente

### Fase 3: Crear servicio específico para aplicar crédito
1. **Nuevo método**: `customer_account_service.apply_credit_to_sale()`
   - Verificar crédito disponible
   - Aplicar crédito sin crear Payment
   - Actualizar balance directamente

### Fase 4: Testing exhaustivo
1. **Crear tests completos para**:
   - Pago total con efectivo
   - Pago total con crédito
   - Pago mixto (efectivo + crédito)
   - Crédito insuficiente
   - Casos edge (cliente sin cuenta, caja cerrada, etc.)

## Estructura Final del Flujo

```
web/sales.py:
├── Validar crédito disponible (si aplica)
├── create_sale() → Registra venta y deuda
├── Aplicar pagos según método:
│   ├── efectivo → create_payment() + record_payment()
│   ├── crédito → apply_credit_to_sale()
│   └── mixto → ambos anteriores
└── Actualizar status de la venta
```

## Beneficios
- ✅ Lógica clara y separada
- ✅ Fácil testing de cada componente
- ✅ Manejo robusto de pagos mixtos
- ✅ Menos bugs por duplicación
- ✅ Más fácil de mantener y extender

## Estado Actual (Base para próxima sesión)

### Lo que funciona actualmente:
- ✅ Pago total con crédito (test `test_credit_simple.py` pasa)
- ✅ Registro correcto de ventas en customer_accounts
- ✅ Balance del cliente se actualiza correctamente
- ✅ No hay duplicación de crédito

### Lo que necesita trabajo:
- ❌ Pagos mixtos (crédito + efectivo)
- ❌ Validación previa de crédito disponible
- ❌ Lógica duplicada entre archivos
- ❌ Testing exhaustivo de todos los escenarios

### Archivos involucrados:
- `src/app/crud/sale.py` - Lógica de creación de ventas
- `src/app/web/sales.py` - Endpoints web y manejo de pagos
- `src/app/services/customer_account_service.py` - Sistema de balances
- `src/app/services/payment_service.py` - Procesamiento de pagos
- `tests/test_credit_simple.py` - Test que funciona actualmente

### Próximos pasos recomendados:
1. Crear tests que fallen para pagos mixtos
2. Implementar validación previa de crédito
3. Refactorizar según el plan de fases
4. Validar todos los escenarios con tests
