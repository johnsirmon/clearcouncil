#!/usr/bin/env python3
"""
ClearCouncil - Simple Starter Script

This script provides basic functionality with graceful handling of missing dependencies.
For full functionality, run the setup script first.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def check_basic_dependencies():
    """Check if basic dependencies are available."""
    missing = []
    
    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    try:
        import pandas
    except ImportError:
        missing.append("pandas")
    
    return missing

def show_help():
    """Show basic help information."""
    print("🏛️  ClearCouncil - Local Government Transparency Tool")
    print("=" * 55)
    print()
    print("SETUP REQUIRED:")
    print("Before using ClearCouncil, please run the setup script:")
    print()
    print("  On Windows:    setup.bat")
    print("  On Mac/Linux:  ./setup.sh")
    print()
    print("BASIC COMMANDS:")
    print("  list-councils              List available councils")
    print("  download-pdfs              Download council documents")
    print("  analyze-voting             Analyze representative voting")
    print("  explain-terms              Explain municipal terms")
    print()
    print("EXAMPLES:")
    print('  python clearcouncil.py list-councils')
    print('  python clearcouncil.py explain-terms "movant" "second"')
    print('  python clearcouncil.py analyze-voting york_county_sc "District 2" "last year"')
    print()
    print("For detailed help: python clearcouncil.py <command> --help")
    print()

def show_dependency_error(missing_deps):
    """Show dependency error with helpful instructions."""
    print("❌ Missing Required Dependencies")
    print("=" * 35)
    print()
    print("The following packages are required but not installed:")
    for dep in missing_deps:
        print(f"  • {dep}")
    print()
    print("SOLUTION:")
    print("Run the setup script to automatically install dependencies:")
    print()
    print("  On Windows:    setup.bat")
    print("  On Mac/Linux:  ./setup.sh")
    print()
    print("Or install manually:")
    print("  pip install python-dotenv PyYAML requests pandas PyPDF2")
    print()

def list_councils_simple():
    """Simple council listing without full dependency chain."""
    config_dir = Path(__file__).parent / "config" / "councils"
    
    if not config_dir.exists():
        print("❌ Council configuration directory not found")
        print("   Make sure you're in the correct directory")
        return
    
    council_files = list(config_dir.glob("*.yaml"))
    
    if not council_files:
        print("❌ No council configurations found")
        return
    
    print("📋 Available Councils:")
    print("=" * 25)
    
    for file_path in council_files:
        if file_path.name != "template.yaml":
            council_id = file_path.stem
            print(f"  • {council_id}")
    
    print()
    print("To analyze a council, use:")
    print(f"  python clearcouncil.py analyze-voting <council_id> <representative> <time_range>")
    print()

def explain_basic_terms():
    """Explain basic municipal terms without full glossary system."""
    terms = {
        "movant": "The person who makes a motion (proposes an action) in a council meeting",
        "second": "A council member who supports a motion so it can be discussed and voted on",
        "rezoning": "Changing the designated use of a piece of land (residential, commercial, etc.)",
        "ordinance": "A local law passed by the city or county government",
        "motion": "A formal proposal for action made during a council meeting",
        "abstain": "To choose not to vote for or against a motion",
        "variance": "Permission to deviate from normal zoning requirements",
        "public hearing": "A meeting where citizens can speak about an issue before the council votes"
    }
    
    print("📚 Common Municipal Government Terms")
    print("=" * 40)
    print()
    
    for term, definition in terms.items():
        print(f"🏛️  {term.upper()}")
        print(f"   {definition}")
        print()
    
    print("For more detailed explanations and examples:")
    print("  python clearcouncil.py explain-terms <term1> <term2> ...")
    print()

def main():
    """Main entry point for simple script."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args or args[0] in ["-h", "--help", "help"]:
        show_help()
        return
    
    command = args[0].lower()
    
    # Handle commands that don't require full dependencies
    if command == "list-councils":
        list_councils_simple()
        return
    
    if command == "explain-basic" or (command == "explain-terms" and len(args) == 1):
        explain_basic_terms()
        return
    
    # For other commands, check dependencies
    missing_deps = check_basic_dependencies()
    if missing_deps:
        show_dependency_error(missing_deps)
        return
    
    # If dependencies are available, try to use the full CLI
    try:
        from clearcouncil.cli.main import main as full_main
        
        # Restore original sys.argv for the full CLI
        sys.argv = [sys.argv[0]] + args
        full_main()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print()
        print("SOLUTION:")
        print("Run the setup script to install all dependencies:")
        print("  On Windows:    setup.bat")
        print("  On Mac/Linux:  ./setup.sh")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("If the problem persists, please check:")
        print("1. All dependencies are installed")
        print("2. You have a valid .env file with API keys (if needed)")
        print("3. You're in the correct directory")
        print()

if __name__ == "__main__":
    main()