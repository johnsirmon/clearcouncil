"""Enhanced data processing pipeline for faster web access."""

import logging
import asyncio
import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
from dataclasses import dataclass

from ..core.models import VotingRecord, Document, DocumentMetadata, ProcessingResult
from ..processors.pdf_processor import PDFProcessor
from ..parsers.voting_parser import VotingParser
from ..config.settings import CouncilConfig
from .database import DatabaseManager

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStatus:
    """Status of data processing operations."""
    total_documents: int
    processed_documents: int
    failed_documents: int
    total_records: int
    processing_time: float
    errors: List[str]


class EnhancedDataProcessor:
    """Enhanced data processor optimized for web interface."""
    
    def __init__(self, config: CouncilConfig, db_manager: DatabaseManager):
        """Initialize enhanced data processor."""
        self.config = config
        self.db = db_manager
        self.pdf_processor = PDFProcessor(config)
        self.voting_parser = VotingParser(config)
        
    async def process_all_documents(self, force_reprocess: bool = False) -> ProcessingStatus:
        """Process all PDF documents with parallel processing."""
        start_time = datetime.now()
        
        # Get all PDF files
        pdf_dir = self.config.get_data_path("pdf")
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return ProcessingStatus(0, 0, 0, 0, 0, ["No PDF files found"])
        
        # Filter out already processed files if not forcing reprocess
        if not force_reprocess:
            pdf_files = await self._filter_unprocessed_files(pdf_files)
        
        logger.info(f"Processing {len(pdf_files)} PDF files...")
        
        # Process files in parallel
        results = []
        errors = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.processing.max_workers) as executor:
            # Submit all processing tasks
            future_to_file = {
                executor.submit(self._process_single_document, pdf_file): pdf_file
                for pdf_file in pdf_files
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                pdf_file = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if not result.success:
                        errors.append(f"Failed to process {pdf_file.name}: {result.error}")
                        
                except Exception as e:
                    errors.append(f"Exception processing {pdf_file.name}: {str(e)}")
                    logger.error(f"Exception processing {pdf_file.name}", exc_info=True)
        
        # Calculate statistics
        successful_results = [r for r in results if r.success]
        failed_count = len(results) - len(successful_results)
        
        # Count total voting records
        total_records = 0
        for result in successful_results:
            if hasattr(result, 'voting_records_count'):
                total_records += result.voting_records_count
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Processing complete: {len(successful_results)}/{len(pdf_files)} files processed successfully")
        
        return ProcessingStatus(
            total_documents=len(pdf_files),
            processed_documents=len(successful_results),
            failed_documents=failed_count,
            total_records=total_records,
            processing_time=processing_time,
            errors=errors
        )
    
    async def _filter_unprocessed_files(self, pdf_files: List[Path]) -> List[Path]:
        """Filter out files that have already been processed."""
        unprocessed_files = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            for pdf_file in pdf_files:
                # Check if document exists in database
                cursor.execute('''
                    SELECT id, processing_status FROM documents 
                    WHERE file_path = ? AND council_id = ?
                ''', (str(pdf_file), self.config.identifier))
                
                result = cursor.fetchone()
                
                if not result or result[1] != 'completed':
                    unprocessed_files.append(pdf_file)
        
        return unprocessed_files
    
    def _process_single_document(self, pdf_file: Path) -> ProcessingResult:
        """Process a single PDF document."""
        try:
            # Extract document metadata from filename
            metadata = self._extract_metadata_from_filename(pdf_file)
            
            # Record document in database
            document_id = self._record_document(pdf_file, metadata)
            
            # Process PDF content
            processing_result = self.pdf_processor.process_with_result(pdf_file)
            
            if not processing_result.success:
                self._update_document_status(document_id, 'failed', processing_result.error)
                return processing_result
            
            # Parse voting records
            voting_records = self.voting_parser.parse_text(processing_result.document.content)
            
            # Store voting records in database
            records_count = self._store_voting_records(
                voting_records, document_id, metadata
            )
            
            # Update document status
            self._update_document_status(document_id, 'completed')
            
            # Add records count to result
            processing_result.voting_records_count = records_count
            
            logger.info(f"Processed {pdf_file.name}: {records_count} voting records extracted")
            
            return processing_result
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {e}")
            return ProcessingResult.error_result(str(e))
    
    def _extract_metadata_from_filename(self, pdf_file: Path) -> DocumentMetadata:
        """Extract metadata from PDF filename."""
        filename = pdf_file.name
        
        # Parse filename pattern (e.g., "2023-04-15 County Council - Full Minutes-2001.pdf")
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        type_pattern = r'(County Council|Planning Commission|Board of Zoning Appeals|Finance & Operations Committee)'
        doc_type_pattern = r'(Full Minutes|Agenda|Summary)'
        id_pattern = r'-(\d+)\.pdf$'
        
        # Extract date
        date_match = re.search(date_pattern, filename)
        meeting_date = None
        if date_match:
            try:
                meeting_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
            except ValueError:
                pass
        
        # Extract meeting type
        type_match = re.search(type_pattern, filename)
        meeting_type = type_match.group(1) if type_match else None
        
        # Extract document type
        doc_type_match = re.search(doc_type_pattern, filename)
        document_type = doc_type_match.group(1) if doc_type_match else None
        
        # Extract document ID
        id_match = re.search(id_pattern, filename)
        document_id = id_match.group(1) if id_match else None
        
        return DocumentMetadata(
            meeting_date=meeting_date,
            meeting_type=meeting_type,
            document_type=document_type,
            document_id=document_id,
            file_path=pdf_file,
            council_id=self.config.identifier
        )
    
    def _record_document(self, pdf_file: Path, metadata: DocumentMetadata) -> str:
        """Record document in database."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if document already exists
            cursor.execute('''
                SELECT id FROM documents 
                WHERE file_path = ? AND council_id = ?
            ''', (str(pdf_file), self.config.identifier))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            
            # Insert new document
            cursor.execute('''
                INSERT INTO documents (
                    document_id, title, meeting_date, meeting_type, 
                    document_type, file_path, council_id, processing_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.document_id,
                pdf_file.stem,
                metadata.meeting_date,
                metadata.meeting_type,
                metadata.document_type,
                str(pdf_file),
                self.config.identifier,
                'processing'
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def _update_document_status(self, document_id: str, status: str, error: str = None):
        """Update document processing status."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE documents 
                SET processing_status = ?, processed_at = ?
                WHERE id = ?
            ''', (status, datetime.now(), document_id))
            
            conn.commit()
    
    def _store_voting_records(self, voting_records: List[VotingRecord], 
                            document_id: str, metadata: DocumentMetadata) -> int:
        """Store voting records in database."""
        count = 0
        
        for record in voting_records:
            try:
                self.db.insert_voting_record(
                    record, 
                    self.config.identifier,
                    document_id,
                    metadata.meeting_date
                )
                count += 1
            except Exception as e:
                logger.error(f"Error storing voting record: {e}")
                continue
        
        return count
    
    async def update_representative_stats(self) -> Dict:
        """Update representative statistics for faster access."""
        logger.info("Updating representative statistics...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all representatives
            cursor.execute('''
                SELECT id, name, district, council_id FROM representatives
                WHERE council_id = ?
            ''', (self.config.identifier,))
            
            representatives = cursor.fetchall()
            updated_count = 0
            
            for rep in representatives:
                rep_id, name, district, council_id = rep
                
                # Calculate statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_votes,
                        SUM(CASE WHEN movant = ? THEN 1 ELSE 0 END) as motions_made,
                        SUM(CASE WHEN second = ? THEN 1 ELSE 0 END) as seconds_given,
                        MIN(meeting_date) as first_vote,
                        MAX(meeting_date) as last_vote
                    FROM voting_records 
                    WHERE representative_name = ? AND council_id = ?
                ''', (name, name, name, council_id))
                
                stats = cursor.fetchone()
                
                if stats:
                    # Update representative record
                    cursor.execute('''
                        UPDATE representatives 
                        SET total_votes = ?,
                            motions_made = ?,
                            seconds_given = ?,
                            first_seen = COALESCE(?, first_seen),
                            last_seen = COALESCE(?, last_seen),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (
                        stats[0], stats[1], stats[2],
                        stats[3], stats[4], rep_id
                    ))
                    
                    updated_count += 1
            
            conn.commit()
        
        logger.info(f"Updated statistics for {updated_count} representatives")
        return {"updated_representatives": updated_count}
    
    async def create_search_indexes(self) -> Dict:
        """Create search indexes for faster queries."""
        logger.info("Creating search indexes...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create additional indexes if they don't exist
            indexes = [
                ('idx_voting_records_date', 'CREATE INDEX IF NOT EXISTS idx_voting_records_date ON voting_records(meeting_date DESC)'),
                ('idx_voting_records_category', 'CREATE INDEX IF NOT EXISTS idx_voting_records_category ON voting_records(case_category)'),
                ('idx_voting_records_result', 'CREATE INDEX IF NOT EXISTS idx_voting_records_result ON voting_records(vote_result)'),
                ('idx_representatives_name', 'CREATE INDEX IF NOT EXISTS idx_representatives_name ON representatives(name)'),
                ('idx_documents_date', 'CREATE INDEX IF NOT EXISTS idx_documents_date ON documents(meeting_date DESC)'),
                ('idx_documents_status', 'CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status)')
            ]
            
            created_count = 0
            for index_name, sql in indexes:
                try:
                    cursor.execute(sql)
                    created_count += 1
                except Exception as e:
                    logger.error(f"Error creating index {index_name}: {e}")
            
            conn.commit()
        
        logger.info(f"Created {created_count} search indexes")
        return {"created_indexes": created_count}
    
    async def optimize_database(self) -> Dict:
        """Optimize database for better performance."""
        logger.info("Optimizing database...")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Analyze tables for query optimization
            cursor.execute('ANALYZE')
            
            # Vacuum to reclaim space
            cursor.execute('VACUUM')
            
            # Update statistics
            cursor.execute('PRAGMA optimize')
            
            conn.commit()
        
        logger.info("Database optimization complete")
        return {"optimization_complete": True}
    
    def get_processing_status(self) -> Dict:
        """Get current processing status."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get document counts by status
            cursor.execute('''
                SELECT processing_status, COUNT(*) 
                FROM documents 
                WHERE council_id = ?
                GROUP BY processing_status
            ''', (self.config.identifier,))
            
            status_counts = dict(cursor.fetchall())
            
            # Get total voting records
            cursor.execute('''
                SELECT COUNT(*) FROM voting_records 
                WHERE council_id = ?
            ''', (self.config.identifier,))
            
            total_records = cursor.fetchone()[0]
            
            # Get representative count
            cursor.execute('''
                SELECT COUNT(*) FROM representatives 
                WHERE council_id = ?
            ''', (self.config.identifier,))
            
            total_representatives = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute('''
                SELECT MIN(meeting_date), MAX(meeting_date)
                FROM voting_records 
                WHERE council_id = ? AND meeting_date IS NOT NULL
            ''', (self.config.identifier,))
            
            date_range = cursor.fetchone()
            
            return {
                "document_status": status_counts,
                "total_voting_records": total_records,
                "total_representatives": total_representatives,
                "date_range": {
                    "start": date_range[0] if date_range[0] else None,
                    "end": date_range[1] if date_range[1] else None
                },
                "last_updated": datetime.now().isoformat()
            }


class DataProcessingManager:
    """Manager for coordinating data processing operations."""
    
    def __init__(self, council_id: str):
        """Initialize data processing manager."""
        from ..config.settings import load_council_config
        
        self.council_id = council_id
        self.config = load_council_config(council_id)
        self.db = DatabaseManager()
        self.processor = EnhancedDataProcessor(self.config, self.db)
    
    async def full_processing_pipeline(self, force_reprocess: bool = False) -> Dict:
        """Run the complete data processing pipeline."""
        logger.info(f"Starting full processing pipeline for {self.council_id}")
        
        pipeline_start = datetime.now()
        results = {}
        
        try:
            # Step 1: Process all documents
            logger.info("Step 1: Processing documents...")
            processing_status = await self.processor.process_all_documents(force_reprocess)
            results["document_processing"] = processing_status
            
            # Step 2: Update representative statistics
            logger.info("Step 2: Updating representative statistics...")
            stats_result = await self.processor.update_representative_stats()
            results["statistics_update"] = stats_result
            
            # Step 3: Create search indexes
            logger.info("Step 3: Creating search indexes...")
            index_result = await self.processor.create_search_indexes()
            results["index_creation"] = index_result
            
            # Step 4: Optimize database
            logger.info("Step 4: Optimizing database...")
            optimization_result = await self.processor.optimize_database()
            results["database_optimization"] = optimization_result
            
            # Calculate total processing time
            total_time = (datetime.now() - pipeline_start).total_seconds()
            results["total_processing_time"] = total_time
            results["success"] = True
            
            logger.info(f"Full processing pipeline completed in {total_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error in processing pipeline: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def get_status(self) -> Dict:
        """Get current processing status."""
        return self.processor.get_processing_status()