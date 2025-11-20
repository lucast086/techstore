# Plan de Cobertura de Tests - Sistema de Ventas TechStore

**Versión:** 1.1
**Fecha:** 2025-11-20
**Estado:** ✅ FASE 1 COMPLETADA | ✅ FASE 2 COMPLETADA (26/26 tests pasando - 100%)

---

## 📋 Objetivo

Garantizar cobertura completa de tests para todos los escenarios posibles de ventas en TechStore, asegurando que el sistema de pagos, créditos, y transacciones funcione correctamente en producción.

---

## 🔄 Flujo de Trabajo para Cada Test

### Proceso por Test:

```
1. SELECCIÓN → Elegir el próximo test de la lista de prioridades
2. IMPLEMENTACIÓN → Escribir el test siguiendo TDD
3. EJECUCIÓN → Correr el test (probablemente falle)
4. ANÁLISIS → Si falla, generar informe breve:
   - ¿Por qué falla?
   - ¿Cuál es la causa raíz?
   - ¿Cómo se puede solucionar?
5. REVISIÓN → Presentar informe al usuario para aprobación
6. CORRECCIÓN → Una vez aprobado, implementar la solución
7. VERIFICACIÓN → Confirmar que el test pasa
8. SIGUIENTE → Marcar como completado y pasar al siguiente test
```

### Criterios de Completitud por Test:
- ✅ Test implementado y documentado
- ✅ Test ejecuta sin errores
- ✅ Assertions cubren todos los casos esperados
- ✅ Código de producción corregido (si era necesario)
- ✅ Documentación del test actualizada

---

## 📊 Estado Actual

### Tests Existentes: 26 total
- ✅ **PASANDO: 26 tests** (100%)
- ✅ **FASE 1 COMPLETADA** (11/11 tests)
- ✅ **FASE 2 COMPLETADA** (15/15 tests)

### Historial de Correcciones

#### Primera Ronda (Tests 1-3):
- ✅ `test_full_payment_with_credit_exact_amount` - Actualizado para nuevo flujo
- ✅ `test_partial_credit_payment` - Actualizado para nuevo flujo
- ✅ `test_credit_payment_with_partial_sale_amount` - Corregido problema de redondeo

#### Segunda Ronda (Tests 4-6):
- ✅ `test_mixed_payment_credit_plus_cash` - Reescrito para nuevo flujo de pagos
- ✅ `test_credit_payment_creates_correct_transaction_records` - Actualizado assertions
- ✅ `test_no_double_credit_application` - Agregada validación anti-duplicados
- ✅ `test_blocked_account_cannot_use_credit` - Corregido manejo de timezones

#### Tests que ya pasaban:
- ✅ `test_insufficient_credit_error`
- ✅ `test_walk_in_customer_cannot_use_credit`
- ✅ `test_voided_sale_reverses_credit_usage` (pendiente verificación)

### Bug Crítico: ✅ CORREGIDO
El bug de doble registro de crédito está corregido en el código.

---

## 🎯 FASE 1: Corregir Tests Existentes ✅ COMPLETADA

### Prioridad: CRÍTICA
Estos tests ya existían pero estaban fallando. Todos han sido corregidos.

| # | Test | Ubicación | Estado | Commits |
|---|------|-----------|--------|---------|
| 1.1 | `test_mixed_payment_credit_plus_cash` | `test_credit_payment_flows.py` | ✅ PASA | 5117d96 |
| 1.2 | `test_credit_payment_creates_correct_transaction_records` | `test_credit_payment_flows.py` | ✅ PASA | 5117d96 |
| 1.3 | `test_voided_sale_reverses_credit_usage` | `test_credit_payment_flows.py` | ✅ PASA | - |
| 1.4 | `test_no_double_credit_application` | `test_credit_payment_flows.py` | ✅ PASA | 5117d96 |
| 1.5 | `test_blocked_account_cannot_use_credit` | `test_credit_payment_flows.py` | ✅ PASA | 5117d96 |

