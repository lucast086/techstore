# Análisis de Migración a UTC - Sistema de Fechas TechStore SaaS

## Contexto del Problema

### Síntomas Detectados
1. **Pagos no aparecen en cierre de caja**: Un pago realizado desde el perfil de venta no se refleja en el cierre de caja del día
2. **Problema de apertura/cierre**: La caja se abre en una fecha pero al cerrar intenta usar otra fecha
3. **Múltiples fuentes de verdad**: Mezcla de UTC, hora local del servidor, y timezone de Argentina

### Diagnóstico Actual

#### Inconsistencias Encontradas:
- **PostgreSQL**: Usa `func.now()` que puede ser UTC o timezone del servidor
- **Python**: Mezcla de `datetime.now()`, `date.today()`, y `get_local_date()`
- **Modelos**:
  - Campos `Date` (sin timezone): `closing_date`, `expense_date`
  - Campos `DateTime` (con timezone): `created_at`, `sale_date`, `opened_at`
- **Consultas**: Comparan fechas locales con timestamps UTC

#### Ejemplo del Problema:
```python
# Servidor en UTC, usuario en Argentina (UTC-3)
# Usuario hace un pago a las 23:00 hora Argentina del 6/sep
Payment.created_at = '2025-09-07 02:00:00 UTC'  # Se guarda como 7/sep UTC

# Cierre de caja busca pagos del 6/sep local
.filter(func.date(Payment.created_at) == '2025-09-06')  # No encuentra el pago!
```

## Decisión: Migrar Todo a UTC

### Razones:
1. **Objetivo SaaS Multi-timezone**: Soportar múltiples sucursales en diferentes zonas horarias
2. **Estándar de la industria**: UTC es el estándar para aplicaciones distribuidas
3. **Datos en beta**: Momento ideal para hacer la migración sin afectar producción

## Estrategia de Implementación

### 1. Modelo de Datos para Multi-tenant

```python
# Cada store/sucursal tiene su timezone
class Store(BaseModel):
    name = Column(String)
    timezone = Column(String, default='UTC')  # 'America/Argentina/Buenos_Aires'
    # ... otros campos

# Cash closing asociado a store
class CashClosing(BaseModel):
    store_id = Column(Integer, ForeignKey('stores.id'))

    # Fecha LOCAL del store (para UI y lógica de negocio)
    closing_date_local = Column(Date)

    # Timestamps exactos en UTC (para auditoría)
    opened_at = Column(DateTime(timezone=True))  # UTC
    closed_at = Column(DateTime(timezone=True))  # UTC

    # Importante: opening_balance se mantiene con la fecha local de apertura
    opening_local_date = Column(Date)  # Previene el error de cerrar en otro día

# Payments también asociados a store
class Payment(BaseModel):
    store_id = Column(Integer, ForeignKey('stores.id'))
    created_at = Column(DateTime(timezone=True))  # UTC

    # Opción: agregar fecha local para queries eficientes
    payment_date_local = Column(Date)  # Fecha en timezone del store
```

### 2. Funciones de Conversión Centralizadas

```python
# app/utils/timezone_utils.py
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

def get_store_timezone(store) -> ZoneInfo:
    """Get timezone for a specific store."""
    return ZoneInfo(store.timezone or 'UTC')

def local_date_to_utc_range(local_date: date, timezone: str):
    """Convert a local date to UTC datetime range.

    Args:
        local_date: Date in local timezone
        timezone: IANA timezone string (e.g., 'America/Argentina/Buenos_Aires')

    Returns:
        Tuple of (utc_start, utc_end) for the full day in local timezone
    """
    tz = ZoneInfo(timezone)

    # Start and end of day in local timezone
    local_start = datetime.combine(local_date, time.min).replace(tzinfo=tz)
    local_end = datetime.combine(local_date, time.max).replace(tzinfo=tz)

    # Convert to UTC
    utc_start = local_start.astimezone(ZoneInfo('UTC'))
    utc_end = local_end.astimezone(ZoneInfo('UTC'))

    return utc_start, utc_end

def utc_to_local_date(utc_datetime: datetime, timezone: str) -> date:
    """Convert UTC datetime to local date."""
    tz = ZoneInfo(timezone)
    local_dt = utc_datetime.replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)
    return local_dt.date()
```

