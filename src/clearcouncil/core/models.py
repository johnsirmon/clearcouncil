"""Data models for ClearCouncil."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class DocumentMetadata:
    """Metadata extracted from document filename or content."""
    meeting_date: Optional[datetime] = None
    meeting_type: Optional[str] = None
    document_type: Optional[str] = None
    document_id: Optional[str] = None
    file_path: Optional[Path] = None
    council_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'meeting_date': self.meeting_date.isoformat() if self.meeting_date else None,
            'meeting_type': self.meeting_type,
            'document_type': self.document_type,
            'document_id': self.document_id,
            'file_path': str(self.file_path) if self.file_path else None,
            'council_id': self.council_id
        }


@dataclass
class Document:
    """Represents a processed document."""
    content: str
    metadata: DocumentMetadata
    chunks: List[str]
    
    def __post_init__(self):
        """Initialize chunks if not provided."""
        if not self.chunks and self.content:
            # Default chunking - will be overridden by processor
            self.chunks = [self.content]


@dataclass
class ProcessingResult:
    """Result of document processing operation."""
    success: bool
    document: Optional[Document] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    
    @classmethod
    def success_result(cls, document: Document, processing_time: float = None) -> 'ProcessingResult':
        """Create a successful processing result."""
        return cls(success=True, document=document, processing_time=processing_time)
    
    @classmethod
    def error_result(cls, error: str, processing_time: float = None) -> 'ProcessingResult':
        """Create an error processing result."""
        return cls(success=False, error=error, processing_time=processing_time)


@dataclass
class VotingRecord:
    """Represents a voting record from council documents."""
    case_number: Optional[str] = None
    district: Optional[str] = None
    representative: Optional[str] = None
    acres: Optional[str] = None
    owner: Optional[str] = None
    location: Optional[str] = None
    applicant: Optional[str] = None
    planning_commission_date: Optional[str] = None
    staff_recommendation: Optional[str] = None
    pc_recommendation: Optional[str] = None
    zoning_request: Optional[str] = None
    rezoning_action: Optional[str] = None
    movant: Optional[str] = None
    second: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            'Case Number': self.case_number,
            'District': self.district,
            'Representative': self.representative,
            'Acres': self.acres,
            'Owner': self.owner,
            'Location': self.location,
            'Applicant': self.applicant,
            'Planning Commission Date': self.planning_commission_date,
            'Staff Recommendation': self.staff_recommendation,
            'PC Recommendation': self.pc_recommendation,
            'Zoning Request': self.zoning_request,
            'Rezoning Action': self.rezoning_action,
            'Movant': self.movant,
            'Second': self.second
        }