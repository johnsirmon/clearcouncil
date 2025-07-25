"""Base downloader class."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from ..core.exceptions import DownloadError
from ..config.settings import CouncilConfig

logger = logging.getLogger(__name__)


class BaseDownloader(ABC):
    """Base class for document downloaders."""
    
    def __init__(self, config: CouncilConfig):
        """Initialize downloader with configuration."""
        self.config = config
    
    @abstractmethod
    def download_document(self, document_id: str, save_path: Optional[Path] = None) -> Path:
        """Download a single document by ID."""
        pass
    
    def download_range(self, start_id: int, end_id: int, save_path: Optional[Path] = None, force: bool = False) -> List[Path]:
        """Download a range of documents."""
        downloaded_files = []
        total_docs = end_id - start_id + 1
        
        logger.info(f"Starting download of {total_docs} documents (IDs {start_id}-{end_id})")
        
        for i, doc_id in enumerate(range(start_id, end_id + 1), 1):
            try:
                if hasattr(self, 'download_document'):
                    # Check if download_document supports force parameter
                    try:
                        file_path = self.download_document(str(doc_id), save_path, force=force)
                    except TypeError:
                        # Fallback for older signature
                        file_path = self.download_document(str(doc_id), save_path)
                else:
                    raise NotImplementedError("Subclass must implement download_document method")
                
                downloaded_files.append(file_path)
                
                # Progress logging
                if i % 10 == 0 or i == total_docs:
                    logger.info(f"Progress: {i}/{total_docs} documents processed")
                    
            except DownloadError as e:
                logger.warning(f"Failed to download document {doc_id}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error downloading document {doc_id}: {e}")
                continue
        
        # Log final statistics if available
        if hasattr(self, 'get_download_stats'):
            stats = self.get_download_stats()
            logger.info(f"Download completed - Successful: {stats['successful']}, "
                       f"Skipped: {stats['skipped']}, Failed: {stats['failed']}")
        
        return downloaded_files
    
    def download_from_config(self, range_index: int = 0, save_path: Optional[Path] = None) -> List[Path]:
        """Download documents using configured ID ranges."""
        if not self.config.website.id_ranges:
            raise DownloadError("No ID ranges configured for this council")
        
        if range_index >= len(self.config.website.id_ranges):
            raise DownloadError(f"Range index {range_index} out of bounds")
        
        range_config = self.config.website.id_ranges[range_index]
        start_id = range_config['start']
        end_id = range_config['end']
        
        logger.info(f"Downloading documents {start_id}-{end_id}: {range_config.get('description', '')}")
        
        return self.download_range(start_id, end_id, save_path)