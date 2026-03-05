"""
NC Representative Lookup Service.

Provides a unified interface for finding North Carolina representatives by:
- Name (with fuzzy matching)
- District number and chamber
- County name (returns all reps for that county)
- Level (state house, state senate, county council)

Mirrors the interface of SCRepresentativeLookup so callers can use either
interchangeably.
"""

import logging
from typing import Dict, List, Optional, Tuple

from .models import Chamber
from .nc_legislature import NCRepresentative, get_nc_legislators
from .nc_county_councils import (
    get_nc_county_commissioners,
    list_supported_nc_counties,
    NC_COUNTY_COMMISSIONERS,
)

logger = logging.getLogger(__name__)


def _fuzzy_score(a: str, b: str) -> int:
    """Return a similarity score (0-100) between two strings."""
    a, b = a.lower().strip(), b.lower().strip()
    if a == b:
        return 100
    if not a or not b:
        return 0

    def bigrams(s: str) -> set:
        return {s[i:i + 2] for i in range(len(s) - 1)}

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


class NCRepresentativeLookup:
    """Lookup service for North Carolina representatives at all levels."""

    def __init__(self, force_refresh: bool = False):
        """
        Initialise the lookup service.

        Args:
            force_refresh: When True, re-fetch data from legislature website
                           even if a local cache exists.
        """
        self._force_refresh = force_refresh
        self._state_members: Optional[List[NCRepresentative]] = None
        self._county_cache: Dict[str, List[NCRepresentative]] = {}

    # ------------------------------------------------------------------
    # Internal data loading
    # ------------------------------------------------------------------

    def _ensure_state_data(self) -> None:
        if self._state_members is None:
            self._state_members = get_nc_legislators(force_refresh=self._force_refresh)
            logger.debug(f"Loaded {len(self._state_members)} NC state legislators")

    def _get_all_representatives(
        self, include_state: bool = True, include_county: bool = True
    ) -> List[NCRepresentative]:
        reps: List[NCRepresentative] = []
        if include_state:
            self._ensure_state_data()
            reps.extend(self._state_members)
        if include_county:
            for county in list_supported_nc_counties():
                reps.extend(self._get_county_reps(county))
        return reps

    def _get_county_reps(self, county: str) -> List[NCRepresentative]:
        if county not in self._county_cache:
            self._county_cache[county] = get_nc_county_commissioners(county)
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
    ) -> List[Tuple[NCRepresentative, int]]:
        """
        Find representatives whose names are similar to *name*.

        Args:
            name: Name to search for (partial or full).
            threshold: Minimum similarity score (0-100) to include.
            include_state: Search state House and Senate members.
            include_county: Search county council members.

        Returns:
            List of ``(representative, score)`` tuples sorted by score descending.
        """
        all_reps = self._get_all_representatives(include_state, include_county)
        results: List[Tuple[NCRepresentative, int]] = []

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
    ) -> List[NCRepresentative]:
        """
        Find representatives for a specific district.

        Args:
            district: District number or label (e.g. "1", "At-Large").
            chamber: Limit to a specific chamber.  If None, search all.
            county: Limit county council search to this county.

        Returns:
            List of matching NCRepresentative objects.
        """
        results: List[NCRepresentative] = []

        if chamber in (None, Chamber.HOUSE, Chamber.SENATE):
            self._ensure_state_data()
            for rep in self._state_members:
                if rep.district.lstrip("0") == district.lstrip("0"):
                    if chamber is None or rep.chamber == chamber:
                        results.append(rep)

        if chamber in (None, Chamber.COUNTY_COUNCIL):
            counties_to_search = [county] if county else list_supported_nc_counties()
            for c in counties_to_search:
                for rep in self._get_county_reps(c):
                    if rep.district.lower() == district.lower():
                        results.append(rep)

        return results

    def find_by_county(
        self,
        county: str,
        chamber: Optional[Chamber] = None,
    ) -> List[NCRepresentative]:
        """
        Find all representatives associated with a county.

        Args:
            county: County name (case-insensitive).
            chamber: Limit to a specific chamber.  If None, return all.

        Returns:
            List of NCRepresentative objects.
        """
        county_lower = county.strip().lower()
        results: List[NCRepresentative] = []

        if chamber in (None, Chamber.HOUSE, Chamber.SENATE):
            self._ensure_state_data()
            for rep in self._state_members:
                if any(c.lower() == county_lower for c in rep.counties):
                    if chamber is None or rep.chamber == chamber:
                        results.append(rep)

        if chamber in (None, Chamber.COUNTY_COUNCIL):
            for supported in list_supported_nc_counties():
                if supported.lower() == county_lower:
                    results.extend(self._get_county_reps(supported))

        return results

    def find_by_chamber(self, chamber: Chamber) -> List[NCRepresentative]:
        """
        Return all representatives for a given chamber.

        Args:
            chamber: The chamber to retrieve.

        Returns:
            List of NCRepresentative objects.
        """
        if chamber in (Chamber.HOUSE, Chamber.SENATE):
            return get_nc_legislators(chamber=chamber, force_refresh=self._force_refresh)

        if chamber == Chamber.COUNTY_COUNCIL:
            reps: List[NCRepresentative] = []
            for county in list_supported_nc_counties():
                reps.extend(self._get_county_reps(county))
            return reps

        return []

    def get_summary(self) -> Dict:
        """Return a summary of available NC representative data."""
        self._ensure_state_data()

        house_count = sum(1 for r in self._state_members if r.chamber == Chamber.HOUSE)
        senate_count = sum(1 for r in self._state_members if r.chamber == Chamber.SENATE)

        county_counts: Dict[str, int] = {}
        for county in list_supported_nc_counties():
            county_counts[county] = len(self._get_county_reps(county))

        return {
            "nc_house_members": house_count,
            "nc_senate_members": senate_count,
            "county_councils": county_counts,
            "total_county_council_members": sum(county_counts.values()),
            "supported_counties": list_supported_nc_counties(),
        }