**✅ Objetivo Alcanzado:** 11/11 tests pasando (100%)

### Cambios Principales en Código de Producción:
1. **customer_account_service.py**: Validación anti-duplicados en `apply_credit()`
2. **customer_account.py**: Manejo de timezones en property `is_blocked`
3. **sale.py**: Simplificación del flujo (solo SALE transaction)
4. **sales.py**: Centralización de lógica de pagos

---

## 🎯 FASE 2: Tests Básicos de Ventas ✅ COMPLETADA (15/15 tests)

### Categoría: Pagos con Efectivo

| # | Nombre del Test | Descripción | Archivo | Estado |
|---|----------------|-------------|---------|--------|
| 2.1 | `test_cash_payment_full_walk_in` | Walk-in paga completo en efectivo | `test_basic_sales.py` | ✅ PASA |
| 2.2 | `test_cash_payment_full_registered_customer` | Cliente registrado paga completo en efectivo | `test_basic_sales.py` | ✅ PASA |
| 2.3 | `test_cash_overpayment_with_change` | Cliente da más efectivo, recibe cambio | `test_basic_sales.py` | ✅ PASA |
| 2.4 | `test_cash_partial_payment_creates_debt` | Cliente paga parcial en efectivo, genera deuda | `test_basic_sales.py` | ✅ PASA |
| 2.5 | `test_cash_zero_payment_full_debt` | Cliente no paga nada, deuda completa | `test_basic_sales.py` | ✅ PASA |

### Categoría: Pagos con Tarjeta

| # | Nombre del Test | Descripción | Archivo | Estado |
|---|----------------|-------------|---------|--------|
| 2.6 | `test_card_payment_full` | Pago completo con tarjeta | `test_basic_sales.py` | ✅ PASA |
| 2.7 | `test_card_payment_with_operation_number` | Tarjeta con número de operación | `test_basic_sales.py` | ✅ PASA |
| 2.8 | `test_card_partial_payment` | Pago parcial con tarjeta | `test_basic_sales.py` | ✅ PASA |

### Categoría: Pagos con Transferencia

| # | Nombre del Test | Descripción | Archivo | Estado |
|---|----------------|-------------|---------|--------|
| 2.9 | `test_transfer_payment_full` | Pago completo con transferencia | `test_basic_sales.py` | ✅ PASA |
| 2.10 | `test_transfer_with_reference_number` | Transferencia con número de referencia | `test_basic_sales.py` | ✅ PASA |
| 2.11 | `test_transfer_partial_payment` | Pago parcial con transferencia | `test_basic_sales.py` | ✅ PASA |

### Categoría: Pagos Mixtos Simples (sin crédito)

| # | Nombre del Test | Descripción | Archivo | Estado |
|---|----------------|-------------|---------|--------|
| 2.12 | `test_mixed_cash_and_card_full` | Efectivo + Tarjeta = Total | `test_mixed_payments.py` | ✅ PASA |
| 2.13 | `test_mixed_cash_and_transfer_full` | Efectivo + Transferencia = Total | `test_mixed_payments.py` | ✅ PASA |
| 2.14 | `test_mixed_card_and_transfer_full` | Tarjeta + Transferencia = Total | `test_mixed_payments.py` | ✅ PASA |
| 2.15 | `test_mixed_three_methods_full` | Efectivo + Tarjeta + Transferencia = Total | `test_mixed_payments.py` | ✅ PASA |

**✅ Objetivo Alcanzado:** 15/15 tests implementados y pasando (100%)

---

## 🎯 FASE 3: Tests de Productos y Precios (10 tests)

