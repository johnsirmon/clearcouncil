#!/usr/bin/env python3
"""
Dependency installer for ClearCouncil that works without pip.
"""

import sys
import os
import subprocess
import urllib.request
import zipfile
import tempfile
from pathlib import Path

def install_with_user_pip():
    """Try to install dependencies using user pip."""
    print("🔍 Trying to install dependencies with pip...")
    
    basic_packages = [
        "python-dotenv",
        "PyYAML", 
        "requests",
        "pandas",
        "PyPDF2",
        "python-dateutil",
        "tqdm"
    ]
    
    viz_packages = [
        "matplotlib",
        "seaborn"
    ]
    
    try:
        # Try basic packages first
        cmd = [sys.executable, "-m", "pip", "install", "--user"] + basic_packages
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Basic packages installed successfully")
            
            # Try visualization packages
            cmd = [sys.executable, "-m", "pip", "install", "--user"] + viz_packages
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Visualization packages installed successfully")
            else:
                print("⚠️  Visualization packages failed, but basic functionality will work")
            
            return True
        else:
            print(f"❌ pip install failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error using pip: {e}")
        return False

def test_imports():
    """Test if required modules can be imported."""
    print("\n🧪 Testing imports...")
    
    required = ["yaml", "requests", "pandas", "PyPDF2", "dateutil", "tqdm"]
    optional = ["matplotlib", "seaborn", "dotenv"]
    
    missing_required = []
    missing_optional = []
    
    for module in required:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing_required.append(module)
    
    for module in optional:
        try:
            __import__(module)
            print(f"✅ {module} (optional)")
        except ImportError:
            print(f"⚠️  {module} (optional)")
            missing_optional.append(module)
    
    return len(missing_required) == 0

def main():
    """Main installation process."""
    print("🏛️  ClearCouncil Dependency Installer")
    print("=" * 45)
    
    # First, test if everything is already available
    if test_imports():
        print("\n🎉 All required dependencies are already installed!")
        return True
    
    print("\n📦 Installing missing dependencies...")
    
    # Try to install with pip
    if install_with_user_pip():
        print("\n✅ Installation completed!")
        
        # Test again
        if test_imports():
            print("🎉 All dependencies are now working!")
            return True
        else:
            print("⚠️  Some imports still failing after installation")
            return False
    else:
        print("\n❌ Automatic installation failed.")
        print("\n📝 Manual installation instructions:")
        print("=" * 40)
        print("Please run one of these commands in your terminal:")
        print()
        print("Option 1 (Recommended):")
        print("  python3 -m pip install --user python-dotenv PyYAML requests pandas PyPDF2 python-dateutil tqdm matplotlib seaborn")
        print()
        print("Option 2 (If pip not available):")
        print("  # On Ubuntu/Debian:")
        print("  sudo apt install python3-pip")
        print("  # Then run Option 1")
        print()
        print("Option 3 (Conda users):")
        print("  conda install pyyaml requests pandas matplotlib seaborn")
        print("  pip install python-dotenv PyPDF2 python-dateutil tqdm")
        print()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready to test ClearCouncil!")
        print("Run: python3 run_local_tests.py")
    else:
        print("\n⚠️  Manual setup required - see instructions above")