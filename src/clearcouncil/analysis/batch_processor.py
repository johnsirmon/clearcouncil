"""Efficient batch processing for voting analysis with automatic document discovery."""

import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
import re

from ..config.settings import CouncilConfig
from ..core.models import VotingRecord
from ..core.exceptions import ClearCouncilError
from ..downloaders.pdf_downloader import PDFDownloader
from ..parsers.voting_parser import VotingParser
from ..processors.pdf_processor import PDFProcessor
from .time_range import TimeRangeParser
from .representative_tracker import RepresentativeTracker

logger = logging.getLogger(__name__)


class BatchVotingProcessor:
    """Efficiently processes voting data with automatic document discovery and parallel processing."""
    
    def __init__(self, config: CouncilConfig):
        self.config = config
        self.downloader = PDFDownloader(config)
        self.parser = VotingParser(config)
        self.pdf_processor = PDFProcessor(config)
        self.time_parser = TimeRangeParser()
        
    async def get_voting_data_for_period(
        self, 
        time_range: str,
        download_missing: bool = True,
        representative_filter: Optional[str] = None
    ) -> Tuple[RepresentativeTracker, Dict]:
        """
        Efficiently get all voting data for a time period.
        
        Args:
            time_range: Natural language time range
            download_missing: Whether to download missing documents
            representative_filter: Optional filter for specific representative/district
            
        Returns:
            Tuple of (RepresentativeTracker, metadata about the operation)
        """
        start_date, end_date = self.time_parser.parse_time_range(time_range)
        
        logger.info(f"Processing voting data for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Step 1: Discover existing documents in date range
        existing_docs = self._discover_documents_in_range(start_date, end_date)
        
        # Step 2: Download missing documents if requested
        downloaded_docs = []
        if download_missing:
            downloaded_docs = await self._download_missing_documents(start_date, end_date, existing_docs)
        
        # Step 3: Process all relevant documents in parallel
        all_docs = existing_docs + downloaded_docs
        
        if not all_docs:
            logger.warning(f"No documents found for time range {time_range}")
            return RepresentativeTracker(), {
                'time_range': time_range,
                'documents_processed': 0,
                'representatives_found': 0,
                'votes_extracted': 0
            }
        
        # Step 4: Parallel processing of documents
        tracker = await self._process_documents_parallel(all_docs, representative_filter)
        
        # Step 5: Generate metadata
        metadata = {
            'time_range': time_range,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'existing_documents': len(existing_docs),
            'downloaded_documents': len(downloaded_docs),
            'total_documents_processed': len(all_docs),
            'representatives_found': len(tracker.representatives),
            'total_votes_extracted': sum(len(rep.vote_history) for rep in tracker.representatives.values()),
            'document_date_range': self._get_document_date_range(all_docs)
        }
        
        logger.info(f"Processed {metadata['total_documents_processed']} documents, "
                   f"found {metadata['representatives_found']} representatives, "
                   f"extracted {metadata['total_votes_extracted']} votes")
        
        return tracker, metadata
    
    def _discover_documents_in_range(self, start_date: datetime, end_date: datetime) -> List[Path]:
        """Discover existing documents that fall within the date range."""
        pdf_dir = self.config.get_data_path("pdf")
        all_pdfs = list(pdf_dir.glob("*.pdf"))
        
        relevant_docs = []
        pattern = self.config.file_patterns.pdf_pattern
        date_format = self.config.file_patterns.date_format
        
        for pdf_file in all_pdfs:
            try:
                match = re.match(pattern, pdf_file.name)
                if match and 'date' in match.groupdict():
                    date_str = match.group('date')
                    doc_date = datetime.strptime(date_str, date_format)
                    
                    if start_date <= doc_date <= end_date:
                        relevant_docs.append(pdf_file)
                        
            except Exception as e:
                logger.debug(f"Could not parse date from {pdf_file.name}: {e}")
        
        logger.info(f"Found {len(relevant_docs)} existing documents in date range")
        return relevant_docs
    
    async def _download_missing_documents(
        self, 
        start_date: datetime, 
        end_date: datetime,
        existing_docs: List[Path]
    ) -> List[Path]:
        """Download documents that might be missing for the date range."""
        # Calculate expected document IDs based on date range and existing patterns
        existing_ids = self._extract_document_ids(existing_docs)
        
        # Estimate missing document IDs
        potential_ids = self._estimate_missing_document_ids(start_date, end_date, existing_ids)
        
        if not potential_ids:
            logger.info("No missing documents identified for download")
            return []
        
        logger.info(f"Attempting to download {len(potential_ids)} potentially missing documents")
        
        # Download in parallel (but respect rate limits)
        downloaded_docs = []
        semaphore = asyncio.Semaphore(3)  # Limit concurrent downloads
        
        async def download_single(doc_id):
            async with semaphore:
                try:
                    # Use a small delay to be respectful to the server
                    await asyncio.sleep(0.5)
                    
                    # Download in thread pool since downloader is synchronous
                    loop = asyncio.get_event_loop()
                    file_path = await loop.run_in_executor(
                        None, self.downloader.download_document, str(doc_id)
                    )
                    return file_path
                except Exception as e:
                    logger.debug(f"Failed to download document {doc_id}: {e}")
                    return None
        
        # Execute downloads
        tasks = [download_single(doc_id) for doc_id in potential_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful downloads
        for result in results:
            if isinstance(result, Path) and result.exists():
                downloaded_docs.append(result)
        
        logger.info(f"Successfully downloaded {len(downloaded_docs)} new documents")
        return downloaded_docs
    
    async def _process_documents_parallel(
        self, 
        documents: List[Path], 
        representative_filter: Optional[str] = None
    ) -> RepresentativeTracker:
        """Process documents in parallel to extract voting data."""
        tracker = RepresentativeTracker()
        
        # Process documents in parallel using thread pool
        max_workers = min(self.config.processing.max_workers, len(documents))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all parsing tasks
            future_to_doc = {
                executor.submit(self._extract_voting_data_from_document, doc): doc 
                for doc in documents
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_doc):
                doc = future_to_doc[future]
                try:
                    voting_records = future.result()
                    
                    # Filter by representative if specified
                    if representative_filter:
                        voting_records = self._filter_records_by_representative(
                            voting_records, representative_filter
                        )
                    
                    # Add to tracker
                    for record in voting_records:
                        tracker.add_voting_record(record)
                        
                    logger.debug(f"Processed {doc.name}: {len(voting_records)} voting records")
                    
                except Exception as e:
                    logger.warning(f"Failed to process {doc}: {e}")
        
        return tracker
    
    def _extract_voting_data_from_document(self, doc_path: Path) -> List[VotingRecord]:
        """Extract voting data from a single document."""
        try:
            # Parse voting records using the voting parser
            return self.parser.parse_file(doc_path)
        except Exception as e:
            logger.warning(f"Failed to parse voting data from {doc_path}: {e}")
            return []
    
    def _extract_document_ids(self, documents: List[Path]) -> Set[int]:
        """Extract document IDs from existing document filenames."""
        ids = set()
        pattern = self.config.file_patterns.pdf_pattern
        
        for doc in documents:
            try:
                match = re.match(pattern, doc.name)
                if match and 'document_id' in match.groupdict():
                    doc_id = int(match.group('document_id'))
                    ids.add(doc_id)
            except (ValueError, AttributeError):
                continue
        
        return ids
    
    def _estimate_missing_document_ids(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        existing_ids: Set[int]
    ) -> List[int]:
        """Estimate which document IDs might be missing for the date range."""
        if not existing_ids:
            # If no existing documents, use configured ranges
            for range_config in self.config.website.id_ranges:
                if range_config['start'] <= range_config['end']:
                    return list(range(range_config['start'], min(range_config['end'] + 1, range_config['start'] + 50)))
            return []
        
        # Find the range of existing IDs
        min_id = min(existing_ids)
        max_id = max(existing_ids)
        
        # Estimate based on date range (assume roughly monthly meetings)
        months_in_range = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        estimated_docs_needed = max(1, months_in_range)
        
        # Look for gaps in the existing IDs and extend range if needed
        potential_ids = []
        
        # Check for gaps in existing range
        for doc_id in range(min_id, max_id + 1):
            if doc_id not in existing_ids:
                potential_ids.append(doc_id)
        
        # Extend beyond max_id if we need more documents
        if len(potential_ids) < estimated_docs_needed:
            extension_size = min(20, estimated_docs_needed - len(potential_ids))
            potential_ids.extend(range(max_id + 1, max_id + 1 + extension_size))
        
        return potential_ids[:50]  # Limit to avoid excessive downloads
    
    def _filter_records_by_representative(
        self, 
        records: List[VotingRecord], 
        representative_filter: str
    ) -> List[VotingRecord]:
        """Filter voting records by representative name or district."""
        filtered = []
        filter_lower = representative_filter.lower()
        
        for record in records:
            # Check representative name
            if record.representative and filter_lower in record.representative.lower():
                filtered.append(record)
                continue
            
            # Check district
            if record.district and filter_lower in record.district.lower():
                filtered.append(record)
                continue
        
        return filtered
    
    def _get_document_date_range(self, documents: List[Path]) -> Dict:
        """Get the actual date range of processed documents."""
        dates = []
        pattern = self.config.file_patterns.pdf_pattern
        date_format = self.config.file_patterns.date_format
        
        for doc in documents:
            try:
                match = re.match(pattern, doc.name)
                if match and 'date' in match.groupdict():
                    date_str = match.group('date')
                    doc_date = datetime.strptime(date_str, date_format)
                    dates.append(doc_date)
            except Exception:
                continue
        
        if dates:
            return {
                'earliest': min(dates).strftime('%Y-%m-%d'),
                'latest': max(dates).strftime('%Y-%m-%d'),
                'document_count': len(dates)
            }
        
        return {'earliest': None, 'latest': None, 'document_count': 0}