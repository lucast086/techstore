# Plan: Dashboard Statistics Cards & Statistics Module

## Overview
Implementar cards de estadísticas rápidas en el dashboard principal y crear un módulo de estadísticas detalladas con reportes mensuales y anuales.

---

## Reglas de Desarrollo

1. **Sprint por Sprint**: Implementar un sprint completo antes de pasar al siguiente
2. **Validación del Usuario**: El usuario debe validar cada sprint antes de continuar
3. **Commit después de validación**: Solo hacer commit cuando el usuario confirme que funciona
4. **Uso de Agentes**: Usar agentes especializados para desarrollo y testing
5. **TDD**: Escribir tests junto con la implementación

---

## Fase 1: Dashboard Cards (MVP) ← IMPLEMENTAR PRIMERO

### 1.1 Cards a implementar
| Card | Datos | Color Base | Color Alerta | Condición Alerta |
|------|-------|------------|--------------|------------------|
| Reparaciones Recibidas | Cantidad en estado "received" | Amarillo | Rojo | > 5 pendientes |
| Stock Bajo | Productos con stock <= minimum_stock | Naranja | Rojo | > 10 productos |
| Deuda Clientes | Suma de account_balance > 0 | Azul | Rojo | > S/5000 |
| Ventas del Día | Total vendido hoy | Verde | - | Sin alerta |

**Enlace de cada card:** `/statistics/{seccion}` (implementar en Fase 2)

### 1.2 Archivos a crear/modificar

**Nuevo servicio:**
- `src/app/services/dashboard_service.py` - Servicio para obtener estadísticas del dashboard

**Modificar:**
- `src/app/web/auth.py` - Agregar datos de estadísticas al contexto del dashboard
- `src/app/templates/dashboard.html` - Agregar grid de cards con estadísticas

### 1.3 Implementación del servicio

```python
# dashboard_service.py
class DashboardService:
    def get_dashboard_stats(self, db: Session) -> dict:
        """Obtiene estadísticas rápidas para el dashboard."""
        return {
            "repairs_received": self._count_repairs_by_status(db, "received"),
            "low_stock_count": self._count_low_stock_products(db),
            "total_customer_debt": self._sum_customer_debt(db),
            "today_sales_total": self._get_today_sales_total(db),
        }
```

### 1.4 Diseño de Cards (siguiendo patrón de admin/dashboard.html)

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
  <!-- Card pattern -->
  <a href="/statistics/repairs" class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">Reparaciones Recibidas</p>
        <p class="text-2xl font-bold text-gray-900 mt-1">{{ stats.repairs_received }}</p>
      </div>
      <div class="bg-yellow-100 p-3 rounded-lg">
        <svg class="w-6 h-6 text-yellow-600">...</svg>
      </div>
    </div>
  </a>
</div>
```

---

## Fase 2: Módulo de Estadísticas

### 2.1 Estructura de rutas
```
/statistics                  → Vista general (índice)
/statistics/repairs          → Estadísticas de reparaciones
/statistics/inventory        → Estadísticas de inventario
/statistics/accounts         → Estadísticas de cuentas por cobrar
/statistics/sales            → Estadísticas de ventas
/statistics/monthly          → Informe mensual
/statistics/annual           → Comparativa anual
```

### 2.2 Archivos a crear

**Web routes:**
- `src/app/web/statistics.py` - Rutas web para estadísticas

**Templates:**
- `src/app/templates/statistics/index.html` - Vista general
- `src/app/templates/statistics/repairs.html` - Detalle reparaciones
- `src/app/templates/statistics/inventory.html` - Detalle inventario
- `src/app/templates/statistics/accounts.html` - Detalle cuentas
- `src/app/templates/statistics/sales.html` - Detalle ventas
- `src/app/templates/statistics/monthly.html` - Informe mensual
- `src/app/templates/statistics/annual.html` - Comparativa anual

**Servicios:**
- `src/app/services/statistics_service.py` - Lógica de reportes avanzados

---

## Fase 3: Informe Mensual

### 3.1 Datos del informe mensual (basado en CashClosings)
- Total de ventas del mes
- Total de gastos del mes
- Desglose por método de pago:
  - Efectivo
  - Transferencia
  - Tarjeta
  - Crédito (cuentas corrientes)
  - Mixto (con sub-desglose)
- Cantidad de días trabajados
- Promedio de ventas diarias
- Ganancia bruta estimada (ventas - costo de productos)

### 3.2 Cálculo de ganancia (COMPLETO con reparaciones)
```python
def calculate_monthly_profit(self, db: Session, year: int, month: int) -> dict:
    """
    Ganancia = Ingresos - Costos

    INGRESOS:
    - Total de ventas (sales.total_amount)
    - Total de reparaciones entregadas (repairs.final_cost)

    COSTOS:
    - Costo de productos vendidos: sum(sale_item.quantity * product.purchase_price)
    - Costo de partes en reparaciones: sum(repair.parts_cost)
    - Gastos del mes: sum(expenses.amount)

    RESULTADO:
    - ganancia_bruta = ingresos - costo_productos - costo_partes
    - ganancia_neta = ganancia_bruta - gastos
    """
