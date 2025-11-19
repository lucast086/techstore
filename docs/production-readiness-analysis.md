# Análisis de Estado para Producción - Feature Accounts Receivable

**Fecha:** 2025-10-12
**Rama:** `feature/accounts-receivable-redesign`
**Branch base:** `main`

---

## 📊 Resumen Ejecutivo

### Estado General: ⚠️ NO LISTO PARA PRODUCCIÓN

**Razón Principal:** Bug crítico identificado en el sistema de pagos con crédito del cliente que causa registro incorrecto de deudas.

**Trabajo Pendiente Estimado:** 2-3 días de desarrollo y testing adicional

---

## ✅ Correcciones Implementadas

### 1. Fix: Registro correcto del monto total de ventas (Commit 80f0647)

**Problema Resuelto:**
- Pagos parciales en efectivo no registraban correctamente la deuda del cliente
- Solo se registraba el monto impago, causando inconsistencias

**Solución Implementada:**
```python
# ANTES: Solo registraba unpaid_amount
unpaid_amount = sale.total_amount - sale.paid_amount
if unpaid_amount > 0:
    record_sale(unpaid_amount)

# AHORA: Siempre registra el monto total
record_sale(sale.total_amount)  # Registra venta completa como deuda
record_payment(sale.paid_amount)  # Registra pago que reduce la deuda
```

**Impacto:**
- ✅ Contabilidad correcta de ventas parcialmente pagadas
- ✅ Separación clara entre transacciones de venta y pago
- ✅ Auditoría completa del flujo financiero

**Archivos Modificados:**
- `src/app/services/customer_account_service.py` (líneas 171-208)
- `src/app/templates/sales/pos.html` (líneas 1163-1220)
- `tests/integration/test_partial_payment_debt.py` (nuevo)

**Tests Agregados:**
- Test de pago parcial con efectivo
- Test de pago completo con efectivo
- Verificación de transacciones detalladas

---

### 2. Fix: Corrección de lógica de visualización de balances (Commit 972a89e)

**Problema Resuelto:**
- Inconsistencia entre balance mostrado en lista vs detalle de cliente
- Signos invertidos causando confusión
- Uso de sistema legacy `balance_service`

**Solución Implementada:**
- Eliminada completamente la dependencia de `balance_service`
- Unificado el uso de `customer_account_service` en todos los endpoints
- Corregida la lógica de visualización en templates

**Convención de Balances:**
```
Balance Positivo (+) = Cliente DEBE dinero (Accounts Receivable)
Balance Negativo (-) = Cliente TIENE CRÉDITO (Prepaid/Advance)
Balance Cero (0)     = Cuenta saldada
```

**Archivos Modificados:**
- `src/app/crud/customer.py` - Actualizado todos los métodos de balance
- `src/app/templates/customers/list.html` - Líneas 182, 188
- `src/app/templates/customers/detail.html` - Líneas 169, 183, 269-275

**Beneficios:**
- ✅ Consistencia en todas las páginas del sistema
- ✅ Eliminación de código legacy
- ✅ Claridad en la visualización para usuarios

---

### 3. Feature: Unificación del sistema de balances + UX del POS (Commit f2a53b9)

**Nuevas Funcionalidades:**

#### A. Sistema de Cuentas de Clientes
- Nueva arquitectura completa de cuentas por cobrar
- Registro transaccional detallado de todas las operaciones
- Trazabilidad completa de movimientos financieros

#### B. Sistema de Depósitos por Reparaciones
- Gestión de depósitos/anticipos para reparaciones
- Estados del depósito: ACTIVE, APPLIED, REFUNDED, VOIDED
- Integración con sistema de transacciones del cliente

#### C. Mejoras de UX en POS
- **Notificación automática de crédito disponible:**
  - Aparece cuando se selecciona cliente con crédito
  - Muestra monto disponible en verde
  - Botones de acción rápida: "Usar Saldo", "Pago Mixto", "Cerrar"
  - Auto-cierre después de 15 segundos

- **Pre-llenado inteligente en pagos mixtos:**
  - Calcula automáticamente: `Math.min(creditoDisponible, totalCarrito)`
  - Muestra crédito disponible junto al input
  - Facilita el flujo de pago para el cajero

- **Validación mejorada de crédito:**
  - Verificación en tiempo real de crédito disponible
  - Mensajes de error claros y específicos
  - Prevención de uso de crédito insuficiente

**Archivos Creados:**
- `src/app/models/customer_account.py` (260 líneas)
- `src/app/models/repair_deposit.py` (97 líneas)
- `src/app/crud/customer_account.py` (398 líneas)
- `src/app/crud/repair_deposit.py` (426 líneas)
- `src/app/services/customer_account_service.py` (641 líneas)
- `src/app/services/repair_deposit_service.py` (435 líneas)
- `src/app/api/v1/customer_accounts.py` (405 líneas)
- `src/app/web/customer_accounts.py` (377 líneas)
- Templates para overview, statement, transaction list

