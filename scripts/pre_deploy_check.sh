#!/bin/bash
# Pre-deploy verification script
# Run this before pushing to main/production

set -e

echo "🔍 Running pre-deploy checks..."

# 1. Check single migration head
echo "📋 Checking migration heads..."
HEADS=$(poetry run alembic heads 2>/dev/null | grep -c "head" || true)
if [ "$HEADS" -gt 1 ]; then
    echo "❌ ERROR: Multiple migration heads detected!"
    poetry run alembic heads
    echo "Run: poetry run alembic merge heads -m 'merge heads'"
    exit 1
fi
echo "✅ Single migration head"

# 2. Run tests
echo "🧪 Running tests..."
poetry run pytest -x -q --tb=short

# 3. Check linting
echo "🔧 Checking linting..."
poetry run ruff check .

echo ""
echo "✅ All pre-deploy checks passed!"
