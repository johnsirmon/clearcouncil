#!/usr/bin/env python3
"""
Install script for ClearCouncil Chat dependencies

This script attempts to install the required dependencies for the chat application
using various methods available in different environments.
"""

import subprocess
import sys
import os
from pathlib import Path

def try_install_with_apt():
    """Try to install dependencies using apt (Ubuntu/Debian)."""
    print("🔧 Trying to install dependencies with apt...")
    
    packages = [
        "python3-flask",
        "python3-pip",
        "python3-dotenv",
        "python3-requests"
    ]
    
    for package in packages:
        try:
            result = subprocess.run(
                ["apt", "list", "--installed", package],
                capture_output=True,
                text=True
            )
            
            if package in result.stdout:
                print(f"✅ {package} already installed")
            else:
                print(f"🔄 Installing {package}...")
                subprocess.run(["sudo", "apt", "install", "-y", package], check=True)
                print(f"✅ {package} installed successfully")
                
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
        except FileNotFoundError:
            print("❌ apt not available")
            return False
    
    return True

def try_install_with_pip():
    """Try to install dependencies using pip."""
    print("🔧 Trying to install dependencies with pip...")
    
    packages = [
        "flask>=3.0.0",
        "flask-cors>=4.0.0", 
        "python-dotenv>=1.0.0",
        "requests>=2.31.0"
    ]
    
    for package in packages:
        try:
            print(f"🔄 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def try_install_user_pip():
    """Try to install dependencies using pip --user."""
    print("🔧 Trying to install dependencies with pip --user...")
    
    packages = [
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "python-dotenv>=1.0.0", 
        "requests>=2.31.0"
    ]
    
    for package in packages:
        try:
            print(f"🔄 Installing {package} (user install)...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", package], check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def test_imports():
    """Test if required modules can be imported."""
    print("🧪 Testing imports...")
    
    modules = ["flask", "flask_cors", "dotenv", "requests"]
    all_available = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} available")
        except ImportError:
            print(f"❌ {module} not available")
            all_available = False
    
    return all_available

def create_simple_requirements():
    """Create a simple requirements file for manual installation."""
    print("📝 Creating simple requirements file...")
    
    requirements = """# ClearCouncil Chat Dependencies
flask>=3.0.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
requests>=2.31.0
"""
    
    with open("chat_requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Created chat_requirements.txt")
    print("💡 Try: pip install -r chat_requirements.txt")

def main():
    """Main installation function."""
    print("🏛️ ClearCouncil Chat Dependency Installer")
    print("=" * 50)
    
    # First check if dependencies are already available
    if test_imports():
        print("🎉 All dependencies already available!")
        return True
    
    # Try different installation methods
    methods = [
        ("pip", try_install_with_pip),
        ("pip --user", try_install_user_pip),
        ("apt", try_install_with_apt)
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔄 Trying installation method: {method_name}")
        try:
            if method_func():
                print(f"✅ Installation successful with {method_name}")
                if test_imports():
                    print("🎉 All dependencies now available!")
                    return True
                else:
                    print("⚠️  Installation completed but imports still failing")
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")
    
    # If all methods fail, create requirements file
    print("\n❌ All installation methods failed")
    create_simple_requirements()
    
    print("\n💡 Manual installation options:")
    print("1. pip install -r chat_requirements.txt")
    print("2. sudo apt install python3-flask python3-pip python3-dotenv")
    print("3. Use conda: conda install flask flask-cors python-dotenv requests")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready to run ClearCouncil Chat!")
        print("Next steps:")
        print("1. Add GitHub token to .env file")
        print("2. Run: python clearcouncil_chat.py")
    else:
        print("\n⚠️  Manual installation required")
    
    sys.exit(0 if success else 1)