#!/usr/bin/env python3
"""Test GitHub Models API connection with the provided token."""

import requests
import json
import os

def test_github_api():
    """Test GitHub Models API connection."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set it with: export GITHUB_TOKEN=your_token_here")
        return
    
    print("🔍 Testing GitHub Models API Connection")
    print("=" * 50)
    
    # Test 1: Try a simple chat completion with the new API
    print("\n1️⃣ Testing GitHub Models chat completion...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, can you help me test this API?"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        # Try the new GitHub Models API endpoint
        response = requests.post(
            "https://models.github.ai/inference/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("choices", [{}])[0].get("message", {}).get("content", "No content")
            print(f"✅ Success! AI Response: {message}")
            success = True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            success = False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        success = False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        success = False
    
    # Test 2: Try alternative endpoint if first fails
    if not success:
        print("\n2️⃣ Testing alternative endpoint...")
        try:
            # Try without organization in path
            response = requests.post(
                "https://models.github.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                message = result.get("choices", [{}])[0].get("message", {}).get("content", "No content")
                print(f"✅ Success! AI Response: {message}")
                success = True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    # Test 3: Test token validity with GitHub API
    print("\n3️⃣ Testing token validity...")
    try:
        response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Token valid! User: {user_data.get('login', 'Unknown')}")
        else:
            print(f"❌ Token invalid: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Token test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏛️ ClearCouncil Chat Ready Status:")
    
    # Overall status
    if success:
        print("✅ GitHub Models API: WORKING")
        print("✅ Token: VALID")
        print("✅ Chat Application: READY")
        print("\n🚀 You can now use the full chat application!")
        print("Run: python clearcouncil_chat.py (once Flask is installed)")
    else:
        print("❌ GitHub Models API: NOT WORKING")
        print("⚠️  Token: May need additional permissions")
        print("⚠️  Chat Application: LIMITED TO MOCK RESPONSES")
        print("\n💡 GitHub Models may still be in beta/limited access")
        print("💡 Your chat app will work with mock responses for now")

if __name__ == "__main__":
    test_github_api()