**Archivos Modificados Significativamente:**
- `src/app/web/sales.py` (370 líneas modificadas)
- `src/app/templates/sales/pos.html` (283 líneas añadidas)
- `src/app/crud/sale.py` (98 líneas modificadas)
- `src/app/web/customers.py` (126 líneas modificadas)

**Tests Agregados:**
- `tests/integration/test_cash_closing_credit_scenario.py` (279 líneas)
- `tests/integration/test_repair_delivery_credit.py` (491 líneas)
- `tests/integration/test_repair_deposit_flow.py` (526 líneas)
- `tests/unit/services/test_customer_credit_behavior.py` (250 líneas)
- `tests/unit/services/test_repair_deposit_service.py` (240 líneas)

---

## 🐛 Bug Crítico Identificado

### Problema: Pagos con Crédito del Cliente Registran Deuda Incorrecta

**Descripción del Bug:**
Cuando un cliente usa su crédito disponible para pagar una venta, el sistema:
1. ✅ Consume el crédito correctamente (transacción de tipo `CREDIT_APPLICATION`)
2. ❌ PERO también registra la venta completa como nueva deuda
3. ❌ **Resultado:** Cliente termina debiendo dinero aunque pagó con su crédito

**Ejemplo Concreto:**
```
Estado Inicial:
- Cliente tiene: $1,000 de crédito (account_balance = -$1,000)

Operación:
- Cliente compra: $1,000 de productos
- Método de pago: "account_credit" (usa su crédito)

Flujo del Sistema:
1. Transacción CREDIT_APPLICATION: -$1,000 + $1,000 = $0 ✅
2. Transacción SALE: $0 + $1,000 = +$1,000 ❌

Resultado Actual:
- Balance final: +$1,000 (¡Cliente DEBE dinero!)

Resultado Esperado:
- Balance final: $0 (cuenta saldada)
```

**Causa Raíz:**
El commit 80f0647 cambió la lógica para SIEMPRE registrar el monto total de ventas (correcto para pagos en efectivo), pero esto rompe el flujo de pagos con crédito porque:
- El crédito ya se consume (balance aumenta)
- La venta se registra completa (balance aumenta de nuevo)
- = Doble registro del mismo monto

**Evidencia:**
- Test `test_credit_payment_flows.py` falla consistentemente
- Documentado en `tests/test_credit_payment_flows_findings.md`
- Documentado en `tests/CREDIT_PAYMENT_TEST_SUMMARY.md`

**Impacto:**
- 🔴 **CRÍTICO:** Sistema de pagos con crédito completamente inutilizable
- 🔴 Afecta flujo principal de ventas en POS
- 🔴 Puede causar pérdida de confianza en reportes financieros
- 🔴 Clientes con crédito no pueden usar su saldo correctamente

**Archivos Afectados:**
- `src/app/services/customer_account_service.py` - Método `record_sale()`
- `src/app/crud/sale.py` - Lógica de creación de venta
- `src/app/web/sales.py` - Endpoint de checkout

---

## 🗄️ Impacto en Base de Datos de Producción

### Cambios de Esquema (Migraciones Alembic)

#### Nuevas Tablas que se Crearán:

**1. `customer_accounts`**
```sql
- id (PK)
- customer_id (FK → customers.id, UNIQUE)
- credit_limit (DECIMAL 10,2)
- available_credit (DECIMAL 10,2)
- account_balance (DECIMAL 10,2) -- Saldo actual
- total_sales, total_payments, total_credit_notes, total_debit_notes
- last_transaction_date, last_payment_date
- transaction_count (INT)
- is_active (BOOLEAN)
- blocked_until (DATETIME), block_reason (TEXT)
- notes (TEXT)
- created_by_id, updated_by_id (FK → users.id)
- created_at, updated_at (TIMESTAMP WITH TIMEZONE)

Índices:
- idx_customer_account_activity (last_transaction_date, is_active)
- idx_customer_account_balance (account_balance, is_active)
- ix_customer_accounts_id
- ix_customer_accounts_account_balance
```

**2. `customer_transactions`**
```sql
- id (PK)
- customer_id (FK → customers.id)
- account_id (FK → customer_accounts.id)
- transaction_type (ENUM) -- SALE, PAYMENT, CREDIT_NOTE, etc.
- amount (DECIMAL 10,2)
- balance_before, balance_after (DECIMAL 10,2)
- reference_type (VARCHAR 50), reference_id (INT)
- description (VARCHAR 200)
- notes (TEXT)
- transaction_date (DATETIME)
- created_by_id (FK → users.id)
- created_at (TIMESTAMP WITH TIMEZONE)

Constraints:
- uq_transaction_immutable (id, created_at) -- Inmutabilidad

Índices:
- idx_customer_trans_date (customer_id, transaction_date)
- idx_customer_trans_ref (reference_type, reference_id)
- idx_customer_trans_type (customer_id, transaction_type)
- ix_customer_transactions_customer_id
- ix_customer_transactions_id
- ix_customer_transactions_transaction_date
- ix_customer_transactions_transaction_type
```