```

---

## Fase 4: Comparativa Anual

### 4.1 Métricas a comparar mes a mes
- Total de ventas
- Total de gastos
- Ganancia estimada
- Cantidad de transacciones
- Deuda total de clientes (snapshot fin de mes)

### 4.2 Cálculos de tendencia
- Porcentaje de crecimiento vs mes anterior
- Porcentaje de crecimiento vs mismo mes año anterior
- Promedio móvil de 3 meses

---

## Orden de Implementación

### Sprint 1: Dashboard Cards ← EMPEZAR AQUÍ
1. [ ] Crear `src/app/services/dashboard_service.py`
   - `get_dashboard_stats()` - obtiene las 4 métricas
   - `_count_repairs_received()` - cuenta reparaciones en estado "received"
   - `_count_low_stock_products()` - cuenta productos con stock <= minimum_stock
   - `_sum_customer_debt()` - suma account_balance donde > 0
   - `_get_today_sales_total()` - total de ventas del día
2. [ ] Modificar `src/app/web/auth.py` - agregar stats al contexto
3. [ ] Actualizar `src/app/templates/dashboard.html`:
   - Grid de 4 cards con iconos
   - Colores condicionales (normal vs alerta)
   - Links a `/statistics/*` (placeholder hasta Sprint 2)
4. [ ] Tests para dashboard_service

---

### Sprint 2: Módulo de Estadísticas (Estructura) - FUTURO
5. [ ] Crear `src/app/web/statistics.py` con rutas básicas
6. [ ] Crear templates en `src/app/templates/statistics/`
7. [ ] Agregar enlace "Estadísticas" en navegación

### Sprint 3: Vistas de Detalle - FUTURO
8. [ ] `/statistics/repairs` - reparaciones por estado
9. [ ] `/statistics/inventory` - productos con stock bajo
10. [ ] `/statistics/accounts` - clientes con deuda
11. [ ] `/statistics/sales` - ventas del día/semana

### Sprint 4: Informe Mensual - FUTURO
12. [ ] `statistics_service.py` con lógica de reportes
13. [ ] Agregación de CashClosings por mes
14. [ ] Cálculo de ganancia (productos + reparaciones - gastos)

### Sprint 5: Comparativa Anual - FUTURO
15. [ ] Comparación mes a mes
16. [ ] Porcentajes de crecimiento
17. [ ] Gráficos de tendencia

---

## Dependencias Identificadas

**Modelos existentes a usar:**
- `Repair` - estados y costos
- `Product` - current_stock, minimum_stock, purchase_price
- `CustomerAccount` - account_balance
- `Sale` - total_amount, sale_date, items
- `CashClosing` - agregaciones diarias

**Servicios existentes a reutilizar:**
- `cash_closing_service.get_daily_summary()` - resumen diario
- `repair_service` - estadísticas de reparaciones
- `product_service._calculate_stock_status()` - lógica de stock

---

## Notas Técnicas

- Usar patrón de cards existente en `admin/dashboard.html`
- Seguir arquitectura: Web Route → Service → CRUD
- HTMX para actualizaciones dinámicas si es necesario
- Tailwind CSS para estilos (no Bootstrap)
