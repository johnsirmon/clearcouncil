"""
End-to-end testing framework for ClearCouncil using Playwright.

This module provides comprehensive E2E testing capabilities including:
- User workflow testing
- Cross-browser compatibility
- Performance monitoring
- Visual regression testing
- Mobile responsiveness testing
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import subprocess
import sys

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)


class E2ETestRunner:
    """Comprehensive E2E testing for ClearCouncil application."""
    
    def __init__(self, base_url: str = "http://localhost:5000", headless: bool = True):
        self.base_url = base_url
        self.headless = headless
        self.results_dir = Path("data/results/e2e")
        self.screenshots_dir = self.results_dir / "screenshots"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright not available. Install with: pip install playwright pytest-playwright"
            )
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete E2E test suite."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "test_results": {},
            "summary": {}
        }
        
        async with async_playwright() as p:
            # Test multiple browsers
            browsers = [
                ("chromium", p.chromium),
                ("firefox", p.firefox),
                ("webkit", p.webkit)
            ]
            
            for browser_name, browser_type in browsers:
                logger.info(f"Running tests on {browser_name}")
                
                browser = await browser_type.launch(headless=self.headless)
                
                try:
                    # Desktop testing
                    context = await browser.new_context(
                        viewport={"width": 1920, "height": 1080}
                    )
                    
                    desktop_results = await self._run_browser_tests(
                        context, f"{browser_name}_desktop"
                    )
                    results["test_results"][f"{browser_name}_desktop"] = desktop_results
                    
                    await context.close()
                    
                    # Mobile testing
                    mobile_context = await browser.new_context(
                        viewport={"width": 375, "height": 667},
                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
                    )
                    
                    mobile_results = await self._run_browser_tests(
                        mobile_context, f"{browser_name}_mobile"
                    )
                    results["test_results"][f"{browser_name}_mobile"] = mobile_results
                    
                    await mobile_context.close()
                    
                finally:
                    await browser.close()
        
        # Generate summary
        results["summary"] = self._generate_test_summary(results["test_results"])
        
        return results
    
    async def _run_browser_tests(self, context: BrowserContext, test_name: str) -> Dict[str, Any]:
        """Run tests for a specific browser context."""
        page = await context.new_page()
        
        test_results = {
            "user_workflows": await self._test_user_workflows(page),
            "navigation": await self._test_navigation(page),
            "forms": await self._test_forms(page),
            "data_visualization": await self._test_data_visualization(page),
            "responsive_design": await self._test_responsive_design(page),
            "performance": await self._test_performance(page),
            "accessibility": await self._test_accessibility_e2e(page),
            "error_handling": await self._test_error_handling(page)
        }
        
        await page.close()
        return test_results
    
    async def _test_user_workflows(self, page: Page) -> Dict[str, Any]:
        """Test common user workflows."""
        workflows = {}
        
        # Workflow 1: View council information
        try:
            await page.goto(self.base_url)
            await page.wait_for_load_state("networkidle")
            
            # Take screenshot
            await page.screenshot(
                path=self.screenshots_dir / f"workflow_home_{int(time.time())}.png"
            )
            
            # Click on council selection
            council_link = page.locator("text=York County SC").first
            if await council_link.is_visible():
                await council_link.click()
                await page.wait_for_load_state("networkidle")
                
                workflows["view_council"] = {
                    "status": "pass",
                    "message": "Successfully navigated to council page"
                }
            else:
                workflows["view_council"] = {
                    "status": "fail",
                    "message": "Council link not found"
                }
                
        except Exception as e:
            workflows["view_council"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Workflow 2: Search functionality
        try:
            await page.goto(self.base_url)
            await page.wait_for_load_state("networkidle")
            
            # Look for search input
            search_input = page.locator("input[type='search'], input[placeholder*='search']").first
            if await search_input.is_visible():
                await search_input.fill("voting")
                await search_input.press("Enter")
                await page.wait_for_load_state("networkidle")
                
                workflows["search"] = {
                    "status": "pass",
                    "message": "Search functionality works"
                }
            else:
                workflows["search"] = {
                    "status": "warning",
                    "message": "Search input not found"
                }
                
        except Exception as e:
            workflows["search"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Workflow 3: Dashboard navigation
        try:
            await page.goto(f"{self.base_url}/dashboard")
            await page.wait_for_load_state("networkidle")
            
            # Check for charts or data visualization
            chart_elements = await page.locator("canvas, svg, .chart").count()
            
            if chart_elements > 0:
                workflows["dashboard"] = {
                    "status": "pass",
                    "message": f"Dashboard loaded with {chart_elements} visualizations"
                }
            else:
                workflows["dashboard"] = {
                    "status": "warning",
                    "message": "Dashboard loaded but no visualizations found"
                }
                
        except Exception as e:
            workflows["dashboard"] = {
                "status": "error",
                "message": str(e)
            }
        
        return workflows
    
    async def _test_navigation(self, page: Page) -> Dict[str, Any]:
        """Test navigation functionality."""
        navigation_tests = {}
        
        # Test main navigation links
        try:
            await page.goto(self.base_url)
            await page.wait_for_load_state("networkidle")
            
            # Find navigation links
            nav_links = await page.locator("nav a, .navbar a").all()
            
            working_links = 0
            total_links = len(nav_links)
            
            for link in nav_links:
                try:
                    href = await link.get_attribute("href")
                    if href and not href.startswith("#"):
                        # Test link (without actually clicking to avoid navigation)
                        response = await page.evaluate(f"""
                            fetch('{href}', {{method: 'HEAD'}})
                                .then(r => r.status)
                                .catch(e => 500)
                        """)
                        
                        if response < 400:
                            working_links += 1
                            
                except Exception:
                    pass
            
            navigation_tests["main_navigation"] = {
                "status": "pass" if working_links == total_links else "warning",
                "working_links": working_links,
                "total_links": total_links,
                "message": f"{working_links}/{total_links} navigation links working"
            }
            
        except Exception as e:
            navigation_tests["main_navigation"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Test breadcrumb navigation
        try:
            await page.goto(f"{self.base_url}/council/york_county_sc")
            await page.wait_for_load_state("networkidle")
            
            breadcrumb = page.locator(".breadcrumb, nav[aria-label='breadcrumb']")
            if await breadcrumb.is_visible():
                navigation_tests["breadcrumb"] = {
                    "status": "pass",
                    "message": "Breadcrumb navigation present"
                }
            else:
                navigation_tests["breadcrumb"] = {
                    "status": "warning",
                    "message": "Breadcrumb navigation not found"
                }
                
        except Exception as e:
            navigation_tests["breadcrumb"] = {
                "status": "error",
                "message": str(e)
            }
        
        return navigation_tests
    
    async def _test_forms(self, page: Page) -> Dict[str, Any]:
        """Test form functionality."""
        form_tests = {}
        
        # Test search forms
        try:
            await page.goto(self.base_url)
            await page.wait_for_load_state("networkidle")
            
            # Find forms
            forms = await page.locator("form").all()
            
            for i, form in enumerate(forms):
                try:
                    # Test form inputs
                    inputs = await form.locator("input, select, textarea").all()
                    
                    form_working = True
                    for input_elem in inputs:
                        input_type = await input_elem.get_attribute("type")
                        if input_type not in ["hidden", "submit", "button"]:
                            # Test input functionality
                            try:
                                await input_elem.fill("test")
                                await input_elem.clear()
                            except:
                                form_working = False
                                break
                    
                    form_tests[f"form_{i}"] = {
                        "status": "pass" if form_working else "fail",
                        "inputs_count": len(inputs),
                        "message": f"Form {i} functionality test"
                    }
                    
                except Exception as e:
                    form_tests[f"form_{i}"] = {
                        "status": "error",
                        "message": str(e)
                    }
                    
        except Exception as e:
            form_tests["general"] = {
                "status": "error",
                "message": str(e)
            }
        
        return form_tests
    
    async def _test_data_visualization(self, page: Page) -> Dict[str, Any]:
        """Test data visualization functionality."""
        viz_tests = {}
        
        try:
            await page.goto(f"{self.base_url}/dashboard")
            await page.wait_for_load_state("networkidle")
            
            # Wait for charts to load
            await page.wait_for_timeout(3000)
            
            # Test for different chart types
            chart_types = {
                "plotly": "div[id*='plot'], .plotly-graph-div",
                "canvas": "canvas",
                "svg": "svg",
                "d3": ".d3-chart, [class*='d3-']"
            }
            
            for chart_type, selector in chart_types.items():
                try:
                    count = await page.locator(selector).count()
                    if count > 0:
                        viz_tests[f"{chart_type}_charts"] = {
                            "status": "pass",
                            "count": count,
                            "message": f"Found {count} {chart_type} charts"
                        }
                        
                        # Take screenshot of charts
                        await page.screenshot(
                            path=self.screenshots_dir / f"charts_{chart_type}_{int(time.time())}.png"
                        )
                        
                except Exception as e:
                    viz_tests[f"{chart_type}_charts"] = {
                        "status": "error",
                        "message": str(e)
                    }
            
            # Test chart interactivity
            try:
                plotly_chart = page.locator(".plotly-graph-div").first
                if await plotly_chart.is_visible():
                    # Test hover functionality
                    await plotly_chart.hover()
                    await page.wait_for_timeout(1000)
                    
                    viz_tests["chart_interactivity"] = {
                        "status": "pass",
                        "message": "Chart interactivity working"
                    }
                    
            except Exception as e:
                viz_tests["chart_interactivity"] = {
                    "status": "warning",
                    "message": "Chart interactivity test failed"
                }
                
        except Exception as e:
            viz_tests["general"] = {
                "status": "error",
                "message": str(e)
            }
        
        return viz_tests
    
    async def _test_responsive_design(self, page: Page) -> Dict[str, Any]:
        """Test responsive design functionality."""
        responsive_tests = {}
        
        viewports = [
            {"name": "mobile", "width": 375, "height": 667},
            {"name": "tablet", "width": 768, "height": 1024},
            {"name": "desktop", "width": 1920, "height": 1080}
        ]
        
        for viewport in viewports:
            try:
                await page.set_viewport_size(viewport)
                await page.goto(self.base_url)
                await page.wait_for_load_state("networkidle")
                
                # Check if navigation is responsive
                nav_visible = await page.locator("nav, .navbar").is_visible()
                
                # Check if content is properly displayed
                content_visible = await page.locator("main, .main-content, .container").is_visible()
                
                # Take screenshot
                await page.screenshot(
                    path=self.screenshots_dir / f"responsive_{viewport['name']}_{int(time.time())}.png"
                )
                
                responsive_tests[viewport["name"]] = {
                    "status": "pass" if nav_visible and content_visible else "warning",
                    "viewport": viewport,
                    "nav_visible": nav_visible,
                    "content_visible": content_visible,
                    "message": f"Responsive test for {viewport['name']}"
                }
                
            except Exception as e:
                responsive_tests[viewport["name"]] = {
                    "status": "error",
                    "message": str(e)
                }
        
        return responsive_tests
    
    async def _test_performance(self, page: Page) -> Dict[str, Any]:
        """Test performance metrics."""
        performance_tests = {}
        
        try:
            # Navigate and measure load time
            start_time = time.time()
            await page.goto(self.base_url)
            await page.wait_for_load_state("networkidle")
            load_time = time.time() - start_time
            
            # Get performance metrics
            metrics = await page.evaluate("""
                () => {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        dom_content_loaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                        load_complete: navigation.loadEventEnd - navigation.loadEventStart,
                        first_paint: performance.getEntriesByType('paint').find(p => p.name === 'first-paint')?.startTime || 0,
                        first_contentful_paint: performance.getEntriesByType('paint').find(p => p.name === 'first-contentful-paint')?.startTime || 0
                    };
                }
            """)
            
            performance_tests["load_time"] = {
                "status": "pass" if load_time < 5 else "warning",
                "load_time": load_time,
                "message": f"Page loaded in {load_time:.2f} seconds"
            }
            
            performance_tests["metrics"] = {
                "status": "pass",
                "metrics": metrics,
                "message": "Performance metrics collected"
            }
            
        except Exception as e:
            performance_tests["general"] = {
                "status": "error",
                "message": str(e)
            }
        
        return performance_tests
    
    async def _test_accessibility_e2e(self, page: Page) -> Dict[str, Any]:
        """Test accessibility in E2E context."""
        accessibility_tests = {}
        
        try:
            await page.goto(self.base_url)
            await page.wait_for_load_state("networkidle")
            
            # Test keyboard navigation
            try:
                await page.keyboard.press("Tab")
                focused_element = await page.evaluate("document.activeElement.tagName")
                
                accessibility_tests["keyboard_navigation"] = {
                    "status": "pass" if focused_element else "warning",
                    "focused_element": focused_element,
                    "message": "Keyboard navigation test"
                }
                
            except Exception as e:
                accessibility_tests["keyboard_navigation"] = {
                    "status": "error",
                    "message": str(e)
                }
            
            # Test screen reader compatibility
            try:
                aria_labels = await page.locator("[aria-label]").count()
                headings = await page.locator("h1, h2, h3, h4, h5, h6").count()
                
                accessibility_tests["screen_reader"] = {
                    "status": "pass" if aria_labels > 0 and headings > 0 else "warning",
                    "aria_labels": aria_labels,
                    "headings": headings,
                    "message": f"Found {aria_labels} ARIA labels and {headings} headings"
                }
                
            except Exception as e:
                accessibility_tests["screen_reader"] = {
                    "status": "error",
                    "message": str(e)
                }
                
        except Exception as e:
            accessibility_tests["general"] = {
                "status": "error",
                "message": str(e)
            }
        
        return accessibility_tests
    
    async def _test_error_handling(self, page: Page) -> Dict[str, Any]:
        """Test error handling."""
        error_tests = {}
        
        # Test 404 page
        try:
            response = await page.goto(f"{self.base_url}/nonexistent-page")
            
            error_tests["404_handling"] = {
                "status": "pass" if response.status == 404 else "warning",
                "status_code": response.status,
                "message": f"404 page returned status {response.status}"
            }
            
        except Exception as e:
            error_tests["404_handling"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Test JavaScript errors
        try:
            js_errors = []
            
            def handle_console(msg):
                if msg.type == "error":
                    js_errors.append(msg.text)
            
            page.on("console", handle_console)
            
            await page.goto(self.base_url)
            await page.wait_for_load_state("networkidle")
            
            error_tests["javascript_errors"] = {
                "status": "pass" if not js_errors else "warning",
                "errors": js_errors,
                "message": f"Found {len(js_errors)} JavaScript errors"
            }
            
        except Exception as e:
            error_tests["javascript_errors"] = {
                "status": "error",
                "message": str(e)
            }
        
        return error_tests
    
    def _generate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of test results."""
        summary = {
            "total_test_suites": len(test_results),
            "passed_tests": 0,
            "failed_tests": 0,
            "warning_tests": 0,
            "error_tests": 0,
            "browser_results": {}
        }
        
        for browser, results in test_results.items():
            browser_summary = {
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "errors": 0
            }
            
            for category, tests in results.items():
                for test_name, test_result in tests.items():
                    status = test_result.get("status", "unknown")
                    
                    if status == "pass":
                        browser_summary["passed"] += 1
                        summary["passed_tests"] += 1
                    elif status == "fail":
                        browser_summary["failed"] += 1
                        summary["failed_tests"] += 1
                    elif status == "warning":
                        browser_summary["warnings"] += 1
                        summary["warning_tests"] += 1
                    elif status == "error":
                        browser_summary["errors"] += 1
                        summary["error_tests"] += 1
            
            summary["browser_results"][browser] = browser_summary
        
        summary["overall_status"] = "pass" if summary["failed_tests"] == 0 and summary["error_tests"] == 0 else "fail"
        
        return summary
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> Path:
        """Save test results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"e2e_test_results_{timestamp}.json"
        
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"E2E test results saved to: {filepath}")
        return filepath
    
    def generate_html_report(self, results: Dict[str, Any], filename: str = None) -> Path:
        """Generate HTML report from test results."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"e2e_test_report_{timestamp}.html"
        
        filepath = self.results_dir / filename
        
        html_content = self._generate_html_report_content(results)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        logger.info(f"E2E HTML report saved to: {filepath}")
        return filepath
    
    def _generate_html_report_content(self, results: Dict[str, Any]) -> str:
        """Generate HTML content for E2E test report."""
        summary = results.get("summary", {})
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ClearCouncil E2E Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .summary-item {{ text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .browser-section {{ margin: 20px 0; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                .test-category {{ margin: 15px 0; }}
                .test-result {{ margin: 5px 0; padding: 8px; border-radius: 3px; }}
                .pass {{ background: #d4edda; color: #155724; }}
                .fail {{ background: #f8d7da; color: #721c24; }}
                .warning {{ background: #fff3cd; color: #856404; }}
                .error {{ background: #f8d7da; color: #721c24; }}
                .screenshot {{ max-width: 300px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ClearCouncil E2E Test Report</h1>
                <p>Generated: {results.get('timestamp', 'Unknown')}</p>
                <p>Base URL: {results.get('base_url', 'Unknown')}</p>
            </div>
            
            <div class="summary">
                <div class="summary-item">
                    <h3>{summary.get('passed_tests', 0)}</h3>
                    <p>Passed</p>
                </div>
                <div class="summary-item">
                    <h3>{summary.get('failed_tests', 0)}</h3>
                    <p>Failed</p>
                </div>
                <div class="summary-item">
                    <h3>{summary.get('warning_tests', 0)}</h3>
                    <p>Warnings</p>
                </div>
                <div class="summary-item">
                    <h3>{summary.get('error_tests', 0)}</h3>
                    <p>Errors</p>
                </div>
            </div>
        """
        
        # Add browser-specific results
        for browser, test_results in results.get("test_results", {}).items():
            html += f"""
            <div class="browser-section">
                <h2>{browser.replace('_', ' ').title()}</h2>
            """
            
            for category, tests in test_results.items():
                html += f"""
                <div class="test-category">
                    <h3>{category.replace('_', ' ').title()}</h3>
                """
                
                for test_name, test_result in tests.items():
                    status = test_result.get("status", "unknown")
                    message = test_result.get("message", "No message")
                    
                    html += f"""
                    <div class="test-result {status}">
                        <strong>{test_name.replace('_', ' ').title()}</strong>: {status.upper()}<br>
                        {message}
                    </div>
                    """
                
                html += "</div>"
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html


def run_e2e_tests():
    """Run E2E tests from command line."""
    runner = E2ETestRunner()
    
    async def main():
        results = await runner.run_full_test_suite()
        
        # Save results
        json_file = runner.save_results(results)
        html_file = runner.generate_html_report(results)
        
        print(f"E2E test results saved to: {json_file}")
        print(f"E2E HTML report saved to: {html_file}")
        
        return results
    
    return asyncio.run(main())


if __name__ == "__main__":
    run_e2e_tests()