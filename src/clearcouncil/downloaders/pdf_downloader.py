"""PDF document downloader."""

import re
import requests
from pathlib import Path
from typing import Optional
import logging

from .base_downloader import BaseDownloader
from ..core.exceptions import DownloadError

logger = logging.getLogger(__name__)


class PDFDownloader(BaseDownloader):
    """Downloads PDF documents from council websites."""
    
    def __init__(self, config):
        """Initialize PDF downloader."""
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClearCouncil Document Downloader 1.0'
        })
    
    def download_document(self, document_id: str, save_path: Optional[Path] = None) -> Path:
        """Download a single PDF document by ID."""
        # Build URL from template
        url = self.config.website.document_url_template.format(
            base_url=self.config.website.base_url,
            id=document_id
        )
        
        # Determine save directory
        if save_path is None:
            save_path = self.config.get_data_path("pdf")
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # First, make a HEAD request to get filename from headers
            response = self.session.head(url, timeout=30)
            response.raise_for_status()
            
            filename = self._extract_filename_from_response(response, document_id)
            file_path = save_path / filename
            
            # Download the actual file
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Verify it's actually a PDF
            if not self._is_pdf_content(response.content):
                raise DownloadError(f"Downloaded content for ID {document_id} is not a valid PDF")
            
            # Save to file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.debug(f"Downloaded {filename} ({len(response.content)} bytes)")
            return file_path
            
        except requests.RequestException as e:
            raise DownloadError(f"Failed to download document {document_id}: {e}")
        except Exception as e:
            raise DownloadError(f"Unexpected error downloading document {document_id}: {e}")
    
    def _extract_filename_from_response(self, response: requests.Response, document_id: str) -> str:
        """Extract filename from HTTP response headers."""
        # Try to get filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        if content_disposition:
            # Look for filename in Content-Disposition header
            filename_match = re.search(r'filename="([^"]+)"', content_disposition)
            if filename_match:
                return filename_match.group(1)
            
            # Alternative format
            filename_match = re.search(r'filename=([^;\\s]+)', content_disposition)
            if filename_match:
                return filename_match.group(1).strip('"')
        
        # Fallback to generic filename
        return f"document_{document_id}.pdf"
    
    def _is_pdf_content(self, content: bytes) -> bool:
        """Check if content is a valid PDF by looking at header."""
        return content.startswith(b'%PDF-')
    
    def test_connection(self) -> bool:
        """Test if the council website is accessible."""
        try:
            # Use the first ID range to test
            if not self.config.website.id_ranges:
                return False
            
            test_id = str(self.config.website.id_ranges[0]['start'])
            url = self.config.website.document_url_template.format(
                base_url=self.config.website.base_url,
                id=test_id
            )
            
            response = self.session.head(url, timeout=10)
            return response.status_code < 500  # Accept redirects, not found, etc.
            
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            return False