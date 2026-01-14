# Plan: Dashboard Statistics Cards & Statistics Module

## Resumen de Estado

| Sprint | Descripción | Estado |
|--------|-------------|--------|
| 1 | Dashboard Cards (alertas) | ✅ Completado |
| 2a | Página Admin Statistics | ✅ Completado |
| 2b | Infraestructura PDF (ReportLab) | ✅ Completado |
| 2c | Reporte Inventario Bajo Stock | ✅ Completado |
| 2d | Reporte Cuentas por Cobrar | ✅ Completado |
| 2e | Reporte Reparaciones del Mes | ✅ Completado |
| 3 | Estado de Resultados (P&L) | ✅ Completado |
| 4 | Comparativa Anual | ⏳ Pendiente |

---

## Archivos Principales

| Archivo | Propósito |
|---------|-----------|
| `src/app/services/dashboard_service.py` | Estadísticas del dashboard y constantes de alerta |
| `src/app/services/report_service.py` | Generación de reportes PDF con ReportLab |
| `src/app/web/admin.py` | Endpoints de reportes (`/admin/reports/*`) |
| `src/app/templates/admin/statistics.html` | Página principal de estadísticas |
| `src/app/templates/admin/partials/statistics_content.html` | UI de reportes con selectores |

---

## Reportes PDF Disponibles

### 1. Inventario Bajo Stock
- **Endpoint**: `/admin/reports/low-stock/pdf`
- **Método**: `generate_low_stock_report()`
- **Contenido**: SKU, Producto, Stock Actual/Mín/Máx, Recomendación Compra
- **Filtros**: Solo productos activos, excluye servicios

### 2. Cuentas por Cobrar
- **Endpoint**: `/admin/reports/accounts-receivable/pdf`
- **Método**: `generate_accounts_receivable_report()`
- **Contenido**: Cliente, Teléfono, Saldo, Última Actividad, Facturas Pendientes

### 3. Reparaciones del Mes
- **Endpoint**: `/admin/reports/repairs-monthly/pdf?year=YYYY&month=MM`
- **Método**: `generate_monthly_repairs_report()`
- **Contenido**: Lista de reparaciones, resumen por estado, totales

### 4. Estado de Resultados (P&L)
- **Endpoint**: `/admin/reports/financial-monthly/pdf?year=YYYY&month=MM`
- **Método**: `generate_monthly_financial_report()`
- **Contenido**:
  - INGRESOS: Productos, Servicios, Reparaciones
  - COSTOS: COGS productos (purchase_price), repuestos reparaciones (parts_cost)
  - UTILIDAD BRUTA: Por línea de negocio
  - GASTOS OPERATIVOS: Por categoría
  - UTILIDAD NETA: Con margen porcentual

---

## Constantes de Alerta (Dashboard)

```python
# src/app/services/dashboard_service.py
REPAIRS_RECEIVED_ALERT_THRESHOLD = 5
LOW_STOCK_ALERT_THRESHOLD = 30
CUSTOMER_DEBT_ALERT_THRESHOLD = Decimal("1500000")
```

---

## Sprint Pendiente: Comparativa Anual

### Objetivo
Reporte comparativo de métricas mes a mes para un año completo.

### Funcionalidad Propuesta
- Tabla con 12 meses mostrando: Ventas, Costos, Utilidad
- Porcentajes de crecimiento vs mes anterior
- Totales anuales
- Gráficos de tendencia (opcional, requiere librería adicional)

### Tareas
1. [ ] Método `generate_annual_comparison_report()` en report_service
2. [ ] Endpoint `/admin/reports/annual-comparison/pdf?year=YYYY`
3. [ ] Selector de año en UI
4. [ ] Tests

---

## Notas Técnicas

- **Timezone**: Usar `local_date_to_utc_range()` para queries por fecha
- **PDF**: ReportLab (programático, sin templates HTML)
- **Descarga**: JavaScript fetch + blob para forzar descarga
- **Acceso**: Restringido a rol admin
- **Arquitectura**: Web Route → Service → CRUD