**3. `repair_deposits`**
```sql
- id (PK)
- repair_id (FK → repairs.id)
- customer_id (FK → customers.id)
- sale_id (FK → sales.id, NULLABLE)
- amount (NUMERIC 10,2)
- payment_method (ENUM) -- CASH, CARD, TRANSFER, CHECK, OTHER
- receipt_number (VARCHAR 50)
- status (ENUM) -- ACTIVE, APPLIED, REFUNDED, VOIDED
- refunded_amount (NUMERIC 10,2), refund_date, refund_reason, refunded_by_id
- transaction_id (FK → customer_transactions.id)
- notes (TEXT)
- received_by_id (FK → users.id)
- created_at, updated_at (TIMESTAMP WITH TIMEZONE)

Índices:
- idx_repair_deposits_repair
- idx_repair_deposits_customer
- idx_repair_deposits_status
- ix_repair_deposits_id
```

#### Nuevos Tipos ENUM:

**1. `TransactionType`**
```sql
'SALE'               -- Venta (aumenta deuda)
'PAYMENT'            -- Pago (reduce deuda)
'CREDIT_NOTE'        -- Nota de crédito (reduce deuda)
'DEBIT_NOTE'         -- Nota de débito (aumenta deuda)
'CREDIT_APPLICATION' -- Aplicación de crédito prepagado
'OPENING_BALANCE'    -- Balance inicial
'ADJUSTMENT'         -- Ajuste manual
'REPAIR_DEPOSIT'     -- Depósito de reparación
```

**2. `DepositStatus`**
```sql
'ACTIVE'    -- Depósito activo, no usado
'APPLIED'   -- Aplicado a una venta
'REFUNDED'  -- Reembolsado al cliente
'VOIDED'    -- Anulado
```

**3. `PaymentMethod`** (para repair_deposits)
```sql
'CASH'      -- Efectivo
'CARD'      -- Tarjeta
'TRANSFER'  -- Transferencia
'CHECK'     -- Cheque
'OTHER'     -- Otro
```

#### Modificaciones a Tablas Existentes:
- ✅ **Ninguna tabla existente será modificada destructivamente**
- ✅ Solo se agregan relaciones FK desde las nuevas tablas
- ✅ No hay pérdida de datos en tablas actuales

#### Migraciones Alembic Pendientes:
```
eeaba3b9fb9f - fix customer_transaction created_at field (HEAD)
2f6b7ca83c23 - fix_customer_transactions_created_at_default
cdf3f4a27197 - add_repair_deposit_to_transaction_type_enum
21c7a72117d8 - Add performance indexes for repair deposits
ab0541798b68 - Add is_service field to products
94cd63111bbe - Add repair deposits system
4447d3d7b467 - Merge customer accounts branch
add_customer_accounts - Add customer accounts and transactions tables
```

---

## 📋 Plan de Migración: Pasos para No Perder Datos

### FASE 1: PRE-MIGRACIÓN (Preparación)

#### 1.1. Backup Completo de Base de Datos
```bash
# En servidor de producción
pg_dump -h localhost -U postgres -d techstore_production \
  -F c -b -v -f "backup_pre_migration_$(date +%Y%m%d_%H%M%S).dump"

# Verificar integridad del backup
pg_restore --list backup_pre_migration_YYYYMMDD_HHMMSS.dump | head -20

# Almacenar en ubicación segura (S3, backup server, etc.)
```

**Checklist:**
- [ ] Backup creado exitosamente
- [ ] Verificada integridad del backup
- [ ] Backup almacenado en ubicación segura
- [ ] Probada restauración en ambiente de prueba
- [ ] Documentado procedimiento de rollback

---

#### 1.2. Análisis de Datos Actuales

**Script: `scripts/analyze_production_data.py`** (CREAR)

```python
# Este script debe generar un reporte con:
1. Total de clientes en el sistema
2. Clientes con ventas pendientes de pago (paid_amount < total_amount)
3. Total de saldo pendiente por cobrar
4. Ventas con pagos parciales (lista detallada)
5. Pagos históricos sin customer_id (walk-in customers)
6. Reparaciones con depósitos no formalizados
7. Inconsistencias entre sales.paid_amount y payments.amount
```

**Output Esperado:** `production_data_analysis_YYYYMMDD.json`

