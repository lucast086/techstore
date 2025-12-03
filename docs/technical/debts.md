## Epic 8 - new features and technical debts in order

###
 * traduction to spanish   DONE

### Products
  * improve product search
  * edition view              DONE

### Reports
Payment report when pay is made. maybe size a5

### Repairs
 * add auto whatsapp when status change
 * ambiguos estimated cost is showed in diagnosis and cost breakdown

### Cash
* cierre de mes. que suma todos los cierres de caja.
* seccion compras que permite cargar compras con un valor total de factura, ademas de lista de items con cantidad valor unitario y codigo o que
  permite cargar un producto nuevo si no existe. El valor total se plasma como gasto compras a proveedores. y se agregan los stocks a los productos.

### Analytics
* story 77
* ademas una seccion de estadisticas de ventas, reparaciones, y otras estadisticas que saco del coso de instagram. todas en admin panel.
STORY 45 AGREGAR ACA LAS COSAS PASAR POR PM Y PO Y ANALYST

### Category
 * Expand/Collapse All

### Customers
 * customer profile fails
 * statment pdf is not working, pdf error

### Payments
 * Send Whatsapp when pay is made
 * Payments Pendientes (no IMPLEMENTADO) QUE QUIERO LOGRAR CON ESTO? ELIMINAR OPTION?

### Sales
 * Send periodic whatsapp remember account balance (only debt)
 * check filter behavior in sales history (customers, payment status, DATE)
 * when walk-in-customer payment method must be only cash
 * send invoice whatsapp when a sales is made


### dashboard
* new lateral bar
* estadisticas importantes (VALOR DOLAR - )


### technical

 * analyze coverage to get 80% test coverage?

---

## DEUDA TÉCNICA PRIORITARIA: Unificar arquitectura de pagos

**Fecha**: 2025-12-03
**Prioridad**: ALTA
**Esfuerzo estimado**: 2-3 días

### Problema actual

Existen dos modelos para registrar pagos que pueden desincronizarse:

| Modelo | Tabla | Propósito | Tiene `payment_method` |
|--------|-------|-----------|------------------------|
| `Payment` | `payments` | Registro físico del pago (recibo) | ✅ Sí |
| `CustomerTransaction` | `customer_transactions` | Libro mayor del cliente | ❌ No |

**Riesgo identificado**: En `payment_service.py` si falla la creación de `CustomerTransaction`, el `Payment` se guarda igual (try/except sin rollback), causando:
- Desincronización entre tablas
- Balance del cliente incorrecto
- Inconsistencias en reportes vs cuenta corriente

### Solución propuesta (Opción B)

1. **Agregar `payment_method` a `CustomerTransaction`**:
   ```python
   payment_method = Column(String(50), nullable=True)  # cash, transfer, card, mixed
   ```

2. **Usar `CustomerTransaction` como única fuente de verdad** para:
   - Cierre de caja (consultar transacciones por método de pago)
   - Reportes financieros
   - Balance de clientes

3. **Mantener `Payment` solo para**:
   - Generación de recibos
   - Datos adicionales del pago (referencia, notas)

4. **Migración de datos**:
   - Crear migración que agregue `payment_method` a `customer_transactions`
   - Script para poblar `payment_method` desde `payments.payment_method` usando `reference_id`

### Archivos a modificar

- `src/app/models/customer_account.py` - Agregar campo
- `src/app/services/customer_account_service.py` - Recibir payment_method en record_payment
- `src/app/services/payment_service.py` - Pasar payment_method
- `src/app/crud/cash_closing.py` - Consultar customer_transactions en lugar de payments
- Migración Alembic

### Beneficios

- Una sola fuente de verdad para movimientos financieros
- Consultas más simples para cierre de caja
- Eliminación de riesgo de desincronización
- Código más mantenible (menos lugares donde actualizar)
