#!/bin/bash
# Living Twin Development Environment Setup for Linux
# This script automates the installation of development tools

set -e  # Exit on any error

echo "🚀 Setting up Living Twin development environment for Linux..."
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

# Detect Linux distribution
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    DISTRO=$ID
else
    print_error "Cannot detect Linux distribution!"
    exit 1
fi

print_status "Detected Linux distribution: $DISTRO"

# Update package manager
print_status "Updating package manager..."
case $DISTRO in
    ubuntu|debian)
        sudo apt update
        INSTALL_CMD="sudo apt install -y"
        ;;
    fedora|centos|rhel)
        sudo dnf update -y
        INSTALL_CMD="sudo dnf install -y"
        ;;
    arch|manjaro)
        sudo pacman -Syu --noconfirm
        INSTALL_CMD="sudo pacman -S --noconfirm"
        ;;
    *)
        print_warning "Unsupported distribution. Assuming apt-based system."
        sudo apt update
        INSTALL_CMD="sudo apt install -y"
        ;;
esac

# Install basic development tools
print_status "Installing basic development tools..."
case $DISTRO in
    ubuntu|debian)
        $INSTALL_CMD curl wget git build-essential software-properties-common apt-transport-https ca-certificates gnupg lsb-release
        ;;
    fedora|centos|rhel)
        $INSTALL_CMD curl wget git gcc gcc-c++ make dnf-plugins-core
        ;;
    arch|manjaro)
        $INSTALL_CMD curl wget git base-devel
        ;;
esac

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    case $DISTRO in
        ubuntu|debian)
            # Add Docker's official GPG key
            curl -fsSL https://download.docker.com/linux/$DISTRO/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            # Add Docker repository
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$DISTRO $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # Install Docker
            sudo apt update
            $INSTALL_CMD docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        fedora)
            sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
            $INSTALL_CMD docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        centos|rhel)
            sudo yum config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            $INSTALL_CMD docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        arch|manjaro)
            $INSTALL_CMD docker docker-compose
            ;;
    esac
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Enable and start Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    
    print_success "Docker installed successfully!"
    print_warning "Please log out and back in for Docker group permissions to take effect"
else
    print_success "Docker already installed: $(docker --version)"
fi

# Install Docker Compose (if not installed with Docker)
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_status "Installing Docker Compose..."
    case $DISTRO in
        ubuntu|debian|fedora|centos|rhel)
            # Install via pip as fallback
            if command -v pip3 &> /dev/null; then
                pip3 install --user docker-compose
            else
                # Download binary
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
            fi
            ;;
        arch|manjaro)
            # Already installed with docker package
            ;;
    esac
    print_success "Docker Compose installed!"
fi

# Install Node.js 20
print_status "Installing Node.js 20..."
if ! command -v node &> /dev/null || [[ $(node --version | cut -d'v' -f2 | cut -d'.' -f1) -lt 20 ]]; then
    case $DISTRO in
        ubuntu|debian)
            # Install via NodeSource repository
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            $INSTALL_CMD nodejs
            ;;
        fedora|centos|rhel)
            # Install via NodeSource repository
            curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
            $INSTALL_CMD nodejs
            ;;
        arch|manjaro)
            $INSTALL_CMD nodejs npm
            ;;
    esac
    print_success "Node.js 20 installed: $(node --version)"
else
    print_success "Node.js already installed: $(node --version)"
fi

# Install Python 3.11
print_status "Installing Python 3.11..."
case $DISTRO in
    ubuntu|debian)
        # Add deadsnakes PPA for newer Python versions
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update
        $INSTALL_CMD python3.11 python3.11-venv python3.11-pip python3.11-dev
        ;;
    fedora)
        $INSTALL_CMD python3.11 python3.11-pip python3.11-devel
        ;;
    centos|rhel)
        # Enable EPEL repository
        $INSTALL_CMD epel-release
        $INSTALL_CMD python3.11 python3.11-pip python3.11-devel
        ;;
    arch|manjaro)
        $INSTALL_CMD python python-pip
        ;;
esac

if command -v python3.11 &> /dev/null; then
    print_success "Python 3.11 installed: $(python3.11 --version)"
elif command -v python3 &> /dev/null; then
    print_success "Python 3 installed: $(python3 --version)"
else
    print_warning "Python installation may have failed"
fi

# Install additional development tools
print_status "Installing additional development tools..."
case $DISTRO in
    ubuntu|debian)
        $INSTALL_CMD jq tree htop vim nano
        ;;
    fedora|centos|rhel)
        $INSTALL_CMD jq tree htop vim nano
        ;;
    arch|manjaro)
        $INSTALL_CMD jq tree htop vim nano
        ;;
esac

# Optional: Flutter for mobile development
echo ""
read -p "$(echo -e ${YELLOW}Install Flutter for mobile development? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! command -v flutter &> /dev/null; then
        print_status "Installing Flutter..."
        case $DISTRO in
            ubuntu|debian)
                sudo snap install flutter --classic
                ;;
            fedora|centos|rhel)
                # Manual installation
                cd /tmp
                wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz
                sudo tar xf flutter_linux_3.16.0-stable.tar.xz -C /opt/
                echo 'export PATH="$PATH:/opt/flutter/bin"' >> ~/.bashrc
                export PATH="$PATH:/opt/flutter/bin"
                ;;
            arch|manjaro)
                # Install from AUR (requires yay or similar)
                if command -v yay &> /dev/null; then
                    yay -S flutter
                else
                    print_warning "Please install Flutter manually from AUR or use snap"
                fi
                ;;
        esac
        
        # Run flutter doctor
        if command -v flutter &> /dev/null; then
            print_status "Running flutter doctor..."
            flutter doctor
            print_success "Flutter installed!"
        fi
    else
        print_success "Flutter already installed: $(flutter --version | head -n1)"
    fi
fi

# Optional: Android Studio
echo ""
read -p "$(echo -e ${YELLOW}Install Android Studio for Android development? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    case $DISTRO in
        ubuntu|debian)
            sudo snap install android-studio --classic
            ;;
        fedora|centos|rhel)
            # Download and install manually
            print_status "Please download Android Studio from https://developer.android.com/studio"
            print_status "and follow the installation instructions"
            ;;
        arch|manjaro)
            if command -v yay &> /dev/null; then
                yay -S android-studio
            else
                print_warning "Please install Android Studio from AUR"
            fi
            ;;
    esac
    print_success "Android Studio installation initiated!"
fi

# Optional: VS Code
echo ""
read -p "$(echo -e ${YELLOW}Install Visual Studio Code? [y/N]:${NC} )" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    case $DISTRO in
        ubuntu|debian)
            # Add Microsoft GPG key and repository
            wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
            sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
            echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
            sudo apt update
            $INSTALL_CMD code
            ;;
        fedora|centos|rhel)
            sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
            echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/vscode.repo
            $INSTALL_CMD code
            ;;
        arch|manjaro)
            if command -v yay &> /dev/null; then
                yay -S visual-studio-code-bin
            else
                print_warning "Please install VS Code from AUR"
            fi
            ;;
    esac
    print_success "VS Code installed!"
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

echo ""
echo "=================================================="
print_success "Living Twin development environment setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Log out and back in for Docker group permissions"
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
