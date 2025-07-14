"""Municipal government terminology glossary."""

from typing import Dict, Optional, List
import re
import yaml
from pathlib import Path


class MunicipalGlossary:
    """Provides definitions and explanations for municipal government terms."""
    
    def __init__(self, custom_terms_file: Optional[Path] = None):
        """Initialize with built-in terms and optional custom terms."""
        self.terms = self._load_default_terms()
        
        if custom_terms_file and custom_terms_file.exists():
            self._load_custom_terms(custom_terms_file)
    
    def _load_default_terms(self) -> Dict[str, Dict]:
        """Load default municipal government terms."""
        return {
            # Voting Terms
            "movant": {
                "definition": "The person who makes a motion during a meeting",
                "explanation": "In council meetings, when someone wants to propose an action or decision, they 'make a motion'. The person who does this is called the movant.",
                "example": "Councilman Smith was the movant for the rezoning proposal.",
                "category": "voting"
            },
            "second": {
                "definition": "A council member who supports a motion so it can be discussed and voted on",
                "explanation": "After someone makes a motion, another council member must 'second' it before the council can discuss and vote on it. This ensures at least two people think the idea is worth considering.",
                "example": "Councilwoman Jones seconded the motion to approve the budget.",
                "category": "voting"
            },
            "motion": {
                "definition": "A formal proposal for action made during a council meeting",
                "explanation": "A motion is a specific proposal that the council can vote on. It must be stated clearly so everyone knows exactly what they're voting for or against.",
                "example": "Motion to approve the rezoning of property at 123 Main Street.",
                "category": "voting"
            },
            "abstain": {
                "definition": "To choose not to vote for or against a motion",
                "explanation": "Sometimes a council member may abstain from voting due to a conflict of interest or if they feel they don't have enough information to make a decision.",
                "example": "The councilman abstained because he owns property nearby.",
                "category": "voting"
            },
            
            # Zoning and Development Terms
            "rezoning": {
                "definition": "Changing the designated use of a piece of land",
                "explanation": "Every piece of land in a city/county is zoned for specific uses (residential, commercial, industrial, etc.). Rezoning changes what can be built or done on that land.",
                "example": "Rezoning farmland to allow a shopping center to be built.",
                "category": "zoning"
            },
            "zoning": {
                "definition": "Legal designation that determines what can be built or done on a piece of land",
                "explanation": "Zoning protects communities by ensuring compatible land uses. For example, it prevents a factory from being built next to a school.",
                "example": "This land is zoned R-1 for single-family residential homes.",
                "category": "zoning"
            },
            "variance": {
                "definition": "Permission to deviate from zoning requirements",
                "explanation": "Sometimes property owners need to build something that doesn't quite fit the zoning rules. A variance allows them to do this if it won't harm the community.",
                "example": "A variance to build a garage 2 feet closer to the property line than normally allowed.",
                "category": "zoning"
            },
            "conditional use permit": {
                "definition": "Permission to use property for a purpose that requires special approval",
                "explanation": "Some uses are allowed in a zone but only with special conditions to protect the neighborhood.",
                "example": "A conditional use permit for a church in a residential area.",
                "category": "zoning"
            },
            "setback": {
                "definition": "Required distance between a building and property line",
                "explanation": "Setbacks ensure buildings aren't too close to roads or neighboring properties, providing space for safety, privacy, and aesthetics.",
                "example": "The house must be built at least 25 feet back from the street.",
                "category": "zoning"
            },
            
            # Administrative Terms
            "ordinance": {
                "definition": "A law passed by the local government",
                "explanation": "Ordinances are local laws that apply within the city or county limits. They cover things like noise regulations, building codes, and business licensing.",
                "example": "The noise ordinance prohibits loud music after 10 PM.",
                "category": "administration"
            },
            "resolution": {
                "definition": "A formal statement of position or intent by the council",
                "explanation": "Unlike ordinances, resolutions don't create laws but express the council's opinion or establish policy directions.",
                "example": "A resolution supporting environmental protection efforts.",
                "category": "administration"
            },
            "public hearing": {
                "definition": "A meeting where citizens can speak about an issue before the council votes",
                "explanation": "Public hearings give community members a chance to share their opinions on important decisions that affect them.",
                "example": "A public hearing on the proposed tax increase.",
                "category": "administration"
            },
            "agenda": {
                "definition": "The list of topics to be discussed at a meeting",
                "explanation": "The agenda is published before meetings so citizens know what will be discussed and can plan to attend for topics they care about.",
                "example": "The rezoning request is item 5 on tonight's agenda.",
                "category": "administration"
            },
            
            # Financial Terms
            "millage rate": {
                "definition": "The tax rate per $1,000 of property value",
                "explanation": "This determines how much property tax you pay. If your home is worth $100,000 and the millage rate is 10, you pay $1,000 in property taxes.",
                "example": "The council voted to increase the millage rate by 2 mills.",
                "category": "finance"
            },
            "budget amendment": {
                "definition": "A change to the approved annual budget",
                "explanation": "Sometimes the government needs to spend money on something not in the original budget, or move money between departments.",
                "example": "A budget amendment to fund emergency road repairs.",
                "category": "finance"
            },
            "capital improvement": {
                "definition": "Major purchases or construction projects funded by the government",
                "explanation": "These are big, long-term investments like new roads, buildings, or equipment that will benefit the community for many years.",
                "example": "Building a new fire station is a capital improvement.",
                "category": "finance"
            },
            
            # Planning Terms
            "comprehensive plan": {
                "definition": "A long-term vision for how the community should grow and develop",
                "explanation": "This plan guides decisions about zoning, roads, schools, and other development for 10-20 years into the future.",
                "example": "The comprehensive plan calls for more mixed-use development downtown.",
                "category": "planning"
            },
            "impact fee": {
                "definition": "A charge on new development to help pay for infrastructure needs",
                "explanation": "When new houses or businesses are built, they create demand for roads, schools, and utilities. Impact fees help pay for these needs.",
                "example": "The developer paid impact fees to help fund a new traffic light.",
                "category": "planning"
            },
            "right of way": {
                "definition": "Land reserved for public use, typically for roads or utilities",
                "explanation": "The government needs space for roads, sidewalks, and utility lines. Right of way ensures this space is available.",
                "example": "The new road will require 10 feet of right of way on each side.",
                "category": "planning"
            }
        }
    
    def _load_custom_terms(self, file_path: Path):
        """Load custom terms from a YAML file."""
        try:
            with open(file_path, 'r') as f:
                custom_terms = yaml.safe_load(f)
                self.terms.update(custom_terms)
        except Exception as e:
            print(f"Warning: Could not load custom terms from {file_path}: {e}")
    
    def get_definition(self, term: str) -> Optional[Dict]:
        """Get definition for a specific term."""
        term_key = term.lower().strip()
        return self.terms.get(term_key)
    
    def get_explanation(self, term: str) -> Optional[str]:
        """Get detailed explanation for a term."""
        definition_data = self.get_definition(term)
        if definition_data:
            return definition_data.get('explanation', definition_data.get('definition'))
        return None
    
    def find_terms_in_text(self, text: str) -> List[str]:
        """Find municipal terms that appear in the given text."""
        found_terms = []
        text_lower = text.lower()
        
        for term in self.terms.keys():
            # Use word boundaries to match whole terms
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower):
                found_terms.append(term)
        
        return found_terms
    
    def get_terms_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all terms in a specific category."""
        return {
            term: data for term, data in self.terms.items()
            if data.get('category') == category
        }
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories."""
        categories = set()
        for term_data in self.terms.values():
            if 'category' in term_data:
                categories.add(term_data['category'])
        return sorted(list(categories))
    
    def create_glossary_for_text(self, text: str) -> Dict[str, Dict]:
        """Create a glossary for terms found in specific text."""
        found_terms = self.find_terms_in_text(text)
        return {
            term: self.terms[term] for term in found_terms
            if term in self.terms
        }
    
    def add_term(self, term: str, definition: str, explanation: str = None, 
                 category: str = "custom", example: str = None):
        """Add a new term to the glossary."""
        self.terms[term.lower()] = {
            'definition': definition,
            'explanation': explanation or definition,
            'category': category,
            'example': example
        }
    
    def export_glossary(self, file_path: Path, category: Optional[str] = None):
        """Export glossary to a YAML file."""
        if category:
            terms_to_export = self.get_terms_by_category(category)
        else:
            terms_to_export = self.terms
        
        with open(file_path, 'w') as f:
            yaml.dump(terms_to_export, f, default_flow_style=False, sort_keys=True)