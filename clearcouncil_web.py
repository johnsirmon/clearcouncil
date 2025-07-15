#!/usr/bin/env python3
"""
ClearCouncil Web Interface Launcher

This script provides a simple way to launch the ClearCouncil web interface.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point for web interface."""
    import logging
    from clearcouncil.web.cli_integration import web
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run web CLI
    web()

if __name__ == "__main__":
    main()