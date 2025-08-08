#!/bin/bash

# Discover vNext Development Stop Script
# This script stops both backend and frontend servers

echo "🛑 Stopping Discover vNext Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Stop all processes
print_status "Stopping backend servers (port 8000)..."
pkill -f "uvicorn.*8000" 2>/dev/null || true

print_status "Stopping frontend servers (port 3000)..."
pkill -f "npm.*start" 2>/dev/null || true
pkill -f "node.*3000" 2>/dev/null || true

# Wait for processes to stop
sleep 2

print_success "✅ All servers stopped!"
echo ""
echo "To restart: ./start-dev.sh or make start"