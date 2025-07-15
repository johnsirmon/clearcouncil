"""Representative tracking and voting history management."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict
import logging
from fuzzywuzzy import fuzz, process

from ..core.models import VotingRecord

logger = logging.getLogger(__name__)


@dataclass
class Vote:
    """Represents a single vote by a representative."""
    case_number: str
    representative: str
    district: str
    vote_type: str  # "movant", "second", "for", "against", "abstain"
    date: Optional[datetime] = None
    description: str = ""
    category: str = ""  # "rezoning", "ordinance", "budget", etc.


@dataclass
class RepresentativeProfile:
    """Profile information for a representative."""
    name: str
    district: str
    total_votes: int = 0
    votes_for: int = 0
    votes_against: int = 0
    abstentions: int = 0
    motions_made: int = 0
    seconds_given: int = 0
    vote_history: List[Vote] = None
    
    def __post_init__(self):
        if self.vote_history is None:
            self.vote_history = []
    
    @property
    def participation_rate(self) -> float:
        """Calculate participation rate (non-abstentions / total)."""
        if self.total_votes == 0:
            return 0.0
        return (self.total_votes - self.abstentions) / self.total_votes
    
    @property
    def agreement_rate_with(self, other: 'RepresentativeProfile') -> float:
        """Calculate agreement rate with another representative."""
        # This would need vote-by-vote comparison
        # Placeholder for now
        return 0.0


class RepresentativeTracker:
    """Tracks representatives and their voting patterns."""
    
    def __init__(self):
        self.representatives: Dict[str, RepresentativeProfile] = {}
        self.votes_by_case: Dict[str, List[Vote]] = defaultdict(list)
        self.votes_by_date: Dict[str, List[Vote]] = defaultdict(list)
    
    def add_voting_record(self, record: VotingRecord) -> None:
        """Add a voting record and extract representative votes."""
        # Accept records with either case numbers or basic voting info (movant + result)
        if not record.case_number and not (record.movant and record.result):
            logger.warning("Voting record missing case number and basic voting info, skipping")
            return
        
        # Extract votes from the record
        votes = self._extract_votes_from_record(record)
        
        for vote in votes:
            self._add_vote(vote)
    
    def _extract_votes_from_record(self, record: VotingRecord) -> List[Vote]:
        """Extract individual votes from a voting record."""
        votes = []
        
        # Create a unique identifier for records without case numbers
        case_id = record.case_number or f"vote_{record.movant}_{record.result}_{len(self.votes_by_case)}"
        
        # Create base vote info
        base_info = {
            'case_number': case_id,
            'date': None,  # Would need to be parsed from record
            'description': record.result or record.rezoning_action or record.zoning_request or '',
            'category': self._categorize_vote(record)
        }
        
        # Extract movant (person who made the motion)
        if record.movant:
            votes.append(Vote(
                representative=record.representative or record.movant,
                district=record.district or '',
                vote_type="movant",
                **base_info
            ))
        
        # Extract second (person who seconded the motion)
        if record.second:
            # Try to match second to a known representative
            # For now, create a vote without district info
            votes.append(Vote(
                representative=record.second,
                district="Unknown",  # Would need district mapping
                vote_type="second",
                **base_info
            ))
        
        return votes
    
    def _categorize_vote(self, record: VotingRecord) -> str:
        """Categorize the type of vote based on the record content."""
        if record.zoning_request or record.rezoning_action:
            return "rezoning"
        elif "ordinance" in (record.rezoning_action or "").lower():
            return "ordinance"
        elif "budget" in (record.rezoning_action or "").lower():
            return "budget"
        else:
            return "other"
    
    def _add_vote(self, vote: Vote) -> None:
        """Add a vote to the tracking system."""
        # Validate representative name
        if not self._is_valid_representative_name(vote.representative):
            logger.warning(f"Skipping invalid representative name: '{vote.representative}'")
            return
            
        # Update representative profile
        if vote.representative not in self.representatives:
            self.representatives[vote.representative] = RepresentativeProfile(
                name=vote.representative,
                district=vote.district
            )
        
        rep = self.representatives[vote.representative]
        rep.vote_history.append(vote)
        rep.total_votes += 1
        
        # Update vote counts based on type
        if vote.vote_type == "movant":
            rep.motions_made += 1
        elif vote.vote_type == "second":
            rep.seconds_given += 1
        elif vote.vote_type == "for":
            rep.votes_for += 1
        elif vote.vote_type == "against":
            rep.votes_against += 1
        elif vote.vote_type == "abstain":
            rep.abstentions += 1
        
        # Add to case and date indexes
        self.votes_by_case[vote.case_number].append(vote)
        if vote.date:
            date_key = vote.date.strftime("%Y-%m-%d")
            self.votes_by_date[date_key].append(vote)
    
    def get_representative(self, name_or_district: str, fuzzy_threshold: int = 70) -> Optional[RepresentativeProfile]:
        """
        Get representative by name or district with fuzzy matching support.
        
        Args:
            name_or_district: Name or district to search for
            fuzzy_threshold: Minimum similarity score (0-100) for fuzzy matching
            
        Returns:
            RepresentativeProfile if found, None otherwise
        """
        # Try exact name match first
        if name_or_district in self.representatives:
            return self.representatives[name_or_district]
        
        # Try exact district match
        for rep in self.representatives.values():
            if rep.district.lower() == name_or_district.lower():
                return rep
        
        # Try partial name matching (last name only)
        search_lower = name_or_district.lower().strip()
        for rep_name, rep in self.representatives.items():
            # Skip invalid entries
            if ":" in rep_name or len(rep_name.strip()) < 2:
                continue
                
            # Check if search term is contained in the full name
            if search_lower in rep_name.lower():
                logger.info(f"Found partial match: '{name_or_district}' -> '{rep_name}'")
                return rep
            
            # Check if it matches the last name
            name_parts = rep_name.lower().split()
            if name_parts and search_lower == name_parts[-1]:
                logger.info(f"Found last name match: '{name_or_district}' -> '{rep_name}'")
                return rep
        
        # Try fuzzy name matching
        representative_names = [name for name in self.representatives.keys() 
                               if ":" not in name and len(name.strip()) >= 2]
        if representative_names:
            # Find the best match using fuzzy string matching
            best_match, score = process.extractOne(
                name_or_district, 
                representative_names,
                scorer=fuzz.ratio
            )
            
            if score >= fuzzy_threshold:
                logger.info(f"Found fuzzy match: '{name_or_district}' -> '{best_match}' (score: {score})")
                return self.representatives[best_match]
        
        # Try fuzzy district matching
        districts = [rep.district for rep in self.representatives.values() 
                    if rep.district and rep.district.strip()]
        if districts:
            best_district_match, district_score = process.extractOne(
                name_or_district,
                districts,
                scorer=fuzz.ratio
            )
            
            if district_score >= fuzzy_threshold:
                for rep in self.representatives.values():
                    if rep.district == best_district_match:
                        logger.info(f"Found fuzzy district match: '{name_or_district}' -> '{best_district_match}' (score: {district_score})")
                        return rep
        
        return None
    
    def get_similar_representatives(self, name_or_district: str, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Get a list of similar representative names with similarity scores.
        
        Args:
            name_or_district: Name or district to search for
            limit: Maximum number of suggestions to return
            
        Returns:
            List of tuples (representative_name, similarity_score)
        """
        # Filter out invalid entries
        representative_names = [name for name in self.representatives.keys() 
                               if ":" not in name and len(name.strip()) >= 2]
        if not representative_names:
            return []
        
        # Get fuzzy matches with scores
        matches = process.extract(
            name_or_district,
            representative_names,
            scorer=fuzz.ratio,
            limit=limit
        )
        
        return matches
    
    def get_representatives_by_district(self, district: str) -> List[RepresentativeProfile]:
        """Get all representatives for a district."""
        return [
            rep for rep in self.representatives.values() 
            if rep.district.lower() == district.lower()
        ]
    
    def get_votes_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Vote]:
        """Get all votes within a date range."""
        votes = []
        for rep in self.representatives.values():
            for vote in rep.vote_history:
                if vote.date and start_date <= vote.date <= end_date:
                    votes.append(vote)
        return votes
    
    def get_representative_comparison(self, rep_names: List[str]) -> Dict:
        """Compare multiple representatives' voting patterns."""
        comparison = {
            'representatives': [],
            'common_cases': [],
            'agreement_matrix': {}
        }
        
        reps = [self.get_representative(name) for name in rep_names]
        reps = [rep for rep in reps if rep is not None]
        
        if len(reps) < 2:
            return comparison
        
        comparison['representatives'] = reps
        
        # Find cases where multiple representatives voted
        case_participation = defaultdict(list)
        for rep in reps:
            for vote in rep.vote_history:
                case_participation[vote.case_number].append((rep.name, vote))
        
        # Find common cases (where 2+ representatives participated)
        common_cases = {
            case: votes for case, votes in case_participation.items() 
            if len(votes) >= 2
        }
        comparison['common_cases'] = list(common_cases.keys())
        
        return comparison
    
    def get_voting_summary(self) -> Dict:
        """Get overall voting summary statistics."""
        return {
            'total_representatives': len(self.representatives),
            'total_cases': len(self.votes_by_case),
            'most_active_representative': max(
                self.representatives.values(), 
                key=lambda r: r.total_votes,
                default=None
            ),
            'representatives_by_district': self._group_by_district()
        }
    
    def _group_by_district(self) -> Dict[str, List[str]]:
        """Group representatives by district."""
        by_district = defaultdict(list)
        for rep in self.representatives.values():
            by_district[rep.district].append(rep.name)
        return dict(by_district)
    
    def _is_valid_representative_name(self, name: str) -> bool:
        """Check if a representative name is valid."""
        if not name or not isinstance(name, str):
            return False
        
        name = name.strip()
        
        # Reject names that are too short
        if len(name) < 2:
            return False
        
        # Reject names that contain colons (parsing artifacts)
        if ":" in name:
            return False
        
        # Reject names that are all uppercase with special characters (likely parsing errors)
        if name.isupper() and any(char in name for char in ":<>[]{}()"):
            return False
        
        # Reject common parsing artifacts
        invalid_patterns = [
            "SECOND:",
            "MOVANT:",
            "AYES:",
            "NAYS:",
            "ABSTAIN:",
            "MOTION:",
            "VOTE:",
        ]
        
        for pattern in invalid_patterns:
            if pattern in name.upper():
                return False
        
        return True