### Categoría: Modificación Manual de Precios ⭐ NUEVO

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 3.1 | `test_manual_price_override_single_product` | Modificar precio de un producto en carrito | `test_product_pricing.py` | P1 |
| 3.2 | `test_manual_price_higher_than_original` | Precio manual > precio catálogo | `test_product_pricing.py` | P1 |
| 3.3 | `test_manual_price_lower_than_original` | Precio manual < precio catálogo (descuento) | `test_product_pricing.py` | P1 |
| 3.4 | `test_manual_price_zero` | Precio manual = $0 (producto gratis) | `test_product_pricing.py` | P2 |
| 3.5 | `test_manual_price_with_tax_calculation` | Precio manual + impuesto correcto | `test_product_pricing.py` | P1 |

### Categoría: Múltiples Productos

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 3.6 | `test_multiple_products_same_item` | 5 unidades del mismo producto | `test_product_pricing.py` | P1 |
| 3.7 | `test_multiple_different_products` | 3+ productos diferentes | `test_product_pricing.py` | P1 |
| 3.8 | `test_mixed_physical_and_service_products` | Productos físicos + servicios | `test_product_pricing.py` | P2 |
| 3.9 | `test_product_without_sufficient_stock` | Stock insuficiente (debe fallar) | `test_product_pricing.py` | P1 |
| 3.10 | `test_service_product_no_stock_validation` | Servicio ignora validación de stock | `test_product_pricing.py` | P2 |

**Objetivo de Fase 3:** 10 tests nuevos implementados y pasando

---

## 🎯 FASE 4: Tests de Descuentos e Impuestos (12 tests)

### Categoría: Descuentos por Item

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 4.1 | `test_item_discount_percentage` | Descuento del 20% en un item | `test_discounts_taxes.py` | P1 |
| 4.2 | `test_item_discount_fixed_amount` | Descuento fijo $50 en un item | `test_discounts_taxes.py` | P1 |
| 4.3 | `test_item_discount_combined` | Porcentaje + monto fijo en un item | `test_discounts_taxes.py` | P2 |
| 4.4 | `test_item_discount_exceeds_price` | Descuento > precio (debe prevenir) | `test_discounts_taxes.py` | P2 |

### Categoría: Descuentos Globales

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 4.5 | `test_global_sale_discount` | Descuento aplicado a toda la venta | `test_discounts_taxes.py` | P1 |
| 4.6 | `test_global_and_item_discount_combined` | Descuentos item + global | `test_discounts_taxes.py` | P2 |
| 4.7 | `test_discount_distribution_multiple_items` | Distribución proporcional de descuento | `test_discounts_taxes.py` | P2 |

### Categoría: Impuestos

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 4.8 | `test_standard_tax_rate_10_percent` | Impuesto estándar 10% | `test_discounts_taxes.py` | P1 |
| 4.9 | `test_zero_tax_rate_exempt_product` | Producto exento de impuesto | `test_discounts_taxes.py` | P2 |
| 4.10 | `test_multiple_tax_rates_same_sale` | Productos con diferentes tasas | `test_discounts_taxes.py` | P2 |
| 4.11 | `test_tax_calculation_after_discount` | Impuesto sobre precio con descuento | `test_discounts_taxes.py` | P1 |
| 4.12 | `test_decimal_rounding_precision` | Redondeo correcto a 2 decimales | `test_discounts_taxes.py` | P1 |

**Objetivo de Fase 4:** 12 tests nuevos implementados y pasando

---

## 🎯 FASE 5: Tests de Balance y Crédito de Cliente (15 tests)

### Categoría: Cliente con Crédito Disponible

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 5.1 | `test_customer_credit_sufficient_exact` | Crédito = Total venta | `test_customer_balance.py` | ✅ EXISTE |
| 5.2 | `test_customer_credit_sufficient_excess` | Crédito > Total venta | `test_customer_balance.py` | ✅ EXISTE |
| 5.3 | `test_customer_credit_insufficient` | Crédito < Total venta (error) | `test_customer_balance.py` | ✅ EXISTE |
| 5.4 | `test_use_partial_credit_plus_cash` | Crédito parcial + efectivo | `test_customer_balance.py` | ❌ FALLA |
| 5.5 | `test_use_partial_credit_plus_card` | Crédito parcial + tarjeta | `test_customer_balance.py` | P1 |

