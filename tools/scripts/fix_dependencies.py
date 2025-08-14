#!/usr/bin/env python3
"""
Dependency Resolution Script for Living Twin API

This script helps resolve dependency conflicts by:
1. Upgrading pip to the latest version
2. Installing dependencies with conflict resolution
3. Providing clear error messages and suggestions
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            check=check, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        return e

def upgrade_pip():
    """Upgrade pip to the latest version."""
    print("🔧 Upgrading pip...")
    result = run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    if result.returncode == 0:
        print("✅ pip upgraded successfully")
    else:
        print("❌ Failed to upgrade pip")
        return False
    return True

def install_dependencies_with_resolution():
    """Install dependencies with conflict resolution."""
    api_dir = Path(__file__).parent.parent.parent / "apps" / "api"
    
    print("📦 Installing Python dependencies with conflict resolution...")
    
    # First, try installing from pyproject.toml (preferred)
    print("Trying to install from pyproject.toml...")
    result = run_command([sys.executable, "-m", "pip", "install", "-e", "."], cwd=api_dir, check=False)
    
    if result.returncode == 0:
        print("✅ Dependencies installed successfully from pyproject.toml")
        return True
    
    # If that fails, try requirements.txt with dependency resolver
    print("Falling back to requirements.txt with dependency resolver...")
    result = run_command([
        sys.executable, "-m", "pip", "install", 
        "--use-pep517",
        "--upgrade",
        "-r", "requirements.txt"
    ], cwd=api_dir, check=False)
    
    if result.returncode == 0:
        print("✅ Dependencies installed successfully from requirements.txt")
        return True
    
    # If still failing, try with --force-reinstall for conflicting packages
    print("Trying to force reinstall conflicting packages...")
    conflicting_packages = [
        "python-multipart>=0.0.9",
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.30.1"
    ]
    
    for package in conflicting_packages:
        print(f"Force reinstalling {package}...")
        result = run_command([
            sys.executable, "-m", "pip", "install", 
            "--force-reinstall", 
            "--no-deps", 
            package
        ], cwd=api_dir, check=False)
    
    # Now try installing all dependencies again
    result = run_command([
        sys.executable, "-m", "pip", "install", 
        "-r", "requirements.txt"
    ], cwd=api_dir, check=False)
    
    if result.returncode == 0:
        print("✅ Dependencies installed successfully after force reinstall")
        return True
    else:
        print("❌ Failed to install dependencies")
        return False

def install_dev_dependencies():
    """Install development dependencies."""
    api_dir = Path(__file__).parent.parent.parent / "apps" / "api"
    
    if (api_dir / "requirements-dev.txt").exists():
        print("📦 Installing development dependencies...")
        result = run_command([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements-dev.txt"
        ], cwd=api_dir, check=False)
        
        if result.returncode == 0:
            print("✅ Development dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install development dependencies")
            return False
    else:
        print("ℹ️  No requirements-dev.txt found, skipping dev dependencies")
        return True

def verify_installation():
    """Verify that key packages are installed correctly."""
    print("🔍 Verifying installation...")
    
    key_packages = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pydantic",
        "neo4j"
    ]
    
    all_good = True
    for package in key_packages:
        result = run_command([
            sys.executable, "-c", f"import {package.replace('-', '_')}; print(f'{package} imported successfully')"
        ], check=False)
        
        if result.returncode != 0:
            print(f"❌ Failed to import {package}")
            all_good = False
        else:
            print(f"✅ {package} is working")
    
    return all_good

def main():
    """Main function to fix dependencies."""
    print("🚀 Living Twin Dependency Fixer")
    print("=" * 40)
    
    # Step 1: Upgrade pip
    if not upgrade_pip():
        print("❌ Failed to upgrade pip. Exiting.")
        sys.exit(1)
    
    # Step 2: Install dependencies with resolution
    if not install_dependencies_with_resolution():
        print("❌ Failed to install dependencies. Please check the error messages above.")
        sys.exit(1)
    
    # Step 3: Install dev dependencies
    if not install_dev_dependencies():
        print("⚠️  Development dependencies failed to install, but continuing...")
    
    # Step 4: Verify installation
    if verify_installation():
        print("🎉 All dependencies installed and verified successfully!")
        print("\nNext steps:")
        print("  1. Run 'make docker-up' to start local services")
        print("  2. Run 'make seed-db' to populate test data")
        print("  3. Test the API with: cd apps/api && python -m uvicorn app.main:app --reload")
    else:
        print("⚠️  Some packages may have issues. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
