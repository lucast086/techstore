# ADR-003: PostgreSQL as Primary Database

## Status
Accepted

## Context
TechStore requires a database that can handle:
- Complex relationships (customers, products, sales, repairs)
- Financial transactions with ACID guarantees
- Concurrent users (100+ concurrent connections)
- Future scaling needs
- JSON data for flexible fields

Options evaluated:
- PostgreSQL
- MySQL/MariaDB
- MongoDB
- SQLite
- Firebase/Supabase

## Decision
We will use **PostgreSQL 15** as our primary database.

## Rationale

### Why PostgreSQL:

1. **ACID Compliance**: Critical for financial data integrity
   ```sql
   BEGIN;
   INSERT INTO sales (...) VALUES (...);
   UPDATE customers SET balance = balance + 100 WHERE id = 1;
   INSERT INTO account_movements (...) VALUES (...);
   COMMIT;
   ```

2. **Rich Data Types**: 
   - JSON/JSONB for flexible schemas
   - Arrays for multi-value fields
   - Custom types and enums
   - Full-text search capabilities

3. **Performance**:
   - Excellent query planner
   - Parallel query execution
   - Efficient indexing strategies
   - Materialized views for reporting

4. **Reliability**:
   - Proven in production for decades
   - Point-in-time recovery
   - Streaming replication
   - Active community support

5. **Railway Support**:
   - First-class PostgreSQL support
   - Automatic backups
   - Easy scaling options

### Why Not Others:

**MongoDB**:
- NoSQL doesn't fit relational data model
- ACID transactions more complex
- Aggregation pipeline learning curve

**MySQL**:
- Less feature-rich (JSON support, CTEs)
- Weaker data integrity checks
- Less sophisticated query planner

**SQLite**:
- Not suitable for concurrent writes
- Limited data types
- No true client-server architecture

## Implementation Details

### Connection Management:
```python
# SQLAlchemy connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Performance Optimizations:
```sql
-- Key indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_sales_customer_date ON sales(customer_id, created_at);
CREATE INDEX idx_repairs_status ON repair_orders(status) WHERE status != 'delivered';

-- Partial indexes for common queries
CREATE INDEX idx_active_repairs ON repair_orders(customer_id) 
WHERE status IN ('received', 'diagnosed', 'in_repair', 'ready');
```

### JSON Usage Example:
```sql
-- Store flexible repair metadata
ALTER TABLE repair_orders ADD COLUMN metadata JSONB DEFAULT '{}';

-- Query JSON data
SELECT * FROM repair_orders 
WHERE metadata->>'warranty' = 'true'
AND metadata->>'priority' = 'high';
```

## Consequences

### Positive:
- Rock-solid reliability
- Excellent performance
- Future-proof feature set
- Great tooling ecosystem
- Easy hiring (widely known)

### Negative:
- Requires more memory than MySQL
- Slightly more complex configuration
- Vertical scaling limits (mitigated by read replicas)

### Scaling Strategy:
1. **Phase 1**: Single primary with automated backups
2. **Phase 2**: Read replica for reporting queries
3. **Phase 3**: Connection pooling with PgBouncer
4. **Phase 4**: Partitioning for large tables
5. **Phase 5**: Citus for horizontal scaling (if needed)

## Monitoring

Key metrics to track:
- Connection pool usage
- Query performance (pg_stat_statements)
- Table bloat
- Index usage
- Lock contention

## References
- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- [Railway PostgreSQL Guide](https://docs.railway.app/databases/postgresql)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)