### 3. Queries Correctas para "Día Local"

```python
# app/crud/cash_closing.py
def get_daily_summary(db: Session, store_id: int, local_date: date):
    """Get summary for a specific day in store's local timezone."""

    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise ValueError("Store not found")

    # Convert local date to UTC range
    utc_start, utc_end = local_date_to_utc_range(local_date, store.timezone)

    # Query payments in UTC range
    payments = (
        db.query(Payment)
        .filter(
            Payment.store_id == store_id,
            Payment.created_at >= utc_start,
            Payment.created_at <= utc_end,
            Payment.voided == False
        )
        .all()
    )

    # Query sales in UTC range
    sales = (
        db.query(Sale)
        .filter(
            Sale.store_id == store_id,
            Sale.sale_date >= utc_start,
            Sale.sale_date <= utc_end,
            Sale.is_voided == False
        )
        .all()
    )

    return calculate_summary(payments, sales)
```

### 4. Prevención del Error de Apertura/Cierre

```python
# app/services/cash_closing_service.py
class CashClosingService:

    def open_register(self, db: Session, store_id: int, local_date: date, opening_balance: Decimal):
        """Open cash register for a specific date in store's timezone."""

        # Check no unclosed registers
        unclosed = db.query(CashClosing).filter(
            CashClosing.store_id == store_id,
            CashClosing.closed_at == None
        ).first()

        if unclosed:
            raise ValueError(
                f"Cannot open new register. Close register from {unclosed.opening_local_date} first"
            )

        closing = CashClosing(
            store_id=store_id,
            opening_local_date=local_date,  # Store the LOCAL date
            closing_date_local=local_date,  # Will be same for closing
            opening_balance=opening_balance,
            opened_at=datetime.now(ZoneInfo('UTC')),  # UTC timestamp
            is_finalized=False
        )

        db.add(closing)
        db.commit()
        return closing

    def close_register(self, db: Session, store_id: int, closing_date: date, cash_count: Decimal):
        """Close cash register - MUST use same date as opening."""

        # Find open register
        open_register = db.query(CashClosing).filter(
            CashClosing.store_id == store_id,
            CashClosing.closed_at == None
        ).first()

        if not open_register:
            raise ValueError("No open register found")

        # CRITICAL: Enforce same date as opening
        if closing_date != open_register.opening_local_date:
            raise ValueError(
                f"Must close with opening date {open_register.opening_local_date}. "
                f"You're trying to close with {closing_date}"
            )

        # Get store timezone for calculations
        store = db.query(Store).filter(Store.id == store_id).first()
        utc_start, utc_end = local_date_to_utc_range(
            open_register.opening_local_date,
            store.timezone
        )

        # Calculate totals for the LOCAL date in UTC range
        # ... (calculate sales, payments, etc.)

        open_register.closed_at = datetime.now(ZoneInfo('UTC'))
        open_register.cash_count = cash_count
        open_register.is_finalized = True

        db.commit()
        return open_register
```

## Plan de Migración

### Fase 1: Preparación (1-2 horas)
1. ✅ Agregar modelo `Store` con campo `timezone`
2. ✅ Agregar `store_id` a modelos relevantes (Sale, Payment, CashClosing, etc.)
3. ✅ Crear funciones de conversión timezone en `utils/timezone_utils.py`
4. ✅ Agregar campos `*_local_date` donde sea necesario para performance

### Fase 2: Migración de Código (2-3 horas)
1. ⬜ Reemplazar todos los `datetime.now()` → `datetime.now(ZoneInfo('UTC'))`
2. ⬜ Reemplazar todos los `date.today()` → Función que considere store timezone
3. ⬜ Reemplazar todos los `func.now()` → `func.now()` con PostgreSQL en UTC
4. ⬜ Actualizar todas las queries para usar rangos UTC

