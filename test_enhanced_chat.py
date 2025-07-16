#!/usr/bin/env python3
"""Test the enhanced chat server with real voting data."""

import subprocess
import time
import requests
import json
import sys
import os

def test_enhanced_chat():
    """Test the enhanced chat functionality."""
    print("🧪 Testing Enhanced ClearCouncil Chat")
    print("=" * 50)
    
    # Start server in background
    print("🚀 Starting enhanced server...")
    server_process = None
    
    try:
        server_process = subprocess.Popen(
            [sys.executable, "clearcouncil_chat_enhanced.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        try:
            response = requests.get("http://localhost:5003/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed")
                print(f"   Data loaded: {data.get('data_loaded', False)}")
                print(f"   AI working: {data.get('ai_working', False)}")
                print(f"   Components: {data.get('components', {})}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
        
        # Test representatives endpoint
        print("🏛️ Testing representatives endpoint...")
        try:
            response = requests.get("http://localhost:5003/api/representatives", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Representatives loaded: {data.get('count', 0)}")
                if data.get('representatives'):
                    print(f"   Sample: {data['representatives'][0]['name']}")
            else:
                print(f"   ❌ Representatives endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Representatives endpoint error: {e}")
        
        # Test setting council
        print("🏛️ Testing council selection...")
        try:
            response = requests.post("http://localhost:5003/api/set-council", 
                                   json={"council_id": "york_county_sc"}, 
                                   timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Council set successfully")
                print(f"   Data loaded: {data.get('data_loaded', False)}")
            else:
                print(f"   ❌ Council setting failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Council setting error: {e}")
        
        # Test chat with real data queries
        print("💬 Testing chat with real data...")
        
        test_messages = [
            "Who are the most active representatives?",
            "Tell me about Robert Winkler",
            "Show me voting statistics",
            "What representatives are available?",
            "Tell me about Allison Love's voting record"
        ]
        
        for msg in test_messages:
            print(f"\n👤 Testing: {msg}")
            try:
                response = requests.post("http://localhost:5003/api/chat", 
                                       json={"message": msg}, 
                                       timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '').replace('\\n', '\n')
                    print(f"🤖 Response: {response_text[:200]}...")
                    print(f"   Data loaded: {data.get('data_loaded', False)}")
                else:
                    print(f"   ❌ Chat failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Chat error: {e}")
        
        print("\n🎉 Enhanced chat test completed!")
        print("🌐 Access the enhanced chat at: http://localhost:5003")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("🛑 Server stopped")

if __name__ == "__main__":
    test_enhanced_chat()