-- Fix PostgreSQL sequences that are out of sync
-- This happens when data is inserted manually or after restoring backups

-- Fix repairstatushistorys sequence
SELECT setval('repairstatushistorys_id_seq', COALESCE((SELECT MAX(id) FROM repairstatushistorys), 1), true);

-- Fix all other sequences to be safe
SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1), true);
SELECT setval('customers_id_seq', COALESCE((SELECT MAX(id) FROM customers), 1), true);
SELECT setval('products_id_seq', COALESCE((SELECT MAX(id) FROM products), 1), true);
SELECT setval('categories_id_seq', COALESCE((SELECT MAX(id) FROM categories), 1), true);
SELECT setval('repairs_id_seq', COALESCE((SELECT MAX(id) FROM repairs), 1), true);
SELECT setval('sales_id_seq', COALESCE((SELECT MAX(id) FROM sales), 1), true);
SELECT setval('sale_items_id_seq', COALESCE((SELECT MAX(id) FROM sale_items), 1), true);
SELECT setval('expenses_id_seq', COALESCE((SELECT MAX(id) FROM expenses), 1), true);
SELECT setval('expense_categories_id_seq', COALESCE((SELECT MAX(id) FROM expense_categories), 1), true);
SELECT setval('suppliers_id_seq', COALESCE((SELECT MAX(id) FROM suppliers), 1), true);
SELECT setval('cash_closings_id_seq', COALESCE((SELECT MAX(id) FROM cash_closings), 1), true);
SELECT setval('customer_transactions_id_seq', COALESCE((SELECT MAX(id) FROM customer_transactions), 1), true);

-- Show results
SELECT 'repairstatushistorys_id_seq' as sequence_name, last_value FROM repairstatushistorys_id_seq
UNION ALL
SELECT 'users_id_seq', last_value FROM users_id_seq
UNION ALL
SELECT 'customers_id_seq', last_value FROM customers_id_seq
UNION ALL
SELECT 'products_id_seq', last_value FROM products_id_seq
UNION ALL
SELECT 'categories_id_seq', last_value FROM categories_id_seq
UNION ALL
SELECT 'repairs_id_seq', last_value FROM repairs_id_seq
UNION ALL
SELECT 'sales_id_seq', last_value FROM sales_id_seq
UNION ALL
SELECT 'expenses_id_seq', last_value FROM expenses_id_seq
UNION ALL
SELECT 'cash_closings_id_seq', last_value FROM cash_closings_id_seq;