**Checklist:**
- [ ] Script creado y probado en staging
- [ ] Reporte generado de producción
- [ ] Identificados clientes con saldo pendiente
- [ ] Identificadas ventas parcialmente pagadas
- [ ] Documentadas inconsistencias (si existen)

---

#### 1.3. Cálculo de Balances Iniciales

**Script: `scripts/calculate_initial_balances.py`** (CREAR)

```python
# Para cada cliente, calcular:
for customer in all_customers:
    total_sales = sum(sales where customer_id = customer.id)
    total_paid = sum(payments where customer_id = customer.id)
    initial_balance = total_sales - total_paid

    # Validar:
    if initial_balance < 0:
        # Cliente tiene crédito (pagó de más o anticipos)
        log_warning(f"Cliente {customer.id} tiene crédito: {initial_balance}")

    # Guardar para migración
    save_initial_balance(customer.id, initial_balance)
```

**Output Esperado:** `initial_balances_YYYYMMDD.csv`

**Checklist:**
- [ ] Script creado y probado
- [ ] Balances calculados para todos los clientes
- [ ] Identificados clientes con crédito (balance negativo)
- [ ] Validación: sum(initial_balances) == total_accounts_receivable
- [ ] Archivo CSV generado y revisado

---

### FASE 2: MIGRACIÓN (Ejecución)

#### 2.1. Aplicar Migraciones de Alembic

```bash
# En staging primero (OBLIGATORIO)
cd /app
poetry run alembic upgrade head

# Verificar que se crearon las tablas
psql -U postgres -d techstore_staging -c "\dt customer*"
psql -U postgres -d techstore_staging -c "\dt repair_deposits"

# Si todo OK, aplicar en producción
# (Durante ventana de mantenimiento)
poetry run alembic upgrade head
```

**Checklist:**
- [ ] Migraciones aplicadas en staging sin errores
- [ ] Verificadas todas las tablas creadas
- [ ] Verificados todos los índices creados
- [ ] Verificadas constraints y FKs
- [ ] Aplicadas en producción exitosamente

---

#### 2.2. Crear Customer Accounts Iniciales

**Script: `scripts/migrate_customer_accounts.py`** (CREAR)

```python
# Para cada cliente existente:
1. Crear registro en customer_accounts
2. Establecer credit_limit = 0 (valor por defecto)
3. Calcular y establecer available_credit
4. Establecer account_balance desde archivo CSV (paso 1.3)
5. Calcular total_sales y total_payments históricos
6. Establecer last_transaction_date, last_payment_date
7. Establecer is_active = True
8. Establecer created_by_id = SYSTEM_USER_ID
```

**Checklist:**
- [ ] Script creado y probado en staging
- [ ] Customer account creado para cada cliente
- [ ] Balances iniciales correctamente cargados
- [ ] Validación: count(customer_accounts) == count(customers)
- [ ] Sin errores de FK constraints

---

#### 2.3. Generar Transacciones Históricas

**Script: `scripts/generate_historical_transactions.py`** (CREAR)

**Opción A: Balance Neto Únicamente** (Recomendado - más simple)
```python
# Para cada cliente con balance != 0:
if initial_balance != 0:
    create_customer_transaction(
        type = "OPENING_BALANCE",
        amount = abs(initial_balance),
        balance_before = 0,
        balance_after = initial_balance,
        description = "Balance inicial del sistema legacy",
        transaction_date = migration_date
    )
```

**Opción B: Transacciones Detalladas** (Opcional - más completo)
```python
# Para cada venta histórica:
for sale in historic_sales:
    create_customer_transaction(
        type = "SALE",
        amount = sale.total_amount,
        reference_type = "sale",
        reference_id = sale.id,
        description = f"Venta #{sale.id}",
        transaction_date = sale.created_at
    )

# Para cada pago histórico:
for payment in historic_payments:
    create_customer_transaction(
        type = "PAYMENT",
        amount = payment.amount,
        reference_type = "payment",
        reference_id = payment.id,
        description = f"Pago {payment.payment_type}",
        transaction_date = payment.payment_date
    )
```

**Checklist:**
- [ ] Decidida estrategia (Opción A vs Opción B)
- [ ] Script creado y probado
- [ ] Transacciones generadas para todos los clientes
- [ ] Validación: balance_after de última transacción == account_balance
- [ ] Sin inconsistencias en balance_before/balance_after

---

#### 2.4. Migrar Depósitos de Reparaciones

**Script: `scripts/migrate_repair_deposits.py`** (CREAR)

