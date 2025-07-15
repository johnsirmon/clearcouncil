#!/usr/bin/env python3
"""
ClearCouncil Web Interface Setup Script

This script sets up the ClearCouncil web interface with all dependencies.
"""

import subprocess
import sys
import os
import logging
from pathlib import Path


def setup_logging():
    """Setup logging for the setup process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def run_command(command, description):
    """Run a command with error handling."""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        return False


def check_python_version():
    """Check Python version compatibility."""
    logger = logging.getLogger(__name__)
    
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True


def install_dependencies():
    """Install Python dependencies."""
    logger = logging.getLogger(__name__)
    
    # Install basic dependencies
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing dependencies"),
        ("pip install -e .", "Installing ClearCouncil in development mode")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def setup_directories():
    """Create necessary directories."""
    logger = logging.getLogger(__name__)
    
    directories = [
        "data",
        "data/PDFs",
        "data/transcripts",
        "data/faiss_indexes",
        "data/results",
        "data/results/charts",
        "data/backups",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return True


def create_env_file():
    """Create .env file if it doesn't exist."""
    logger = logging.getLogger(__name__)
    
    env_file = Path(".env")
    if env_file.exists():
        logger.info(".env file already exists")
        return True
    
    env_content = """# ClearCouncil Configuration
# OpenAI API Key (required for embeddings and search)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/clearcouncil.db

# Web Interface Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your_secret_key_here

# Logging Configuration
LOG_LEVEL=INFO
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    logger.info("Created .env file")
    logger.info("Please update .env with your OpenAI API key and other settings")
    return True


def initialize_database():
    """Initialize the database."""
    logger = logging.getLogger(__name__)
    
    try:
        # Add src to path for imports
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from clearcouncil.web.database import DatabaseManager
        
        logger.info("Initializing database...")
        db = DatabaseManager()
        logger.info("Database initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False


def test_installation():
    """Test the installation."""
    logger = logging.getLogger(__name__)
    
    tests = [
        ("python clearcouncil.py --help", "Testing CLI"),
        ("python clearcouncil_web.py --help", "Testing web CLI"),
        ("python clearcouncil_simple.py --help", "Testing simple CLI")
    ]
    
    all_passed = True
    
    for command, description in tests:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed


def main():
    """Main setup function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🏛️  ClearCouncil Web Interface Setup")
    logger.info("=" * 50)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Setting up directories", setup_directories),
        ("Creating .env file", create_env_file),
        ("Installing dependencies", install_dependencies),
        ("Initializing database", initialize_database),
        ("Testing installation", test_installation)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        logger.info(f"\n📋 {step_name}...")
        
        if step_function():
            logger.info(f"✅ {step_name} completed successfully")
        else:
            logger.error(f"❌ {step_name} failed")
            failed_steps.append(step_name)
    
    logger.info("\n" + "=" * 50)
    
    if not failed_steps:
        logger.info("🎉 Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Update .env with your OpenAI API key")
        logger.info("2. Process your council data:")
        logger.info("   python clearcouncil_web.py process-data york_county_sc")
        logger.info("3. Start the web server:")
        logger.info("   python clearcouncil_web.py serve")
        logger.info("4. Open http://localhost:5000 in your browser")
        
    else:
        logger.error("❌ Setup failed!")
        logger.error("Failed steps:")
        for step in failed_steps:
            logger.error(f"  - {step}")
        
        logger.error("\nPlease fix the errors above and run setup again.")
        sys.exit(1)


if __name__ == "__main__":
    main()