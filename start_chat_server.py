#!/usr/bin/env python3
"""
Start the ClearCouncil Chat Server

This script starts the web server and provides setup information.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_setup():
    """Check if the setup is complete."""
    print("🔍 Checking setup...")
    
    issues = []
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        issues.append("❌ .env file not found")
    else:
        # Check if GitHub token is configured
        github_token = None
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('GITHUB_TOKEN='):
                    github_token = line.split('=', 1)[1].strip()
                    break
        
        if not github_token or github_token == 'your_github_token_here':
            issues.append("❌ GitHub token not configured in .env")
        else:
            print("✅ GitHub token configured")
    
    # Check if chatbot module is available
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from clearcouncil_chat_minimal import ClearCouncilChatBot
        print("✅ ChatBot module available")
    except ImportError as e:
        issues.append(f"❌ ChatBot module not available: {e}")
    
    # Check if ClearCouncil is available
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from clearcouncil.config.settings import list_available_councils
        councils = list_available_councils()
        print(f"✅ ClearCouncil available ({len(councils)} councils)")
    except ImportError as e:
        issues.append(f"❌ ClearCouncil limited: {e}")
    
    return issues

def show_instructions():
    """Show setup instructions."""
    print("\n💡 Setup Instructions:")
    print("1. Make sure you have a GitHub token with 'models' permission")
    print("2. Add it to your .env file: GITHUB_TOKEN=your_token_here")
    print("3. Get a token at: https://github.com/settings/tokens")
    print("4. Required scopes: repo, user, models")

def main():
    """Main function."""
    print("🏛️ ClearCouncil AI Chat Server")
    print("=" * 50)
    
    # Check setup
    issues = check_setup()
    
    if issues:
        print("\n⚠️  Setup issues found:")
        for issue in issues:
            print(f"   {issue}")
        
        show_instructions()
        
        response = input("\n❓ Start server anyway? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("🛑 Server startup cancelled")
            return
    
    print("\n🚀 Starting ClearCouncil Chat Server...")
    print("📱 Open in browser: http://localhost:5002")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run([sys.executable, "clearcouncil_chat_server.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()