```python
# Identificar reparaciones con depósitos:
# (Puede requerir análisis manual si no está estructurado)

# Posibles fuentes:
1. Campo "notes" en repairs con menciones de depósito/anticipo
2. Pagos con descripción que indique depósito
3. Consulta manual a usuarios del sistema

# Para cada depósito identificado:
create_repair_deposit(
    repair_id = repair.id,
    customer_id = repair.customer_id,
    amount = deposit_amount,
    payment_method = "CASH",  # O el que corresponda
    status = "ACTIVE" if not used else "APPLIED",
    notes = "Migrado desde sistema legacy"
)

# Crear transacción correspondiente:
create_customer_transaction(
    type = "REPAIR_DEPOSIT",
    amount = deposit_amount,
    description = f"Depósito reparación #{repair.id}"
)
```

**Checklist:**
- [ ] Identificados todos los depósitos pendientes
- [ ] Validados con equipo operativo
- [ ] Depósitos migrados a nuevo sistema
- [ ] Transacciones creadas correctamente
- [ ] Balance de clientes ajustado por depósitos

---

### FASE 3: POST-MIGRACIÓN (Validación)

#### 3.1. Validación de Integridad de Datos

**Script: `scripts/validate_migration.py`** (CREAR)

```python
# Tests de validación:

1. Validar conteos:
   assert count(customer_accounts) == count(customers)
   assert count(customers with balance != 0) == count(opening_balance_transactions)

2. Validar balances:
   for customer in all_customers:
       account_balance = customer.account.account_balance
       calculated_balance = sum(transactions)
       assert account_balance == calculated_balance

3. Validar totales:
   system_total_ar = sum(all account_balances where balance > 0)
   legacy_total_ar = sum(sales.total - sales.paid)
   assert abs(system_total_ar - legacy_total_ar) < tolerance

4. Validar FKs:
   assert all customer_accounts.customer_id IN customers.id
   assert all customer_transactions.customer_id IN customers.id
   assert all repair_deposits.repair_id IN repairs.id

5. Validar constraints:
   assert no customer with multiple customer_accounts (UNIQUE constraint)
   assert all transactions have balance_before/balance_after consistent
```

**Checklist:**
- [ ] Todos los tests de validación pasan
- [ ] No hay inconsistencias en balances
- [ ] Totales coinciden con sistema legacy (dentro de tolerancia)
- [ ] No hay violaciones de constraints
- [ ] Revisión manual de casos edge

---

#### 3.2. Pruebas Funcionales en Staging

**Casos de prueba:**

1. **Crear nueva venta con pago completo en efectivo**
   - [ ] Venta se crea correctamente
   - [ ] Transacciones registradas (SALE + PAYMENT)
   - [ ] Balance del cliente no cambia (venta pagada)
   - [ ] Payment registrado correctamente

2. **Crear venta parcialmente pagada**
   - [ ] Venta se crea correctamente
   - [ ] Transacciones registradas (SALE + PAYMENT)
   - [ ] Balance del cliente aumenta por monto impago
   - [ ] Balance visible en customer detail

3. **Pagar deuda existente**
   - [ ] Cliente con balance > 0
   - [ ] Registrar pago
   - [ ] Transacción PAYMENT creada
   - [ ] Balance reducido correctamente
   - [ ] Visible en statement del cliente

4. **Cliente con crédito hace compra**
   - [ ] Cliente con balance < 0 (crédito disponible)
   - [ ] Hacer venta usando crédito
   - [ ] ⚠️ **ESTE TEST FALLARÁ HASTA CORREGIR EL BUG**
   - [ ] Balance debería ajustarse correctamente

5. **Depósito de reparación**
   - [ ] Crear reparación
   - [ ] Registrar depósito
   - [ ] Transacción REPAIR_DEPOSIT creada
   - [ ] Balance cliente ajustado (crédito)
   - [ ] Visible en repair detail

6. **Reportes financieros**
   - [ ] Dashboard muestra métricas correctas
   - [ ] Customer statement genera PDF
   - [ ] Account overview muestra transacciones
   - [ ] Cash closing incluye transacciones de cuenta

**Checklist:**
- [ ] Todos los casos de prueba ejecutados
- [ ] Documentados bugs encontrados (si hay)
- [ ] Flujos principales funcionan correctamente
- [ ] UX es intuitiva para usuarios finales
- [ ] Performance es aceptable (queries optimizados)

---

#### 3.3. Comparación de Reportes Before/After

**Generar reportes comparativos:**

```sql
-- Reporte ANTES de migración (desde backup)
SELECT
    'Legacy System' as source,
    COUNT(DISTINCT customer_id) as customers_with_debt,
    SUM(total_amount - paid_amount) as total_accounts_receivable,
    AVG(total_amount - paid_amount) as avg_debt_per_customer
FROM sales
WHERE paid_amount < total_amount;

-- Reporte DESPUÉS de migración (desde nuevo sistema)
SELECT
    'New System' as source,
    COUNT(*) as customers_with_debt,
    SUM(account_balance) as total_accounts_receivable,
    AVG(account_balance) as avg_debt_per_customer
FROM customer_accounts
WHERE account_balance > 0;

-- Comparar y documentar diferencias
```

