#!/bin/bash
# Living Twin Development Environment Validation Script
# This script checks if all required tools are properly installed

echo "🔍 Validating Living Twin development environment..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Function to print colored output
print_check() {
    local status=$1
    local message=$2
    local details=$3
    
    case $status in
        "PASS")
            echo -e "${GREEN}✅ PASS${NC} $message"
            if [[ -n "$details" ]]; then
                echo -e "   ${BLUE}ℹ️  $details${NC}"
            fi
            ((PASSED++))
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL${NC} $message"
            if [[ -n "$details" ]]; then
                echo -e "   ${RED}💡 $details${NC}"
            fi
            ((FAILED++))
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️  WARN${NC} $message"
            if [[ -n "$details" ]]; then
                echo -e "   ${YELLOW}💡 $details${NC}"
            fi
            ((WARNINGS++))
            ;;
    esac
}

# Check operating system
echo "🖥️  Operating System"
echo "-------------------"
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_check "PASS" "macOS detected" "$(sw_vers -productName) $(sw_vers -productVersion)"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        print_check "PASS" "Linux detected" "$PRETTY_NAME"
    else
        print_check "PASS" "Linux detected" "Unknown distribution"
    fi
else
    print_check "WARN" "Unknown operating system" "Some features may not work correctly"
fi
echo

# Check core tools
echo "🔧 Core Development Tools"
echo "-------------------------"

# Docker
if command -v docker &> /dev/null; then
    docker_version=$(docker --version 2>/dev/null)
    if docker info &> /dev/null; then
        print_check "PASS" "Docker" "$docker_version (daemon running)"
    else
        print_check "WARN" "Docker" "$docker_version (daemon not running - start Docker Desktop)"
    fi
else
    print_check "FAIL" "Docker" "Install Docker Desktop or Docker Engine"
fi

# Docker Compose
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version 2>/dev/null)
    print_check "PASS" "Docker Compose (standalone)" "$compose_version"
elif docker compose version &> /dev/null 2>&1; then
    compose_version=$(docker compose version 2>/dev/null)
    print_check "PASS" "Docker Compose (plugin)" "$compose_version"
else
    print_check "FAIL" "Docker Compose" "Install Docker Compose"
fi

# Git
if command -v git &> /dev/null; then
    git_version=$(git --version)
    git_user=$(git config --global user.name 2>/dev/null || echo "Not configured")
    git_email=$(git config --global user.email 2>/dev/null || echo "Not configured")
    print_check "PASS" "Git" "$git_version"
    if [[ "$git_user" == "Not configured" ]] || [[ "$git_email" == "Not configured" ]]; then
        print_check "WARN" "Git configuration" "Run: git config --global user.name 'Your Name' && git config --global user.email 'your@email.com'"
    else
        print_check "PASS" "Git configuration" "User: $git_user, Email: $git_email"
    fi
else
    print_check "FAIL" "Git" "Install Git"
fi
echo

# Check backend development tools
echo "🐍 Backend Development"
echo "----------------------"

# Python
if command -v python3.11 &> /dev/null; then
    python_version=$(python3.11 --version)
    print_check "PASS" "Python 3.11" "$python_version"
elif command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    major_version=$(echo $python_version | cut -d' ' -f2 | cut -d'.' -f1)
    minor_version=$(echo $python_version | cut -d' ' -f2 | cut -d'.' -f2)
    if [[ $major_version -eq 3 ]] && [[ $minor_version -ge 11 ]]; then
        print_check "PASS" "Python 3" "$python_version (compatible)"
    else
        print_check "WARN" "Python 3" "$python_version (recommend 3.11+)"
    fi
else
    print_check "FAIL" "Python" "Install Python 3.11+"
fi

# pip
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    if command -v pip3 &> /dev/null; then
        pip_version=$(pip3 --version)
        print_check "PASS" "pip3" "$pip_version"
    else
        pip_version=$(pip --version)
        print_check "PASS" "pip" "$pip_version"
    fi
else
    print_check "FAIL" "pip" "Install pip (Python package manager)"
fi

# Virtual environment capability
if command -v python3 &> /dev/null; then
    if python3 -m venv --help &> /dev/null; then
        print_check "PASS" "Python venv" "Virtual environment support available"
    else
        print_check "WARN" "Python venv" "Install python3-venv package"
    fi
fi
echo

# Check frontend development tools
echo "🌐 Frontend Development"
echo "-----------------------"

# Node.js
if command -v node &> /dev/null; then
    node_version=$(node --version)
    major_version=$(echo $node_version | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ $major_version -ge 20 ]]; then
        print_check "PASS" "Node.js" "$node_version"
    elif [[ $major_version -ge 18 ]]; then
        print_check "WARN" "Node.js" "$node_version (recommend 20+)"
    else
        print_check "FAIL" "Node.js" "$node_version (requires 18+, recommend 20+)"
    fi
else
    print_check "FAIL" "Node.js" "Install Node.js 20+"
fi

# npm
if command -v npm &> /dev/null; then
    npm_version=$(npm --version)
    print_check "PASS" "npm" "v$npm_version"
else
    print_check "FAIL" "npm" "Install npm (comes with Node.js)"
fi
echo

# Check mobile development tools
echo "📱 Mobile Development"
echo "--------------------"

