"""Document parsers for ClearCouncil."""

from .voting_parser import VotingParser
from .base_parser import BaseParser

__all__ = ["VotingParser", "BaseParser"]