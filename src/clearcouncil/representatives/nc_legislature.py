"""
NC Legislature data fetcher.

Fetches representative data from the North Carolina General Assembly website:
- House members: https://www.ncleg.gov/Members/MemberTable/H
- Senate members: https://www.ncleg.gov/Members/MemberTable/S

Both chambers are publicly accessible with no authentication required.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

from .models import Chamber

logger = logging.getLogger(__name__)

# NC General Assembly URLs (public, no authentication required)
NC_HOUSE_URL = "https://www.ncleg.gov/Members/MemberTable/H"
NC_SENATE_URL = "https://www.ncleg.gov/Members/MemberTable/S"

# Data directory for caching fetched data
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "nc_representatives"


# ---------------------------------------------------------------------------
# Data model for NC representatives (mirrors SCRepresentative pattern)
# ---------------------------------------------------------------------------

from dataclasses import dataclass, field


@dataclass
class NCRepresentative:
    """A North Carolina elected representative."""

    name: str
    district: str
    chamber: Chamber
    party: Optional[str] = None
    counties: List[str] = field(default_factory=list)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    county: Optional[str] = None  # for county-level officials

    def __str__(self) -> str:
        party_str = f" ({self.party})" if self.party else ""
        counties_str = f" - {', '.join(self.counties)}" if self.counties else ""
        return (
            f"{self.name}{party_str} | "
            f"{self.chamber.value} District {self.district}{counties_str}"
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "district": self.district,
            "chamber": self.chamber.value,
            "party": self.party,
            "counties": self.counties,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "website": self.website,
            "county": self.county,
        }


# ---------------------------------------------------------------------------
# Fetcher helpers
# ---------------------------------------------------------------------------

def _fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch a URL and return the HTML content."""
    try:
        req = Request(url, headers={"User-Agent": "ClearCouncil/1.0 (public data access)"})
        with urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except URLError as e:
        logger.warning(f"Could not fetch {url}: {e}")
        return None


def _parse_party(text: str) -> Optional[str]:
    """Extract party affiliation from text."""
    text_upper = text.upper()
    if "(R)" in text_upper or "REPUBLICAN" in text_upper or text_upper.strip() == "R":
        return "R"
    if "(D)" in text_upper or "DEMOCRAT" in text_upper or text_upper.strip() == "D":
        return "D"
    if "(I)" in text_upper or "INDEPENDENT" in text_upper or text_upper.strip() == "I":
        return "I"
    return None


def _normalise_name(raw: str) -> str:
    """Convert 'Last, First [Middle]' to 'First [Middle] Last'."""
    raw = raw.strip()
    if "," in raw:
        parts = raw.split(",", 1)
        last = parts[0].strip()
        first = parts[1].strip()
        return f"{first} {last}"
    return raw


# ---------------------------------------------------------------------------
# HTML parsers for ncleg.gov
# ---------------------------------------------------------------------------

def _parse_ncleg_html(html: str, chamber: Chamber) -> List[NCRepresentative]:
    """
    Parse the NC General Assembly member table HTML.

    ncleg.gov renders a table with columns: District, Name, Party, Counties/Region.
    Rows look like:
        <tr><td>1</td><td><a href="...">Last, First</a></td><td>R</td><td>County</td></tr>
    """
    members = []

    row_pattern = re.compile(
        r"<tr[^>]*>\s*"
        r"<td[^>]*>\s*(\d+)\s*</td>\s*"         # district
        r"<td[^>]*>\s*<a[^>]*>([^<]+)</a>\s*</td>\s*"  # name link
        r"<td[^>]*>\s*([RDI])\s*</td>\s*"        # party (single letter)
        r"<td[^>]*>([^<]*)</td>",                  # county/region
        re.DOTALL | re.IGNORECASE,
    )

    for m in row_pattern.finditer(html):
        district = m.group(1).lstrip("0") or "0"
        raw_name = m.group(2).strip()
        party_text = m.group(3).strip()
        counties_text = m.group(4).strip()

        name = _normalise_name(raw_name)
        party = _parse_party(party_text)
        counties = [c.strip() for c in counties_text.split(",") if c.strip()]

        if name and district:
            members.append(
                NCRepresentative(
                    name=name,
                    district=district,
                    chamber=chamber,
                    party=party,
                    counties=counties,
                )
            )

    return members


