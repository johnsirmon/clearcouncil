"""PDF document processor."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter

from .base_processor import BaseProcessor
from ..core.models import Document, DocumentMetadata
from ..core.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    """Processes PDF documents and extracts text and metadata."""
    
    def __init__(self, config):
        """Initialize PDF processor."""
        super().__init__(config)
        self.text_splitter = CharacterTextSplitter(
            chunk_size=config.processing.chunk_size
        )
    
    def process_file(self, file_path: Path) -> Document:
        """Process a PDF file and return a Document object."""
        self.validate_file(file_path)
        
        if not file_path.suffix.lower() == '.pdf':
            raise ProcessingError(f"File is not a PDF: {file_path}")
        
        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(file_path)
            
            # Extract metadata from filename
            metadata = self._extract_metadata_from_filename(file_path)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(text)
            
            return Document(
                content=text,
                metadata=metadata,
                chunks=chunks
            )
            
        except Exception as e:
            raise ProcessingError(f"Failed to process PDF {file_path}: {e}")
    
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text content from PDF file."""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                text_parts = []
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_parts.append(page.extract_text())
                
                return ''.join(text_parts)
                
        except Exception as e:
            raise ProcessingError(f"Failed to extract text from PDF: {e}")
    
    def _extract_metadata_from_filename(self, file_path: Path) -> DocumentMetadata:
        """Extract metadata from PDF filename using configured pattern."""
        filename = file_path.name
        pattern = self.config.file_patterns.pdf_pattern
        
        metadata = DocumentMetadata(
            file_path=file_path,
            council_id=self.config.identifier
        )
        
        try:
            match = re.match(pattern, filename)
            if match:
                groups = match.groupdict()
                
                # Parse date if available
                if 'date' in groups and groups['date']:
                    try:
                        date_format = self.config.file_patterns.date_format
                        metadata.meeting_date = datetime.strptime(
                            groups['date'], date_format
                        )
                    except ValueError as e:
                        logger.warning(f"Failed to parse date '{groups['date']}': {e}")
                
                # Extract other fields
                metadata.meeting_type = groups.get('meeting_type')
                metadata.document_type = groups.get('document_type')
                metadata.document_id = groups.get('document_id')
                
                logger.debug(f"Extracted metadata from {filename}: {metadata}")
            else:
                logger.warning(f"Filename does not match pattern: {filename}")
                
        except Exception as e:
            logger.warning(f"Failed to extract metadata from filename {filename}: {e}")
        
        return metadata
    
    def get_supported_extensions(self) -> list:
        """Get list of supported file extensions."""
        return ['.pdf']