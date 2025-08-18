#!/bin/bash

# Living Twin Monorepo - Dependency Installation Script
# This script installs all dependencies using the correct package managers:
# - UV for Python
# - PNPM for JavaScript/TypeScript
# - Flutter for Dart

set -e  # Exit on error

echo "🚀 Living Twin Monorepo - Installing Dependencies"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from monorepo root
if [ ! -f "pnpm-workspace.yaml" ]; then
    echo -e "${RED}Error: Please run this script from the monorepo root directory${NC}"
    exit 1
fi

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Install UV for Python if not present
echo -e "\n${YELLOW}1. Python Dependencies (UV)${NC}"
echo "--------------------------------"
if ! command_exists uv; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo -e "${GREEN}✓ UV is already installed${NC}"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd apps/api
uv sync
echo -e "${GREEN}✓ Python dependencies installed${NC}"
cd ../..

# 2. Install PNPM if not present
echo -e "\n${YELLOW}2. JavaScript/TypeScript Dependencies (PNPM)${NC}"
echo "---------------------------------------------"
if ! command_exists pnpm; then
    echo "Installing PNPM..."
    npm install -g pnpm
else
    echo -e "${GREEN}✓ PNPM is already installed${NC}"
fi

# Install JavaScript dependencies
echo "Installing JavaScript dependencies..."
pnpm install
echo -e "${GREEN}✓ JavaScript dependencies installed${NC}"

# 3. Install Flutter dependencies
echo -e "\n${YELLOW}3. Flutter/Dart Dependencies${NC}"
echo "-----------------------------"
if ! command_exists flutter; then
    echo -e "${RED}Warning: Flutter is not installed. Please install Flutter first.${NC}"
    echo "Visit: https://flutter.dev/docs/get-started/install"
else
    echo -e "${GREEN}✓ Flutter is installed${NC}"
    cd apps/mobile
    
    # Get Flutter dependencies
    echo "Installing Flutter dependencies..."
    flutter pub get
    
    # Run code generation if build_runner is configured
    if grep -q "build_runner" pubspec.yaml; then
        echo "Running code generation..."
        flutter pub run build_runner build --delete-conflicting-outputs || true
    fi
    
    echo -e "${GREEN}✓ Flutter dependencies installed${NC}"
    cd ../..
fi

# 4. Create .env file if it doesn't exist
echo -e "\n${YELLOW}4. Environment Configuration${NC}"
echo "----------------------------"
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file (please update with your values)${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create mobile .env if it doesn't exist
if [ ! -f "apps/mobile/.env" ]; then
    echo "Creating apps/mobile/.env file..."
    cat > apps/mobile/.env << EOF
# Mobile App Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000
API_RETRY_ATTEMPTS=3
PIN_REQUIRED=false
BIOMETRIC_ENABLED=true
SECURE_STORAGE_ENABLED=true
CACHE_MEMORY_SIZE=100
CACHE_DISK_SIZE_MB=50
CACHE_TTL_HOURS=24
EOF
    echo -e "${GREEN}✓ Created apps/mobile/.env file${NC}"
else
    echo -e "${GREEN}✓ apps/mobile/.env already exists${NC}"
fi

# 5. Docker services check
echo -e "\n${YELLOW}5. Docker Services${NC}"
echo "------------------"
if command_exists docker; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    
    # Check if Redis is running
    if docker ps | grep -q redis-twin; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}! Redis is not running. Start with: docker-compose up -d redis${NC}"
    fi
    
    # Check if Neo4j is running
    if docker ps | grep -q neo4j-twin; then
        echo -e "${GREEN}✓ Neo4j is running${NC}"
    else
        echo -e "${YELLOW}! Neo4j is not running. Start with: docker-compose up -d neo4j${NC}"
    fi
else
    echo -e "${RED}Warning: Docker is not installed${NC}"
fi

# 6. Summary
echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Dependency Installation Complete!${NC}"
echo -e "${GREEN}================================================${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Update .env file with your API keys and configuration"
echo "2. Start Docker services: docker-compose up -d redis neo4j firebase-emulator"
echo "3. Run the API: cd apps/api && uv run uvicorn app.main:app --reload"
echo "4. Run the admin web: pnpm --filter admin_web dev"
echo "5. Run the mobile app: cd apps/mobile && flutter run"

echo -e "\n${YELLOW}Quick Commands:${NC}"
echo "• Python API:    cd apps/api && uv sync"
echo "• Admin Web:     pnpm install"
echo "• Mobile:        cd apps/mobile && flutter pub get"
echo "• All Services:  docker-compose up -d"

echo -e "\n${YELLOW}Health Check:${NC}"
echo "• API Health:    curl http://localhost:8000/api/health/ready"
echo "• Redis:         redis-cli -a redis123 ping"
echo "• Neo4j:         http://localhost:7474"
