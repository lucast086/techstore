#!/bin/bash
# Reset local database for fresh start

echo "🔄 Resetting local database..."

# PostgreSQL connection info
DB_HOST="db"
DB_USER="postgres"
DB_PASS="postgres"
DB_NAME="techstore_db"

# Drop and recreate database
echo "📦 Dropping existing database..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"

echo "📦 Creating new database..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

echo "✅ Database reset complete!"
