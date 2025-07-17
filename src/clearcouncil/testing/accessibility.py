"""Accessibility testing utilities for ClearCouncil."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

try:
    from axe_core_python.axe import Axe
    from playwright.sync_api import sync_playwright, Page
    from bs4 import BeautifulSoup
    ACCESSIBILITY_AVAILABLE = True
except ImportError:
    ACCESSIBILITY_AVAILABLE = False

logger = logging.getLogger(__name__)


class AccessibilityTester:
    """Comprehensive accessibility testing for ClearCouncil web interface."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results_dir = Path("data/results/accessibility")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        if not ACCESSIBILITY_AVAILABLE:
            raise ImportError(
                "Accessibility testing dependencies not available. "
                "Install with: pip install axe-core-python playwright beautifulsoup4"
            )
    
    def test_page_accessibility(self, path: str = "/", 
                              level: str = "AA") -> Dict[str, Any]:
        """Test accessibility of a specific page."""
        url = urljoin(self.base_url, path)
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")
                
                # Run axe-core accessibility tests
                axe = Axe()
                results = axe.run(page, {"tags": [f"wcag{level.lower()}"]})
                
                # Additional manual checks
                manual_results = self._run_manual_checks(page)
                
                # Combine results
                accessibility_report = {
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "level": level,
                    "axe_results": results,
                    "manual_checks": manual_results,
                    "summary": self._generate_summary(results, manual_checks)
                }
                
                return accessibility_report
                
            finally:
                browser.close()
    
    def _run_manual_checks(self, page: Page) -> Dict[str, Any]:
        """Run additional manual accessibility checks."""
        checks = {
            "keyboard_navigation": self._check_keyboard_navigation(page),
            "alt_text": self._check_alt_text(page),
            "heading_structure": self._check_heading_structure(page),
            "form_labels": self._check_form_labels(page),
            "skip_links": self._check_skip_links(page),
            "focus_indicators": self._check_focus_indicators(page)
        }
        
        return checks
    
    def _check_keyboard_navigation(self, page: Page) -> Dict[str, Any]:
        """Check if all interactive elements are keyboard accessible."""
        try:
            # Test tab navigation
            interactive_elements = page.query_selector_all(
                "button, input, select, textarea, a[href], [tabindex]"
            )
            
            accessible_count = 0
            total_count = len(interactive_elements)
            
            for element in interactive_elements:
                if element.is_visible():
                    try:
                        element.focus()
                        accessible_count += 1
                    except:
                        pass
            
            return {
                "status": "pass" if accessible_count == total_count else "fail",
                "accessible_elements": accessible_count,
                "total_elements": total_count,
                "message": f"{accessible_count}/{total_count} interactive elements are keyboard accessible"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_alt_text(self, page: Page) -> Dict[str, Any]:
        """Check if all images have appropriate alt text."""
        try:
            images = page.query_selector_all("img")
            
            missing_alt = []
            decorative_count = 0
            
            for img in images:
                alt = img.get_attribute("alt")
                src = img.get_attribute("src")
                
                if alt is None:
                    missing_alt.append(src)
                elif alt == "":
                    decorative_count += 1
            
            return {
                "status": "pass" if not missing_alt else "fail",
                "total_images": len(images),
                "missing_alt": missing_alt,
                "decorative_images": decorative_count,
                "message": f"{len(missing_alt)} images missing alt text"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_heading_structure(self, page: Page) -> Dict[str, Any]:
        """Check if heading structure is logical."""
        try:
            headings = page.query_selector_all("h1, h2, h3, h4, h5, h6")
            
            structure_issues = []
            prev_level = 0
            
            for heading in headings:
                level = int(heading.tag_name[1])
                
                if level > prev_level + 1:
                    structure_issues.append({
                        "element": heading.tag_name,
                        "text": heading.text_content()[:50],
                        "issue": f"Skipped from h{prev_level} to h{level}"
                    })
                
                prev_level = level
            
            return {
                "status": "pass" if not structure_issues else "fail",
                "total_headings": len(headings),
                "structure_issues": structure_issues,
                "message": f"{len(structure_issues)} heading structure issues found"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_form_labels(self, page: Page) -> Dict[str, Any]:
        """Check if form inputs have proper labels."""
        try:
            inputs = page.query_selector_all("input, select, textarea")
            
            unlabeled = []
            
            for input_elem in inputs:
                input_type = input_elem.get_attribute("type")
                if input_type in ["hidden", "submit", "button"]:
                    continue
                
                # Check for label association
                input_id = input_elem.get_attribute("id")
                aria_label = input_elem.get_attribute("aria-label")
                aria_labelledby = input_elem.get_attribute("aria-labelledby")
                
                has_label = False
                
                if input_id:
                    label = page.query_selector(f"label[for='{input_id}']")
                    if label:
                        has_label = True
                
                if aria_label or aria_labelledby:
                    has_label = True
                
                if not has_label:
                    unlabeled.append({
                        "type": input_type,
                        "name": input_elem.get_attribute("name"),
                        "id": input_id
                    })
            
            return {
                "status": "pass" if not unlabeled else "fail",
                "total_inputs": len(inputs),
                "unlabeled_inputs": unlabeled,
                "message": f"{len(unlabeled)} inputs without proper labels"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_skip_links(self, page: Page) -> Dict[str, Any]:
        """Check for skip navigation links."""
        try:
            skip_links = page.query_selector_all("a[href^='#']")
            
            main_skip_found = False
            for link in skip_links:
                text = link.text_content().lower()
                if "skip" in text and ("main" in text or "content" in text):
                    main_skip_found = True
                    break
            
            return {
                "status": "pass" if main_skip_found else "warning",
                "skip_links_found": len(skip_links),
                "main_skip_found": main_skip_found,
                "message": "Skip to main content link found" if main_skip_found else "No skip to main content link found"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _check_focus_indicators(self, page: Page) -> Dict[str, Any]:
        """Check if focus indicators are visible."""
        try:
            # This is a simplified check - full testing would require visual comparison
            focusable_elements = page.query_selector_all(
                "button, input, select, textarea, a[href], [tabindex]"
            )
            
            elements_with_focus_style = 0
            
            for element in focusable_elements:
                if element.is_visible():
                    # Check if element has focus-related CSS
                    outline = page.evaluate(
                        "(element) => getComputedStyle(element, ':focus').outline",
                        element
                    )
                    
                    if outline and outline != "none":
                        elements_with_focus_style += 1
            
            return {
                "status": "pass" if elements_with_focus_style > 0 else "warning",
                "total_focusable": len(focusable_elements),
                "with_focus_style": elements_with_focus_style,
                "message": f"{elements_with_focus_style}/{len(focusable_elements)} elements have focus indicators"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _generate_summary(self, axe_results: Dict, manual_results: Dict) -> Dict[str, Any]:
        """Generate a summary of accessibility test results."""
        violations = axe_results.get("violations", [])
        
        total_issues = len(violations)
        critical_issues = len([v for v in violations if v.get("impact") == "critical"])
        serious_issues = len([v for v in violations if v.get("impact") == "serious"])
        
        manual_failures = len([
            check for check in manual_results.values() 
            if check.get("status") == "fail"
        ])
        
        manual_warnings = len([
            check for check in manual_results.values() 
            if check.get("status") == "warning"
        ])
        
        return {
            "total_axe_violations": total_issues,
            "critical_issues": critical_issues,
            "serious_issues": serious_issues,
            "manual_failures": manual_failures,
            "manual_warnings": manual_warnings,
            "overall_status": "fail" if (critical_issues > 0 or serious_issues > 0 or manual_failures > 0) else "pass"
        }
    
    def test_all_routes(self, routes: List[str]) -> Dict[str, Any]:
        """Test accessibility for multiple routes."""
        results = {}
        
        for route in routes:
            logger.info(f"Testing accessibility for route: {route}")
            try:
                results[route] = self.test_page_accessibility(route)
            except Exception as e:
                results[route] = {
                    "url": urljoin(self.base_url, route),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> Path:
        """Save accessibility test results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accessibility_report_{timestamp}.json"
        
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Accessibility report saved to: {filepath}")
        return filepath
    
    def generate_html_report(self, results: Dict[str, Any], filename: str = None) -> Path:
        """Generate HTML accessibility report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accessibility_report_{timestamp}.html"
        
        filepath = self.results_dir / filename
        
        html_content = self._generate_html_report_content(results)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML accessibility report saved to: {filepath}")
        return filepath
    
    def _generate_html_report_content(self, results: Dict[str, Any]) -> str:
        """Generate HTML content for accessibility report."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ClearCouncil Accessibility Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
                .route-section { margin: 20px 0; border: 1px solid #ddd; padding: 15px; }
                .pass { color: green; }
                .fail { color: red; }
                .warning { color: orange; }
                .error { color: red; font-weight: bold; }
                .violation { margin: 10px 0; padding: 10px; background: #ffe6e6; }
                .check-result { margin: 5px 0; padding: 8px; background: #f9f9f9; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>ClearCouncil Accessibility Report</h1>
                <p>Generated: {timestamp}</p>
            </div>
        """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Add results for each route
        for route, result in results.items():
            if "error" in result:
                html += f"""
                <div class="route-section">
                    <h2>Route: {route}</h2>
                    <p class="error">Error: {result['error']}</p>
                </div>
                """
                continue
            
            summary = result.get("summary", {})
            status_class = "pass" if summary.get("overall_status") == "pass" else "fail"
            
            html += f"""
            <div class="route-section">
                <h2>Route: {route}</h2>
                <p class="{status_class}">Overall Status: {summary.get('overall_status', 'unknown').upper()}</p>
                
                <h3>Summary</h3>
                <table>
                    <tr><th>Metric</th><th>Count</th></tr>
                    <tr><td>Axe Violations</td><td>{summary.get('total_axe_violations', 0)}</td></tr>
                    <tr><td>Critical Issues</td><td>{summary.get('critical_issues', 0)}</td></tr>
                    <tr><td>Serious Issues</td><td>{summary.get('serious_issues', 0)}</td></tr>
                    <tr><td>Manual Failures</td><td>{summary.get('manual_failures', 0)}</td></tr>
                    <tr><td>Manual Warnings</td><td>{summary.get('manual_warnings', 0)}</td></tr>
                </table>
            """
            
            # Add axe violations
            violations = result.get("axe_results", {}).get("violations", [])
            if violations:
                html += "<h3>Axe-core Violations</h3>"
                for violation in violations:
                    html += f"""
                    <div class="violation">
                        <strong>{violation.get('id', 'Unknown')}</strong> - {violation.get('impact', 'unknown')} impact<br>
                        <em>{violation.get('description', 'No description')}</em><br>
                        Help: <a href="{violation.get('helpUrl', '#')}" target="_blank">Learn more</a>
                    </div>
                    """
            
            # Add manual check results
            manual_checks = result.get("manual_checks", {})
            if manual_checks:
                html += "<h3>Manual Checks</h3>"
                for check_name, check_result in manual_checks.items():
                    status = check_result.get("status", "unknown")
                    message = check_result.get("message", "No message")
                    html += f"""
                    <div class="check-result">
                        <strong>{check_name.replace('_', ' ').title()}</strong>: 
                        <span class="{status}">{status.upper()}</span><br>
                        {message}
                    </div>
                    """
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html


def get_clearcouncil_routes() -> List[str]:
    """Get list of routes to test for ClearCouncil application."""
    return [
        "/",
        "/dashboard",
        "/council/york_county_sc",
        "/insights",
        "/data-sources",
        "/transparency",
        "/chat"
    ]