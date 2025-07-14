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
    
    def parse_text(self, text: str) -> List[VotingRecord]:
        """Parse text and extract voting records."""
        lines = text.split('\n')
        records = []
        current_record = VotingRecord()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for each configured field
            for field_name in self.config.parsing.voting_fields:
                value = self._extract_field_value(line, field_name)
                if value is not None:
                    self._set_record_field(current_record, field_name, value)
                    
                    # Special handling for MOVANT which indicates end of record
                    if field_name == "MOVANT":
                        # Also extract SECOND from the same line
                        second_value = self._extract_second_from_movant_line(line)
                        if second_value:
                            current_record.second = second_value
                        
                        # Add completed record and start new one
                        if self._is_valid_record(current_record):
                            records.append(current_record)
                        current_record = VotingRecord()
                    break
        
        # Add final record if it has data
        if self._is_valid_record(current_record):
            records.append(current_record)
        
        logger.info(f"Extracted {len(records)} voting records")
        return records
    
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
            "MOVANT": r"MOVANT:\s*(.+?)(?:\s*SECOND:|$)"
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
            "MOVANT": lambda r, v: setattr(r, 'movant', v)
        }
        
        if field_name in field_mapping:
            field_mapping[field_name](record, value)
    
    def _parse_council_district(self, record: VotingRecord, value: str):
        """Parse council district which may include representative name."""
        # Format might be "District - Representative Name"
        if ' - ' in value:
            parts = value.split(' - ', 1)
            record.district = parts[0].strip()
            record.representative = parts[1].strip()
        else:
            record.district = value
    
    def _is_valid_record(self, record: VotingRecord) -> bool:
        """Check if a record has enough data to be considered valid."""
        # A record is valid if it has at least a case number or district
        return bool(record.case_number or record.district)
    
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