# Flutter
if command -v flutter &> /dev/null; then
    flutter_version=$(flutter --version | head -n1)
    print_check "PASS" "Flutter" "$flutter_version"
    
    # Run flutter doctor for detailed analysis
    echo "   Running flutter doctor..."
    flutter_doctor_output=$(flutter doctor 2>/dev/null)
    if echo "$flutter_doctor_output" | grep -q "No issues found"; then
        print_check "PASS" "Flutter doctor" "All checks passed"
    else
        print_check "WARN" "Flutter doctor" "Some issues found - run 'flutter doctor' for details"
    fi
else
    print_check "WARN" "Flutter" "Install Flutter for mobile development"
fi

# Android development (if Flutter is installed)
if command -v flutter &> /dev/null; then
    if flutter doctor | grep -q "Android toolchain"; then
        if flutter doctor | grep -q "Android toolchain.*✓"; then
            print_check "PASS" "Android toolchain" "Ready for Android development"
        else
            print_check "WARN" "Android toolchain" "Issues detected - run 'flutter doctor' for details"
        fi
    else
        print_check "WARN" "Android toolchain" "Install Android Studio and SDK"
    fi
    
    # iOS development (macOS only)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v xcodebuild &> /dev/null; then
            xcode_version=$(xcodebuild -version | head -n1)
            print_check "PASS" "Xcode" "$xcode_version"
        else
            print_check "WARN" "Xcode" "Install Xcode for iOS development"
        fi
    fi
fi
echo

# Check additional development tools
echo "🛠️  Additional Tools"
echo "-------------------"

# jq (JSON processor)
if command -v jq &> /dev/null; then
    jq_version=$(jq --version)
    print_check "PASS" "jq" "$jq_version"
else
    print_check "WARN" "jq" "Install jq for JSON processing"
fi

# curl
if command -v curl &> /dev/null; then
    curl_version=$(curl --version | head -n1)
    print_check "PASS" "curl" "$curl_version"
else
    print_check "WARN" "curl" "Install curl for HTTP requests"
fi

# make
if command -v make &> /dev/null; then
    make_version=$(make --version | head -n1)
    print_check "PASS" "make" "$make_version"
else
    print_check "WARN" "make" "Install make for build automation"
fi
echo

# Check project-specific requirements
echo "🏗️  Project Environment"
echo "----------------------"

# Check if we're in the project directory
if [[ -f "Makefile" ]] && [[ -f "docker-compose.yml" ]] && [[ -d "apps" ]]; then
    print_check "PASS" "Project structure" "Living Twin monorepo detected"
    
    # Check .env file
    if [[ -f ".env" ]]; then
        print_check "PASS" "Environment file" ".env file exists"
    else
        if [[ -f ".env.example" ]]; then
            print_check "WARN" "Environment file" "Copy .env.example to .env and configure"
        else
            print_check "WARN" "Environment file" "Create .env file with configuration"
        fi
    fi
    
    # Check Python virtual environment
    if [[ -d ".venv" ]]; then
        print_check "PASS" "Python virtual environment" ".venv directory exists"
    else
        print_check "WARN" "Python virtual environment" "Run 'make install' to create virtual environment"
    fi
    
    # Check Node.js dependencies
    if [[ -d "apps/admin_web/node_modules" ]]; then
        print_check "PASS" "Node.js dependencies" "Frontend dependencies installed"
    else
        print_check "WARN" "Node.js dependencies" "Run 'make node-setup' to install frontend dependencies"
    fi
    
else
    print_check "WARN" "Project structure" "Not in Living Twin project directory"
fi
echo

# Summary
echo "📊 Validation Summary"
echo "===================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo

# Recommendations based on results
if [[ $FAILED -gt 0 ]]; then
    echo -e "${RED}🚨 Critical Issues Found${NC}"
    echo "Please install the failed components before proceeding."
    echo
fi

if [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Recommendations${NC}"
    echo "Consider addressing the warnings for the best development experience."
    echo
fi

if [[ $FAILED -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}🎉 Perfect! Your development environment is fully configured.${NC}"
    echo
fi

# Next steps
echo "📋 Next Steps"
echo "============="
if [[ -f "Makefile" ]]; then
    echo "1. Set up the project environment:"
    echo "   make install"
    echo "   make node-setup"
    echo
    echo "2. Start the development environment:"
    echo "   make dev-local    # Local development with containers"
    echo "   make dev-openai   # Development with OpenAI integration"
    echo
    echo "3. Access the applications:"
    echo "   - Neo4j Browser: http://localhost:7474"
    echo "   - API: http://localhost:8080"
    echo "   - Admin Web: http://localhost:5173"
    echo
else
    echo "1. Clone the Living Twin repository:"
    echo "   git clone https://github.com/kpernyer/living-twin-monorep.git"
    echo "   cd living-twin-monorep"
    echo
    echo "2. Run this validation script again from the project directory"
    echo
fi

echo "📚 For more information:"
echo "   - Development setup: docs/DEVELOPMENT_ENVIRONMENT_SETUP.md"
echo "   - Local development: docs/README_LOCAL_DEV.md"
echo "   - Architecture: docs/ARCHITECTURE.md"

# Exit with appropriate code
if [[ $FAILED -gt 0 ]]; then
    exit 1
else
    exit 0
fi
