#!/bin/bash
# Create admin user in Railway deployment

echo "🚀 Creating admin user in Railway..."
echo "=================================="

# Make POST request to create admin
response=$(curl -X POST https://techstore-sb.up.railway.app/api/v1/setup/create-admin \
  -H "Content-Type: application/json" \
  -s)

# Pretty print the response
echo "Response:"
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"

echo ""
echo "=================================="
echo "✅ If successful, you can now login at:"
echo "   https://techstore-sb.up.railway.app/login"
echo "   Email: admin@techstore.com"
echo "   Password: Admin123!"
echo ""
echo "⚠️  IMPORTANT: Remove the temp_setup endpoint after this!"
