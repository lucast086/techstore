#!/bin/bash

# Script to switch between development and production environments

set -e

# Get the project root directory (parent of scripts directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root to ensure we find .env files
cd "$PROJECT_ROOT"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show current environment
show_current() {
    # Debug: Show where we're looking
    # print_color "$BLUE" "📂 Working directory: $(pwd)"

    if [ -f .env ]; then
        current_env=$(grep -E "^ENVIRONMENT=" .env | cut -d '=' -f2 | tr -d '"')
        if [ -z "$current_env" ]; then
            print_color "$YELLOW" "⚠️  No ENVIRONMENT variable found in .env"
        else
            print_color "$BLUE" "📍 Current environment: $current_env"
        fi

        # Show database connection
        db_url=$(grep -E "^DATABASE_URL=" .env | cut -d '=' -f2)
        if [ ! -z "$db_url" ]; then
            # Extract just the database name and host for display (hide credentials)
            db_display=$(echo "$db_url" | sed 's|postgresql://[^@]*@|postgresql://***@|')
            print_color "$BLUE" "   Database: $db_display"
        fi
    else
        print_color "$YELLOW" "⚠️  No .env file found"
    fi
}

# Function to switch environment
switch_env() {
    target_env=$1

    case $target_env in
        dev|development)
            env_file=".env.development"
            env_name="development"
            ;;
        prod|production)
            env_file=".env.production"
            env_name="production"
            ;;
        *)
            print_color "$RED" "❌ Invalid environment: $target_env"
            echo "Usage: $0 [dev|development|prod|production|status]"
            exit 1
            ;;
    esac

    # Check if source file exists
    if [ ! -f "$env_file" ]; then
        print_color "$RED" "❌ Environment file $env_file not found"
        print_color "$YELLOW" "   Looking in: $(pwd)"
        print_color "$YELLOW" "   Available .env files:"
        ls -la .env* 2>/dev/null || print_color "$RED" "   No .env files found"
        exit 1
    fi

    # Backup current .env if it exists
    if [ -f .env ]; then
        backup_file=".env.backup.$(date +%Y%m%d_%H%M%S)"
        cp .env "$backup_file"
        print_color "$YELLOW" "📦 Backed up current .env to $backup_file"
    fi

    # Switch to new environment
    cp "$env_file" .env
    print_color "$GREEN" "✅ Switched to $env_name environment"

    # Show new configuration
    show_current

    # Warn if production
    if [ "$env_name" = "production" ]; then
        print_color "$YELLOW" ""
        print_color "$YELLOW" "⚠️  WARNING: You are now using PRODUCTION environment!"
        print_color "$YELLOW" "   - Make sure production database credentials are configured"
        print_color "$YELLOW" "   - Be careful with any destructive operations"
        print_color "$YELLOW" "   - Consider running tests before deploying"
    fi
}

# Main script logic
case "${1:-status}" in
    dev|development)
        print_color "$BLUE" "🔄 Switching to development environment..."
        switch_env "development"
        ;;
    prod|production)
        print_color "$BLUE" "🔄 Switching to production environment..."

        # Extra confirmation for production
        print_color "$YELLOW" "⚠️  Are you sure you want to switch to PRODUCTION? (yes/no)"
        read -r confirmation
        if [ "$confirmation" = "yes" ]; then
            switch_env "production"
        else
            print_color "$RED" "❌ Cancelled switching to production"
            exit 0
        fi
        ;;
    status|current)
        show_current
        ;;
    *)
        print_color "$RED" "❌ Invalid command: $1"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  dev, development  - Switch to development environment"
        echo "  prod, production  - Switch to production environment (requires confirmation)"
        echo "  status, current   - Show current environment (default)"
        echo ""
        echo "Examples:"
        echo "  $0              # Show current environment"
        echo "  $0 dev          # Switch to development"
        echo "  $0 prod         # Switch to production (with confirmation)"
        exit 1
        ;;
esac
