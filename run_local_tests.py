#!/usr/bin/env python3
"""
Local Test Runner for ClearCouncil
This script tests ClearCouncil functionality in your local environment.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_command(command, description, expect_success=True):
    """Run a command and report results."""
    print(f"\n🧪 Testing: {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        # Split command properly for subprocess
        if isinstance(command, str):
            cmd_parts = command.split()
        else:
            cmd_parts = command
        
        result = subprocess.run(
            cmd_parts, 
            capture_output=True, 
            text=True, 
            timeout=30,
            cwd=Path(__file__).parent
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            return True
        else:
            if expect_success:
                print(f"❌ FAILED (exit code: {result.returncode})")
            else:
                print(f"⚠️  EXPECTED FAILURE (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT (command took too long)")
        return False
    except FileNotFoundError:
        print("❌ COMMAND NOT FOUND")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are available."""
    print("\n🔍 Checking Dependencies")
    print("=" * 30)
    
    required_modules = [
        'yaml', 'requests', 'pandas', 'PyPDF2', 
        'dateutil', 'tqdm'
    ]
    
    optional_modules = [
        'matplotlib', 'seaborn', 'dotenv', 'langchain', 'openai'
    ]
    
    available = []
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            available.append(module)
            print(f"✅ {module}")
        except ImportError:
            missing.append(module)
            print(f"❌ {module}")
    
    print(f"\n📊 Optional modules:")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"⚠️  {module} (optional)")
    
    return len(missing) == 0, missing

def test_basic_functionality():
    """Test basic ClearCouncil functionality."""
    print("\n🚀 Testing Basic Functionality")
    print("=" * 40)
    
    tests = [
        # Test simple script (should always work)
        ("python3 clearcouncil_simple.py --help", "Simple script help", True),
        ("python3 clearcouncil_simple.py list-councils", "List councils (simple)", True),
        ("python3 clearcouncil_simple.py explain-basic", "Explain basic terms", True),
    ]
    
    results = []
    for command, description, expect_success in tests:
        success = run_command(command, description, expect_success)
        results.append((description, success))
    
    return results

def test_full_functionality():
    """Test full ClearCouncil functionality."""
    print("\n🎯 Testing Full Functionality")
    print("=" * 35)
    
    tests = [
        # Test full CLI (requires dependencies)
        ("python3 clearcouncil.py --help", "Full CLI help", True),
        ("python3 clearcouncil.py list-councils", "List councils (full)", True),
        ("python3 clearcouncil.py explain-terms movant second", "Explain specific terms", True),
        ("python3 clearcouncil.py explain-terms --category voting", "Explain voting terms", True),
    ]
    
    results = []
    for command, description, expect_success in tests:
        success = run_command(command, description, expect_success)
        results.append((description, success))
    
    return results

def test_real_world_examples():
    """Test the real-world examples from README."""
    print("\n🌍 Testing Real-World Examples")
    print("=" * 40)
    
    tests = [
        # These might fail due to no documents, but should run without errors
        ('python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months"', 
         "Basic representative analysis", False),  # Expect failure due to no docs
        
        ('python3 clearcouncil.py update-documents york_county_sc "last 3 months"', 
         "Update documents", False),  # Might fail due to network/website
        
        ('python3 clearcouncil.py analyze-district york_county_sc "District 2" "last year"',
         "District analysis", False),  # Expect failure due to no docs
    ]
    
    results = []
    for command, description, expect_success in tests:
        success = run_command(command, description, expect_success)
        results.append((description, success))
    
    return results

def test_chart_generation():
    """Test chart generation capabilities."""
    print("\n📊 Testing Chart Generation")
    print("=" * 35)
    
    # First check if matplotlib is available
    try:
        import matplotlib
        print("✅ matplotlib is available")
        
        tests = [
            ('python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --create-charts',
             "Analysis with charts", False),  # Expect failure due to no docs
        ]
        
        results = []
        for command, description, expect_success in tests:
            success = run_command(command, description, expect_success)
            results.append((description, success))
        
        return results
        
    except ImportError:
        print("⚠️  matplotlib not available - skipping chart tests")
        return [("Chart generation", False)]

def create_test_environment():
    """Create necessary directories and files for testing."""
    print("\n📁 Setting Up Test Environment")
    print("=" * 40)
    
    # Create data directories
    directories = [
        "data",
        "data/PDFs",
        "data/transcripts", 
        "data/faiss_indexes",
        "data/results",
        "data/results/charts"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_path}")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write("# OpenAI API Key (optional for basic features)\n")
            f.write("# OPENAI_API_KEY=your_key_here\n")
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def generate_report(all_results):
    """Generate a summary report of all tests."""
    print("\n📋 TEST SUMMARY REPORT")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        print(f"\n{category}:")
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {test_name}")
            total_tests += 1
            if success:
                passed_tests += 1
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! ClearCouncil is ready to use.")
    elif passed_tests >= total_tests * 0.5:
        print("\n✅ BASIC FUNCTIONALITY WORKING! Some advanced features may need setup.")
    else:
        print("\n⚠️  SETUP REQUIRED. Please install dependencies and try again.")
    
    print(f"\n💡 Next Steps:")
    if passed_tests < total_tests:
        print("   1. Install missing dependencies:")
        print("      pip install --user python-dotenv PyYAML requests pandas PyPDF2 python-dateutil tqdm")
        print("   2. For charts: pip install --user matplotlib seaborn")
        print("   3. Run this test again")
    else:
        print("   1. Try downloading real documents:")
        print("      python clearcouncil.py update-documents york_county_sc \"last year\"")
        print("   2. Run analysis with real data:")
        print("      python clearcouncil.py analyze-voting york_county_sc \"District 2\" \"last year\" --create-charts")

def main():
    """Main test runner."""
    print("🏛️  ClearCouncil Local Environment Test")
    print("=" * 50)
    print("This script will test ClearCouncil functionality in your local environment.")
    print("Some tests may fail if dependencies aren't installed - this is expected.")
    
    # Setup test environment
    create_test_environment()
    
    # Check dependencies
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Some tests will fail. Install dependencies to get full functionality.")
    
    # Run all tests
    all_results = {}
    
    all_results["Basic Functionality"] = test_basic_functionality()
    
    if deps_ok:
        all_results["Full Functionality"] = test_full_functionality()
        all_results["Real-World Examples"] = test_real_world_examples()
        all_results["Chart Generation"] = test_chart_generation()
    else:
        print("\n⚠️  Skipping advanced tests due to missing dependencies")
        print("Install dependencies and run again for full testing")
    
    # Generate report
    generate_report(all_results)

if __name__ == "__main__":
    main()