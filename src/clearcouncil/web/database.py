"""Database models and operations for web interface."""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import json
import time
import threading

from ..core.models import VotingRecord, DocumentMetadata
from ..config.settings import CouncilConfig

logger = logging.getLogger(__name__)


def retry_on_database_locked(max_retries=3, delay=0.1):
    """Decorator to retry database operations on lock errors."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e) and attempt < max_retries - 1:
                        logger.warning(f"Database locked, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    raise
            return None
        return wrapper
    return decorator


class DatabaseManager:
    """Manages SQLite database for optimized data storage."""
    
    def __init__(self, db_path: str = "data/clearcouncil.db"):
        """Initialize database manager."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Representatives table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS representatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    district TEXT,
                    council_id TEXT NOT NULL,
                    first_seen DATE,
                    last_seen DATE,
                    total_votes INTEGER DEFAULT 0,
                    motions_made INTEGER DEFAULT 0,
                    seconds_given INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Voting records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS voting_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_number TEXT,
                    representative_id INTEGER,
                    district TEXT,
                    representative_name TEXT,
                    meeting_date DATE,
                    meeting_type TEXT,
                    vote_type TEXT,
                    vote_result TEXT,
                    case_category TEXT,
                    location TEXT,
                    acres REAL,
                    owner TEXT,
                    applicant TEXT,
                    zoning_request TEXT,
                    staff_recommendation TEXT,
                    pc_recommendation TEXT,
                    movant TEXT,
                    second TEXT,
                    ayes TEXT,
                    nays TEXT,
                    council_id TEXT NOT NULL,
                    document_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (representative_id) REFERENCES representatives (id)
                )
            ''')
            
            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT UNIQUE,
                    title TEXT,
                    meeting_date DATE,
                    meeting_type TEXT,
                    document_type TEXT,
                    file_path TEXT,
                    council_id TEXT NOT NULL,
                    content_summary TEXT,
                    processing_status TEXT DEFAULT 'pending',
                    processed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Council meetings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_date DATE NOT NULL,
                    meeting_type TEXT NOT NULL,
                    council_id TEXT NOT NULL,
                    attendees TEXT,
                    agenda_items TEXT,
                    votes_count INTEGER DEFAULT 0,
                    document_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (document_id)
                )
            ''')
            
            # Search cache table for faster queries
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE,
                    query_text TEXT,
                    results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_voting_records_representative 
                ON voting_records(representative_id, meeting_date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_voting_records_council_date 
                ON voting_records(council_id, meeting_date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_representatives_council 
                ON representatives(council_id, district)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_documents_council_date 
                ON documents(council_id, meeting_date)
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        try:
            yield conn
        finally:
            conn.close()
    
    @retry_on_database_locked(max_retries=5, delay=0.1)
    def insert_voting_record(self, record: VotingRecord, council_id: str, 
                           document_id: str = None, meeting_date: datetime = None) -> int:
        """Insert a voting record into the database."""
        with self._lock:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # First, get or create representative
                rep_id = self.get_or_create_representative(
                    record.representative, record.district, council_id
                )
                
                # Determine case category from zoning request
                category = self.categorize_case(record.zoning_request)
                
                cursor.execute('''
                    INSERT INTO voting_records (
                        case_number, representative_id, district, representative_name,
                        meeting_date, vote_type, vote_result, case_category,
                        location, acres, owner, applicant, zoning_request,
                        staff_recommendation, pc_recommendation, movant, second,
                        ayes, nays, council_id, document_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.case_number, rep_id, record.district, record.representative,
                    meeting_date, 'vote', record.result, category,
                    record.location, record.acres, record.owner, record.applicant,
                    record.zoning_request, record.staff_recommendation, record.pc_recommendation,
                    record.movant, record.second, record.ayes, record.nays,
                    council_id, document_id
                ))
                
                record_id = cursor.lastrowid
                
                # Update representative statistics
                self.update_representative_stats(rep_id, record)
                
                conn.commit()
                return record_id
    
    @retry_on_database_locked(max_retries=5, delay=0.1)
    def get_or_create_representative(self, name: str, district: str, council_id: str) -> int:
        """Get or create a representative record."""
        if not name:
            return None
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Try to find existing representative
            cursor.execute('''
                SELECT id FROM representatives 
                WHERE name = ? AND council_id = ? AND district = ?
            ''', (name, council_id, district))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            
            # Create new representative
            cursor.execute('''
                INSERT INTO representatives (name, district, council_id, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, district, council_id, datetime.now(), datetime.now()))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_representative_stats(self, rep_id: int, record: VotingRecord):
        """Update representative statistics."""
        if not rep_id:
            return
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update vote count
            cursor.execute('''
                UPDATE representatives 
                SET total_votes = total_votes + 1,
                    motions_made = motions_made + ?,
                    seconds_given = seconds_given + ?,
                    last_seen = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                1 if record.movant == record.representative else 0,
                1 if record.second == record.representative else 0,
                datetime.now(),
                rep_id
            ))
            
            conn.commit()
    
    def categorize_case(self, zoning_request: str) -> str:
        """Categorize a case based on zoning request."""
        if not zoning_request:
            return 'Other'
        
        zoning_request = zoning_request.lower()
        
        if 'residential' in zoning_request or 'rr' in zoning_request:
            return 'Residential'
        elif 'commercial' in zoning_request or 'business' in zoning_request:
            return 'Commercial'
        elif 'industrial' in zoning_request:
            return 'Industrial'
        elif 'conditional' in zoning_request or 'cu' in zoning_request:
            return 'Conditional Use'
        elif 'variance' in zoning_request:
            return 'Variance'
        elif 'subdivision' in zoning_request:
            return 'Subdivision'
        else:
            return 'Other'
    
    def get_representatives(self, council_id: str) -> List[Dict]:
        """Get all representatives for a council."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM representatives 
                WHERE council_id = ? 
                ORDER BY district, name
            ''', (council_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_representative_stats(self, rep_id: int, start_date: datetime = None, 
                               end_date: datetime = None) -> Dict:
        """Get statistics for a specific representative."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Base query
            base_query = '''
                SELECT 
                    COUNT(*) as total_votes,
                    SUM(CASE WHEN movant = representative_name THEN 1 ELSE 0 END) as motions_made,
                    SUM(CASE WHEN second = representative_name THEN 1 ELSE 0 END) as seconds_given,
                    case_category,
                    COUNT(CASE WHEN case_category = 'Residential' THEN 1 END) as residential_votes,
                    COUNT(CASE WHEN case_category = 'Commercial' THEN 1 END) as commercial_votes,
                    COUNT(CASE WHEN case_category = 'Industrial' THEN 1 END) as industrial_votes
                FROM voting_records 
                WHERE representative_id = ?
            '''
            
            params = [rep_id]
            
            if start_date:
                base_query += ' AND meeting_date >= ?'
                params.append(start_date)
            
            if end_date:
                base_query += ' AND meeting_date <= ?'
                params.append(end_date)
            
            cursor.execute(base_query, params)
            stats = dict(cursor.fetchone())
            
            # Get monthly activity
            cursor.execute('''
                SELECT 
                    strftime('%Y-%m', meeting_date) as month,
                    COUNT(*) as votes
                FROM voting_records 
                WHERE representative_id = ?
                {}
                GROUP BY month
                ORDER BY month
            '''.format(
                ' AND meeting_date >= ?' if start_date else '',
                ' AND meeting_date <= ?' if end_date else ''
            ), params)
            
            stats['monthly_activity'] = dict(cursor.fetchall())
            
            return stats
    
    def get_voting_records(self, council_id: str, representative_id: int = None,
                          start_date: datetime = None, end_date: datetime = None,
                          category: str = None) -> List[Dict]:
        """Get voting records with optional filtering."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT vr.*, r.name as rep_name, r.district
                FROM voting_records vr
                JOIN representatives r ON vr.representative_id = r.id
                WHERE vr.council_id = ?
            '''
            
            params = [council_id]
            
            if representative_id:
                query += ' AND vr.representative_id = ?'
                params.append(representative_id)
            
            if start_date:
                query += ' AND vr.meeting_date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND vr.meeting_date <= ?'
                params.append(end_date)
            
            if category:
                query += ' AND vr.case_category = ?'
                params.append(category)
            
            query += ' ORDER BY vr.meeting_date DESC'
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_meeting_dates(self, council_id: str) -> List[str]:
        """Get all available meeting dates for a council."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT meeting_date 
                FROM voting_records 
                WHERE council_id = ? AND meeting_date IS NOT NULL
                ORDER BY meeting_date DESC
            ''', (council_id,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def get_case_categories(self, council_id: str) -> List[str]:
        """Get all case categories for a council."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT case_category 
                FROM voting_records 
                WHERE council_id = ? AND case_category IS NOT NULL
                ORDER BY case_category
            ''', (council_id,))
            
            return [row[0] for row in cursor.fetchall()]


# Global database instance
db = DatabaseManager()


def init_db(app):
    """Initialize database for Flask app."""
    global db
    db_path = app.config.get('DATABASE_URL', 'sqlite:///clearcouncil.db')
    if db_path.startswith('sqlite:///'):
        db_path = db_path[10:]  # Remove 'sqlite:///' prefix
    
    db = DatabaseManager(db_path)
    app.db = db


def get_db_connection():
    """Get database connection for Flask app."""
    return db.get_connection()