### Categoría: Cliente con Deuda Existente

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 5.6 | `test_customer_with_debt_buys_more` | Deuda existente + nueva compra | `test_customer_balance.py` | P1 |
| 5.7 | `test_customer_pays_old_debt_and_new_purchase` | Pago deuda antigua + compra | `test_customer_balance.py` | P1 |
| 5.8 | `test_customer_exceeds_credit_limit` | Deuda + compra > límite | `test_customer_balance.py` | P1 |
| 5.9 | `test_customer_at_credit_limit_cannot_buy` | En el límite, no puede comprar | `test_customer_balance.py` | P1 |

### Categoría: Cliente con Balance Cero

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 5.10 | `test_first_purchase_creates_account` | Primera compra crea cuenta | `test_customer_balance.py` | P1 |
| 5.11 | `test_zero_balance_after_full_payment` | Balance = 0 después de saldar | `test_customer_balance.py` | P1 |

### Categoría: Cuenta Bloqueada

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 5.12 | `test_blocked_account_cannot_use_credit` | Cuenta bloqueada rechaza crédito | `test_customer_balance.py` | ❌ FALLA |
| 5.13 | `test_blocked_account_cash_payment_allowed` | Bloqueada acepta efectivo | `test_customer_balance.py` | P1 |
| 5.14 | `test_blocked_account_with_block_reason` | Razón de bloqueo registrada | `test_customer_balance.py` | P2 |
| 5.15 | `test_unblock_account_restores_credit` | Desbloquear restaura crédito | `test_customer_balance.py` | P2 |

**Objetivo de Fase 5:** 15 tests (algunos existen, completar los faltantes)

---

## 🎯 FASE 6: Tests de Transacciones y Registros (12 tests)

### Categoría: Registro de Transacciones

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 6.1 | `test_sale_transaction_recorded` | Transacción SALE registrada | `test_transactions.py` | ❌ FALLA |
| 6.2 | `test_payment_transaction_recorded` | Transacción PAYMENT registrada | `test_transactions.py` | P1 |
| 6.3 | `test_credit_application_transaction` | Transacción CREDIT_APPLICATION | `test_transactions.py` | ✅ EXISTE |
| 6.4 | `test_transaction_order_sale_then_payment` | Orden: SALE → PAYMENT | `test_transactions.py` | P1 |
| 6.5 | `test_balance_before_after_consistency` | balance_before/after correcto | `test_transactions.py` | P1 |

### Categoría: Prevención de Duplicados

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 6.6 | `test_no_double_credit_application` | No duplicar crédito | `test_transactions.py` | ❌ FALLA |
| 6.7 | `test_no_double_payment_recording` | No duplicar pago | `test_transactions.py` | P1 |
| 6.8 | `test_idempotent_sale_creation` | Crear venta es idempotente | `test_transactions.py` | P2 |

### Categoría: Auditoría y Trazabilidad

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 6.9 | `test_transaction_references_sale` | reference_type/id correctos | `test_transactions.py` | P1 |
| 6.10 | `test_transaction_created_by_user` | created_by_id registrado | `test_transactions.py` | P2 |
| 6.11 | `test_transaction_timestamps` | Timestamps correctos | `test_transactions.py` | P2 |
| 6.12 | `test_transaction_immutability` | Transacciones no se modifican | `test_transactions.py` | P2 |

**Objetivo de Fase 6:** 12 tests implementados y pasando

---

## 🎯 FASE 7: Tests de Cash Register (8 tests)

