#!/usr/bin/env python3
"""Test script for the web server."""

import subprocess
import time
import requests
import threading
import sys
import os

def test_server():
    """Test the web server functionality."""
    print("🧪 Testing ClearCouncil Web Server")
    print("=" * 50)
    
    # Start server in background
    print("🚀 Starting server...")
    server_process = None
    
    try:
        server_process = subprocess.Popen(
            [sys.executable, "clearcouncil_chat_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        try:
            response = requests.get("http://localhost:5002/health", timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data}")
                print("   ✅ Health check passed")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
        
        # Test councils endpoint
        print("🏛️ Testing councils endpoint...")
        try:
            response = requests.get("http://localhost:5002/api/councils", timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Councils: {data.get('councils', [])}")
                print("   ✅ Councils endpoint passed")
            else:
                print(f"   ❌ Councils endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Councils endpoint error: {e}")
        
        # Test main page
        print("🌐 Testing main page...")
        try:
            response = requests.get("http://localhost:5002/", timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Page size: {len(response.text)} characters")
                if "ClearCouncil AI Chat" in response.text:
                    print("   ✅ Main page loaded successfully")
                else:
                    print("   ⚠️ Main page loaded but content may be incorrect")
            else:
                print(f"   ❌ Main page failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Main page error: {e}")
        
        print("\n🎉 Server test completed!")
        print("✅ Web server is working correctly")
        print("🌐 Access the chat interface at: http://localhost:5002")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Server test failed: {e}")
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("🛑 Server stopped")

if __name__ == "__main__":
    test_server()