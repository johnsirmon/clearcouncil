#!/usr/bin/env python3
"""
ClearCouncil - Quick start script

This script provides a simple way to run ClearCouncil commands without installation.
For full functionality, install the package using: pip install -e .
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from clearcouncil.cli.main import main

if __name__ == "__main__":
    main()