### Categoría: Caja Abierta

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 7.1 | `test_sale_with_open_cash_register` | Venta con caja abierta (OK) | `test_cash_register.py` | P1 |
| 7.2 | `test_cash_register_tracks_sales` | Caja registra ventas | `test_cash_register.py` | P1 |
| 7.3 | `test_cash_register_cash_only` | Solo efectivo afecta caja | `test_cash_register.py` | P1 |

### Categoría: Caja Cerrada

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 7.4 | `test_sale_with_closed_cash_register_fails` | Caja cerrada rechaza venta | `test_cash_register.py` | P1 |
| 7.5 | `test_cash_register_not_opened_today_fails` | Sin caja del día rechaza venta | `test_cash_register.py` | P1 |

### Categoría: Cierre de Caja

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 7.6 | `test_cash_register_closing_includes_sales` | Cierre incluye ventas del día | `test_cash_register.py` | P2 |
| 7.7 | `test_cash_register_closing_balance_correct` | Balance de cierre correcto | `test_cash_register.py` | P2 |
| 7.8 | `test_cannot_reopen_closed_register` | No reabrir caja cerrada | `test_cash_register.py` | P2 |

**Objetivo de Fase 7:** 8 tests implementados y pasando

---

## 🎯 FASE 8: Tests de Integración con Reparaciones (10 tests)

### Categoría: Depósitos de Reparación

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 8.1 | `test_repair_deposit_creates_credit` | Depósito crea crédito | `test_repair_integration.py` | P1 |
| 8.2 | `test_repair_deposit_applied_to_sale` | Depósito aplicado a venta final | `test_repair_integration.py` | P1 |
| 8.3 | `test_repair_partial_deposit_plus_cash` | Depósito parcial + efectivo | `test_repair_integration.py` | P1 |
| 8.4 | `test_repair_deposit_exceeds_final_cost` | Depósito > costo final | `test_repair_integration.py` | P2 |
| 8.5 | `test_repair_deposit_refund` | Reembolso de depósito | `test_repair_integration.py` | P2 |

### Categoría: Venta de Reparación

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 8.6 | `test_complete_repair_with_sale` | Completar reparación con venta | `test_repair_integration.py` | P1 |
| 8.7 | `test_repair_service_product_in_sale` | Producto de reparación en venta | `test_repair_integration.py` | P1 |
| 8.8 | `test_repair_delivery_updates_status` | Entrega actualiza estado | `test_repair_integration.py` | P2 |
| 8.9 | `test_repair_with_additional_parts` | Reparación + partes adicionales | `test_repair_integration.py` | P2 |
| 8.10 | `test_multiple_repairs_single_sale` | Múltiples reparaciones en una venta | `test_repair_integration.py` | P2 |

**Objetivo de Fase 8:** 10 tests implementados y pasando

---

## 🎯 FASE 9: Tests de Anulaciones y Reversas (8 tests)

### Categoría: Anulación de Ventas

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 9.1 | `test_void_sale_with_cash_payment` | Anular venta con efectivo | `test_void_operations.py` | P1 |
| 9.2 | `test_void_sale_with_credit_reverses` | Anular venta con crédito (reversa) | `test_void_operations.py` | ❌ FALLA |
| 9.3 | `test_void_partial_payment_sale` | Anular venta parcialmente pagada | `test_void_operations.py` | P1 |
| 9.4 | `test_void_sale_restores_inventory` | Anular restaura inventario | `test_void_operations.py` | P1 |
| 9.5 | `test_void_sale_updates_cash_register` | Anular actualiza caja | `test_void_operations.py` | P2 |

### Categoría: Notas de Crédito/Débito

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 9.6 | `test_credit_note_reduces_debt` | Nota de crédito reduce deuda | `test_void_operations.py` | P2 |
| 9.7 | `test_debit_note_increases_debt` | Nota de débito aumenta deuda | `test_void_operations.py` | P2 |
| 9.8 | `test_void_cannot_be_undone` | Anulación es permanente | `test_void_operations.py` | P2 |

