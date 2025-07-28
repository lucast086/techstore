#!/bin/bash
set -e

echo "🚀 Initializing TechStore Database..."

# Load environment variables
if [ -f /workspace/.env ]; then
  export $(cat /workspace/.env | grep -v '^#' | xargs)
fi

# Default values if not set
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
POSTGRES_SERVER=${POSTGRES_SERVER:-db}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_DB=${POSTGRES_DB:-techstore_db}

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -c '\q' 2>/dev/null; do
  echo "PostgreSQL is not ready yet... waiting"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Create database if it doesn't exist
echo "📦 Creating database if needed..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1 || \
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB"

# Create test database
echo "🧪 Creating test database..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -tc "SELECT 1 FROM pg_database WHERE datname = 'test_$POSTGRES_DB'" | grep -q 1 || \
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER -c "CREATE DATABASE test_$POSTGRES_DB"

# Run migrations
echo "🔄 Running database migrations..."
cd /workspace
export PYTHONPATH=/workspace/src

# Check if alembic has any migrations
if [ -d "alembic/versions" ] && [ "$(ls -A alembic/versions/*.py 2>/dev/null)" ]; then
  poetry run alembic upgrade head
else
  echo "⚠️  No migrations found. Creating initial migration..."
  poetry run alembic revision --autogenerate -m "Initial migration"
  poetry run alembic upgrade head
fi

echo "✅ Database initialization complete!"