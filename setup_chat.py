#!/usr/bin/env python3
"""
Setup script for ClearCouncil Chat Application

This script sets up the ClearCouncil Chat application with GitHub Models integration.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install additional requirements for chat functionality."""
    print("📦 Installing chat application requirements...")
    
    additional_requirements = [
        "flask-cors>=4.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0"
    ]
    
    for req in additional_requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ Installed {req}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {req}")
            return False
    
    return True

def setup_environment():
    """Set up environment variables."""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    # Create .env.example if it doesn't exist
    if not env_example.exists():
        env_example_content = """# ClearCouncil Chat Environment Variables

# GitHub Personal Access Token (required for free AI models)
# Get yours at: https://github.com/settings/tokens
# Select "repo" and "user" scopes
GITHUB_TOKEN=your_github_token_here

# OpenAI API Key (optional, for existing ClearCouncil features)
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
"""
        env_example.write_text(env_example_content)
        print("✅ Created .env.example file")
    
    # Check if .env exists
    if not env_file.exists():
        print(f"⚠️  .env file not found. Please:")
        print(f"   1. Copy .env.example to .env")
        print(f"   2. Add your GitHub token from: https://github.com/settings/tokens")
        print(f"   3. Required scopes: 'repo' and 'user'")
        return False
    
    # Check if GitHub token is configured
    try:
        from dotenv import load_dotenv
        load_dotenv()
        github_token = os.getenv('GITHUB_TOKEN')
        
        if not github_token or github_token == 'your_github_token_here':
            print("⚠️  GitHub token not configured in .env file")
            print("   Please add your GitHub token to use free AI models")
            return False
        
        print("✅ GitHub token configured")
        return True
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

def create_startup_script():
    """Create startup script for easy launching."""
    print("🚀 Creating startup script...")
    
    startup_script = Path("start_chat.sh")
    startup_content = """#!/bin/bash
# ClearCouncil Chat Application Startup Script

echo "🏛️ Starting ClearCouncil Chat Application..."
echo "📡 Using GitHub Models (Free AI)"
echo "🌐 Web interface will be available at: http://localhost:5002"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and add your GitHub token"
    echo "Get your token at: https://github.com/settings/tokens"
    exit 1
fi

# Start the application
python clearcouncil_chat.py
"""
    
    startup_script.write_text(startup_content)
    startup_script.chmod(0o755)
    print("✅ Created start_chat.sh")
    
    # Create Windows batch file too
    bat_script = Path("start_chat.bat")
    bat_content = """@echo off
echo 🏛️ Starting ClearCouncil Chat Application...
echo 📡 Using GitHub Models (Free AI)
echo 🌐 Web interface will be available at: http://localhost:5002
echo.

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please copy .env.example to .env and add your GitHub token
    echo Get your token at: https://github.com/settings/tokens
    pause
    exit /b 1
)

REM Start the application
python clearcouncil_chat.py
pause
"""
    
    bat_script.write_text(bat_content)
    print("✅ Created start_chat.bat")

def test_github_connection():
    """Test GitHub Models connection."""
    print("🔍 Testing GitHub Models connection...")
    
    try:
        from dotenv import load_dotenv
        import requests
        
        load_dotenv()
        github_token = os.getenv('GITHUB_TOKEN')
        
        if not github_token:
            print("⚠️  No GitHub token found")
            return False
        
        # Test GitHub Models API
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://models.inference.ai.azure.com/catalog/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Connected to GitHub Models! Found {len(models)} available models")
            return True
        else:
            print(f"❌ GitHub Models API error: {response.status_code}")
            return False
            
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🏛️ ClearCouncil Chat Application Setup")
    print("=====================================")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup incomplete")
        print("Please configure your .env file and run setup again")
        sys.exit(1)
    
    # Test GitHub connection
    if not test_github_connection():
        print("❌ GitHub Models connection failed")
        print("Please check your GitHub token and try again")
        sys.exit(1)
    
    # Create startup scripts
    create_startup_script()
    
    print("\n🎉 Setup Complete!")
    print("================")
    print("✅ ClearCouncil Chat is ready to use!")
    print("")
    print("🚀 To start the application:")
    print("   Linux/Mac: ./start_chat.sh")
    print("   Windows:   start_chat.bat")
    print("   Manual:    python clearcouncil_chat.py")
    print("")
    print("🌐 Web interface: http://localhost:5002")
    print("📡 AI Model: GitHub GPT-4o-mini (Free)")
    print("")
    print("💡 Features:")
    print("   • Chat with your council data")
    print("   • Search documents with AI")
    print("   • Analyze voting patterns")
    print("   • Ask questions in natural language")
    print("")
    print("📖 Need help? Check the README.md for usage examples")

if __name__ == "__main__":
    main()