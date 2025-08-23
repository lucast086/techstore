# Cash Register Validation System

## Overview

The cash register validation system ensures proper cash flow tracking by requiring an open cash register before certain operations can be performed. This prevents accounting discrepancies and maintains data integrity.

## Architecture

### Components

1. **Cash Closing Model** (`app/models/cash_closing.py`)
   - Tracks cash register state (open/closed/finalized)
   - Stores opening balance, sales totals, expenses, and cash count
   - Maintains audit trail with timestamps and user references

2. **System Configuration** (`app/models/system_config.py`)
   - Stores configurable system settings
   - Manages default opening balance (currently 10,000)
   - Supports different value types (decimal, integer, boolean, string)

3. **Configuration Service** (`app/services/config_service.py`)
   - Provides interface for reading/writing system configurations
   - Type-safe value conversion
   - Default value fallback support

4. **Repair Service Validation** (`app/services/repair_service.py`)
   - Validates cash register status before marking repairs as delivered
   - Enforces business rules for repair workflow

## Implementation Details

### Cash Register Validation

The validation occurs at the service layer to ensure consistency across all interfaces (Web, API):

```python
# In repair_service.py
def update_status(self, db: Session, repair_id: int, status_update: RepairStatusUpdate, user_id: int):
    # Validate cash register is open when marking as delivered
    if status_update.status == "delivered":
        from app.crud.cash_closing import cash_closing
        from datetime import date

        if not cash_closing.is_cash_register_open(db, target_date=date.today()):
            raise ValueError("Cash register must be open to deliver repairs. Please open the cash register first.")
```

### Cash Register State Management

The system tracks three states for cash registers:

1. **Not Opened**: No record exists for the date
2. **Open**: Record exists with `is_finalized=False`
3. **Closed/Finalized**: Record exists with `is_finalized=True`

### Multiple Open Register Prevention

The system prevents opening a new cash register if any unfinalized register exists:

```python
def open_cash_register(self, db: Session, *, target_date: date, opening_balance: Decimal, opened_by: int):
    # Check for any unfinalized register from any date
    unfinalized = self.get_unfinalized_register(db)
    if unfinalized:
        raise ValueError(f"Cannot open new cash register. Please close the cash register from {unfinalized.closing_date} first.")
```

## Database Schema

### system_configs Table
```sql
CREATE TABLE system_configs (
    id INTEGER PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    value_type VARCHAR(20) NOT NULL DEFAULT 'string',
    description TEXT,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Default Configurations
- `default_opening_balance`: 10000.00 (decimal)
- `cash_difference_threshold`: 100.00 (decimal)
- `allow_negative_stock`: false (boolean)
- `default_tax_rate`: 0.00 (decimal)

## Error Handling

### Frontend Error Display

Errors are displayed using HTMX error handling with JavaScript event listeners:

```javascript
document.body.addEventListener('htmx:responseError', function(evt) {
    if (evt.detail.xhr.status === 400) {
        const errorContainer = document.getElementById('status-error-message');
        if (errorContainer) {
            errorContainer.innerHTML = evt.detail.xhr.responseText;
            setTimeout(() => errorContainer.innerHTML = '', 10000);
        }
    }
});
```

### Backend Error Response

Errors return structured HTML for display:

```python
error_html = f"""
<div class="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4">
    <div class="flex">
        <svg class="h-5 w-5 text-red-400 mr-2">...</svg>
        <div>
            <p class="font-medium">Error al actualizar estado</p>
            <p class="text-sm mt-1">{str(e)}</p>
        </div>
    </div>
</div>
"""
return HTMLResponse(content=error_html, status_code=400)
```

## API Endpoints

### Configuration Management
- `GET /api/v1/config/{key}` - Get configuration value
- `PUT /api/v1/config/{key}` - Update configuration value
- `GET /api/v1/config` - List all configurations

### Cash Register Operations
- `POST /cash-closings/open` - Open cash register
- `POST /cash-closings` - Create cash closing
- `POST /cash-closings/{id}/finalize` - Finalize cash closing
- `GET /cash-closings` - List cash closings

## Testing

### Unit Tests
Located in `tests/unit/services/test_repair_service_cash_validation.py`:

- Test delivery without open cash (blocked)
- Test delivery with open cash (allowed)
- Test other status changes without cash (allowed)
- Test validation with previous day's register
- Integration flow testing

### Test Coverage
- Cash register state validation
- Multiple open register prevention
- Configuration service operations
- Error message generation and display

## Migration

The system includes database migration:
- `alembic/versions/db1b8739bca5_add_system_config_table_for_settings.py`
- Creates system_configs table
- Inserts default configuration values

## Security Considerations

1. **Role-based Access**: Only admin and manager roles can operate cash registers
2. **Audit Trail**: All operations tracked with user ID and timestamps
3. **Data Integrity**: Finalized cash closings are immutable
4. **Validation**: Server-side validation prevents bypassing frontend checks

## Performance Optimization

1. **Lazy Loading**: Cash register checks only performed when needed
2. **Caching**: Configuration values cached within request context
3. **Indexed Queries**: Database indexes on frequently queried fields

## Future Enhancements

1. **Admin Panel**: UI for managing system configurations
2. **Reporting**: Cash flow reports and analytics
3. **Notifications**: Alert users when cash register needs closing
4. **Batch Operations**: Support for multiple cash registers per location
5. **Integration**: Connect with accounting systems
