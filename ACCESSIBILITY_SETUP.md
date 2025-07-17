# ClearCouncil Accessibility Testing Setup

This document describes the accessibility testing infrastructure added to ClearCouncil.

## Overview

We've implemented a comprehensive accessibility testing framework that includes:

1. **Automated Testing**: Using axe-core and Playwright for WCAG compliance
2. **Manual Checks**: Custom accessibility validations 
3. **Web Interface**: Built-in accessibility reports and guidelines
4. **Integration**: Seamless integration with existing Flask application

## Quick Start

### 1. Install Dependencies

```bash
# Install accessibility testing packages
python install_accessibility_deps.py
```

### 2. Run Accessibility Tests

```bash
# Test all routes
python test_accessibility.py

# Or test specific routes via web interface
# Visit: http://localhost:5000/accessibility/test?route=all
```

### 3. View Results

- **Web Interface**: Visit `http://localhost:5000/accessibility/report`
- **JSON Reports**: Saved in `data/results/accessibility/`
- **HTML Reports**: Also saved in `data/results/accessibility/`

## Features Added

### Core Testing Infrastructure

- **`src/clearcouncil/testing/accessibility.py`**: Main testing framework
- **`test_accessibility.py`**: Standalone test runner
- **`install_accessibility_deps.py`**: Dependency installer

### Web Interface Integration

- **`src/clearcouncil/web/accessibility_integration.py`**: Flask integration
- **`/accessibility/test`**: API endpoint for running tests
- **`/accessibility/report`**: Web-based report viewer
- **`/accessibility/guidelines`**: Accessibility guidelines and best practices

### Templates

- **`accessibility_report.html`**: Interactive test results
- **`accessibility_guidelines.html`**: WCAG guidelines and government requirements

## Testing Capabilities

### Automated Tests (axe-core)

- WCAG 2.1 compliance (A, AA, AAA levels)
- 50+ accessibility rules
- Critical/serious/minor issue classification
- Detailed violation descriptions with fix suggestions

### Manual Checks

1. **Keyboard Navigation**: Tab order and focus management
2. **Alt Text**: Image accessibility verification
3. **Heading Structure**: Logical heading hierarchy
4. **Form Labels**: Input labeling and association
5. **Skip Links**: Navigation accessibility
6. **Focus Indicators**: Visual focus management

### Government Compliance

- **Section 508**: Federal accessibility requirements
- **WCAG 2.1 AA**: International accessibility standards
- **ADA Compliance**: Americans with Disabilities Act requirements

## Usage Examples

### Command Line Testing

```bash
# Test all routes
python test_accessibility.py

# Install dependencies first if needed
python install_accessibility_deps.py
```

### Web Interface Testing

```bash
# Start the web server
python clearcouncil_web.py serve --host 127.0.0.1 --port 5000

# Visit in browser:
# http://localhost:5000/accessibility/test?route=/
# http://localhost:5000/accessibility/test?route=all
# http://localhost:5000/accessibility/report
# http://localhost:5000/accessibility/guidelines
```

### API Integration

```python
from clearcouncil.testing.accessibility import AccessibilityTester

# Create tester instance
tester = AccessibilityTester(base_url="http://localhost:5000")

# Test specific page
result = tester.test_page_accessibility("/dashboard", level="AA")

# Test multiple routes
routes = ["/", "/dashboard", "/insights"]
results = tester.test_all_routes(routes)

# Save results
tester.save_results(results)
tester.generate_html_report(results)
```

## Integration with Existing App

The accessibility features are integrated into your existing Flask application:

1. **Automatic Integration**: Added to `app.py` with `init_accessibility_features()`
2. **Blueprint Registration**: Accessibility routes automatically registered
3. **Template Context**: Accessibility helpers available in all templates
4. **Headers**: Accessibility-related HTTP headers added to responses

## Dependencies Added

Added to `requirements.txt`:
- `axe-core-python>=4.7.0` - Accessibility testing engine
- `playwright>=1.40.0` - Browser automation for testing
- `beautifulsoup4>=4.12.0` - HTML parsing for enhancements

## File Structure

```
src/clearcouncil/
├── testing/
│   ├── __init__.py
│   └── accessibility.py          # Main testing framework
├── web/
│   ├── accessibility_integration.py  # Flask integration
│   └── templates/
│       ├── accessibility_report.html
│       └── accessibility_guidelines.html
└── ...

# Root directory
├── test_accessibility.py         # Standalone test runner
├── install_accessibility_deps.py # Dependency installer
└── ACCESSIBILITY_SETUP.md        # This file
```

## Next Steps

1. **Run Initial Tests**: Use `python test_accessibility.py`
2. **Review Results**: Check the generated HTML report
3. **Fix Issues**: Address any accessibility violations found
4. **Integrate CI/CD**: Add accessibility testing to your deployment pipeline
5. **Regular Testing**: Set up automated accessibility testing schedule

## Government Compliance Notes

For government transparency tools like ClearCouncil:

- **Section 508**: Federal agencies must comply
- **WCAG 2.1 AA**: Recommended standard for government sites
- **ADA Requirements**: Public accommodation accessibility
- **State/Local Laws**: Additional accessibility requirements may apply

## Support

For issues with accessibility testing:

1. Check the generated HTML reports for detailed information
2. Review the guidelines at `/accessibility/guidelines`
3. Consult WCAG documentation for specific requirements
4. Use browser developer tools (axe extension) for debugging

The accessibility testing framework provides comprehensive coverage and reporting to help ensure ClearCouncil meets government accessibility requirements.