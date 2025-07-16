#!/usr/bin/env python3
"""
Simple startup script for ClearCouncil Integrated App
"""

import os
import sys
from pathlib import Path

def main():
    """Start the integrated ClearCouncil application"""
    print("🏛️ ClearCouncil Integrated App Startup")
    print("=====================================")
    
    # Check if we're in the right directory
    if not Path("clearcouncil_integrated_app.py").exists():
        print("❌ Error: clearcouncil_integrated_app.py not found")
        print("   Make sure you're in the project directory")
        return 1
    
    # Check if database exists
    if not Path("clearcouncil.db").exists():
        print("❌ Error: clearcouncil.db not found")
        print("   The database file is required for the app to work")
        return 1
    
    # Check environment variables
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("⚠️  Warning: GITHUB_TOKEN not set - chat functionality may be limited")
    else:
        print("✅ GitHub token configured")
    
    print("\n🚀 Starting application...")
    print("📍 URL: http://localhost:5000")
    print("💬 Features: Dashboard, Chat, Search, Representatives, Transparency")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        # Import and run the app
        from clearcouncil_integrated_app import create_app
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Try: pip install flask requests")
        return 1
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())