"""Parser for extracting voting records from council documents."""

import re
from typing import List
import logging

from .base_parser import BaseParser
from ..core.models import VotingRecord
from ..core.exceptions import ParsingError

logger = logging.getLogger(__name__)


class VotingParser(BaseParser):
    """Extracts voting records and rezoning data from council documents."""
    
    # Known representative-to-district mapping for York County
    YORK_COUNTY_DISTRICTS = {
        'Joel Hamilton': 'District 1',
        'Albert Quarles': 'District 2', 
        'Tom Audette': 'District 3',
        'Barbara Candler': 'District 4',
        'Tommy Adkins': 'District 5',
        'Tony Smith': 'District 6',
        'Debi Cloninger': 'District 7',
        'Allison Love': 'At-Large',
        'William "Bump" Roddey': 'At-Large',
        'Christi Cox': 'At-Large',  # May be former representative
        'Bump Roddey': 'At-Large'  # Alternative name format
    }
    
    def parse_text(self, text: str) -> List[VotingRecord]:
        """Parse text and extract voting records."""
        lines = text.split('\n')
        records = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Look for voting result patterns (APPROVED, DENIED, etc.)
            if self._is_voting_result_line(line):
                # Start a new voting record
                current_record = VotingRecord()
                current_record.result = self._extract_voting_result(line)
                
                # Look for MOVANT, SECOND, and AYES in the next few lines
                j = i + 1
                while j < len(lines) and j < i + 15:  # Look ahead max 15 lines
                    next_line = lines[j].strip()
                    
                    if next_line == "MOVANT:" and j + 1 < len(lines):
                        # MOVANT is on the next line
                        movant = lines[j + 1].strip()
                        if movant:
                            current_record.movant = movant
                            current_record.representative = self._clean_representative_name(movant)
                            current_record.district = self._get_district_for_representative(current_record.representative)
                        j += 1  # Skip the movant line
                    
                    elif next_line == "SECOND:" and j + 1 < len(lines):
                        # SECOND is on the next line
                        second = lines[j + 1].strip()
                        if second:
                            current_record.second = second
                            j += 1  # Skip the second line
                    
                    elif next_line == "AYES:" and j + 1 < len(lines):
                        # AYES is on the next line
                        ayes = lines[j + 1].strip()
                        if ayes:
                            current_record.ayes = ayes
                        
                        # AYES usually marks the end of a voting record
                        if self._is_valid_record(current_record):
                            records.append(current_record)
                        break
                    
                    elif next_line == "NAYS:" and j + 1 < len(lines):
                        # NAYS is on the next line
                        nays = lines[j + 1].strip()
                        if nays:
                            current_record.nays = nays
                            j += 1  # Skip the nays line
                    
                    j += 1
            
            # Also look for configured rezoning fields for backward compatibility
            for field_name in getattr(self.config.parsing, 'voting_fields', []):
                value = self._extract_field_value(line, field_name)
                if value is not None:
                    # This would need a current_record context, skip for now
                    break
            
            i += 1
        
        logger.info(f"Extracted {len(records)} voting records")
        return records
    
    def _is_voting_result_line(self, line: str) -> bool:
        """Check if a line contains a voting result."""
        voting_results = ['APPROVED', 'DENIED', 'PASSED', 'FAILED', 'ACCEPTED', 'REJECTED']
        line_upper = line.upper()
        return any(result in line_upper for result in voting_results)
    
    def _extract_voting_result(self, line: str) -> str:
        """Extract the voting result from a line."""
        voting_results = ['APPROVED', 'DENIED', 'PASSED', 'FAILED', 'ACCEPTED', 'REJECTED']
        line_upper = line.upper()
        for result in voting_results:
            if result in line_upper:
                # Extract additional info like [Unanimous] if present
                match = re.search(rf'{result}\s*\[([^\]]+)\]', line_upper)
                if match:
                    return f"{result} [{match.group(1)}]"
                return result
        return line.strip()
    
    def _clean_representative_name(self, name: str) -> str:
        """Clean and standardize representative name."""
        if not name:
            return name
            
        # Remove common prefixes/suffixes
        name = re.sub(r'\b(Council\s+member|Councilman|Councilwoman)\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(Jr\.?|Sr\.?|III?|II?)$', '', name, flags=re.IGNORECASE)
        
        # Basic cleanup
        name = ' '.join(name.split())  # Normalize whitespace
        return name.strip()
    
    def _get_district_for_representative(self, representative_name: str) -> str:
        """Get district for a representative based on known mappings."""
        if not representative_name:
            return None
        
        # Check direct match
        if representative_name in self.YORK_COUNTY_DISTRICTS:
            return self.YORK_COUNTY_DISTRICTS[representative_name]
        
        # Check for partial matches (in case of slight name variations)
        for known_name, district in self.YORK_COUNTY_DISTRICTS.items():
            if known_name.lower() in representative_name.lower() or representative_name.lower() in known_name.lower():
                return district
        
        # If no match found, return None
        return None

    def _extract_field_value(self, line: str, field_name: str) -> str:
        """Extract value for a specific field from a line."""
        patterns = {
            "Council District": r"Council District:\s*(.+?)(?:\s*-|$)",
            "Case #": r"Case #\s*(.+?)(?:\s|$)",
            "Acres": r"Acres:\s*(.+?)(?:\s|$)",
            "Owner": r"Owner:\s*(.+?)(?:\s|$)",
            "Location": r"Location:\s*(.+?)(?:\s|$)",
            "Applicant": r"Applicant:\s*(.+?)(?:\s|$)",
            "Planning Commission Date": r"Planning Commission Date:\s*(.+?)(?:\s|$)",
            "Staff Recommendation": r"Staff Recommendation:\s*(.+?)(?:\s|$)",
            "PC Recommendation": r"PC Recommendation:\s*(.+?)(?:\s|$)",
            "Zoning Request": r"Zoning Request:\s*(.+?)(?:\s|$)",
            "Rezoning Action": r"Rezoning Action:\s*(.+?)(?:\s|$)",
            "MOVANT": r"MOVANT:\s*(.+?)(?:\s*$)",
            "SECOND": r"SECOND:\s*(.+?)(?:\s*$)",
            "AYES": r"AYES:\s*(.+?)(?:\s*$)",
            "NAYS": r"NAYS:\s*(.+?)(?:\s*$)"
        }
        
        if field_name not in patterns:
            return None
        
        match = re.search(patterns[field_name], line, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _extract_second_from_movant_line(self, line: str) -> str:
        """Extract SECOND value from MOVANT line."""
        match = re.search(r"SECOND:\s*(.+?)(?:\s|$)", line, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _set_record_field(self, record: VotingRecord, field_name: str, value: str):
        """Set the appropriate field on a VotingRecord."""
        field_mapping = {
            "Council District": self._parse_council_district,
            "Case #": lambda r, v: setattr(r, 'case_number', v),
            "Acres": lambda r, v: setattr(r, 'acres', v),
            "Owner": lambda r, v: setattr(r, 'owner', v),
            "Location": lambda r, v: setattr(r, 'location', v),
            "Applicant": lambda r, v: setattr(r, 'applicant', v),
            "Planning Commission Date": lambda r, v: setattr(r, 'planning_commission_date', v),
            "Staff Recommendation": lambda r, v: setattr(r, 'staff_recommendation', v),
            "PC Recommendation": lambda r, v: setattr(r, 'pc_recommendation', v),
            "Zoning Request": lambda r, v: setattr(r, 'zoning_request', v),
            "Rezoning Action": lambda r, v: setattr(r, 'rezoning_action', v),
            "MOVANT": self._set_movant_field
        }
        
        if field_name in field_mapping:
            field_mapping[field_name](record, value)
            
    def _set_movant_field(self, record: VotingRecord, value: str):
        """Set movant field and try to extract representative name."""
        record.movant = value
        
        # Try to extract a clean representative name from the movant
        representative = self._extract_representative_from_text(f"Council member {value}")
        if representative:
            record.representative = representative
        elif value and len(value.split()) <= 3:  # Reasonable name length
            record.representative = value.strip()
    
    def _parse_council_district(self, record: VotingRecord, value: str):
        """Parse council district which may include representative name."""
        # Format might be "District - Representative Name"
        if ' - ' in value:
            parts = value.split(' - ', 1)
            record.district = parts[0].strip()
            record.representative = parts[1].strip()
        else:
            record.district = value
            
    def _extract_representative_from_text(self, text: str) -> str:
        """Extract representative name from various text patterns."""
        # Try multiple patterns to extract representative names
        patterns = [
            r'Council\s+member\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'Councilman\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', 
            r'Councilwoman\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+AYES',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+NAYS',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Basic validation - should be two words (first and last name)
                if len(name.split()) == 2:
                    return name
        
        return None
    
    def _is_valid_record(self, record: VotingRecord) -> bool:
        """Check if a record has enough data to be considered valid."""
        # A record is valid if it has a movant and result, or case number
        return bool(record.movant and record.result) or bool(record.case_number)
    
    def save_to_csv(self, records: List[VotingRecord], file_path) -> None:
        """Save voting records to CSV file."""
        try:
            import pandas as pd
            
            # Convert records to dictionaries
            data = [record.to_dict() for record in records]
            
            # Create DataFrame and save
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            
            logger.info(f"Saved {len(records)} voting records to {file_path}")
            
        except ImportError:
            raise ParsingError("pandas is required for CSV export")
        except Exception as e:
            raise ParsingError(f"Failed to save CSV: {e}")