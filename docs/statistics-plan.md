# Plan: Dashboard Statistics Cards & Statistics Module

## Overview
Implementar cards de estadísticas rápidas en el dashboard principal y crear un módulo de estadísticas con reportes PDF descargables.

---

## Reglas de Desarrollo

1. **Sprint por Sprint**: Implementar un sprint completo antes de pasar al siguiente
2. **Validación del Usuario**: El usuario debe validar cada sprint antes de continuar
3. **Commit después de validación**: Solo hacer commit cuando el usuario confirme que funciona
4. **Uso de Agentes**: Usar agentes especializados para desarrollo y testing
5. **TDD**: Escribir tests junto con la implementación

---

## Sprint 1: Dashboard Cards ✅ COMPLETADO

### Implementado
- [x] `src/app/services/dashboard_service.py` con constantes configurables
- [x] Integración en `src/app/web/auth.py`
- [x] 4 cards en `src/app/templates/dashboard.html`
- [x] Tests completos (24 tests)

### Constantes de Alerta
```python
REPAIRS_RECEIVED_ALERT_THRESHOLD = 5
LOW_STOCK_ALERT_THRESHOLD = 30
CUSTOMER_DEBT_ALERT_THRESHOLD = Decimal("1500000")
```

---

## Sprint 2a: Página de Estadísticas en Admin ✅ COMPLETADO

### Implementado
- [x] Rutas `/admin/statistics` en `src/app/web/admin.py`
- [x] Template `src/app/templates/admin/statistics.html`
- [x] Partial `src/app/templates/admin/partials/statistics_content.html`
- [x] Enlace en sidebar de admin

---

## Sprint 2b: Infraestructura de Reportes PDF ✅ COMPLETADO

### Implementado
- [x] `src/app/services/report_service.py` con ReportLab (ya instalado)
- [x] Métodos base: `_create_header()`, `_create_table()`, `_generate_pdf()`
- [x] UI con 3 reportes y función JavaScript para descarga forzada

---

## Sprint 2c: Reporte Inventario Bajo Stock (PDF) ✅ COMPLETADO

### Contenido del Reporte
| Campo | Descripción |
|-------|-------------|
| SKU | Código del producto |
| Nombre | Nombre del producto |
| Categoría | Categoría del producto |
| Stock Actual | Cantidad actual |
| Stock Mínimo | Nivel de alerta |
| Stock Máximo | Nivel óptimo |
| Recomendación Compra | Stock Máximo - Stock Actual |

### Implementado
- [x] Método `generate_low_stock_report()` en report_service.py
- [x] Endpoint `/admin/reports/low-stock/pdf`
- [x] Botón de descarga habilitado en UI
- [x] Filtro: solo productos activos (is_active=True), excluye servicios

---

## Sprint 2d: Reporte Cuentas por Cobrar (PDF) ✅ COMPLETADO

### Contenido del Reporte
| Campo | Descripción |
|-------|-------------|
| Cliente | Nombre del cliente |
| Teléfono | Celular de contacto |
| Saldo Pendiente | Monto adeudado |
| Última Actividad | Fecha última transacción |
| Facturas Pendientes | Códigos de facturas con status pending/partial |

### Implementado
- [x] Método `generate_accounts_receivable_report()` en report_service.py
- [x] Endpoint `/admin/reports/accounts-receivable/pdf`
- [x] Botón de descarga habilitado en UI

---

## Sprint 2e: Reporte Reparaciones del Mes (PDF) ✅ COMPLETADO

### Contenido del Reporte
| Sección | Descripción |
|---------|-------------|
| Lista de Reparaciones | N° Orden, Fecha, Cliente, Dispositivo, Estado, Costo Final |
| Resumen por Estado | Conteo por cada estado de reparación |
| Totales | Total de reparaciones e ingresos por reparaciones |

### Implementado
- [x] Método `generate_monthly_repairs_report()` en report_service.py
- [x] Endpoint `/admin/reports/repairs-monthly/pdf` con parámetros year/month
- [x] Selector de mes/año en UI con valor por defecto al mes actual
- [x] Uso correcto de timezone con `local_date_to_utc_range()`

---

## Sprints Futuros

### Sprint 3: Informe Mensual Financiero
- Total de ventas del mes
- Total de gastos del mes
- Desglose por método de pago
- Ganancia bruta estimada

### Sprint 4: Comparativa Anual
- Comparación mes a mes
- Porcentajes de crecimiento
- Gráficos de tendencia

---

## Dependencias Identificadas

**Modelos existentes a usar:**
- `Repair` - estados y costos
- `Product` - current_stock, minimum_stock, maximum_stock, purchase_price
- `CustomerAccount` - account_balance
- `Sale` - invoice_number, total_amount, sale_date
- `Customer` - name, phone

**Librería para PDFs:**
- ReportLab (ya instalado en el proyecto)

---

## Notas Técnicas

- Reportes PDF generados con ReportLab (programático, sin templates HTML)
- Rutas de reportes en `/admin/reports/*`
- Acceso restringido a rol admin
- Descarga forzada vía JavaScript fetch + blob
- Seguir arquitectura: Web Route → Service → CRUD
