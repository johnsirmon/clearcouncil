"""PDF document downloader."""

import re
import requests
from pathlib import Path
from typing import Optional, List
import logging
import time
from datetime import datetime
import hashlib

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
        
        # Add retry logic and rate limiting
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.rate_limit_delay = 0.5  # seconds between requests
        
        # Track download statistics
        self.download_stats = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def download_document(self, document_id: str, save_path: Optional[Path] = None, force: bool = False) -> Path:
        """Download a single PDF document by ID."""
        self.download_stats['attempted'] += 1
        
        # Build URL from template
        url = self.config.website.document_url_template.format(
            base_url=self.config.website.base_url,
            id=document_id
        )
        
        # Determine save directory
        if save_path is None:
            save_path = self.config.get_data_path("pdf")
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        time.sleep(self.rate_limit_delay)
        
        for attempt in range(self.max_retries):
            try:
                # First, make a HEAD request to get filename from headers
                response = self.session.head(url, timeout=30)
                response.raise_for_status()
                
                filename = self._extract_filename_from_response(response, document_id)
                file_path = save_path / filename
                
                # Check if file already exists and is valid (unless force=True)
                if not force and file_path.exists() and self._is_valid_existing_file(file_path):
                    logger.debug(f"File {filename} already exists and is valid, skipping")
                    self.download_stats['skipped'] += 1
                    return file_path
                
                # Download the actual file
                response = self.session.get(url, timeout=60)
                response.raise_for_status()
                
                # Verify it's actually a PDF
                if not self._is_pdf_content(response.content):
                    raise DownloadError(f"Downloaded content for ID {document_id} is not a valid PDF")
                
                # Save to file with atomic write
                temp_path = file_path.with_suffix('.tmp')
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify the downloaded file
                if self._is_valid_pdf_file(temp_path):
                    temp_path.rename(file_path)
                    logger.debug(f"Downloaded {filename} ({len(response.content):,} bytes)")
                    self.download_stats['successful'] += 1
                    return file_path
                else:
                    temp_path.unlink()
                    raise DownloadError(f"Downloaded file for ID {document_id} failed validation")
                
            except requests.RequestException as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed for document {document_id}: {e}. Retrying...")
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    self.download_stats['failed'] += 1
                    raise DownloadError(f"Failed to download document {document_id} after {self.max_retries} attempts: {e}")
            except Exception as e:
                self.download_stats['failed'] += 1
                raise DownloadError(f"Unexpected error downloading document {document_id}: {e}")
        
        self.download_stats['failed'] += 1
        raise DownloadError(f"Failed to download document {document_id} after all retry attempts")
    
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
        return content.startswith(b'%PDF-') and len(content) > 1000  # Basic size check
    
    def _is_valid_existing_file(self, file_path: Path) -> bool:
        """Check if an existing file is valid and doesn't need re-downloading."""
        try:
            if not file_path.exists():
                return False
            
            # Check file size (should be at least 1KB)
            if file_path.stat().st_size < 1000:
                return False
            
            # Check if it's a valid PDF
            return self._is_valid_pdf_file(file_path)
        except Exception:
            return False
    
    def _is_valid_pdf_file(self, file_path: Path) -> bool:
        """Check if a file on disk is a valid PDF."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(100)
                return header.startswith(b'%PDF-')
        except Exception:
            return False
    
    def get_download_stats(self) -> dict:
        """Get download statistics."""
        return self.download_stats.copy()
    
    def reset_stats(self):
        """Reset download statistics."""
        self.download_stats = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def download_recent_documents(self, days: int = 30, save_path: Optional[Path] = None) -> List[Path]:
        """Download documents from the last N days based on ID patterns."""
        # This is a simplified approach - in reality, you'd want to map IDs to dates
        # For now, we'll download the latest range
        if not self.config.website.id_ranges:
            raise DownloadError("No ID ranges configured")
        
        # Use the last (most recent) range
        latest_range = self.config.website.id_ranges[-1]
        
        # Download the last 50 documents from the range as an approximation
        end_id = latest_range['end']
        start_id = max(latest_range['start'], end_id - 50)
        
        logger.info(f"Downloading recent documents (IDs {start_id}-{end_id})")
        return self.download_range(start_id, end_id, save_path)
    
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