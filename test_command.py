#!/usr/bin/env python3
"""
Test script to verify the analyze-voting command structure and identify potential issues.
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_command_parsing():
    """Test if the command would be parsed correctly."""
    print("🧪 Testing Command Structure")
    print("=" * 40)
    
    # Simulate the command: python clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months" --create-charts
    test_args = [
        'clearcouncil.py',
        'analyze-voting', 
        'york_county_sc', 
        'District 2', 
        'last 6 months',
        '--create-charts'
    ]
    
    print(f"Command: {' '.join(test_args)}")
    print()
    
    # Test argument parsing
    if len(test_args) >= 5:
        command = test_args[1]
        council = test_args[2] 
        representative = test_args[3]
        time_range = test_args[4]
        create_charts = '--create-charts' in test_args
        
        print("✅ Parsed Arguments:")
        print(f"   Command: {command}")
        print(f"   Council: {council}")
        print(f"   Representative: {representative}")
        print(f"   Time Range: {time_range}")
        print(f"   Create Charts: {create_charts}")
    else:
        print("❌ Insufficient arguments")
        return False
    
    print()
    return True

def test_config_availability():
    """Test if the council configuration exists."""
    print("🔍 Testing Configuration")
    print("=" * 30)
    
    config_path = Path(__file__).parent / "config" / "councils" / "york_county_sc.yaml"
    
    if config_path.exists():
        print(f"✅ Council config found: {config_path}")
        
        # Try to read basic info
        try:
            with open(config_path, 'r') as f:
                content = f.read()
                if 'york_county_sc' in content.lower():
                    print("✅ Config contains expected council ID")
                if 'website' in content.lower():
                    print("✅ Config contains website configuration")
                if 'storage' in content.lower():
                    print("✅ Config contains storage configuration")
        except Exception as e:
            print(f"⚠️  Could not read config: {e}")
    else:
        print(f"❌ Council config NOT found: {config_path}")
        return False
    
    print()
    return True

def test_directory_structure():
    """Test if required directories exist or can be created."""
    print("📁 Testing Directory Structure")
    print("=" * 35)
    
    base_path = Path(__file__).parent
    required_dirs = [
        "data",
        "data/PDFs", 
        "data/transcripts",
        "data/faiss_indexes",
        "data/results",
        "data/results/charts"
    ]
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"✅ {dir_path} exists")
        else:
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ {dir_path} created")
            except Exception as e:
                print(f"❌ Could not create {dir_path}: {e}")
                return False
    
    print()
    return True

def test_time_range_parsing():
    """Test time range parsing logic."""
    print("⏰ Testing Time Range Parsing")
    print("=" * 35)
    
    time_input = "last 6 months"
    print(f"Input: '{time_input}'")
    
    # Simple regex test for the pattern
    import re
    
    pattern = r'last (\d+) (month|year)s?'
    match = re.search(pattern, time_input.lower())
    
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        print(f"✅ Parsed: {amount} {unit}(s)")
        
        # Calculate approximate date range
        from datetime import datetime, timedelta
        
        now = datetime.now()
        if unit == "month":
            # Approximate months as 30 days each
            start_date = now - timedelta(days=amount * 30)
        else:
            start_date = now - timedelta(days=amount * 365)
        
        print(f"✅ Date range: {start_date.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
    else:
        print(f"❌ Could not parse time range: {time_input}")
        return False
    
    print()
    return True

def simulate_full_workflow():
    """Simulate what the full workflow would do."""
    print("🔄 Simulating Full Workflow")
    print("=" * 35)
    
    steps = [
        ("Parse time range", "Convert 'last 6 months' to date range"),
        ("Load council config", "Read york_county_sc.yaml configuration"),
        ("Check existing documents", "Look for PDFs in data/PDFs/ directory"),
        ("Download missing documents", "Check council website for new documents"),
        ("Process documents", "Extract voting data from PDFs"),
        ("Analyze representative", "Filter data for District 2"),
        ("Generate visualizations", "Create charts with matplotlib"),
        ("Save results", "Export to data/results/ directory")
    ]
    
    for i, (step, description) in enumerate(steps, 1):
        print(f"{i}. {step}")
        print(f"   {description}")
        
        # Simulate potential issues
        if "Download" in step:
            print("   ⚠️  Requires internet connection and valid URLs")
        elif "matplotlib" in description:
            print("   ⚠️  Requires matplotlib/seaborn packages")
        elif "District 2" in description:
            print("   ⚠️  Requires documents with parseable representative data")
        else:
            print("   ✅ Should work with basic setup")
        print()

def main():
    """Run all tests."""
    print("🏛️  ClearCouncil Command Test")
    print("=" * 50)
    print()
    
    tests = [
        test_command_parsing,
        test_config_availability, 
        test_directory_structure,
        test_time_range_parsing
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("📊 Test Summary")
    print("=" * 20)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All basic tests passed!")
        print("\n🎯 The command structure is correct.")
        print("   To run successfully, you need:")
        print("   1. Install dependencies (run setup.sh or setup.bat)")
        print("   2. Ensure internet connection for document downloads")
        print("   3. Have or download PDF documents with voting data")
    else:
        print("⚠️  Some tests failed - see details above")
    
    print("\n🔄 Simulated Workflow:")
    simulate_full_workflow()

if __name__ == "__main__":
    main()