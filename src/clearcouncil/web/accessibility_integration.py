"""
Accessibility integration for ClearCouncil web interface.

This module provides accessibility enhancements and testing integration
for the existing Flask application.
"""

from flask import Blueprint, jsonify, render_template, request
import logging
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Create accessibility blueprint
accessibility_bp = Blueprint('accessibility', __name__, url_prefix='/accessibility')


@accessibility_bp.route('/test', methods=['GET'])
def test_accessibility():
    """Endpoint to trigger accessibility testing."""
    try:
        from ..testing.accessibility import AccessibilityTester, get_clearcouncil_routes
        
        tester = AccessibilityTester(base_url=request.host_url.rstrip('/'))
        routes = get_clearcouncil_routes()
        
        # Test specific route if provided
        route = request.args.get('route', '/')
        level = request.args.get('level', 'AA')
        
        if route == 'all':
            results = tester.test_all_routes(routes)
        else:
            results = {route: tester.test_page_accessibility(route, level)}
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except ImportError as e:
        return jsonify({
            'success': False,
            'error': 'Accessibility testing dependencies not installed',
            'message': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Accessibility testing error: {e}")
        return jsonify({
            'success': False,
            'error': 'Accessibility testing failed',
            'message': str(e)
        }), 500


@accessibility_bp.route('/report', methods=['GET'])
def accessibility_report():
    """Display accessibility testing report."""
    try:
        # Look for latest accessibility report
        results_dir = Path('data/results/accessibility')
        if not results_dir.exists():
            return render_template('accessibility_report.html', 
                                 error="No accessibility reports found")
        
        # Find latest JSON report
        json_files = list(results_dir.glob('accessibility_report_*.json'))
        if not json_files:
            return render_template('accessibility_report.html', 
                                 error="No accessibility reports found")
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            results = json.load(f)
        
        return render_template('accessibility_report.html', 
                             results=results, 
                             report_file=latest_file.name)
        
    except Exception as e:
        logger.error(f"Error loading accessibility report: {e}")
        return render_template('accessibility_report.html', 
                             error=f"Error loading report: {e}")


@accessibility_bp.route('/guidelines', methods=['GET'])
def accessibility_guidelines():
    """Display accessibility guidelines and best practices."""
    guidelines = {
        'wcag_principles': [
            {
                'principle': 'Perceivable',
                'description': 'Information must be presentable in ways users can perceive',
                'examples': ['Alt text for images', 'Sufficient color contrast', 'Captions for videos']
            },
            {
                'principle': 'Operable', 
                'description': 'Interface components must be operable',
                'examples': ['Keyboard navigation', 'No seizure-inducing content', 'Sufficient time limits']
            },
            {
                'principle': 'Understandable',
                'description': 'Information and UI operation must be understandable',
                'examples': ['Clear language', 'Predictable functionality', 'Error identification']
            },
            {
                'principle': 'Robust',
                'description': 'Content must be robust enough for various assistive technologies',
                'examples': ['Valid HTML', 'Compatible with screen readers', 'Future-proof markup']
            }
        ],
        'government_requirements': [
            'Section 508 compliance for federal agencies',
            'WCAG 2.1 AA standards',
            'State and local accessibility laws',
            'ADA compliance requirements'
        ],
        'testing_checklist': [
            'Keyboard navigation testing',
            'Screen reader compatibility',
            'Color contrast verification',
            'Alt text for images',
            'Form label associations',
            'Heading structure validation',
            'Focus indicator visibility',
            'Skip navigation links'
        ]
    }
    
    return render_template('accessibility_guidelines.html', guidelines=guidelines)


def add_accessibility_headers(response):
    """Add accessibility-related headers to responses."""
    # Add security headers that help with accessibility
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Add accessibility-specific headers
    response.headers['Content-Language'] = 'en-US'
    
    return response


def enhance_accessibility_context():
    """Provide accessibility context for templates."""
    return {
        'accessibility_enabled': True,
        'skip_links': [
            {'href': '#main-content', 'text': 'Skip to main content'},
            {'href': '#navigation', 'text': 'Skip to navigation'},
            {'href': '#search', 'text': 'Skip to search'}
        ],
        'aria_labels': {
            'main_nav': 'Main navigation',
            'breadcrumb': 'Breadcrumb navigation',
            'search': 'Search ClearCouncil data',
            'filters': 'Filter options',
            'results': 'Search results'
        }
    }


class AccessibilityEnhancer:
    """Helper class for accessibility enhancements."""
    
    @staticmethod
    def enhance_form_accessibility(form_html: str) -> str:
        """Add accessibility enhancements to form HTML."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(form_html, 'html.parser')
        
        # Add labels to inputs that don't have them
        inputs = soup.find_all(['input', 'select', 'textarea'])
        for input_elem in inputs:
            if input_elem.get('type') in ['hidden', 'submit', 'button']:
                continue
                
            # Check if input has a label
            input_id = input_elem.get('id')
            if not input_id:
                continue
                
            # Look for existing label
            label = soup.find('label', {'for': input_id})
            if not label and not input_elem.get('aria-label'):
                # Create label based on name or id
                label_text = input_elem.get('name', input_id).replace('_', ' ').title()
                new_label = soup.new_tag('label', **{'for': input_id})
                new_label.string = label_text
                input_elem.insert_before(new_label)
        
        return str(soup)
    
    @staticmethod
    def add_aria_labels(html: str, labels: Dict[str, str]) -> str:
        """Add ARIA labels to HTML elements."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        for selector, label in labels.items():
            elements = soup.select(selector)
            for elem in elements:
                if not elem.get('aria-label'):
                    elem['aria-label'] = label
        
        return str(soup)
    
    @staticmethod
    def ensure_heading_structure(html: str) -> str:
        """Ensure proper heading structure."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            return html
        
        # Ensure there's only one h1
        h1_count = len(soup.find_all('h1'))
        if h1_count == 0:
            # Convert first heading to h1
            if headings:
                headings[0].name = 'h1'
        elif h1_count > 1:
            # Convert additional h1s to h2
            h1_elements = soup.find_all('h1')
            for i, h1 in enumerate(h1_elements[1:], 1):
                h1.name = 'h2'
        
        return str(soup)


def init_accessibility_features(app):
    """Initialize accessibility features for the Flask app."""
    # Register accessibility blueprint
    app.register_blueprint(accessibility_bp)
    
    # Add accessibility context to all templates
    @app.context_processor
    def inject_accessibility_context():
        return enhance_accessibility_context()
    
    # Add accessibility headers to all responses
    @app.after_request
    def add_accessibility_headers_to_response(response):
        return add_accessibility_headers(response)
    
    # Add accessibility-specific template filters
    @app.template_filter('enhance_accessibility')
    def enhance_accessibility_filter(html):
        enhancer = AccessibilityEnhancer()
        html = enhancer.ensure_heading_structure(html)
        return html
    
    logger.info("Accessibility features initialized")