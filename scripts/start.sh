#!/bin/bash
# Startup script for Railway deployment

echo "🚀 Starting deployment process..."

# Run database migrations
echo "📦 Running database migrations..."
poetry run alembic upgrade head

# Check if migrations succeeded
if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migration failed!"
    exit 1
fi

# Start the application
echo "🌐 Starting web server..."
exec uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
