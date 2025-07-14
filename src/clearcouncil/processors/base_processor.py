"""Base processor class for document processing."""

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..core.models import Document, ProcessingResult
from ..core.exceptions import ProcessingError
from ..config.settings import CouncilConfig

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """Base class for all document processors."""
    
    def __init__(self, config: CouncilConfig):
        """Initialize the processor with configuration."""
        self.config = config
    
    @abstractmethod
    def process_file(self, file_path: Path) -> Document:
        """Process a single file and return a Document object."""
        pass
    
    def process_with_result(self, file_path: Path) -> ProcessingResult:
        """Process a file and return a ProcessingResult with error handling."""
        start_time = time.time()
        
        try:
            logger.info(f"Processing file: {file_path}")
            document = self.process_file(file_path)
            processing_time = time.time() - start_time
            
            logger.info(f"Successfully processed {file_path} in {processing_time:.2f}s")
            return ProcessingResult.success_result(document, processing_time)
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Failed to process {file_path}: {str(e)}"
            logger.error(error_msg)
            return ProcessingResult.error_result(error_msg, processing_time)
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate that a file can be processed."""
        if not file_path.exists():
            raise ProcessingError(f"File does not exist: {file_path}")
        
        if not file_path.is_file():
            raise ProcessingError(f"Path is not a file: {file_path}")
        
        return True