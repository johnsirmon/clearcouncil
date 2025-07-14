"""Time range parsing and handling for voting analysis."""

import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TimeRangeParser:
    """Parses natural language and specific date ranges for analysis."""
    
    @staticmethod
    def parse_time_range(time_input: str) -> Tuple[datetime, datetime]:
        """
        Parse time range input and return start and end dates.
        
        Supports:
        - Natural language: "last year", "last 5 months", "past 2 years"
        - Specific dates: "2023-01-01 to 2024-01-01"
        - Relative dates: "6 months ago", "since 2023"
        """
        time_input = time_input.lower().strip()
        now = datetime.now()
        
        # Handle natural language patterns
        if "last year" in time_input or "past year" in time_input:
            start_date = now - relativedelta(years=1)
            return start_date, now
        
        # Handle "last X months/years"
        last_match = re.search(r'last (\d+) (month|year)s?', time_input)
        if last_match:
            amount = int(last_match.group(1))
            unit = last_match.group(2)
            
            if unit == "month":
                start_date = now - relativedelta(months=amount)
            else:  # year
                start_date = now - relativedelta(years=amount)
            
            return start_date, now
        
        # Handle "past X months/years"
        past_match = re.search(r'past (\d+) (month|year)s?', time_input)
        if past_match:
            amount = int(past_match.group(1))
            unit = past_match.group(2)
            
            if unit == "month":
                start_date = now - relativedelta(months=amount)
            else:  # year
                start_date = now - relativedelta(years=amount)
            
            return start_date, now
        
        # Handle "X months/years ago"
        ago_match = re.search(r'(\d+) (month|year)s? ago', time_input)
        if ago_match:
            amount = int(ago_match.group(1))
            unit = ago_match.group(2)
            
            if unit == "month":
                end_date = now - relativedelta(months=amount)
            else:  # year
                end_date = now - relativedelta(years=amount)
            
            # Default to 1 month range
            start_date = end_date - relativedelta(months=1)
            return start_date, end_date
        
        # Handle "since YYYY" format
        since_match = re.search(r'since (\d{4})', time_input)
        if since_match:
            year = int(since_match.group(1))
            start_date = datetime(year, 1, 1)
            return start_date, now
        
        # Handle specific date ranges "YYYY-MM-DD to YYYY-MM-DD"
        date_range_match = re.search(
            r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})', 
            time_input
        )
        if date_range_match:
            start_str = date_range_match.group(1)
            end_str = date_range_match.group(2)
            
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
            
            return start_date, end_date
        
        # Handle single date format
        single_date_match = re.search(r'(\d{4}-\d{2}-\d{2})', time_input)
        if single_date_match:
            date_str = single_date_match.group(1)
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Default to 1 month around that date
            start_date = target_date - timedelta(days=15)
            end_date = target_date + timedelta(days=15)
            
            return start_date, end_date
        
        # Default: last 6 months if nothing matches
        logger.warning(f"Could not parse time range '{time_input}', defaulting to last 6 months")
        start_date = now - relativedelta(months=6)
        return start_date, now
    
    @staticmethod
    def format_date_range(start_date: datetime, end_date: datetime) -> str:
        """Format date range for display."""
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    @staticmethod
    def get_suggested_ranges() -> list:
        """Get list of suggested time ranges for user interface."""
        return [
            "last 3 months",
            "last 6 months", 
            "last year",
            "past 2 years",
            "since 2023",
            "2023-01-01 to 2023-12-31"
        ]