**Objetivo de Fase 9:** 8 tests implementados y pasando

---

## 🎯 FASE 10: Tests de Casos Edge y Validaciones (15 tests)

### Categoría: Montos Extremos

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 10.1 | `test_sale_minimum_amount_one_cent` | Venta de $0.01 | `test_edge_cases.py` | P2 |
| 10.2 | `test_sale_maximum_amount` | Venta de $999,999.99 | `test_edge_cases.py` | P2 |
| 10.3 | `test_zero_amount_sale_rejected` | Venta $0 rechazada | `test_edge_cases.py` | P2 |

### Categoría: Datos Inválidos

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 10.4 | `test_nonexistent_customer_id_fails` | Customer_id inválido | `test_edge_cases.py` | P1 |
| 10.5 | `test_nonexistent_product_id_fails` | Product_id inválido | `test_edge_cases.py` | P1 |
| 10.6 | `test_negative_quantity_rejected` | Cantidad negativa rechazada | `test_edge_cases.py` | P1 |
| 10.7 | `test_negative_price_rejected` | Precio negativo rechazado | `test_edge_cases.py` | P1 |
| 10.8 | `test_discount_over_100_percent_rejected` | Descuento > 100% rechazado | `test_edge_cases.py` | P2 |
| 10.9 | `test_empty_cart_rejected` | Carrito vacío rechazado | `test_edge_cases.py` | P1 |

### Categoría: Concurrencia

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 10.10 | `test_concurrent_sales_same_customer` | Dos ventas simultáneas mismo cliente | `test_edge_cases.py` | P2 |
| 10.11 | `test_concurrent_credit_usage` | Uso de crédito concurrente | `test_edge_cases.py` | P2 |
| 10.12 | `test_race_condition_balance_update` | Race condition en balance | `test_edge_cases.py` | P2 |

### Categoría: Precisión Decimal

| # | Nombre del Test | Descripción | Archivo | Prioridad |
|---|----------------|-------------|---------|-----------|
| 10.13 | `test_decimal_precision_two_places` | Precisión 2 decimales | `test_edge_cases.py` | P1 |
| 10.14 | `test_rounding_tax_calculation` | Redondeo en impuestos | `test_edge_cases.py` | P1 |
| 10.15 | `test_accumulated_rounding_errors` | Errores de redondeo acumulados | `test_edge_cases.py` | P2 |

**Objetivo de Fase 10:** 15 tests implementados y pasando

---

## 📈 Resumen de Cobertura Total

| Fase | Categoría | Tests | Estado Actual | Objetivo |
|------|-----------|-------|---------------|----------|
| **FASE 1** | Corregir Existentes | 11 | ✅ 11/11 (100%) | ✅ 11/11 (100%) |
| **FASE 2** | Ventas Básicas | 15 | ✅ 15/15 (100%) | ✅ 15/15 (100%) |
| **FASE 3** | Productos y Precios | 10 | ⚪ 0/10 (0%) | ✅ 10/10 (100%) |
| **FASE 4** | Descuentos e Impuestos | 12 | ⚪ 0/12 (0%) | ✅ 12/12 (100%) |
| **FASE 5** | Balance y Crédito | 15 | ⚪ 0/15 (0%) | ✅ 15/15 (100%) |
| **FASE 6** | Transacciones | 12 | ⚪ 0/12 (0%) | ✅ 12/12 (100%) |
| **FASE 7** | Cash Register | 8 | ⚪ 0/8 (0%) | ✅ 8/8 (100%) |
| **FASE 8** | Reparaciones | 10 | ⚪ 0/10 (0%) | ✅ 10/10 (100%) |
| **FASE 9** | Anulaciones | 8 | ⚪ 0/8 (0%) | ✅ 8/8 (100%) |
| **FASE 10** | Casos Edge | 15 | ⚪ 0/15 (0%) | ✅ 15/15 (100%) |
| **TOTAL** | | **116 tests** | **26/116 (22.4%)** | **116/116 (100%)** |

