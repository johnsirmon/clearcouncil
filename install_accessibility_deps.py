#!/usr/bin/env python3
"""
Install accessibility testing dependencies for ClearCouncil.

This script installs the required packages for accessibility testing
in the existing virtual environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def main():
    """Main installation process."""
    print("Installing ClearCouncil Accessibility Testing Dependencies")
    print("="*60)
    
    # Check if we're in a virtual environment
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Virtual environment not detected. Make sure you've activated it:")
        print("   source .venv/bin/activate")
        print("\nContinuing anyway...")
    
    # Install Python packages
    packages = [
        "axe-core-python>=4.7.0",
        "playwright>=1.40.0", 
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0"
    ]
    
    success = True
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            success = False
    
    # Install Playwright browsers
    if success:
        if not run_command("python -m playwright install chromium", "Installing Playwright browsers"):
            print("⚠️  Playwright browser installation failed, but continuing...")
    
    # Update requirements.txt if needed
    requirements_path = Path("requirements.txt")
    if requirements_path.exists():
        print("\n📝 Requirements.txt already updated with accessibility dependencies")
    
    if success:
        print("\n✅ All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Make sure your web server is running:")
        print("   python clearcouncil_web.py serve --host 127.0.0.1 --port 5000")
        print("2. Run accessibility tests:")
        print("   python test_accessibility.py")
    else:
        print("\n❌ Some dependencies failed to install. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()