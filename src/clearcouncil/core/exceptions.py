"""Custom exceptions for ClearCouncil."""


class ClearCouncilError(Exception):
    """Base exception for ClearCouncil errors."""
    pass


class ConfigurationError(ClearCouncilError):
    """Raised when there's a configuration issue."""
    pass


class ProcessingError(ClearCouncilError):
    """Raised when document processing fails."""
    pass


class DownloadError(ClearCouncilError):
    """Raised when document download fails."""
    pass


class ParsingError(ClearCouncilError):
    """Raised when document parsing fails."""
    pass


class DatabaseError(ClearCouncilError):
    """Raised when vector database operations fail."""
    pass