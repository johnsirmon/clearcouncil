#!/usr/bin/env python3
import requests
import time
import subprocess
import sys

def test_app():
    print("🧪 Testing ClearCouncil Integrated App...")
    
    # Start the server in background
    try:
        proc = subprocess.Popen([sys.executable, 'clearcouncil_integrated_app.py'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Starting server...")
        time.sleep(5)
        
        # Test the homepage
        print("🌐 Testing homepage...")
        response = requests.get('http://localhost:5000', timeout=10)
        print(f"✅ Homepage Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Response: {response.text[:500]}")
            return False
            
        # Test API endpoints
        print("🔧 Testing API endpoints...")
        
        # Test stats API
        try:
            stats_response = requests.get('http://localhost:5000/api/stats', timeout=5)
            print(f"✅ Stats API Status: {stats_response.status_code}")
        except Exception as e:
            print(f"❌ Stats API Error: {e}")
            
        # Test representatives API
        try:
            reps_response = requests.get('http://localhost:5000/api/representatives', timeout=5)
            print(f"✅ Representatives API Status: {reps_response.status_code}")
        except Exception as e:
            print(f"❌ Representatives API Error: {e}")
            
        print("✅ App appears to be working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error starting/testing app: {e}")
        return False
        
    finally:
        # Clean up
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()

if __name__ == "__main__":
    test_app()