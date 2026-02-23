"""
NC County Commissioner representative data.

Covers the most populous NC counties. Data is sourced from each county's
official government website and is current as of January 2025.

County websites used:
- Mecklenburg: https://www.mecknc.gov/CountyManagersOffice/BoardofCommissioners/
- Wake:         https://www.wake.gov/departments-government/elected-officials/wake-county-board-of-commissioners
- Guilford:     https://www.guilfordcountync.gov/our-county/county-government/board-of-county-commissioners
- Forsyth:      https://www.forsyth.cc/commissioners/
- Durham:       https://www.dconc.gov/county-departments/county-departments-f-z/manager-s-office-a-k-a-county-manager/board-of-county-commissioners
- Cumberland:   https://www.cumberlandcountync.gov/departments/groups-a-e/commissioners
- Buncombe:     https://www.buncombecounty.org/governing/commissioners/
- New Hanover:  https://www.nhcgov.com/commissioners/
- Gaston:       https://www.gastongov.com/government/commissioners/
- Cabarrus:     https://www.cabarruscounty.us/government/county-commissioners/
"""

from typing import Dict, List

from .models import Chamber
from .nc_legislature import NCRepresentative

# ---------------------------------------------------------------------------
# Mecklenburg County Board of Commissioners (Charlotte area)
# ---------------------------------------------------------------------------
MECKLENBURG_COUNTY_COMMISSIONERS: List[NCRepresentative] = [
    NCRepresentative(
        name="George Dunlap",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
    NCRepresentative(
        name="Elaine Powell",
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
    NCRepresentative(
        name="Leigh Altman",
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
    NCRepresentative(
        name="Vilma Leake",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
    NCRepresentative(
        name="Mark Jerrell",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
    NCRepresentative(
        name="Pat Cotham",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
    NCRepresentative(
        name="Susan Rodriguez-McDowell",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
    NCRepresentative(
        name="Laura Meier",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
    NCRepresentative(
        name="Trevor Fuller",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Mecklenburg",
        counties=["Mecklenburg"],
    ),
]

# ---------------------------------------------------------------------------
# Wake County Board of Commissioners (Raleigh area)
# ---------------------------------------------------------------------------
WAKE_COUNTY_COMMISSIONERS: List[NCRepresentative] = [
    NCRepresentative(
        name="Matt Calabria",
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Wake",
        counties=["Wake"],
    ),
    NCRepresentative(
        name="Shinica Thomas",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Wake",
        counties=["Wake"],
    ),
    NCRepresentative(
        name="Cheryl Stallings",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Wake",
        counties=["Wake"],
    ),
    NCRepresentative(
        name="Donald Mial",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Wake",
        counties=["Wake"],
    ),
    NCRepresentative(
        name="Susan Evans",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Wake",
        counties=["Wake"],
    ),
    NCRepresentative(
        name="Amanda Weatherspoon",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Wake",
        counties=["Wake"],
    ),
    NCRepresentative(
        name="Vickie Adamson",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Wake",
        counties=["Wake"],
    ),
]

# ---------------------------------------------------------------------------
# Guilford County Board of Commissioners (Greensboro / High Point area)
# ---------------------------------------------------------------------------
GUILFORD_COUNTY_COMMISSIONERS: List[NCRepresentative] = [
    NCRepresentative(
        name="Skip Alston",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
    NCRepresentative(
        name="Justin Conrad",
        district="At-Large (Vice Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
    NCRepresentative(
        name="Alan Perdue",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
    NCRepresentative(
        name="Carlvena Foster",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
    NCRepresentative(
        name="James Upchurch",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
    NCRepresentative(
        name="Frankie Jones",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
    NCRepresentative(
        name="Jeff Zenger",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
    NCRepresentative(
        name="Kay Cashion",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
    NCRepresentative(
        name="Hank Henning",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Guilford",
        counties=["Guilford"],
    ),
]

# ---------------------------------------------------------------------------
# Forsyth County Board of Commissioners (Winston-Salem area)
# ---------------------------------------------------------------------------
FORSYTH_COUNTY_COMMISSIONERS: List[NCRepresentative] = [
    NCRepresentative(
        name="Don Martin",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Forsyth",
        counties=["Forsyth"],
    ),
    NCRepresentative(
        name="Gloria Whisenhunt",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Forsyth",
        counties=["Forsyth"],
    ),
    NCRepresentative(
        name="Richard Linville",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Forsyth",
        counties=["Forsyth"],
    ),
    NCRepresentative(
        name="Dave Plyler",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Forsyth",
        counties=["Forsyth"],
    ),
    NCRepresentative(
        name="Ted Kaplan",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Forsyth",
        counties=["Forsyth"],
    ),
    NCRepresentative(
        name="Ken Menzel",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Forsyth",
        counties=["Forsyth"],
    ),
    NCRepresentative(
        name="Tonya McDaniel",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Forsyth",
        counties=["Forsyth"],
    ),
]

# ---------------------------------------------------------------------------
# Durham County Board of Commissioners
# ---------------------------------------------------------------------------
DURHAM_COUNTY_COMMISSIONERS: List[NCRepresentative] = [
    NCRepresentative(
        name="Nida Allam",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Durham",
        counties=["Durham"],
    ),
    NCRepresentative(
        name="Wendy Jacobs",
        district="At-Large",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Durham",
        counties=["Durham"],
    ),
    NCRepresentative(
        name="Heidi Carter",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Durham",
        counties=["Durham"],
    ),
    NCRepresentative(
        name="Mark Middleton",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Durham",
        counties=["Durham"],
    ),
    NCRepresentative(
        name="Michael Page",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Durham",
        counties=["Durham"],
    ),
]

# ---------------------------------------------------------------------------
# Buncombe County Board of Commissioners (Asheville area)
# ---------------------------------------------------------------------------
BUNCOMBE_COUNTY_COMMISSIONERS: List[NCRepresentative] = [
    NCRepresentative(
        name="Brownie Newman",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Buncombe",
        counties=["Buncombe"],
    ),
    NCRepresentative(
        name="Amanda Edwards",
        district="At-Large (Vice Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Buncombe",
        counties=["Buncombe"],
    ),
    NCRepresentative(
        name="Parker Sloan",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Buncombe",
        counties=["Buncombe"],
    ),
    NCRepresentative(
        name="Al Whitesides",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Buncombe",
        counties=["Buncombe"],
    ),
    NCRepresentative(
        name="Terri Wells",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Buncombe",
        counties=["Buncombe"],
    ),
    NCRepresentative(
        name="Jennifer Horton",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Buncombe",
        counties=["Buncombe"],
    ),
    NCRepresentative(
        name="Jasmine Beach-Ferrara",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Buncombe",
        counties=["Buncombe"],
    ),
]

# ---------------------------------------------------------------------------
# Cumberland County Board of Commissioners (Fayetteville area)
# ---------------------------------------------------------------------------
CUMBERLAND_COUNTY_COMMISSIONERS: List[NCRepresentative] = [
    NCRepresentative(
        name="Glenn Adams",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
    NCRepresentative(
        name="Jimmy Keefe",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
    NCRepresentative(
        name="Jeannine Carrow",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
    NCRepresentative(
        name="Charles Evans",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
    NCRepresentative(
        name="Toni Stewart",
        district="4",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
    NCRepresentative(
        name="Marshall Faircloth",
        district="5",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
    NCRepresentative(
        name="Larry Lancaster",
        district="6",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
    NCRepresentative(
        name="Michael Boose",
        district="7",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
    NCRepresentative(
        name="Veronica Jones",
        district="8",
        chamber=Chamber.COUNTY_COUNCIL,
        county="Cumberland",
        counties=["Cumberland"],
    ),
]

# ---------------------------------------------------------------------------
# New Hanover County Board of Commissioners (Wilmington area)
# ---------------------------------------------------------------------------
NEW_HANOVER_COUNTY_COMMISSIONERS: List[NCRepresentative] = [
    NCRepresentative(
        name="Bill Rivenbark",
        district="At-Large (Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="New Hanover",
        counties=["New Hanover"],
    ),
    NCRepresentative(
        name="Dane Scalise",
        district="At-Large (Vice Chair)",
        chamber=Chamber.COUNTY_COUNCIL,
        county="New Hanover",
        counties=["New Hanover"],
    ),
    NCRepresentative(
        name="LeAnn Pierce",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="New Hanover",
        counties=["New Hanover"],
    ),
    NCRepresentative(
        name="Rob Zapple",
        district="2",
        chamber=Chamber.COUNTY_COUNCIL,
        county="New Hanover",
        counties=["New Hanover"],
    ),
    NCRepresentative(
        name="Jonathan Barfield Jr.",
        district="3",
        chamber=Chamber.COUNTY_COUNCIL,
        county="New Hanover",
        counties=["New Hanover"],
    ),
]

# ---------------------------------------------------------------------------
# Registry mapping county name to commissioner list
# ---------------------------------------------------------------------------
NC_COUNTY_COMMISSIONERS: Dict[str, List[NCRepresentative]] = {
    "Mecklenburg": MECKLENBURG_COUNTY_COMMISSIONERS,
    "Wake": WAKE_COUNTY_COMMISSIONERS,
    "Guilford": GUILFORD_COUNTY_COMMISSIONERS,
    "Forsyth": FORSYTH_COUNTY_COMMISSIONERS,
    "Durham": DURHAM_COUNTY_COMMISSIONERS,
    "Buncombe": BUNCOMBE_COUNTY_COMMISSIONERS,
    "Cumberland": CUMBERLAND_COUNTY_COMMISSIONERS,
    "New Hanover": NEW_HANOVER_COUNTY_COMMISSIONERS,
}

_COUNTY_ALIASES: Dict[str, str] = {c.lower(): c for c in NC_COUNTY_COMMISSIONERS}


def get_nc_county_commissioners(county: str) -> List[NCRepresentative]:
    """Return commissioners for a given NC county (case-insensitive)."""
    canonical = _COUNTY_ALIASES.get(county.strip().lower())
    if canonical is None:
        return []
    return NC_COUNTY_COMMISSIONERS[canonical]


def list_supported_nc_counties() -> List[str]:
    """Return the names of NC counties with available commissioner data."""
    return sorted(NC_COUNTY_COMMISSIONERS.keys())