### Fase 3: Migración de Datos (1 hora)
1. ⬜ Script para migrar timestamps existentes a UTC
2. ⬜ Script para llenar campos `*_local_date` basados en timezone
3. ⬜ Validar integridad de datos migrados

### Fase 4: Testing (2 horas)
1. ⬜ Tests para conversiones timezone
2. ⬜ Tests para cierre de caja multi-día
3. ⬜ Tests para queries con rangos UTC
4. ⬜ Tests de UI con diferentes timezones

## Configuración PostgreSQL Requerida

```sql
-- Asegurar que PostgreSQL use UTC
ALTER DATABASE techstore_db SET timezone = 'UTC';

-- Verificar configuración
SHOW timezone;  -- Debe mostrar 'UTC'
```

## Archivos a Modificar

### Alta Prioridad (afectan lógica de negocio):
- `/workspace/src/app/crud/cash_closing.py` - Queries de cierre
- `/workspace/src/app/crud/sale.py` - Queries de ventas
- `/workspace/src/app/crud/payment.py` - Queries de pagos
- `/workspace/src/app/services/cash_closing_service.py` - Lógica de apertura/cierre
- `/workspace/src/app/models/base.py` - Default timestamps

### Media Prioridad (validaciones):
- `/workspace/src/app/schemas/expense.py` - Validación de fechas
- `/workspace/src/app/schemas/cash_closing.py` - Validación de fechas
- `/workspace/src/app/services/expense_service.py` - Validaciones

### Baja Prioridad (reportes/UI):
- `/workspace/src/app/utils/pdf_generator.py` - Fechas en PDFs
- `/workspace/src/app/services/invoice_service.py` - Fechas en facturas
- `/workspace/src/app/web/*.py` - Mostrar fechas en timezone local

## Consideraciones Especiales

### 1. Performance
Con datos en UTC y queries por fecha local, considerar:
- Índices en campos de fecha/timestamp
- Campos `*_local_date` pre-calculados para queries frecuentes
- Caché de conversiones timezone

### 2. UI/UX
- Siempre mostrar fechas/horas en timezone del store
- Agregar indicador de timezone en la UI
- Selector de timezone en configuración de store

### 3. API
- Timestamps en responses siempre en UTC con formato ISO 8601
- Aceptar timezone como parámetro opcional en endpoints
- Documentar claramente el manejo de timezones

## Beneficios de Esta Arquitectura

1. **Escalabilidad**: Soporta múltiples stores en diferentes timezones
2. **Consistencia**: Una sola fuente de verdad (UTC)
3. **Auditoría**: Timestamps precisos sin ambigüedad
4. **Integraciones**: Compatible con sistemas externos
5. **Prevención de Errores**: Imposible cerrar caja en fecha incorrecta

## Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Confusión developer sobre timezone | Documentación clara y funciones helper |
| Queries lentas por conversión | Campos `*_local_date` pre-calculados |
| Errores en migración de datos | Backup antes de migrar, validación post-migración |
| UI muestra hora incorrecta | Tests E2E con diferentes timezones |

## Próximos Pasos

1. **Validar decisión** de migrar a UTC
2. **Crear branch** `feature/utc-migration`
3. **Implementar Fase 1** (modelos y utilidades)
4. **Tests unitarios** de conversiones
5. **Implementar Fase 2** gradualmente
6. **Migrar datos** de prueba
7. **Testing completo** con diferentes timezones
8. **Documentar** para otros developers

## Conclusión

La migración a UTC es la decisión correcta para un SaaS multi-timezone. Aunque requiere trabajo inicial, previene problemas futuros y hace el sistema verdaderamente escalable. El momento es ideal al estar en beta con datos que se pueden migrar o reiniciar.

---

*Documento creado: 2025-09-07*
*Contexto: Análisis de problemas de timezone en cierre de caja y pagos*
