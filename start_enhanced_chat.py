#!/usr/bin/env python3
"""
Start the Enhanced ClearCouncil Chat Server

This script starts the enhanced web server with real voting data.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_data_file():
    """Check if voting data file exists."""
    data_file = Path("clearcouncil_data.json")
    return data_file.exists()

def main():
    """Main function."""
    print("🏛️ Enhanced ClearCouncil AI Chat Server")
    print("=" * 50)
    
    # Check if data file exists
    if not check_data_file():
        print("⚠️  Voting data file not found. Loading data first...")
        try:
            subprocess.run([sys.executable, "data_preloader.py"])
            print("✅ Data loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print("💡 Try running: python data_preloader.py")
            return
    else:
        print("✅ Voting data file found")
    
    # Check environment
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Environment file found")
    else:
        print("⚠️  .env file not found - AI features may be limited")
    
    print("\n🚀 Starting Enhanced ClearCouncil Chat Server...")
    print("📊 Features:")
    print("   • Real voting data from 39 representatives")
    print("   • 3,795 voting records")
    print("   • AI-powered responses with actual council data")
    print("   • Representative profiles and voting statistics")
    print("")
    print("📱 Open in browser: http://localhost:5003")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start the enhanced server
        subprocess.run([sys.executable, "clearcouncil_chat_enhanced.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()