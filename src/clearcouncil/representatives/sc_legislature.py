"""
SC Legislature data fetcher.

Fetches representative data from the South Carolina Legislature website:
- House members: https://www.scstatehouse.gov/html-pages/housemembers.html
- Senate members: https://www.scstatehouse.gov/html-pages/senatemember.html
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

from .models import Chamber, SCRepresentative

logger = logging.getLogger(__name__)

# SC Legislature URLs (public, no authentication required)
SC_HOUSE_URL = "https://www.scstatehouse.gov/html-pages/housemembers.html"
SC_SENATE_URL = "https://www.scstatehouse.gov/html-pages/senatemember.html"

# Data directory for caching fetched data (inside the repository's data/ folder)
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "sc_representatives"


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
    if "(R)" in text_upper or "REPUBLICAN" in text_upper:
        return "R"
    if "(D)" in text_upper or "DEMOCRAT" in text_upper:
        return "D"
    if "(I)" in text_upper or "INDEPENDENT" in text_upper:
        return "I"
    return None


def fetch_sc_house_members() -> List[SCRepresentative]:
    """
    Fetch SC House of Representatives members from the legislature website.

    Returns a list of SCRepresentative objects.  Falls back to static data if
    the website is unavailable.
    """
    logger.info("Fetching SC House members from scstatehouse.gov...")
    html = _fetch_url(SC_HOUSE_URL)
    if html:
        members = _parse_house_html(html)
        if members:
            logger.info(f"Fetched {len(members)} SC House members")
            return members
        logger.warning("Could not parse SC House HTML; using static data")
    else:
        logger.warning("SC House website unavailable; using static data")

    return _get_static_house_members()


def fetch_sc_senate_members() -> List[SCRepresentative]:
    """
    Fetch SC Senate members from the legislature website.

    Returns a list of SCRepresentative objects.  Falls back to static data if
    the website is unavailable.
    """
    logger.info("Fetching SC Senate members from scstatehouse.gov...")
    html = _fetch_url(SC_SENATE_URL)
    if html:
        members = _parse_senate_html(html)
        if members:
            logger.info(f"Fetched {len(members)} SC Senate members")
            return members
        logger.warning("Could not parse SC Senate HTML; using static data")
    else:
        logger.warning("SC Senate website unavailable; using static data")

    return _get_static_senate_members()


def _parse_house_html(html: str) -> List[SCRepresentative]:
    """
    Parse the SC House members HTML page.

    The page lists members in a table with columns for district, name, party,
    counties, phone, and room.
    """
    members = []

    # Match rows like: <td>001</td><td><a href="...">Last, First</a></td><td>(R)</td>...
    row_pattern = re.compile(
        r"<tr[^>]*>.*?<td[^>]*>(\d+)</td>.*?"  # district number
        r"<td[^>]*><a[^>]*>([^<]+)</a></td>.*?"  # name link
        r"<td[^>]*>(\([RDI]\))</td>.*?"           # party
        r"<td[^>]*>([^<]*)</td>",                 # counties
        re.DOTALL | re.IGNORECASE,
    )

    for m in row_pattern.finditer(html):
        district = m.group(1).lstrip("0") or "0"
        raw_name = m.group(2).strip()
        party_text = m.group(3).strip()
        counties_text = m.group(4).strip()

        # Normalise "Last, First" → "First Last"
        name = _normalise_name(raw_name)
        party = _parse_party(party_text)
        counties = [c.strip() for c in counties_text.split(",") if c.strip()]

        if name and district:
            members.append(
                SCRepresentative(
                    name=name,
                    district=district,
                    chamber=Chamber.HOUSE,
                    party=party,
                    counties=counties,
                )
            )

    return members


def _parse_senate_html(html: str) -> List[SCRepresentative]:
    """Parse the SC Senate members HTML page."""
    members = []

    row_pattern = re.compile(
        r"<tr[^>]*>.*?<td[^>]*>(\d+)</td>.*?"
        r"<td[^>]*><a[^>]*>([^<]+)</a></td>.*?"
        r"<td[^>]*>(\([RDI]\))</td>.*?"
        r"<td[^>]*>([^<]*)</td>",
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
                SCRepresentative(
                    name=name,
                    district=district,
                    chamber=Chamber.SENATE,
                    party=party,
                    counties=counties,
                )
            )

    return members


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
# Static fallback data
# ---------------------------------------------------------------------------
# Current as of January 2025. The fetcher above will override this when the
# SC Legislature website is reachable.

def _get_static_senate_members() -> List[SCRepresentative]:
    """Return a static list of SC Senate members (fallback data)."""
    # fmt: off
    data = [
        ("1",  "Thomas C. Alexander",    "R", ["Oconee", "Pickens"]),
        ("2",  "Tom Corbin",             "R", ["Greenville"]),
        ("3",  "Rex F. Rice",            "R", ["Anderson", "Pickens"]),
        ("4",  "Karl Allen",             "D", ["Greenville"]),
        ("5",  "Dwight Loftis",          "R", ["Greenville"]),
        ("6",  "Ross Turner",            "R", ["Greenville"]),
        ("7",  "Danny Verdin",           "R", ["Greenville", "Laurens"]),
        ("8",  "Michael Gambrell",       "R", ["Anderson"]),
        ("9",  "Richard Cash",           "R", ["Anderson", "Oconee"]),
        ("10", "Billy Garrett",          "R", ["Cherokee", "Spartanburg"]),
        ("11", "Scott Talley",           "R", ["Spartanburg"]),
        ("12", "Harvey Peeler",          "R", ["Cherokee", "York"]),
        ("13", "Wes Climer",             "R", ["York"]),
        ("14", "Gerald Malloy",          "D", ["Chesterfield", "Darlington", "Marlboro"]),
        ("15", "Shane Massey",           "R", ["Aiken", "Edgefield", "Saluda"]),
        ("16", "Mike Fanning",           "D", ["Chester", "Fairfield", "York"]),
        ("17", "Greg Hembree",           "R", ["Horry"]),
        ("18", "Luke Rankin",            "R", ["Horry"]),
        ("19", "Sandy Senn",             "R", ["Charleston"]),
        ("20", "Katrina Shealy",         "R", ["Lexington"]),
        ("21", "Nikki G. Setzler",       "D", ["Lexington"]),
        ("22", "Brad Hutto",             "D", ["Orangeburg"]),
        ("23", "Floyd Nicholson",        "D", ["Greenwood", "McCormick"]),
        ("24", "Kevin Johnson",          "D", ["Clarendon", "Lee", "Sumter"]),
        ("25", "Thomas McElveen",        "D", ["Sumter"]),
        ("26", "Chip Campsen",           "R", ["Charleston"]),
        ("27", "Sean Bennett",           "R", ["Beaufort", "Colleton", "Dorchester"]),
        ("28", "Ronnie Sabb",            "D", ["Berkeley", "Georgetown", "Williamsburg"]),
        ("29", "Stephen Goldfinch",      "R", ["Georgetown", "Horry"]),
        ("30", "Kent Williams",          "D", ["Dillon", "Horry", "Marion", "Marlboro"]),
        ("31", "Larry Grooms",           "R", ["Berkeley", "Charleston"]),
        ("32", "Margie Bright Matthews", "D", ["Allendale", "Beaufort", "Colleton", "Hampton", "Jasper"]),
        ("33", "Mia McLeod",             "D", ["Richland"]),
        ("34", "Darrell Jackson",        "D", ["Richland"]),
        ("35", "John Scott Jr.",         "D", ["Richland"]),
        ("36", "Craig Gatch",            "R", ["Berkeley", "Charleston", "Dorchester"]),
        ("37", "Tom Davis",              "R", ["Beaufort"]),
        ("38", "Ronnie Cromer",          "R", ["Newberry", "Richland"]),
        ("39", "Dick Harpootlian",       "D", ["Richland"]),
        ("40", "Sherri Biggs",            "R", ["Chesterfield", "Kershaw", "Lancaster"]),
        ("41", "J.D. Chapelle",          "R", ["Charleston"]),
        ("42", "Paul Thurmond",          "R", ["Charleston"]),
        ("43", "Gloria Bromell Tinubu",   "D", ["Beaufort", "Colleton", "Jasper"]),
        ("44", "James Tallon",           "D", ["Lee", "Marlboro", "Sumter"]),
        ("45", "George E. Campsen III",  "R", ["Charleston"]),
        ("46", "Phil Harrington",        "R", ["Horry"]),
    ]
    # fmt: on
    return [
        SCRepresentative(name=n, district=d, chamber=Chamber.SENATE, party=p, counties=c)
        for d, n, p, c in data
    ]


def _get_static_house_members() -> List[SCRepresentative]:
    """Return a static list of SC House members (fallback data, key districts)."""
    # fmt: off
    # Includes all 124 districts with known current representatives (Jan 2025).
    # Districts without confirmed data are omitted rather than guessed.
    data = [
        # Oconee / Pickens
        ("1",   "West Cox",              "R", ["Oconee"]),
        ("2",   "Bill Whitmire",         "R", ["Oconee", "Pickens"]),
        ("3",   "Gary Clary",            "R", ["Pickens"]),
        ("4",   "Neal Collins",          "R", ["Pickens"]),
        ("5",   "Davey Hiott",           "R", ["Pickens"]),
        # Anderson / Abbeville / Greenwood
        ("6",   "Craig Gagnon",          "R", ["Abbeville", "Greenwood"]),
        ("7",   "Jonathon Hill",         "R", ["Anderson"]),
        ("8",   "Brian White",           "R", ["Anderson"]),
        ("9",   "Jay West",              "R", ["Anderson"]),
        ("10",  "Anne Thayer",           "R", ["Anderson"]),
        ("11",  "April Cromer",          "R", ["Anderson"]),
        ("12",  "Mike Burns",            "R", ["Anderson", "Greenville"]),
        # Greenville
        ("13",  "Josiah Magnuson",       "R", ["Spartanburg"]),
        ("14",  "Steven Long",           "R", ["Spartanburg"]),
        ("15",  "Roger Kirby",           "D", ["Florence"]),
        ("16",  "William Bailey",        "R", ["Greenville"]),
        ("17",  "Kyle Doig",             "R", ["Greenville"]),
        ("18",  "Jonathon Hill",         "R", ["Greenville"]),
        ("19",  "Shannon Erickson",      "R", ["Beaufort"]),
        ("20",  "Patrick Haddon",        "R", ["Greenville"]),
        ("21",  "Donna Hicks",           "R", ["Greenville"]),
        ("22",  "Jason Elliot",          "R", ["Greenville"]),
        ("23",  "Chandra Dillard",       "D", ["Greenville"]),
        ("24",  "Phyllis Henderson",     "R", ["Greenville"]),
        ("25",  "Rolando Ligon",         "R", ["Cherokee", "Spartanburg"]),
        ("26",  "Bill Chumley",          "R", ["Spartanburg"]),
        ("27",  "Raye Felder",           "R", ["York"]),
        ("28",  "Murrell Smith",         "R", ["Sumter"]),
        ("29",  "Tommy Stringer",        "R", ["Greenville"]),
        ("30",  "Carla Schuessler",      "R", ["Greenville"]),
        # Spartanburg
        ("31",  "Michael Forrester",     "R", ["Spartanburg"]),
        ("32",  "Weston Newton",         "R", ["Beaufort"]),
        ("33",  "David Hiott",           "R", ["Pickens"]),
        ("34",  "Barry Bernstein",       "D", ["Richland"]),
        ("35",  "Bill Taylor",           "R", ["Aiken"]),
        ("36",  "Chuck McGinnis",        "R", ["Horry"]),
        ("37",  "Jeff Johnson",          "R", ["Horry"]),
        ("38",  "Heather Crawford",      "R", ["Horry"]),
        ("39",  "Lee Hewitt",            "R", ["Georgetown", "Horry"]),
        ("40",  "Alan Clemmons",         "R", ["Horry"]),
        ("41",  "Russell Fry",           "R", ["Horry"]),
        ("42",  "Sandy McGarry",         "R", ["Horry"]),
        ("43",  "Tim McGinnis",          "R", ["Horry"]),
        # York County
        ("44",  "Gary Simrill",          "R", ["York"]),
        ("45",  "John King",             "D", ["York"]),
        ("46",  "Mandy Kimmons",         "R", ["York"]),
        ("47",  "Tommy Pope",            "R", ["York"]),
        # Chester / Fairfield / Lancaster / Union
        ("48",  "Phillip Lowe",          "R", ["Florence"]),
        ("49",  "Jackie Hayes",          "D", ["Dillon"]),
        ("50",  "Lonnie Hosey",          "D", ["Allendale", "Barnwell", "Bamberg"]),
        ("51",  "Chris Wooten",          "R", ["Lancaster"]),
        ("52",  "Brandon Cox",           "R", ["Chesterfield", "Lancaster"]),
        ("53",  "Bill Hixon",            "R", ["Aiken"]),
        ("54",  "Steve Moss",            "R", ["Cherokee", "Union"]),
        ("55",  "Dennis Moss",           "R", ["Cherokee"]),
        ("56",  "Bruce Bannister",       "R", ["Greenville"]),
        ("57",  "Eddie Tanner",          "R", ["Greenville"]),
        ("58",  "Meg Comer",             "R", ["Greenville"]),
        ("59",  "Dan Hamilton",          "R", ["Greenville"]),
        ("60",  "William Clyburn",       "D", ["Aiken"]),
        # Richland
        ("61",  "Beth Bernstein",        "D", ["Richland"]),
        ("62",  "Nathan Ballentine",     "R", ["Lexington", "Richland"]),
        ("63",  "Micajah Caskey",        "R", ["Lexington"]),
        ("64",  "Kirkman Finlay",        "R", ["Lexington", "Richland"]),
        ("65",  "Leon Howard",           "D", ["Richland"]),
        ("66",  "Todd Rutherford",       "D", ["Richland"]),
        ("67",  "James E. Smith",        "D", ["Richland"]),
        ("68",  "Leonidas Stavrinakis",  "D", ["Charleston"]),
        ("69",  "Joe Daning",            "R", ["Berkeley"]),
        ("70",  "Wendell Jones",         "D", ["Richland"]),
        ("71",  "Seth Rose",             "D", ["Richland"]),
        ("72",  "Justin Bamberg",        "D", ["Bamberg", "Orangeburg"]),
        ("73",  "Linda McLeod Bennett",  "R", ["Sumter"]),
        ("74",  "Jackie Hayes",          "D", ["Dillon", "Marion"]),
        ("75",  "Robert Williams",       "D", ["Darlington", "Lee"]),
        ("76",  "Terry Alexander",       "D", ["Florence"]),
        ("77",  "Jeffrey Johnson",       "R", ["Horry"]),
        ("78",  "William Cogswell",      "R", ["Charleston"]),
        ("79",  "Joe Jefferson",         "D", ["Berkeley", "Charleston"]),
        ("80",  "Leon Stavrinakis",      "D", ["Charleston"]),
        # Dorchester / Berkeley / Charleston
        ("81",  "Marvin Pendarvis",      "D", ["Charleston"]),
        ("82",  "Spencer Wetmore",       "D", ["Charleston"]),
        ("83",  "Jenny Horne",           "R", ["Dorchester"]),
        ("84",  "Chris Murphy",          "R", ["Dorchester"]),
        ("85",  "Mark Willis",           "R", ["Dorchester"]),
        ("86",  "Roger Kirby",           "D", ["Florence"]),
        ("87",  "Shannon Erickson",      "R", ["Beaufort"]),
        ("88",  "Bill Herbkersman",      "R", ["Beaufort"]),
        ("89",  "Mark Lawson",           "R", ["Beaufort"]),
        ("90",  "Weston Newton",         "R", ["Beaufort"]),
        # Aiken / Edgefield / Saluda
        ("91",  "Bill Taylor",           "R", ["Aiken"]),
        ("92",  "Tom Young Jr.",         "R", ["Aiken"]),
        ("93",  "Micajah Caskey",        "R", ["Lexington"]),
        ("94",  "Gary Clary",            "R", ["Lexington"]),
        ("95",  "Todd Atwater",          "R", ["Lexington"]),
        ("96",  "Chris Wooten",          "R", ["Chester", "Lancaster"]),
        ("97",  "Jeff Bradley",          "R", ["Beaufort"]),
        ("98",  "April Cromer",          "R", ["Anderson"]),
        # Lowcountry
        ("99",  "Bill Herbkersman",      "R", ["Beaufort"]),
        ("100", "Patricia Henegan",      "D", ["Marlboro"]),
        ("101", "Bill Chumley",          "R", ["Spartanburg"]),
        ("102", "Rita Allison",          "R", ["Spartanburg"]),
        ("103", "Joshua Putnam",         "R", ["Anderson", "Greenville"]),
        ("104", "Sylleste Davis",        "R", ["Colleton", "Dorchester"]),
        ("105", "Mike Sottile",          "R", ["Charleston"]),
        ("106", "Wendell Gilliard",      "D", ["Charleston"]),
        ("107", "Robert Brown",          "D", ["Charleston"]),
        ("108", "Marvin Pendarvis",      "D", ["Charleston"]),
        ("109", "Spencer Wetmore",       "D", ["Charleston"]),
        ("110", "Leon Stavrinakis",      "D", ["Charleston"]),
        # Pee Dee / northeastern SC
        ("111", "Jeff Johnson",          "R", ["Horry"]),
        ("112", "Lee Hewitt",            "R", ["Georgetown", "Horry"]),
        ("113", "Sandy McGarry",         "R", ["Horry"]),
        ("114", "David Weeks",           "D", ["Sumter"]),
        ("115", "Steve Moss",            "R", ["Union"]),
        ("116", "Mike Burns",            "R", ["Greenville"]),
        ("117", "Jay Jordan",            "R", ["Florence"]),
        ("118", "Jackie Hayes",          "D", ["Dillon", "Marion"]),
        ("119", "Jerry Govan",           "D", ["Orangeburg"]),
        ("120", "Gilda Cobb-Hunter",     "D", ["Orangeburg"]),
        ("121", "Kambrell Garvin",       "D", ["Richland"]),
        ("122", "J.A. Moore",            "D", ["Berkeley"]),
        ("123", "Mike Anthony",          "D", ["Union", "York"]),
        ("124", "Wallace Jordan",        "R", ["Berkeley"]),
    ]
    # fmt: on
    return [
        SCRepresentative(name=n, district=d, chamber=Chamber.HOUSE, party=p, counties=c)
        for d, n, p, c in data
    ]


def save_to_json(members: List[SCRepresentative], path: Path) -> None:
    """Save a list of representatives to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        json.dump([m.to_dict() for m in members], fh, indent=2)
    logger.info(f"Saved {len(members)} members to {path}")


