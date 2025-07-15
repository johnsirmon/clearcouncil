"""Base parser class for extracting structured data."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
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
            file_path = Path(file_path)
            
            # For PDF files, use the PDF processor for better text extraction
            if file_path.suffix.lower() == '.pdf':
                return self._parse_pdf_file(file_path)
            else:
                # For other files, use regular text reading with UTF-8
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                return self.parse_text(text)
        except Exception as e:
            raise ParsingError(f"Failed to parse file {file_path}: {e}")
    
    def _parse_pdf_file(self, file_path: Path) -> List[Any]:
        """Parse a PDF file using PyMuPDF for better text extraction."""
        try:
            import fitz  # PyMuPDF
            
            # Open PDF and extract text
            doc = fitz.open(str(file_path))
            text_parts = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_parts.append(page.get_text())
            
            doc.close()
            
            # Join all text and parse
            full_text = '\n'.join(text_parts).strip()
            
            if not full_text:
                logger.warning(f"No text extracted from PDF: {file_path}")
                return []
            
            return self.parse_text(full_text)
            
        except ImportError:
            raise ParsingError("PyMuPDF (fitz) is required for PDF parsing. Install with: pip install PyMuPDF")
        except Exception as e:
            raise ParsingError(f"Failed to extract text from PDF {file_path}: {e}")