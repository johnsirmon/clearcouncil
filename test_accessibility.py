#!/usr/bin/env python3
"""
Accessibility testing script for ClearCouncil application.

This script tests the accessibility of all major routes in the ClearCouncil
web application and generates comprehensive reports.
"""

import sys
import os
from pathlib import Path
import logging
import time
import subprocess
import signal
from contextlib import contextmanager

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from clearcouncil.testing.accessibility import AccessibilityTester, get_clearcouncil_routes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@contextmanager
def web_server():
    """Context manager to start and stop the web server for testing."""
    logger.info("Starting ClearCouncil web server...")
    
    # Start the web server
    server_process = subprocess.Popen([
        "python", "clearcouncil_web.py", "serve", 
        "--host", "127.0.0.1", "--port", "5000"
    ])
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        yield
    finally:
        logger.info("Stopping web server...")
        server_process.terminate()
        server_process.wait(timeout=10)


def check_dependencies():
    """Check if required accessibility testing dependencies are installed."""
    missing_deps = []
    
    try:
        import axe_core_python
    except ImportError:
        missing_deps.append("axe-core-python")
    
    try:
        import playwright
    except ImportError:
        missing_deps.append("playwright")
    
    try:
        import bs4
    except ImportError:
        missing_deps.append("beautifulsoup4")
    
    if missing_deps:
        logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
        logger.error("Install with: pip install " + " ".join(missing_deps))
        return False
    
    return True


def install_playwright():
    """Install Playwright browsers."""
    try:
        logger.info("Installing Playwright browsers...")
        result = subprocess.run([
            "python", "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Playwright browsers installed successfully")
            return True
        else:
            logger.error(f"Failed to install Playwright browsers: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error installing Playwright browsers: {e}")
        return False


def run_accessibility_tests():
    """Run comprehensive accessibility tests."""
    logger.info("Starting accessibility tests for ClearCouncil...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Cannot proceed without required dependencies")
        return False
    
    # Install Playwright browsers if needed
    if not install_playwright():
        logger.warning("Playwright browser installation failed, but continuing...")
    
    # Initialize accessibility tester
    tester = AccessibilityTester(base_url="http://127.0.0.1:5000")
    
    # Get routes to test
    routes = get_clearcouncil_routes()
    logger.info(f"Testing {len(routes)} routes: {routes}")
    
    try:
        # Check if server is already running
        import requests
        try:
            response = requests.get("http://127.0.0.1:5000", timeout=5)
            server_running = True
            logger.info("Web server is already running")
        except:
            server_running = False
            logger.info("Web server is not running, will start it")
        
        if server_running:
            # Server is already running, just run tests
            results = tester.test_all_routes(routes)
        else:
            # Start server and run tests
            with web_server():
                results = tester.test_all_routes(routes)
        
        # Save results
        json_file = tester.save_results(results)
        html_file = tester.generate_html_report(results)
        
        # Print summary
        print("\n" + "="*60)
        print("ACCESSIBILITY TEST SUMMARY")
        print("="*60)
        
        total_routes = len(results)
        passed_routes = 0
        failed_routes = 0
        error_routes = 0
        
        for route, result in results.items():
            if "error" in result:
                status = "ERROR"
                error_routes += 1
            elif result.get("summary", {}).get("overall_status") == "pass":
                status = "PASS"
                passed_routes += 1
            else:
                status = "FAIL"
                failed_routes += 1
            
            print(f"{route:30} - {status}")
        
        print(f"\nTotal routes tested: {total_routes}")
        print(f"Passed: {passed_routes}")
        print(f"Failed: {failed_routes}")
        print(f"Errors: {error_routes}")
        
        print(f"\nDetailed reports saved to:")
        print(f"JSON: {json_file}")
        print(f"HTML: {html_file}")
        
        return failed_routes == 0 and error_routes == 0
        
    except Exception as e:
        logger.error(f"Error during accessibility testing: {e}")
        return False


def main():
    """Main entry point."""
    print("ClearCouncil Accessibility Testing")
    print("="*40)
    
    success = run_accessibility_tests()
    
    if success:
        print("\n✅ All accessibility tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some accessibility tests failed. Check the reports for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()