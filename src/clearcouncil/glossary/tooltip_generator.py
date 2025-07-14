"""Generate tooltips and explanations for municipal terms in reports and visualizations."""

from typing import Dict, List, Optional
import re
from .municipal_glossary import MunicipalGlossary


class TooltipGenerator:
    """Generates tooltips and inline explanations for municipal terms."""
    
    def __init__(self, glossary: MunicipalGlossary):
        self.glossary = glossary
    
    def annotate_text_with_tooltips(self, text: str, format_type: str = "html") -> str:
        """
        Add tooltips to municipal terms found in text.
        
        Args:
            text: The text to annotate
            format_type: "html", "markdown", or "plain"
            
        Returns:
            Annotated text with tooltips
        """
        if format_type == "html":
            return self._annotate_html(text)
        elif format_type == "markdown":
            return self._annotate_markdown(text)
        else:
            return self._annotate_plain(text)
    
    def _annotate_html(self, text: str) -> str:
        """Add HTML tooltips to text."""
        found_terms = self.glossary.find_terms_in_text(text)
        
        # Sort terms by length (longest first) to avoid partial replacements
        found_terms.sort(key=len, reverse=True)
        
        for term in found_terms:
            term_data = self.glossary.get_definition(term)
            if term_data:
                tooltip_content = self._create_tooltip_content(term, term_data)
                
                # Create HTML with tooltip
                html_replacement = (
                    f'<span class="municipal-term" '
                    f'title="{tooltip_content}" '
                    f'data-toggle="tooltip" '
                    f'style="border-bottom: 1px dotted #007bff; cursor: help;">'
                    f'{term}</span>'
                )
                
                # Replace term with HTML version (case-insensitive, whole words only)
                pattern = r'\b' + re.escape(term) + r'\b'
                text = re.sub(pattern, html_replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _annotate_markdown(self, text: str) -> str:
        """Add markdown-style annotations to text."""
        found_terms = self.glossary.find_terms_in_text(text)
        
        for term in found_terms:
            term_data = self.glossary.get_definition(term)
            if term_data:
                explanation = term_data.get('explanation', term_data['definition'])
                
                # Create markdown footnote-style annotation
                markdown_replacement = f'[{term}](# "{explanation}")'
                
                pattern = r'\b' + re.escape(term) + r'\b'
                text = re.sub(pattern, markdown_replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _annotate_plain(self, text: str) -> str:
        """Add plain text explanations."""
        found_terms = self.glossary.find_terms_in_text(text)
        
        # Add explanations at the end
        if found_terms:
            text += "\n\nTerm Definitions:\n"
            for term in found_terms:
                term_data = self.glossary.get_definition(term)
                if term_data:
                    text += f"• {term.title()}: {term_data['definition']}\n"
        
        return text
    
    def _create_tooltip_content(self, term: str, term_data: Dict) -> str:
        """Create content for a tooltip."""
        tooltip = term_data['definition']
        
        if 'explanation' in term_data and term_data['explanation'] != term_data['definition']:
            tooltip += f" | {term_data['explanation']}"
        
        if 'example' in term_data:
            tooltip += f" | Example: {term_data['example']}"
        
        return tooltip.replace('"', '&quot;')  # Escape quotes for HTML
    
    def create_glossary_sidebar(self, text: str, format_type: str = "html") -> str:
        """Create a sidebar glossary for terms found in text."""
        found_terms = self.glossary.find_terms_in_text(text)
        
        if not found_terms:
            return ""
        
        if format_type == "html":
            return self._create_html_sidebar(found_terms)
        elif format_type == "markdown":
            return self._create_markdown_sidebar(found_terms)
        else:
            return self._create_plain_sidebar(found_terms)
    
    def _create_html_sidebar(self, terms: List[str]) -> str:
        """Create HTML sidebar with term definitions."""
        html = '<div class="glossary-sidebar" style="background: #f8f9fa; padding: 15px; border-left: 3px solid #007bff; margin: 20px 0;">\n'
        html += '<h4 style="margin-top: 0; color: #007bff;">📚 Municipal Terms in This Report</h4>\n'
        
        # Group terms by category
        categorized_terms = {}
        for term in terms:
            term_data = self.glossary.get_definition(term)
            if term_data:
                category = term_data.get('category', 'general')
                if category not in categorized_terms:
                    categorized_terms[category] = []
                categorized_terms[category].append((term, term_data))
        
        for category, category_terms in categorized_terms.items():
            html += f'<h5 style="color: #495057; margin-top: 15px; margin-bottom: 8px;">{category.title()}</h5>\n'
            for term, term_data in category_terms:
                html += f'<div style="margin-bottom: 10px;">\n'
                html += f'  <strong>{term.title()}</strong>: {term_data["definition"]}\n'
                if 'explanation' in term_data and term_data['explanation'] != term_data['definition']:
                    html += f'<br><em style="color: #6c757d;">{term_data["explanation"]}</em>\n'
                html += '</div>\n'
        
        html += '</div>'
        return html
    
    def _create_markdown_sidebar(self, terms: List[str]) -> str:
        """Create markdown sidebar with term definitions."""
        markdown = "## 📚 Municipal Terms in This Report\n\n"
        
        for term in terms:
            term_data = self.glossary.get_definition(term)
            if term_data:
                markdown += f"**{term.title()}**: {term_data['definition']}\n"
                if 'explanation' in term_data and term_data['explanation'] != term_data['definition']:
                    markdown += f"  \n  *{term_data['explanation']}*\n"
                markdown += "\n"
        
        return markdown
    
    def _create_plain_sidebar(self, terms: List[str]) -> str:
        """Create plain text sidebar with term definitions."""
        sidebar = "MUNICIPAL TERMS IN THIS REPORT\n"
        sidebar += "=" * 35 + "\n\n"
        
        for term in terms:
            term_data = self.glossary.get_definition(term)
            if term_data:
                sidebar += f"{term.upper()}\n"
                sidebar += f"  {term_data['definition']}\n"
                if 'explanation' in term_data and term_data['explanation'] != term_data['definition']:
                    sidebar += f"  {term_data['explanation']}\n"
                sidebar += "\n"
        
        return sidebar
    
    def create_term_explanations_for_chart(self, chart_data: Dict) -> Dict[str, str]:
        """Create explanations for terms that might appear in chart labels or data."""
        explanations = {}
        
        # Check all text content in the chart data
        all_text = str(chart_data)
        found_terms = self.glossary.find_terms_in_text(all_text)
        
        for term in found_terms:
            term_data = self.glossary.get_definition(term)
            if term_data:
                explanations[term] = term_data.get('explanation', term_data['definition'])
        
        return explanations