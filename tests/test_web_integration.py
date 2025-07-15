#!/usr/bin/env python3
"""
Test script to verify web interface integration with existing CLI.
"""

import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def run_command(command, description, capture_output=True):
    """Run a command and return success status."""
    print(f"🧪 Testing: {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"   ✅ SUCCESS")
            return True, result.stdout if capture_output else ""
        else:
            print(f"   ❌ FAILED (exit code: {result.returncode})")
            if capture_output and result.stderr:
                print(f"   Error: {result.stderr}")
            return False, result.stderr if capture_output else ""
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT")
        return False, "Command timeout"
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False, str(e)


def test_basic_imports():
    """Test basic import functionality."""
    print("\n📦 Testing Basic Imports")
    print("=" * 40)
    
    imports_to_test = [
        "from clearcouncil.web.app import create_app",
        "from clearcouncil.web.database import DatabaseManager",
        "from clearcouncil.web.charts import InteractiveChartGenerator",
        "from clearcouncil.web.data_processor import DataProcessingManager",
        "from clearcouncil.web.cli_integration import web"
    ]
    
    all_passed = True
    
    for import_statement in imports_to_test:
        try:
            exec(import_statement)
            print(f"✅ {import_statement}")
        except Exception as e:
            print(f"❌ {import_statement}")
            print(f"   Error: {e}")
            all_passed = False
    
    return all_passed


def test_cli_integration():
    """Test CLI integration."""
    print("\n🖥️  Testing CLI Integration")
    print("=" * 40)
    
    tests = [
        ("python clearcouncil.py --help", "Main CLI help"),
        ("python clearcouncil_web.py --help", "Web CLI help"),
        ("python clearcouncil_simple.py --help", "Simple CLI help"),
        ("python clearcouncil.py list-councils", "List councils"),
        ("python clearcouncil_web.py list-councils", "Web list councils"),
    ]
    
    all_passed = True
    
    for command, description in tests:
        success, output = run_command(command, description)
        if not success:
            all_passed = False
    
    return all_passed


def test_database_initialization():
    """Test database initialization."""
    print("\n🗄️  Testing Database Initialization")
    print("=" * 40)
    
    try:
        from clearcouncil.web.database import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        print(f"Creating test database at: {db_path}")
        
        # Initialize database
        db = DatabaseManager(db_path)
        print("✅ Database initialized successfully")
        
        # Test database operations
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            expected_tables = {'representatives', 'voting_records', 'documents', 'meetings', 'search_cache'}
            actual_tables = {table[0] for table in tables}
            
            if expected_tables.issubset(actual_tables):
                print(f"✅ All expected tables created: {', '.join(expected_tables)}")
            else:
                missing = expected_tables - actual_tables
                print(f"❌ Missing tables: {', '.join(missing)}")
                return False
        
        # Clean up
        os.unlink(db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def test_web_app_creation():
    """Test web application creation."""
    print("\n🌐 Testing Web Application Creation")
    print("=" * 40)
    
    try:
        from clearcouncil.web.app import create_app
        
        # Create test app
        app = create_app('testing')
        print("✅ Flask app created successfully")
        
        # Test app configuration
        if app.config['SECRET_KEY']:
            print("✅ App configured with secret key")
        else:
            print("❌ App missing secret key")
            return False
        
        # Test routes registration
        with app.test_client() as client:
            # Test main route
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Main route accessible")
            else:
                print(f"❌ Main route failed: {response.status_code}")
                return False
            
            # Test API route
            response = client.get('/api/councils')
            if response.status_code == 200:
                print("✅ API route accessible")
            else:
                print(f"❌ API route failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web app creation failed: {e}")
        return False


def test_chart_generation():
    """Test chart generation."""
    print("\n📊 Testing Chart Generation")
    print("=" * 40)
    
    try:
        from clearcouncil.web.charts import InteractiveChartGenerator
        from clearcouncil.web.database import DatabaseManager
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        db = DatabaseManager(db_path)
        chart_gen = InteractiveChartGenerator(db)
        
        # Test empty chart creation
        empty_chart = chart_gen._create_empty_chart("Test message")
        if empty_chart:
            print("✅ Empty chart creation works")
        else:
            print("❌ Empty chart creation failed")
            return False
        
        # Clean up
        os.unlink(db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        return False


def test_data_processing():
    """Test data processing pipeline."""
    print("\n⚙️  Testing Data Processing Pipeline")
    print("=" * 40)
    
    try:
        from clearcouncil.web.data_processor import DataProcessingManager
        from clearcouncil.config.settings import list_available_councils
        
        # Get available councils
        councils = list_available_councils()
        if not councils:
            print("❌ No councils available for testing")
            return False
        
        # Test with first available council
        council_id = councils[0]
        print(f"Testing with council: {council_id}")
        
        # Create processing manager
        manager = DataProcessingManager(council_id)
        print("✅ Data processing manager created")
        
        # Test status retrieval
        status = manager.get_status()
        if isinstance(status, dict):
            print("✅ Status retrieval works")
            print(f"   Status keys: {list(status.keys())}")
        else:
            print("❌ Status retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🏛️  ClearCouncil Web Interface Integration Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("CLI Integration", test_cli_integration),
        ("Database Initialization", test_database_initialization),
        ("Web App Creation", test_web_app_creation),
        ("Chart Generation", test_chart_generation),
        ("Data Processing", test_data_processing)
    ]
    
    results = {}
    passed_tests = 0
    
    for test_name, test_function in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            success = test_function()
            results[test_name] = success
            if success:
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Results: {passed_tests}/{len(tests)} tests passed")
    
    if passed_tests == len(tests):
        print("🎉 ALL TESTS PASSED!")
        print("\nYour ClearCouncil web interface is ready!")
        print("\nNext steps:")
        print("1. Run: python setup_web.py")
        print("2. Update .env with your OpenAI API key")
        print("3. Run: python clearcouncil_web.py process-data york_county_sc")
        print("4. Run: python clearcouncil_web.py serve")
        print("5. Open: http://localhost:5000")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)