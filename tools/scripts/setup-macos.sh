#!/bin/bash
# Living Twin Development Environment Setup for macOS
# This script automates the installation of development tools

set -e  # Exit on any error

echo "🚀 Setting up Living Twin development environment for macOS..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only!"
    exit 1
fi

# Install Homebrew if not present
print_status "Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    print_status "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    print_success "Homebrew installed successfully!"
else
    print_success "Homebrew already installed: $(brew --version | head -n1)"
fi

# Update Homebrew
print_status "Updating Homebrew..."
brew update

# Install core development tools
print_status "Installing core development tools..."

# Docker Desktop
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker Desktop..."
    brew install --cask docker
    print_success "Docker Desktop installed!"
    print_warning "Please start Docker Desktop from Applications folder before continuing"
else
    print_success "Docker already installed: $(docker --version)"
fi

# Git
if ! command -v git &> /dev/null; then
    print_status "Installing Git..."
    brew install git
    print_success "Git installed!"
else
    print_success "Git already installed: $(git --version)"
fi

# Node.js 20
print_status "Installing Node.js 20..."
if command -v node &> /dev/null; then
    current_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ $current_version -lt 20 ]]; then
        print_warning "Node.js version $current_version detected. Installing Node.js 20..."
        brew install node@20
        brew link --force node@20
    else
        print_success "Node.js already installed: $(node --version)"
    fi
else
    brew install node@20
    brew link --force node@20
    print_success "Node.js 20 installed!"
fi

# Python 3.11 (for local development if needed)
print_status "Checking Python installation..."
if command -v python3.11 &> /dev/null; then
    print_success "Python 3.11 already installed: $(python3.11 --version)"
else
    print_status "Installing Python 3.11..."
    brew install python@3.11
    print_success "Python 3.11 installed!"
fi

# Optional: Flutter for mobile development
echo ""
read -p "$(echo -e ${YELLOW}Install Flutter for mobile development? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! command -v flutter &> /dev/null; then
        print_status "Installing Flutter..."
        brew install --cask flutter
        print_success "Flutter installed!"
        
        # Run flutter doctor to check setup
        print_status "Running flutter doctor..."
        flutter doctor
    else
        print_success "Flutter already installed: $(flutter --version | head -n1)"
    fi
fi

# Optional: Android Studio
echo ""
read -p "$(echo -e ${YELLOW}Install Android Studio for Android development? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! brew list --cask android-studio &> /dev/null; then
        print_status "Installing Android Studio..."
        brew install --cask android-studio
        print_success "Android Studio installed!"
        print_warning "Please open Android Studio and complete the setup wizard"
    else
        print_success "Android Studio already installed!"
    fi
fi

# Optional: VS Code
echo ""
read -p "$(echo -e ${YELLOW}Install Visual Studio Code? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! brew list --cask visual-studio-code &> /dev/null; then
        print_status "Installing Visual Studio Code..."
        brew install --cask visual-studio-code
        print_success "VS Code installed!"
    else
        print_success "VS Code already installed!"
    fi
fi

# Create development directory structure
print_status "Setting up development environment..."
mkdir -p ~/Development/living-twin

# Set up Git configuration if not already done
if [[ -z $(git config --global user.name) ]]; then
    echo ""
    read -p "$(echo -e ${YELLOW}Enter your Git username:${NC} )" git_username
    read -p "$(echo -e ${YELLOW}Enter your Git email:${NC} )" git_email
    
    git config --global user.name "$git_username"
    git config --global user.email "$git_email"
    print_success "Git configuration completed!"
fi

# Install useful development tools
print_status "Installing additional development tools..."
brew install jq curl wget tree htop

echo ""
echo "=================================================="
print_success "Living Twin development environment setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Start Docker Desktop from Applications"
echo "2. Clone the repository:"
echo "   git clone https://github.com/kpernyer/living-twin-monorep.git"
echo "3. Navigate to the project and run setup:"
echo "   cd living-twin-monorep"
echo "   make install"
echo ""
echo "🔍 To validate your environment, run:"
echo "   ./tools/scripts/validate-environment.sh"
echo ""
echo "📚 For more information, see docs/DEVELOPMENT_ENVIRONMENT_SETUP.md"
echo "=================================================="