---

## 🚀 Orden de Ejecución Recomendado

### Ciclo por Fase:
```
INICIO FASE
  ↓
  Para cada test en la fase:
    1. Implementar test
    2. Ejecutar test
    3. Si FALLA → Generar informe
    4. Revisar y aprobar solución
    5. Implementar corrección
    6. Verificar que pasa
    7. Marcar como ✅
  ↓
FIN FASE → Reporte de completitud
  ↓
SIGUIENTE FASE
```

### Prioridades (P0 > P1 > P2):
- **P0 (Crítico):** Debe funcionar para producción
- **P1 (Alto):** Funcionalidad esencial
- **P2 (Medio):** Casos edge y mejoras

---

## 📝 Plantilla de Informe por Test Fallido

Cuando un test falle, se generará un informe con este formato:

```markdown
## 🔴 Informe de Fallo: [Nombre del Test]

**Test:** `test_nombre_del_test`
**Archivo:** `tests/ruta/archivo.py`
**Fecha:** YYYY-MM-DD

### ❌ Error Observado
[Descripción breve del error que muestra pytest]

### 🔍 Causa Raíz
[Análisis de por qué está fallando]

### 🛠️ Solución Propuesta
[Descripción de cómo corregir]

**Archivos a Modificar:**
- `ruta/archivo1.py` (líneas X-Y)
- `ruta/archivo2.py` (líneas A-B)

**Cambios Específicos:**
1. [Cambio 1]
2. [Cambio 2]

### ⚠️ Impacto
[Impacto de la corrección en el sistema]

### ✅ Criterio de Aceptación
- [ ] Test pasa sin errores
- [ ] No rompe otros tests
- [ ] Lógica de negocio correcta

---
**Estado:** PENDIENTE APROBACIÓN
```

---

## 📊 Tracking de Progreso

### Completitud por Fase

```
FASE 1: [■■■■■■] 11/11  (100%)  - ✅ COMPLETADA
FASE 2: [■■■■■■] 15/15  (100%)  - ✅ COMPLETADA
FASE 3: [□□□□□□] 0/10   (0%)    - PENDIENTE
FASE 4: [□□□□□□] 0/12   (0%)    - PENDIENTE
FASE 5: [□□□□□□] 0/15   (0%)    - PENDIENTE
FASE 6: [□□□□□□] 0/12   (0%)    - PENDIENTE
FASE 7: [□□□□□□] 0/8    (0%)    - PENDIENTE
FASE 8: [□□□□□□] 0/10   (0%)    - PENDIENTE
FASE 9: [□□□□□□] 0/8    (0%)    - PENDIENTE
FASE 10:[□□□□□□] 0/15   (0%)    - PENDIENTE

TOTAL:  [■■□□□□□□□□] 26/116 (22.4%)
```

### Última Actualización
**Fecha:** 2025-11-20
**Tests Pasando:** 26/116 (22.4%)
**Tests Fallando:** 0/116
**Tests Pendientes:** 90/116

---

## 🎯 Próximo Paso

**✅ FASE 1 COMPLETADA - ✅ FASE 2 COMPLETADA**

**INICIAR FASE 3:** Tests de Productos y Precios (10 tests)

**Primer Test a Abordar:**
`test_manual_price_override_single_product` - Modificar precio de un producto en carrito

**Comando para ejecutar:**
```bash
poetry run pytest tests/test_product_pricing.py -xvs
```

---

## 📚 Referencias

- **Documento de Arquitectura:** `docs/technical/architecture-guide.md`
- **Plan de Refactor:** `docs/plan-refactor-payment-system.md`
- **Análisis de Producción:** `docs/production-readiness-analysis.md`
- **Feature Guide:** `docs/feature-implementation-guide.md`

---

**FIN DEL DOCUMENTO**
