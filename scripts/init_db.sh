#!/bin/bash
# Database initialization script for TechStore SaaS

set -e

echo "🚀 Initializing TechStore Database..."

# Check if PostgreSQL is running
if ! pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running or not accessible"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Run Alembic migrations
echo "📦 Running database migrations..."
poetry run alembic upgrade head

# Create admin user if it doesn't exist
echo "👤 Creating admin user..."
poetry run python scripts/seed_admin.py

echo "✨ Database initialization complete!"