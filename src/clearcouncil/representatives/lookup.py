"""
SC Representative Lookup Service.

Provides a unified interface for finding representatives by:
- Name (with fuzzy matching)
- District number and chamber
- County name (returns all reps for that county)
- Level (state house, state senate, county council)
"""

import logging
from typing import Dict, List, Optional, Tuple

from .models import Chamber, SCRepresentative
from .sc_legislature import get_sc_legislators
from .county_councils import get_county_council, list_supported_counties

logger = logging.getLogger(__name__)


def _fuzzy_score(a: str, b: str) -> int:
    """
    Return a simple similarity score (0-100) between two strings.

    Uses character-level Jaccard similarity on bigrams as a lightweight
    fallback when fuzzywuzzy is not installed.
    """
    a, b = a.lower().strip(), b.lower().strip()
    if a == b:
        return 100
    if not a or not b:
        return 0

    def bigrams(s: str) -> set:
        return {s[i:i+2] for i in range(len(s) - 1)}

    bg_a, bg_b = bigrams(a), bigrams(b)
    if not bg_a or not bg_b:
        return 0
    intersection = len(bg_a & bg_b)
    union = len(bg_a | bg_b)
    return int(100 * intersection / union)


try:
    from fuzzywuzzy import fuzz as _fuzz

    def _fuzzy_score(a: str, b: str) -> int:  # noqa: F811
        return _fuzz.token_sort_ratio(a, b)

except ImportError:
    pass  # use the bigram fallback defined above


class SCRepresentativeLookup:
    """Lookup service for South Carolina representatives at all levels."""

    def __init__(self, force_refresh: bool = False):
        """
        Initialise the lookup service.

        Args:
            force_refresh: When True, re-fetch data from legislature website
                           even if a local cache exists.
        """
        self._force_refresh = force_refresh
        self._state_members: Optional[List[SCRepresentative]] = None
        self._county_cache: Dict[str, List[SCRepresentative]] = {}

    # ------------------------------------------------------------------
    # Internal data loading
    # ------------------------------------------------------------------

    def _ensure_state_data(self) -> None:
        if self._state_members is None:
            self._state_members = get_sc_legislators(force_refresh=self._force_refresh)
            logger.debug(f"Loaded {len(self._state_members)} state legislators")

    def _get_all_representatives(
        self, include_state: bool = True, include_county: bool = True
    ) -> List[SCRepresentative]:
        reps: List[SCRepresentative] = []
        if include_state:
            self._ensure_state_data()
            reps.extend(self._state_members)
        if include_county:
            for county in list_supported_counties():
                reps.extend(self._get_county_reps(county))
        return reps

    def _get_county_reps(self, county: str) -> List[SCRepresentative]:
        if county not in self._county_cache:
            self._county_cache[county] = get_county_council(county)
        return self._county_cache[county]

    # ------------------------------------------------------------------
    # Public lookup methods
    # ------------------------------------------------------------------

    def find_by_name(
        self,
        name: str,
        threshold: int = 60,
        include_state: bool = True,
        include_county: bool = True,
    ) -> List[Tuple[SCRepresentative, int]]:
        """
        Find representatives whose names are similar to *name*.

        Args:
            name: Name to search for (partial or full).
            threshold: Minimum similarity score (0-100) to include in results.
            include_state: Search state House and Senate members.
            include_county: Search county council members.

        Returns:
            List of ``(representative, score)`` tuples sorted by score descending.
        """
        all_reps = self._get_all_representatives(include_state, include_county)
        results: List[Tuple[SCRepresentative, int]] = []

        for rep in all_reps:
            score = _fuzzy_score(name, rep.name)
            if score >= threshold:
                results.append((rep, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def find_by_district(
        self,
        district: str,
        chamber: Optional[Chamber] = None,
        county: Optional[str] = None,
    ) -> List[SCRepresentative]:
        """
        Find representatives for a specific district.

        Args:
            district: District number or label (e.g. "1", "At-Large").
            chamber: Limit to a specific chamber.  If None, search all.
            county: Limit county council search to this county.

        Returns:
            List of matching SCRepresentative objects.
        """
        results: List[SCRepresentative] = []

        if chamber in (None, Chamber.HOUSE, Chamber.SENATE):
            self._ensure_state_data()
            for rep in self._state_members:
                if rep.district.lstrip("0") == district.lstrip("0"):
                    if chamber is None or rep.chamber == chamber:
                        results.append(rep)

        if chamber in (None, Chamber.COUNTY_COUNCIL):
            counties_to_search = [county] if county else list_supported_counties()
            for c in counties_to_search:
                for rep in self._get_county_reps(c):
                    if rep.district.lower() == district.lower():
                        results.append(rep)

        return results

    def find_by_county(
        self,
        county: str,
        chamber: Optional[Chamber] = None,
    ) -> List[SCRepresentative]:
        """
        Find all representatives associated with a county.

        For state legislators this matches any rep whose *counties* list
        contains the given county.  For county councils it returns the full
        council roster.

        Args:
            county: County name (case-insensitive).
            chamber: Limit to a specific chamber.  If None, return all.

        Returns:
            List of SCRepresentative objects.
        """
        county_lower = county.strip().lower()
        results: List[SCRepresentative] = []

        if chamber in (None, Chamber.HOUSE, Chamber.SENATE):
            self._ensure_state_data()
            for rep in self._state_members:
                if any(c.lower() == county_lower for c in rep.counties):
                    if chamber is None or rep.chamber == chamber:
                        results.append(rep)

        if chamber in (None, Chamber.COUNTY_COUNCIL):
            # Use proper-case county name for the county councils registry
            for supported in list_supported_counties():
                if supported.lower() == county_lower:
                    results.extend(self._get_county_reps(supported))

        return results

    def find_by_chamber(self, chamber: Chamber) -> List[SCRepresentative]:
        """
        Return all representatives for a given chamber.

        Args:
            chamber: The chamber to retrieve.

        Returns:
            List of SCRepresentative objects.
        """
        if chamber in (Chamber.HOUSE, Chamber.SENATE):
            return get_sc_legislators(chamber=chamber, force_refresh=self._force_refresh)

        if chamber == Chamber.COUNTY_COUNCIL:
            reps: List[SCRepresentative] = []
            for county in list_supported_counties():
                reps.extend(self._get_county_reps(county))
            return reps

        return []

    def get_summary(self) -> Dict:
        """Return a summary of available representative data."""
        self._ensure_state_data()

        house_count = sum(1 for r in self._state_members if r.chamber == Chamber.HOUSE)
        senate_count = sum(1 for r in self._state_members if r.chamber == Chamber.SENATE)

        county_counts: Dict[str, int] = {}
        for county in list_supported_counties():
            county_counts[county] = len(self._get_county_reps(county))

        return {
            "sc_house_members": house_count,
            "sc_senate_members": senate_count,
            "county_councils": county_counts,
            "total_county_council_members": sum(county_counts.values()),
            "supported_counties": list_supported_counties(),
        }