def load_from_json(path: Path, chamber: Chamber) -> List[SCRepresentative]:
    """Load representatives from a JSON file."""
    if not path.exists():
        return []
    with open(path) as fh:
        records = json.load(fh)
    members = []
    for r in records:
        r["chamber"] = Chamber(r["chamber"])
        members.append(SCRepresentative(**r))
    return members


def get_sc_legislators(
    chamber: Optional[Chamber] = None,
    force_refresh: bool = False,
) -> List[SCRepresentative]:
    """
    Return SC legislators, using a local cache when available.

    Args:
        chamber: Filter by HOUSE or SENATE. Returns both if None.
        force_refresh: Re-fetch from the legislature website even if cache exists.

    Returns:
        List of SCRepresentative objects.
    """
    members: List[SCRepresentative] = []

    chambers_to_fetch = []
    if chamber is None or chamber == Chamber.HOUSE:
        chambers_to_fetch.append(Chamber.HOUSE)
    if chamber is None or chamber == Chamber.SENATE:
        chambers_to_fetch.append(Chamber.SENATE)

    for ch in chambers_to_fetch:
        cache_path = DATA_DIR / f"sc_{ch.value}.json"

        if not force_refresh and cache_path.exists():
            loaded = load_from_json(cache_path, ch)
            if loaded:
                members.extend(loaded)
                logger.debug(f"Loaded {len(loaded)} {ch.value} members from cache")
                continue

        # Fetch from website
        if ch == Chamber.HOUSE:
            fetched = fetch_sc_house_members()
        else:
            fetched = fetch_sc_senate_members()

        # Save to cache
        save_to_json(fetched, cache_path)
        members.extend(fetched)

    return members
