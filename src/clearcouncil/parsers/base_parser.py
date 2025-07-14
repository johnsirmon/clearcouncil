"""Base parser class for extracting structured data."""

import logging
from abc import ABC, abstractmethod
from typing import List, Any

from ..core.exceptions import ParsingError
from ..config.settings import CouncilConfig

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Base class for document parsers."""
    
    def __init__(self, config: CouncilConfig):
        """Initialize parser with configuration."""
        self.config = config
    
    @abstractmethod
    def parse_text(self, text: str) -> List[Any]:
        """Parse text and return structured data."""
        pass
    
    def parse_file(self, file_path) -> List[Any]:
        """Parse a file and return structured data."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.parse_text(text)
        except Exception as e:
            raise ParsingError(f"Failed to parse file {file_path}: {e}")