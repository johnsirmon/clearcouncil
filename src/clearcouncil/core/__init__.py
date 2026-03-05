"""Core components for ClearCouncil."""

from .models import Document, DocumentMetadata, ProcessingResult
from .exceptions import ClearCouncilError, ProcessingError, ConfigurationError

try:
    from .database import VectorDatabase
except ImportError:
    pass

__all__ = [
    "Document",
    "DocumentMetadata", 
    "ProcessingResult",
    "ClearCouncilError",
    "ProcessingError",
    "ConfigurationError",
    "VectorDatabase",
]