**Checklist:**
- [ ] Reportes generados de ambos sistemas
- [ ] Diferencias documentadas y explicadas
- [ ] Diferencias están dentro de tolerancia aceptable
- [ ] Aprobación de gerencia/contabilidad

---

### FASE 4: ROLLBACK (Plan de Contingencia)

#### 4.1. Criterios para Rollback

**Ejecutar rollback SI:**
- Pérdida de datos críticos detectada
- Inconsistencias graves en balances (> 5% diferencia)
- Sistema de ventas no funciona (errores críticos)
- Performance inaceptable (> 5 segundos para operaciones básicas)
- Bugs críticos en producción que impiden operación normal

**NO ejecutar rollback SI:**
- Bugs menores en UX (pueden corregirse en caliente)
- Performance ligeramente degradada (puede optimizarse después)
- Pequeñas inconsistencias documentadas y explicadas

---

#### 4.2. Procedimiento de Rollback

```bash
# PASO 1: Detener aplicación
systemctl stop techstore-app

# PASO 2: Revertir migraciones de Alembic
cd /app
poetry run alembic downgrade [revision_before_migration]

# PASO 3: Verificar que tablas nuevas fueron eliminadas
psql -U postgres -d techstore_production -c "\dt customer*"
# No debería mostrar: customer_accounts, customer_transactions

# PASO 4: Restaurar backup (si es necesario)
pg_restore -h localhost -U postgres -d techstore_production \
  -c -v backup_pre_migration_YYYYMMDD_HHMMSS.dump

# PASO 5: Verificar integridad post-restauración
psql -U postgres -d techstore_production -c "SELECT COUNT(*) FROM customers;"
psql -U postgres -d techstore_production -c "SELECT COUNT(*) FROM sales;"
psql -U postgres -d techstore_production -c "SELECT SUM(total_amount - paid_amount) FROM sales;"

# PASO 6: Reiniciar aplicación con código anterior
git checkout [commit_before_feature]
systemctl start techstore-app

# PASO 7: Verificar que aplicación funciona
curl http://localhost:8000/health
```

**Checklist:**
- [ ] Procedimiento de rollback documentado
- [ ] Probado en staging
- [ ] Equipo capacitado para ejecutarlo
- [ ] Tiempo estimado de rollback: < 30 minutos

---

### FASE 5: MONITOREO POST-DESPLIEGUE

#### 5.1. Monitoreo Técnico (Primeras 48 horas)

**Logs a Monitorear:**
```bash
# Errores de aplicación
tail -f /var/log/techstore/app.log | grep ERROR

# Errores de base de datos
tail -f /var/log/postgresql/postgresql.log | grep ERROR

# Performance de queries
# (Habilitar pg_stat_statements)
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%customer_account%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Métricas a Vigilar:**
- [ ] Tiempo de respuesta de endpoints de venta (target: < 1 seg)
- [ ] Tiempo de respuesta de customer detail (target: < 2 seg)
- [ ] Errores 500 (target: 0)
- [ ] Errores de validación de crédito (documentar si hay)
- [ ] Queries lentos (> 2 segundos)

---

#### 5.2. Monitoreo de Negocio (Primera Semana)

**Validaciones Diarias:**

**Día 1:**
- [ ] Primeras 10 ventas revisadas manualmente
- [ ] Balances de clientes verificados con cajeros
- [ ] Reportes financieros comparados con día anterior
- [ ] Feedback de usuarios recolectado

**Día 2-3:**
- [ ] Comparación de reportes de cuentas por cobrar
- [ ] Revisión de casos edge reportados por usuarios
- [ ] Ajustes menores si son necesarios
- [ ] Documentación de workarounds (si aplica)

**Día 4-7:**
- [ ] Análisis de métricas de negocio (ventas, pagos, créditos)
- [ ] Comparación con semana anterior
- [ ] Identificación de mejoras de UX
- [ ] Planificación de optimizaciones

---

#### 5.3. Capacitación y Soporte

**Pre-Despliegue:**
- [ ] Manual de usuario actualizado
- [ ] Video tutorial de nuevas funcionalidades
- [ ] Sesión de capacitación con cajeros/vendedores
- [ ] Sesión de capacitación con contabilidad/gerencia
- [ ] FAQ documentado

**Post-Despliegue:**
- [ ] Soporte dedicado disponible primeras 48 horas
- [ ] Canal de comunicación directo (WhatsApp/Slack)
- [ ] Registro de issues reportados
- [ ] Respuestas a preguntas frecuentes
- [ ] Actualización de documentación según feedback

---

## 🔧 Tareas Críticas Pendientes

### 1. Corregir Bug de Pagos con Crédito

**Prioridad:** 🔴 CRÍTICA
**Esfuerzo Estimado:** 4-6 horas
**Bloqueante para producción:** SÍ

**Enfoque Recomendado:**

**Opción A: Lógica Condicional en `record_sale()`**
```python
def record_sale(sale: Sale, db: Session):
    """Record sale in customer account."""

    # Si la venta fue pagada COMPLETAMENTE con crédito,
    # NO registrar como nueva deuda (el crédito ya se consumió)
    if sale.payment_method == "account_credit" and sale.paid_amount >= sale.total_amount:
        logger.info(f"Sale {sale.id} paid entirely with credit, skipping sale transaction")
        return

    # Para ventas con efectivo o parcialmente pagadas, registrar normalmente
    create_transaction(
        type="SALE",
        amount=sale.total_amount,
        description=f"Venta #{sale.id}"
    )
