#!/usr/bin/env python3
"""
Basic test script for ClearCouncil Chat functionality
Tests core components without requiring additional package installation
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test if we can import required modules."""
    print("🧪 Testing imports...")
    
    try:
        import requests
        print("✅ requests module available")
    except ImportError as e:
        print(f"❌ requests module not available: {e}")
        return False
    
    try:
        from clearcouncil.config.settings import list_available_councils
        print("✅ ClearCouncil config module available")
    except ImportError as e:
        print(f"❌ ClearCouncil config module not available: {e}")
        return False
    
    try:
        from clearcouncil.core.database import VectorDatabase
        print("✅ ClearCouncil database module available")
    except ImportError as e:
        print(f"❌ ClearCouncil database module not available: {e}")
        return False
    
    return True

def test_councils():
    """Test if we can list available councils."""
    print("\n🏛️ Testing council configuration...")
    
    try:
        from clearcouncil.config.settings import list_available_councils
        councils = list_available_councils()
        print(f"✅ Found {len(councils)} councils: {councils}")
        return len(councils) > 0
    except Exception as e:
        print(f"❌ Error listing councils: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("\n🔧 Testing environment configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
                
            if 'GITHUB_TOKEN' in env_content:
                print("✅ GITHUB_TOKEN found in .env")
                # Check if it's not the placeholder
                if 'your_github_token_here' not in env_content:
                    print("✅ GITHUB_TOKEN appears to be configured")
                    return True
                else:
                    print("⚠️  GITHUB_TOKEN is placeholder value")
                    return False
            else:
                print("⚠️  GITHUB_TOKEN not found in .env")
                return False
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
            return False
    else:
        print("⚠️  .env file not found")
        return False

def test_github_api():
    """Test GitHub API connection (if token is available)."""
    print("\n📡 Testing GitHub API connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        github_token = os.getenv('GITHUB_TOKEN')
        
        if not github_token or github_token == 'your_github_token_here':
            print("⚠️  No valid GitHub token found")
            return False
        
        import requests
        
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
            print(f"✅ Connected to GitHub Models! Found {len(models)} models")
            return True
        else:
            print(f"❌ GitHub Models API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ GitHub API test failed: {e}")
        return False

def test_flask_basics():
    """Test basic Flask functionality."""
    print("\n🌐 Testing Flask availability...")
    
    try:
        import flask
        print("✅ Flask module available")
        
        # Test basic Flask app creation
        app = flask.Flask(__name__)
        print("✅ Flask app can be created")
        
        @app.route('/test')
        def test_route():
            return "OK"
        
        print("✅ Flask routes can be defined")
        return True
        
    except ImportError as e:
        print(f"❌ Flask not available: {e}")
        print("💡 Try installing Flask: pip install flask")
        return False
    except Exception as e:
        print(f"❌ Flask test failed: {e}")
        return False

def test_data_access():
    """Test access to existing ClearCouncil data."""
    print("\n📊 Testing data access...")
    
    try:
        from clearcouncil.config.settings import list_available_councils
        councils = list_available_councils()
        
        if not councils:
            print("⚠️  No councils configured")
            return False
        
        # Test loading a council config
        test_council = councils[0]
        print(f"Testing with council: {test_council}")
        
        from clearcouncil.config.settings import load_council_config
        config = load_council_config(test_council)
        print(f"✅ Successfully loaded config for {test_council}")
        
        # Test database access
        from clearcouncil.core.database import VectorDatabase
        db = VectorDatabase(test_council)
        print("✅ Vector database can be initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Data access test failed: {e}")
        return False

def print_summary(results):
    """Print test summary."""
    print("\n📋 Test Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print("=" * 50)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Chat application should work.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        
        # Provide guidance based on failures
        if not results.get('Environment', True):
            print("\n💡 Next steps:")
            print("1. Copy .env.example to .env")
            print("2. Get GitHub token from: https://github.com/settings/tokens")
            print("3. Add token to .env file")
        
        if not results.get('Flask', True):
            print("\n💡 Install Flask:")
            print("pip install flask flask-cors")

def main():
    """Run all tests."""
    print("🏛️ ClearCouncil Chat Basic Test Suite")
    print("====================================")
    
    # Run tests
    results = {
        'Imports': test_imports(),
        'Councils': test_councils(),
        'Environment': test_environment(),
        'GitHub API': test_github_api(),
        'Flask': test_flask_basics(),
        'Data Access': test_data_access()
    }
    
    print_summary(results)
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)