"""Main voting analysis engine that coordinates all analysis components."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from .time_range import TimeRangeParser
from .representative_tracker import RepresentativeTracker, RepresentativeProfile, Vote
from ..core.models import VotingRecord
from ..core.exceptions import ClearCouncilError
from ..parsers.voting_parser import VotingParser
from ..config.settings import CouncilConfig

logger = logging.getLogger(__name__)


class VotingAnalyzer:
    """Main class for analyzing voting patterns and representative behavior."""
    
    def __init__(self, config: CouncilConfig):
        self.config = config
        self.time_parser = TimeRangeParser()
        self.tracker = RepresentativeTracker()
        self.voting_parser = VotingParser(config)
        
    def analyze_representative_voting(
        self, 
        representative_identifier: str, 
        time_range: str,
        comparison_reps: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze voting patterns for a specific representative.
        
        Args:
            representative_identifier: Name or district (e.g., "District 2", "John Smith")
            time_range: Natural language or specific dates
            comparison_reps: Other representatives to compare against
        
        Returns:
            Dictionary with analysis results
        """
        # Parse time range
        start_date, end_date = self.time_parser.parse_time_range(time_range)
        
        # Load voting data for the time period
        self._load_voting_data_for_period(start_date, end_date)
        
        # Get the target representative
        target_rep = self.tracker.get_representative(representative_identifier)
        if not target_rep:
            # Try district-based search
            district_reps = self.tracker.get_representatives_by_district(representative_identifier)
            if district_reps:
                target_rep = district_reps[0]  # Take the first one
            else:
                raise ClearCouncilError(f"Representative '{representative_identifier}' not found")
        
        # Get votes in time range
        votes_in_range = [
            vote for vote in target_rep.vote_history
            if vote.date and start_date <= vote.date <= end_date
        ]
        
        # Build analysis results
        analysis = {
            'representative': {
                'name': target_rep.name,
                'district': target_rep.district,
                'total_votes_in_period': len(votes_in_range),
                'motions_made': len([v for v in votes_in_range if v.vote_type == "movant"]),
                'seconds_given': len([v for v in votes_in_range if v.vote_type == "second"]),
                'participation_rate': target_rep.participation_rate
            },
            'time_period': {
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'formatted_range': self.time_parser.format_date_range(start_date, end_date)
            },
            'voting_breakdown': self._analyze_voting_breakdown(votes_in_range),
            'case_categories': self._analyze_case_categories(votes_in_range),
            'detailed_votes': [self._format_vote_for_display(vote) for vote in votes_in_range]
        }
        
        # Add comparison analysis if requested
        if comparison_reps:
            analysis['comparison'] = self._compare_representatives(
                target_rep, comparison_reps, start_date, end_date
            )
        
        return analysis
    
    def find_missing_documents(self, time_range: str) -> Dict:
        """
        Identify missing documents for a time period that should be downloaded.
        
        Returns information about what documents might be missing.
        """
        start_date, end_date = self.time_parser.parse_time_range(time_range)
        
        # Check existing documents
        pdf_dir = self.config.get_data_path("pdf")
        existing_docs = list(pdf_dir.glob("*.pdf"))
        
        # Parse dates from existing documents
        doc_dates = []
        for doc in existing_docs:
            try:
                # Extract date using the council's file pattern
                import re
                pattern = self.config.file_patterns.pdf_pattern
                match = re.match(pattern, doc.name)
                if match and 'date' in match.groupdict():
                    date_str = match.group('date')
                    doc_date = datetime.strptime(date_str, self.config.file_patterns.date_format)
                    doc_dates.append(doc_date)
            except Exception as e:
                logger.debug(f"Could not parse date from {doc.name}: {e}")
        
        # Find gaps in the date range
        missing_info = {
            'requested_period': {
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d")
            },
            'existing_documents': len(existing_docs),
            'documents_in_range': len([d for d in doc_dates if start_date <= d <= end_date]),
            'earliest_document': min(doc_dates).strftime("%Y-%m-%d") if doc_dates else None,
            'latest_document': max(doc_dates).strftime("%Y-%m-%d") if doc_dates else None,
            'recommendation': self._generate_download_recommendation(start_date, end_date, doc_dates)
        }
        
        return missing_info
    
    def get_district_analysis(self, district: str, time_range: str) -> Dict:
        """Get analysis for all representatives in a specific district."""
        start_date, end_date = self.time_parser.parse_time_range(time_range)
        self._load_voting_data_for_period(start_date, end_date)
        
        district_reps = self.tracker.get_representatives_by_district(district)
        
        if not district_reps:
            raise ClearCouncilError(f"No representatives found for district '{district}'")
        
        analysis = {
            'district': district,
            'time_period': self.time_parser.format_date_range(start_date, end_date),
            'representatives': [],
            'district_summary': {
                'total_representatives': len(district_reps),
                'total_votes': sum(rep.total_votes for rep in district_reps),
                'most_active': max(district_reps, key=lambda r: r.total_votes).name if district_reps else None
            }
        }
        
        for rep in district_reps:
            rep_votes_in_range = [
                vote for vote in rep.vote_history
                if vote.date and start_date <= vote.date <= end_date
            ]
            
            analysis['representatives'].append({
                'name': rep.name,
                'votes_in_period': len(rep_votes_in_range),
                'motions_made': len([v for v in rep_votes_in_range if v.vote_type == "movant"]),
                'seconds_given': len([v for v in rep_votes_in_range if v.vote_type == "second"]),
                'case_categories': self._analyze_case_categories(rep_votes_in_range)
            })
        
        return analysis
    
    def _load_voting_data_for_period(self, start_date: datetime, end_date: datetime) -> None:
        """Load and parse voting data for the specified time period."""
        # Clear existing data
        self.tracker = RepresentativeTracker()
        
        # Get PDF files that might contain voting data
        pdf_dir = self.config.get_data_path("pdf")
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        logger.info(f"Loading voting data from {len(pdf_files)} documents")
        
        for pdf_file in pdf_files:
            try:
                # Parse voting records from the PDF
                voting_records = self.voting_parser.parse_file(pdf_file)
                
                # Add each record to the tracker
                for record in voting_records:
                    self.tracker.add_voting_record(record)
                    
            except Exception as e:
                logger.warning(f"Failed to parse voting data from {pdf_file}: {e}")
        
        logger.info(f"Loaded data for {len(self.tracker.representatives)} representatives")
    
    def _analyze_voting_breakdown(self, votes: List[Vote]) -> Dict:
        """Analyze the breakdown of vote types."""
        breakdown = {
            'motions_made': len([v for v in votes if v.vote_type == "movant"]),
            'seconds_given': len([v for v in votes if v.vote_type == "second"]),
            'votes_for': len([v for v in votes if v.vote_type == "for"]),
            'votes_against': len([v for v in votes if v.vote_type == "against"]),
            'abstentions': len([v for v in votes if v.vote_type == "abstain"])
        }
        
        total = sum(breakdown.values())
        if total > 0:
            breakdown['percentages'] = {
                key: round((value / total) * 100, 1) 
                for key, value in breakdown.items()
            }
        
        return breakdown
    
    def _analyze_case_categories(self, votes: List[Vote]) -> Dict:
        """Analyze votes by category (rezoning, ordinance, etc.)."""
        categories = {}
        for vote in votes:
            category = vote.category
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return categories
    
    def _compare_representatives(
        self, 
        target_rep: RepresentativeProfile, 
        comparison_rep_names: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Compare target representative with others."""
        comparison_data = {
            'target': target_rep.name,
            'compared_with': [],
            'metrics_comparison': {}
        }
        
        for rep_name in comparison_rep_names:
            comp_rep = self.tracker.get_representative(rep_name)
            if comp_rep:
                comp_votes_in_range = [
                    vote for vote in comp_rep.vote_history
                    if vote.date and start_date <= vote.date <= end_date
                ]
                
                comparison_data['compared_with'].append({
                    'name': comp_rep.name,
                    'district': comp_rep.district,
                    'votes_in_period': len(comp_votes_in_range),
                    'motions_made': len([v for v in comp_votes_in_range if v.vote_type == "movant"]),
                    'case_categories': self._analyze_case_categories(comp_votes_in_range)
                })
        
        return comparison_data
    
    def _format_vote_for_display(self, vote: Vote) -> Dict:
        """Format a vote for display with readable information."""
        return {
            'case_number': vote.case_number,
            'vote_type': vote.vote_type,
            'date': vote.date.strftime("%Y-%m-%d") if vote.date else "Unknown",
            'description': vote.description or "No description available",
            'category': vote.category,
            'formatted_type': self._format_vote_type(vote.vote_type)
        }
    
    def _format_vote_type(self, vote_type: str) -> str:
        """Format vote type for user-friendly display."""
        type_mapping = {
            'movant': 'Made Motion',
            'second': 'Seconded Motion', 
            'for': 'Voted For',
            'against': 'Voted Against',
            'abstain': 'Abstained'
        }
        return type_mapping.get(vote_type, vote_type.title())
    
    def _generate_download_recommendation(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        existing_dates: List[datetime]
    ) -> str:
        """Generate recommendation for downloading missing documents."""
        if not existing_dates:
            return f"No documents found. Recommend downloading all documents for the period."
        
        docs_in_range = [d for d in existing_dates if start_date <= d <= end_date]
        
        if len(docs_in_range) == 0:
            return f"No documents found for the requested period. Recommend downloading documents."
        
        # Calculate expected number of documents (assuming monthly meetings)
        months_in_range = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        expected_docs = max(1, months_in_range)
        
        if len(docs_in_range) < expected_docs * 0.7:  # Less than 70% of expected
            return f"Found {len(docs_in_range)} documents, but expected around {expected_docs}. Consider downloading more recent documents."
        
        return f"Found {len(docs_in_range)} documents for the period. Coverage appears adequate."