```

**Opción B: Separar Flujo de Credit Sales**
```python
# En web/sales.py:
if payment_method == "account_credit":
    # Flujo especial para crédito
    sale = create_sale(...)  # Sin registrar en customer_account
    apply_credit_to_sale(sale, amount)  # Solo consume crédito
else:
    # Flujo normal
    sale = create_sale(...)  # Registra deuda
    if amount_paid > 0:
        record_payment(...)  # Reduce deuda
```

**Tests Necesarios:**
- [ ] Pago completo con crédito (balance antes: -$1000, después: $0)
- [ ] Pago parcial con crédito (balance antes: -$500, venta $1000, después: +$500)
- [ ] Pago mixto efectivo+crédito (verificar ambas transacciones)
- [ ] Crédito insuficiente (debe rechazar)

**Archivos a Modificar:**
- `src/app/services/customer_account_service.py`
- `src/app/crud/sale.py` (posiblemente)
- `src/app/web/sales.py` (posiblemente)
- `tests/test_credit_payment_flows.py` (actualizar para que pasen)

---

### 2. Crear Scripts de Migración de Datos

**Prioridad:** 🟠 ALTA
**Esfuerzo Estimado:** 8-12 horas
**Bloqueante para producción:** SÍ

**Scripts a Crear:**
- [ ] `scripts/analyze_production_data.py`
- [ ] `scripts/calculate_initial_balances.py`
- [ ] `scripts/migrate_customer_accounts.py`
- [ ] `scripts/generate_historical_transactions.py`
- [ ] `scripts/migrate_repair_deposits.py`
- [ ] `scripts/validate_migration.py`

**Cada script debe:**
- Tener logging detallado
- Generar reporte de ejecución
- Ser idempotente (poder ejecutarse múltiples veces)
- Tener modo dry-run para pruebas
- Incluir validaciones de datos

---

### 3. Testing Exhaustivo en Staging

**Prioridad:** 🟠 ALTA
**Esfuerzo Estimado:** 6-8 horas
**Bloqueante para producción:** SÍ

**Cobertura Necesaria:**
- [ ] Unit tests: > 80% coverage en services
- [ ] Integration tests: Todos los flujos principales
- [ ] End-to-end tests: Casos reales de usuarios
- [ ] Performance tests: Queries optimizados
- [ ] Migration tests: Scripts en clon de producción

**Tests Críticos a Agregar:**
- [ ] Test de migración completa (desde cero)
- [ ] Test de rollback
- [ ] Test de performance con 1000+ clientes
- [ ] Test de concurrencia (múltiples ventas simultáneas)

---

### 4. Documentación de Usuario

**Prioridad:** 🟡 MEDIA
**Esfuerzo Estimado:** 4-6 horas
**Bloqueante para producción:** NO (pero recomendado)

**Documentos a Crear:**
- [ ] Manual de usuario: Nuevas funcionalidades de crédito
- [ ] Guía rápida: POS con clientes con crédito
- [ ] FAQ: Preguntas frecuentes anticipadas
- [ ] Video tutorial: Flujo completo de venta con crédito
- [ ] Troubleshooting guide: Problemas comunes

---

### 5. Plan de Comunicación

**Prioridad:** 🟡 MEDIA
**Esfuerzo Estimado:** 2-3 horas
**Bloqueante para producción:** NO (pero recomendado)

**Comunicaciones Necesarias:**
- [ ] Notificación de ventana de mantenimiento (48 horas antes)
- [ ] Email a usuarios sobre nuevas funcionalidades
- [ ] Agenda de capacitación
- [ ] Canales de soporte durante migración
- [ ] Anuncio post-migración exitosa

---

## 📊 Resumen de Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Bug crítico de crédito causa pérdidas | Alta | Crítico | Corregir antes de despliegue |
| Pérdida de datos durante migración | Baja | Crítico | Backups + validación exhaustiva |
| Balances incorrectos post-migración | Media | Alto | Scripts de validación + comparación |
| Performance degradada | Media | Medio | Índices optimizados + monitoring |
| Usuarios confundidos con nuevo sistema | Media | Medio | Capacitación + documentación |
| Necesidad de rollback | Baja | Alto | Procedimiento probado en staging |
| Depósitos históricos no migrados | Media | Medio | Análisis manual + validación |

---

## ✅ Checklist de Production-Ready

### Código y Funcionalidad
- [ ] Bug crítico de pagos con crédito **CORREGIDO**
- [ ] Todos los tests unitarios pasan
- [ ] Todos los tests de integración pasan
- [ ] Coverage de tests > 80%
- [ ] Linting sin errores (ruff check)
- [ ] Formatting correcto (ruff format)
- [ ] No hay TODOs críticos en código
- [ ] Code review completado por al menos 1 desarrollador

### Base de Datos
- [ ] Migraciones Alembic probadas en staging
- [ ] Scripts de migración de datos creados
- [ ] Scripts de migración probados con datos reales clonados
- [ ] Validación de integridad de datos ejecutada
- [ ] Performance de queries optimizada (< 2 seg)
- [ ] Índices correctamente creados
- [ ] Backup de producción realizado

### Testing
- [ ] Tests manuales en staging completados
- [ ] Casos de prueba de negocio validados
- [ ] Performance testing ejecutado
- [ ] Stress testing ejecutado (múltiples usuarios simultáneos)
- [ ] Migration testing exitoso (end-to-end)
- [ ] Rollback testing exitoso

### Documentación
- [ ] Manual de usuario actualizado
- [ ] Documentación técnica actualizada
- [ ] README con instrucciones de migración
- [ ] FAQ creado
- [ ] Video tutorial grabado (opcional)
- [ ] Changelog actualizado

### Operaciones
- [ ] Plan de migración documentado
- [ ] Procedimiento de rollback documentado y probado
- [ ] Ventana de mantenimiento programada
- [ ] Equipo de soporte asignado
- [ ] Monitoreo post-despliegue configurado
- [ ] Logs configurados correctamente
- [ ] Alertas configuradas para errores críticos

### Comunicación
- [ ] Usuarios notificados de cambios
- [ ] Capacitación programada
- [ ] Canales de soporte comunicados
- [ ] Stakeholders informados
- [ ] Equipo técnico preparado

---

## 📅 Cronograma Estimado

### Semana 1: Desarrollo y Corrección
- **Día 1-2:** Corregir bug crítico de pagos con crédito
- **Día 3-4:** Crear scripts de migración de datos
- **Día 5:** Testing exhaustivo de correcciones

### Semana 2: Preparación de Migración
- **Día 1-2:** Clonar producción a staging, ejecutar migración completa
- **Día 3:** Validar migración en staging, ajustar scripts
- **Día 4:** Testing de rollback
- **Día 5:** Documentación y capacitación

### Semana 3: Despliegue
- **Lunes:** Notificar usuarios de ventana de mantenimiento
- **Miércoles:** Capacitación final al equipo
- **Viernes (ventana de mantenimiento):**
  - 18:00 - Backup de producción
  - 18:30 - Aplicar migraciones
  - 19:00 - Migrar datos
  - 20:00 - Validaciones
  - 21:00 - Pruebas funcionales
  - 22:00 - Monitoreo intensivo
- **Sábado-Domingo:** Soporte dedicado + monitoreo

---

## 🎯 Conclusión y Recomendaciones

### Estado Actual
El feature branch `accounts-receivable-redesign` contiene una implementación **casi completa** de un sistema robusto de cuentas por cobrar. La arquitectura es sólida, el código es de buena calidad, y la mayoría de funcionalidades están correctamente implementadas.

### Bloqueador Principal
Existe **UN bug crítico** que debe ser corregido antes de cualquier despliegue a producción. Este bug hace que los pagos con crédito del cliente sean incorrectos, lo cual es inaceptable para un sistema financiero.

### Ruta Recomendada
1. **Corregir el bug crítico** (1-2 días)
2. **Crear y probar scripts de migración** (2-3 días)
3. **Testing exhaustivo en staging con datos reales** (1-2 días)
4. **Ejecutar migración en producción** (durante ventana de mantenimiento)
5. **Monitoreo intensivo post-despliegue** (primera semana)

### Tiempo Total Estimado
**5-10 días hábiles** desde inicio de correcciones hasta despliegue completo y estabilizado.

### Riesgo General
🟡 **MEDIO-BAJO** - Una vez corregido el bug crítico y validados los scripts de migración, el riesgo de despliegue es manejable y los beneficios del nuevo sistema superan ampliamente los riesgos.

---

**Documento preparado:** 2025-10-12
**Próxima revisión:** Después de correcciones críticas
**Responsable:** Equipo de Desarrollo TechStore