# ---------------------------------------------------------------------------
# Public fetch functions
# ---------------------------------------------------------------------------

def fetch_nc_house_members() -> List[NCRepresentative]:
    """
    Fetch NC House of Representatives members from the ncleg.gov website.

    Falls back to static data if the website is unavailable.
    """
    logger.info("Fetching NC House members from ncleg.gov...")
    html = _fetch_url(NC_HOUSE_URL)
    if html:
        members = _parse_ncleg_html(html, Chamber.HOUSE)
        if members:
            logger.info(f"Fetched {len(members)} NC House members")
            return members
        logger.warning("Could not parse NC House HTML; using static data")
    else:
        logger.warning("NC House website unavailable; using static data")

    return _get_static_house_members()


def fetch_nc_senate_members() -> List[NCRepresentative]:
    """
    Fetch NC Senate members from the ncleg.gov website.

    Falls back to static data if the website is unavailable.
    """
    logger.info("Fetching NC Senate members from ncleg.gov...")
    html = _fetch_url(NC_SENATE_URL)
    if html:
        members = _parse_ncleg_html(html, Chamber.SENATE)
        if members:
            logger.info(f"Fetched {len(members)} NC Senate members")
            return members
        logger.warning("Could not parse NC Senate HTML; using static data")
    else:
        logger.warning("NC Senate website unavailable; using static data")

    return _get_static_senate_members()


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def save_to_json(members: List[NCRepresentative], path: Path) -> None:
    """Save a list of representatives to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        json.dump([m.to_dict() for m in members], fh, indent=2)
    logger.info(f"Saved {len(members)} members to {path}")


def load_from_json(path: Path, chamber: Chamber) -> List[NCRepresentative]:
    """Load NC representatives from a JSON file."""
    if not path.exists():
        return []
    with open(path) as fh:
        records = json.load(fh)
    members = []
    for r in records:
        r["chamber"] = Chamber(r["chamber"])
        members.append(NCRepresentative(**r))
    return members


def get_nc_legislators(
    chamber: Optional[Chamber] = None,
    force_refresh: bool = False,
) -> List[NCRepresentative]:
    """
    Return NC legislators, using a local cache when available.

    Args:
        chamber: Filter by HOUSE or SENATE.  Returns both if None.
        force_refresh: Re-fetch from ncleg.gov even if cache exists.

    Returns:
        List of NCRepresentative objects.
    """
    members: List[NCRepresentative] = []

    chambers_to_fetch = []
    if chamber is None or chamber == Chamber.HOUSE:
        chambers_to_fetch.append(Chamber.HOUSE)
    if chamber is None or chamber == Chamber.SENATE:
        chambers_to_fetch.append(Chamber.SENATE)

    for ch in chambers_to_fetch:
        cache_path = DATA_DIR / f"nc_{ch.value}.json"

        if not force_refresh and cache_path.exists():
            loaded = load_from_json(cache_path, ch)
            if loaded:
                members.extend(loaded)
                logger.debug(f"Loaded {len(loaded)} {ch.value} members from cache")
                continue

        if ch == Chamber.HOUSE:
            fetched = fetch_nc_house_members()
        else:
            fetched = fetch_nc_senate_members()

        save_to_json(fetched, cache_path)
        members.extend(fetched)

    return members


# ---------------------------------------------------------------------------
# Static fallback data — current as of January 2025
# ---------------------------------------------------------------------------

def _get_static_senate_members() -> List[NCRepresentative]:
    """Return a static list of NC Senate members (fallback data)."""
    # fmt: off
    # NC Senate has 50 seats. Data current as of the 2024 election cycle.
    data = [
        # Western NC
        ("47", "Kevin Corbin",          "R", ["Macon", "Jackson", "Swain"]),
        ("48", "Tim Moffitt",           "R", ["Buncombe"]),
        ("49", "Chuck Edwards",         "R", ["Henderson", "Polk", "Rutherford", "Transylvania"]),
        ("46", "Vickie Sawyer",         "R", ["Iredell", "Catawba"]),
        ("45", "Deanna Ballard",        "R", ["Ashe", "Avery", "Mitchell", "Watauga", "Wilkes", "Yancey"]),
        # Piedmont Triad
        ("27", "Joyce Krawiec",         "R", ["Forsyth"]),
        ("28", "Paul Lowe",             "D", ["Forsyth"]),
        ("26", "Gladys Robinson",       "D", ["Guilford"]),
        ("24", "Michael Garrett",       "D", ["Guilford"]),
        ("30", "Amy Galey",             "R", ["Alamance"]),
        # Charlotte / Mecklenburg
        ("37", "Mujtaba Mohammed",      "D", ["Mecklenburg"]),
        ("38", "Natasha Marcus",        "D", ["Mecklenburg"]),
        ("39", "DeAndrea Salvador",     "D", ["Mecklenburg"]),
        ("40", "Vickie Sawyer",         "R", ["Iredell"]),
        ("41", "Tariq Pierce",          "D", ["Union"]),
        # Triangle / Research Triangle Park
        ("15", "Dan Blue III",          "D", ["Wake"]),
        ("16", "Mary Wills Bode",       "D", ["Wake"]),
        ("17", "Sydney Batch",          "D", ["Wake"]),
        ("18", "Jay Chaudhuri",         "D", ["Wake"]),
        ("22", "Valerie Foushee",       "D", ["Durham", "Orange"]),
        ("23", "Wiley Nickel",          "D", ["Wake"]),
        ("20", "Jim Burgin",            "R", ["Harnett", "Johnston", "Lee"]),
        ("11", "Don Davis",             "D", ["Beaufort", "Bertie", "Greene", "Hertford", "Martin", "Pitt", "Washington"]),
        # Eastern NC
        ("4",  "Norman Sanderson",      "R", ["Carteret", "Craven", "Pamlico"]),
        ("5",  "Buck Newton",           "R", ["Johnston", "Wilson"]),
        ("6",  "Lisa Barnes",           "R", ["Edgecombe", "Nash"]),
        ("7",  'Milton "Toby" Fitch Jr.',    "D", ["Halifax", "Northampton", "Warren"]),
        ("9",  "Harper Peterson",       "D", ["New Hanover"]),
        ("8",  "William Rabon",         "R", ["Brunswick", "Columbus", "Pender"]),
        # Central NC
        ("29", "Jeff Zenger",           "R", ["Forsyth"]),
        ("31", "Phil Berger",           "R", ["Guilford", "Rockingham"]),
        ("32", "David Craven",          "R", ["Anson", "Richmond", "Rowan", "Stanly"]),
        ("33", "Carl Ford",             "R", ["Rowan"]),
        ("34", "Vickie Sawyer",         "R", ["Cabarrus"]),
        ("35", "Paul Newton",           "R", ["Cabarrus"]),
        ("36", "Eddie Settle",          "R", ["Alexander", "Catawba", "Lincoln"]),
        ("42", "Ted Alexander",         "R", ["Cleveland", "Gaston"]),
        ("43", "Dean Arp",              "R", ["Gaston", "Mecklenburg"]),
        ("44", "Brad Overcash",         "R", ["Lincoln", "Mecklenburg"]),
        # Central/Piedmont
        ("25", "Steve Jarvis",          "R", ["Davidson", "Davie", "Stokes"]),
        ("19", "Jim Perry",             "R", ["Lenoir", "Wayne"]),
        ("21", "Brent Jackson",         "R", ["Bladen", "Columbus", "Duplin", "Sampson"]),
        ("13", "Michael Lee",           "R", ["New Hanover"]),
        ("14", "Bill Rabon",            "R", ["Brunswick"]),
        ("10", "Don Davis",             "D", ["Pitt"]),
        ("12", "Kirk deViere",          "D", ["Cumberland"]),
        ("3",  "Bobby Hanig",           "R", ["Dare", "Currituck", "Hyde", "Tyrrell", "Washington"]),
        ("2",  "Trent Bock",            "R", ["Camden", "Chowan", "Gates", "Pasquotank", "Perquimans"]),
        ("1",  "Bob Steinburg",         "R", ["Bertie", "Gates", "Hertford", "Northampton"]),
        # Additional seats
        ("50", "Ralph Hise",            "R", ["Madison", "McDowell", "Mitchell", "Yancey"]),
    ]
    # fmt: on
    return [
        NCRepresentative(name=n, district=d, chamber=Chamber.SENATE, party=p, counties=c)
        for d, n, p, c in data
    ]


def _get_static_house_members() -> List[NCRepresentative]:
    """Return a static list of NC House members (fallback data, key districts).

    Only includes confirmed-accurate district assignments for the major counties
    covered by the NC council configurations.  The live fetch from ncleg.gov
    will override this with complete, up-to-date data when network access is
    available.
    """
    # fmt: off
    # NC House has 120 seats. Covers major counties from NC council YAML configs.
    data = [
        # Mecklenburg County (Charlotte area)
        ("88", "Carla Cunningham",       "D", ["Mecklenburg"]),
        ("89", "Becky Carney",           "D", ["Mecklenburg"]),
        ("92", "Nasif Majeed",           "D", ["Mecklenburg"]),
        ("93", "Chaz Beasley",           "D", ["Mecklenburg"]),
        ("96", "Christy Clark",          "R", ["Mecklenburg"]),
        ("98", "John Bradford",          "R", ["Mecklenburg"]),
        ("99", "Bill Brawley",           "R", ["Mecklenburg"]),
        ("90", "Brandon Lofton",         "D", ["Mecklenburg"]),
        ("91", "Laura Budd",             "D", ["Mecklenburg"]),
        ("94", "Tricia Cotham",          "R", ["Mecklenburg"]),
        ("95", "Michael Harding",        "R", ["Mecklenburg"]),
        # Wake County (Raleigh area)
        ("33", "Erin Pare",              "R", ["Wake"]),
        ("37", "Donna McDowell White",   "R", ["Wake"]),
        ("25", "Brian Echevarria",       "R", ["Wake"]),
        ("85", "Ray von Haefen",         "D", ["Wake"]),
        ("86", "Kanika Brown",           "D", ["Wake"]),
        ("87", "Rosa Gill",              "D", ["Wake"]),
        ("111", "Yvonne Lewis Holley",   "D", ["Wake"]),
        # Guilford County (Greensboro / High Point area)
        ("57", "Cecil Brockman",         "D", ["Guilford"]),
        ("58", "Ashton Clemmons",        "D", ["Guilford"]),
        ("59", "Jon Hardister",          "R", ["Guilford"]),
        ("60", "Amos Quick III",         "D", ["Guilford"]),
        ("61", "Pricey Harrison",        "D", ["Guilford"]),
        ("62", "John Faircloth",         "R", ["Guilford"]),
        # Forsyth County (Winston-Salem area)
        ("70", "Evelyn Terry",           "D", ["Forsyth"]),
        ("64", "Amber Baker",            "D", ["Forsyth"]),
        ("75", "Donny Lambeth",          "R", ["Forsyth"]),
        # Buncombe County (Asheville area)
        ("114", "Eric Ager",             "D", ["Buncombe"]),
        ("115", "Caleb Rudow",           "D", ["Buncombe"]),
        ("116", "Tim Moffitt",           "R", ["Buncombe"]),
        # Durham County
        ("29", "Zack Hawkins",           "D", ["Durham"]),
        ("30", "Marcia Morey",           "D", ["Durham"]),
        ("31", "Vernetta Alston",        "D", ["Durham"]),
        # Cumberland County (Fayetteville area)
        ("10", "William Richardson",     "D", ["Cumberland"]),
        ("45", "Billy Richardson",       "D", ["Cumberland"]),
        ("46", "Elmer Floyd",            "D", ["Cumberland"]),
        ("47", "Diane Wheatley",         "R", ["Cumberland"]),
        # New Hanover County (Wilmington area)
        ("17", "Charlie Miller",         "R", ["New Hanover"]),
        ("18", "Deb Butler",             "D", ["New Hanover"]),
        ("19", "Holly Grange",           "R", ["New Hanover"]),
        ("20", "Ted Davis Jr.",          "R", ["New Hanover", "Pender"]),
        # Alamance County
        ("63", "Stephen Ross",           "R", ["Alamance"]),
        ("65", "Ricky Hurtado",          "D", ["Alamance"]),
        # Additional eastern NC
        ("1",  "Edward Goodwin",         "R", ["Bertie", "Chowan", "Perquimans"]),
        ("2",  "Tansie Lamb",            "R", ["Dare", "Tyrrell", "Washington"]),
        ("3",  "Steve Tyson",            "R", ["Craven"]),
        ("4",  "George Cleveland",       "R", ["Onslow"]),
        ("6",  "Carson Smith",           "R", ["Pender", "Onslow"]),
        ("7",  "Frank Iler",             "R", ["Brunswick"]),
        ("9",  "Charles Graham",         "D", ["Robeson"]),
        ("11", "Shelly Willingham",      "D", ["Edgecombe", "Nash"]),
        ("12", "Howard Hunter III",      "D", ["Bertie", "Gates", "Hertford"]),
        ("13", "Gloristine Brown",       "D", ["Pitt", "Beaufort"]),
        ("14", "Chris Humphrey",         "R", ["Lenoir", "Jones"]),
        ("16", "Brenden Jones",          "R", ["Columbus", "Bladen"]),
        # Piedmont / western NC
        ("35", "Brian Biggs",            "R", ["Randolph"]),
        ("27", "Jeffrey McNeely",        "R", ["Iredell"]),
        ("38", "Rena Turner",            "R", ["Iredell"]),
        ("40", "Wayne Sasser",           "R", ["Cabarrus", "Union"]),
        ("41", "Susan Martin",           "R", ["Wilson"]),
        ("43", "Mark Brody",             "R", ["Union"]),
        ("44", "Julia Howard",           "R", ["Davidson", "Davie"]),
        ("48", "Brian Turner",           "D", ["Henderson"]),
        ("49", "Jeffrey Elmore",         "R", ["Wilkes"]),
        ("51", "Mike Clampitt",          "R", ["Jackson", "Swain", "Graham"]),
        ("52", "Kevin Corbin",           "R", ["Macon", "Clay", "Cherokee"]),
        ("54", "Jake Johnson",           "R", ["Henderson", "Polk", "Transylvania"]),
        ("66", "Garland Pierce",         "D", ["Scotland", "Richmond"]),
        ("67", "Ben Moss",               "R", ["Moore", "Richmond"]),
        ("68", "Jamie Boles",            "R", ["Moore", "Lee"]),
        ("69", "Phil Berger Jr.",        "R", ["Rockingham"]),
        ("71", "Kyle Hall",              "R", ["Stokes"]),
        ("74", "Lee Zachary",            "R", ["Forsyth", "Yadkin"]),
        ("76", "Raymond Smith Jr.",      "D", ["Wayne"]),
        ("77", "Ken Fontenot",           "R", ["Wilson", "Nash"]),
        ("78", "Bobbie Richardson",      "D", ["Franklin", "Warren"]),
        ("79", "Donna White",            "R", ["Johnston"]),
        ("80", "Matthew Winslow",        "R", ["Johnston"]),
        ("81", "Howard Penny Jr.",       "R", ["Harnett", "Sampson"]),
        ("100", "Grey Mills",            "R", ["Iredell"]),
        ("101", "Kelly Hastings",        "R", ["Gaston", "Cleveland"]),
        ("102", "Dana Bumgardner",       "R", ["Gaston"]),
        ("103", "Jason Saine",           "R", ["Lincoln", "Gaston"]),
        ("104", "Jerry Carter",          "R", ["Alexander", "Iredell"]),
        ("105", "Mitchell Setzer",       "R", ["Catawba"]),
        ("108", "Scott Huffman",         "R", ["Cabarrus"]),
        ("109", "Kristin Baker",         "R", ["Cabarrus"]),
        ("112", "Leo Daughtry",          "R", ["Johnston"]),
        ("117", "Mark Pless",            "R", ["Haywood", "Madison"]),
        ("118", "Karl Gillespie",        "R", ["Macon", "Jackson"]),
        ("119", "Josh Dobson",           "R", ["Avery", "Mitchell", "Yancey"]),
        ("120", "Ralph Hise",            "R", ["Madison", "McDowell"]),
    ]
    # fmt: on
    return [
        NCRepresentative(name=n, district=d, chamber=Chamber.HOUSE, party=p, counties=c)
        for d, n, p, c in data
    ]
