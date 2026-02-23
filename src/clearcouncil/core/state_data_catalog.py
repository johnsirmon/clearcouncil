"""
State Data Catalog for South Carolina and North Carolina.

This module catalogs publicly available local government data sources for SC and NC,
documents known access blockers, and provides legally permissible workarounds.

Key findings:
- Most SC/NC counties publish meeting minutes as PDFs on their official websites
- Several use third-party document management systems (IQM2, Legistar, CivicPlus)
- Legistar (Granicus) provides a REST API that is publicly accessible
- IQM2 portals allow direct URL-based document access (no auth for historical docs)
- CivicPlus portals may require account creation for post-2024 documents
- All document portals listed here offer at minimum public PDF access

Workarounds for access blockers (all legally permissible):
- CivicPlus registration: Create a free account with email (no payment required)
- JavaScript-heavy portals: Use requests+BeautifulSoup or Selenium for scraping
- Legistar API: Use the public REST API at webapi.legistar.com for structured data
- Public records requests:
    SC: Submit FOIA requests under the SC Freedom of Information Act (S.C. Code § 30-4-10)
    NC: Submit records requests under the NC Public Records Law (N.C. Gen. Stat. § 132-1 et seq.)
  Both laws require prompt response and prohibit charging more than actual duplication costs
  for electronic records, making bulk PDF access legally and financially accessible.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DataSourceEntry:
    """Information about a single county's data source."""

    county: str
    state: str
    portal_type: str
    primary_url: str
    minutes_url: str
    access_level: str          # "public", "free_registration", "subscription"
    document_formats: List[str] = field(default_factory=list)
    api_available: bool = False
    api_url: Optional[str] = None
    access_notes: str = ""
    known_blockers: List[str] = field(default_factory=list)
    workarounds: List[str] = field(default_factory=list)
    council_identifier: Optional[str] = None   # matches YAML config file name


# ---------------------------------------------------------------------------
# Portal type descriptions
# ---------------------------------------------------------------------------
PORTAL_TYPES = {
    "iqm2": "IQM2 (Civic Plus legacy) — direct URL access, no auth for historical docs",
    "granicus_legistar": "Granicus/Legistar — public REST API + web portal, no auth required",
    "civicplus_civicclerk": "CivicPlus CivicClerk — free account registration may be required for new docs",
    "civicplus_public": "CivicPlus (public mode) — PDFs publicly accessible without auth",
    "custom_pdf": "Custom website — PDFs published directly, no auth required",
    "municode": "Municode — ordinances/code public, minutes may require site-specific auth",
    "granicus_youtube": "Granicus YouTube integration — videos public, no auth needed",
}


# ---------------------------------------------------------------------------
# South Carolina data sources
# ---------------------------------------------------------------------------
SC_DATA_SOURCES: List[DataSourceEntry] = [
    DataSourceEntry(
        county="York",
        state="SC",
        portal_type="iqm2",
        primary_url="https://www.yorkcountysc.gov",
        minutes_url="https://yorkcountysc.iqm2.com/Citizens/Default.aspx",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes=(
            "Historical documents (2018–March 2025) accessible via IQM2 direct URL. "
            "Post-March 2025 documents migrated to CivicClerk portal."
        ),
        known_blockers=[
            "Post-2025 documents require CivicClerk account at https://yorkcosc.portal.civicclerk.com/",
        ],
        workarounds=[
            "Create free CivicClerk account (email/password or social login) for post-2025 docs",
            "Historical IQM2 documents still accessible via direct URL without auth",
        ],
        council_identifier="york_county_sc",
    ),
    DataSourceEntry(
        county="Charleston",
        state="SC",
        portal_type="granicus_legistar",
        primary_url="https://www.charlestoncounty.org",
        minutes_url="https://charlestoncountysc.legistar.com/Calendar.aspx",
        access_level="public",
        document_formats=["PDF", "HTML"],
        api_available=True,
        api_url="https://webapi.legistar.com/v1/charlestoncountysc",
        access_notes="Legistar portal — publicly accessible. REST API available.",
        known_blockers=[],
        workarounds=["Use Legistar REST API at webapi.legistar.com for structured data"],
        council_identifier="charleston_county_sc",
    ),
    DataSourceEntry(
        county="Greenville",
        state="SC",
        portal_type="custom_pdf",
        primary_url="https://www.greenvillecounty.org",
        minutes_url="https://www.greenvillecounty.org/CountyCouncil/Meetings.aspx",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="PDFs published directly on county website, no auth required.",
        known_blockers=[],
        workarounds=[],
        council_identifier="greenville_county_sc",
    ),
    DataSourceEntry(
        county="Richland",
        state="SC",
        portal_type="custom_pdf",
        primary_url="https://www.richlandcountysc.gov",
        minutes_url="https://www.richlandcountysc.gov/Government/County-Council/Meeting-Agendas-and-Minutes",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="PDFs on official county website, no auth required.",
        known_blockers=[],
        workarounds=[],
        council_identifier="richland_county_sc",
    ),
    DataSourceEntry(
        county="Spartanburg",
        state="SC",
        portal_type="iqm2",
        primary_url="https://www.spartanburgcounty.org",
        minutes_url="https://spartanburgcounty.iqm2.com/Citizens/Default.aspx",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="IQM2 portal, publicly accessible without auth.",
        known_blockers=[],
        workarounds=[],
        council_identifier="spartanburg_county_sc",
    ),
    DataSourceEntry(
        county="Horry",
        state="SC",
        portal_type="custom_pdf",
        primary_url="https://www.horrycounty.org",
        minutes_url="https://www.horrycounty.org/Government/Council-Members",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="Minutes and agendas available as PDFs, no auth required.",
        known_blockers=["Older documents may be archived and require records request"],
        workarounds=["Submit SC FOIA request (S.C. Code § 30-4-10) to Horry County Clerk for documents > 5 years old"],
        council_identifier="horry_county_sc",
    ),
    DataSourceEntry(
        county="Lexington",
        state="SC",
        portal_type="custom_pdf",
        primary_url="https://www.lex-co.sc.gov",
        minutes_url="https://www.lex-co.sc.gov/departments/council/",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="Minutes on county website, no auth required.",
        known_blockers=[],
        workarounds=[],
        council_identifier="lexington_county_sc",
    ),
    DataSourceEntry(
        county="Anderson",
        state="SC",
        portal_type="custom_pdf",
        primary_url="https://www.andersoncountysc.org",
        minutes_url="https://www.andersoncountysc.org/council",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="Minutes on county website, no auth required.",
        known_blockers=[],
        workarounds=[],
        council_identifier=None,
    ),
    DataSourceEntry(
        county="Berkeley",
        state="SC",
        portal_type="custom_pdf",
        primary_url="https://www.berkeleycountysc.gov",
        minutes_url="https://www.berkeleycountysc.gov/county-council/",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="Minutes on county website, no auth required.",
        known_blockers=[],
        workarounds=[],
        council_identifier=None,
    ),
    DataSourceEntry(
        county="Beaufort",
        state="SC",
        portal_type="granicus_legistar",
        primary_url="https://www.bcgov.net",
        minutes_url="https://beaufortsc.legistar.com/Calendar.aspx",
        access_level="public",
        document_formats=["PDF", "HTML"],
        api_available=True,
        api_url="https://webapi.legistar.com/v1/beaufortsc",
        access_notes="Legistar portal — publicly accessible. REST API available.",
        known_blockers=[],
        workarounds=["Use Legistar REST API for structured data access"],
        council_identifier=None,
    ),
]


# ---------------------------------------------------------------------------
# North Carolina data sources
# ---------------------------------------------------------------------------
NC_DATA_SOURCES: List[DataSourceEntry] = [
    DataSourceEntry(
        county="Mecklenburg",
        state="NC",
        portal_type="granicus_legistar",
        primary_url="https://mecknc.legistar.com",
        minutes_url="https://mecknc.legistar.com/Calendar.aspx",
        access_level="public",
        document_formats=["PDF", "HTML"],
        api_available=True,
        api_url="https://webapi.legistar.com/v1/mecknc",
        access_notes=(
            "Granicus/Legistar portal with public REST API. No authentication required. "
            "Complete meeting history with agendas, minutes, and vote records available."
        ),
        known_blockers=[],
        workarounds=[
            "Use Legistar REST API: https://webapi.legistar.com/v1/mecknc/EventItems",
            "Direct calendar: https://mecknc.legistar.com/Calendar.aspx",
        ],
        council_identifier="mecklenburg_county_nc",
    ),
    DataSourceEntry(
        county="Wake",
        state="NC",
        portal_type="custom_pdf",
        primary_url="https://www.wake.gov",
        minutes_url="https://www.wake.gov/departments-government/elected-officials/wake-county-board-of-commissioners/agenda-minutes",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes=(
            "PDFs published directly on the official county website. No auth required. "
            "Documents organized by year/month."
        ),
        known_blockers=[
            "No structured API; requires web scraping to discover document URLs",
            "Some older meeting videos require Granicus account to watch",
        ],
        workarounds=[
            "Scrape the agenda-minutes page to extract PDF links",
            "Video recordings available free via Granicus without auth",
        ],
        council_identifier="wake_county_nc",
    ),
    DataSourceEntry(
        county="Guilford",
        state="NC",
        portal_type="custom_pdf",
        primary_url="https://www.guilfordcountync.gov",
        minutes_url="https://www.guilfordcountync.gov/our-county/county-government/board-of-county-commissioners/board-meetings-agendas-minutes",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes=(
            "PDFs on official county website, no auth required. "
            "Meeting recordings linked to YouTube."
        ),
        known_blockers=[],
        workarounds=[],
        council_identifier="guilford_county_nc",
    ),
    DataSourceEntry(
        county="Forsyth",
        state="NC",
        portal_type="civicplus_public",
        primary_url="https://www.forsyth.cc",
        minutes_url="https://www.forsyth.cc/commissioners/meetings.aspx",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes=(
            "CivicPlus portal with public document access. No account required to "
            "download minutes and agendas."
        ),
        known_blockers=[],
        workarounds=[],
        council_identifier="forsyth_county_nc",
    ),
    DataSourceEntry(
        county="Durham",
        state="NC",
        portal_type="custom_pdf",
        primary_url="https://www.dconc.gov",
        minutes_url="https://www.dconc.gov/county-departments/county-departments-f-z/manager-s-office-a-k-a-county-manager/board-of-county-commissioners/minutes-agendas-and-videos",
        access_level="public",
        document_formats=["PDF", "Video"],
        api_available=False,
        access_notes=(
            "PDFs and video recordings publicly available on dconc.gov. "
            "No authentication required."
        ),
        known_blockers=[],
        workarounds=[],
        council_identifier="durham_county_nc",
    ),
    DataSourceEntry(
        county="Buncombe",
        state="NC",
        portal_type="custom_pdf",
        primary_url="https://www.buncombecounty.org",
        minutes_url="https://www.buncombecounty.org/governing/commissioners/meetings.aspx",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes=(
            "PDFs on official county website. Note: County was heavily impacted by "
            "Hurricane Helene (September 2024); some records may have gaps. "
            "Contact Clerk to the Board for missing documents."
        ),
        known_blockers=[
            "Potential record gaps from Hurricane Helene (Sept 2024) recovery period",
        ],
        workarounds=[
            "Submit NC Public Records Law (N.C.G.S. § 132-1) request to Buncombe County Clerk",
            "Contact Buncombe County Manager's Office for affected records",
        ],
        council_identifier="buncombe_county_nc",
    ),
    DataSourceEntry(
        county="Cumberland",
        state="NC",
        portal_type="custom_pdf",
        primary_url="https://www.cumberlandcountync.gov",
        minutes_url="https://www.cumberlandcountync.gov/departments/groups-a-e/commissioners",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="Minutes on official county website, no auth required.",
        known_blockers=[],
        workarounds=[],
        council_identifier=None,
    ),
    DataSourceEntry(
        county="New Hanover",
        state="NC",
        portal_type="granicus_legistar",
        primary_url="https://www.nhcgov.com",
        minutes_url="https://nhcgov.legistar.com/Calendar.aspx",
        access_level="public",
        document_formats=["PDF", "HTML"],
        api_available=True,
        api_url="https://webapi.legistar.com/v1/nhcgov",
        access_notes="Legistar portal — publicly accessible. REST API available.",
        known_blockers=[],
        workarounds=["Use Legistar REST API for structured data access"],
        council_identifier=None,
    ),
    DataSourceEntry(
        county="Gaston",
        state="NC",
        portal_type="custom_pdf",
        primary_url="https://www.gastongov.com",
        minutes_url="https://www.gastongov.com/government/commissioners/meetings/",
        access_level="public",
        document_formats=["PDF"],
        api_available=False,
        access_notes="PDFs on official county website, no auth required.",
        known_blockers=[],
        workarounds=[],
        council_identifier=None,
    ),
    DataSourceEntry(
        county="Cabarrus",
        state="NC",
        portal_type="granicus_legistar",
        primary_url="https://www.cabarruscounty.us",
        minutes_url="https://cabarruscounty.legistar.com/Calendar.aspx",
        access_level="public",
        document_formats=["PDF", "HTML"],
        api_available=True,
        api_url="https://webapi.legistar.com/v1/cabarruscounty",
        access_notes="Legistar portal — publicly accessible. REST API available.",
        known_blockers=[],
        workarounds=["Use Legistar REST API for structured data access"],
        council_identifier=None,
    ),
]

# ---------------------------------------------------------------------------
# Combined catalog
# ---------------------------------------------------------------------------
ALL_DATA_SOURCES: Dict[str, List[DataSourceEntry]] = {
    "SC": SC_DATA_SOURCES,
    "NC": NC_DATA_SOURCES,
}


def get_data_sources(state: Optional[str] = None) -> List[DataSourceEntry]:
    """
    Return data source entries, optionally filtered by state.

    Args:
        state: "SC" or "NC". If None, returns all sources.
    """
    if state is None:
        return SC_DATA_SOURCES + NC_DATA_SOURCES
    return ALL_DATA_SOURCES.get(state.upper(), [])


def get_data_source_by_county(county: str, state: Optional[str] = None) -> Optional[DataSourceEntry]:
    """Return the data source entry for a specific county (case-insensitive)."""
    sources = get_data_sources(state)
    county_lower = county.strip().lower()
    for source in sources:
        if source.county.lower() == county_lower:
            return source
    return None


def get_blocked_sources(state: Optional[str] = None) -> List[DataSourceEntry]:
    """Return sources that have known access blockers."""
    return [s for s in get_data_sources(state) if s.known_blockers]


def get_api_sources(state: Optional[str] = None) -> List[DataSourceEntry]:
    """Return sources with programmatic API access available."""
    return [s for s in get_data_sources(state) if s.api_available]


def get_legistar_sources(state: Optional[str] = None) -> List[DataSourceEntry]:
    """Return sources that use Granicus/Legistar (REST API available)."""
    return [
        s for s in get_data_sources(state)
        if s.portal_type in ("granicus_legistar",)
    ]


def print_catalog_summary(state: Optional[str] = None) -> None:
    """Print a human-readable summary of the data catalog."""
    sources = get_data_sources(state)
    title = f"{state} " if state else "SC + NC "
    print(f"\n📋 {title}Local Government Data Catalog")
    print("=" * 70)

    by_state: Dict[str, List[DataSourceEntry]] = {}
    for s in sources:
        by_state.setdefault(s.state, []).append(s)

    for st, state_sources in sorted(by_state.items()):
        print(f"\n  {st} Counties ({len(state_sources)} total):")
        for src in sorted(state_sources, key=lambda x: x.county):
            blockers = f"  ⚠️  {len(src.known_blockers)} blocker(s)" if src.known_blockers else ""
            api_badge = "  🔌 API" if src.api_available else ""
            print(f"    • {src.county:20s} [{src.portal_type:25s}] {src.access_level:20s}{api_badge}{blockers}")

    print(f"\n  📊 Summary:")
    print(f"    Total counties:       {len(sources)}")
    print(f"    With API access:      {len(get_api_sources(state))}")
    print(f"    Legistar portals:     {len(get_legistar_sources(state))}")
    print(f"    With blockers:        {len(get_blocked_sources(state))}")

    blocked = get_blocked_sources(state)
    if blocked:
        print(f"\n  ⚠️  Access Blockers & Workarounds:")
        for src in blocked:
            print(f"\n    {src.county} County ({src.state}):")
            for b in src.known_blockers:
                print(f"      Blocker:    {b}")
            for w in src.workarounds:
                print(f"      Workaround: {w}")


# ---------------------------------------------------------------------------
# Legistar API helpers
# ---------------------------------------------------------------------------

LEGISTAR_API_BASE = "https://webapi.legistar.com/v1"

LEGISTAR_CLIENTS = {
    # SC
    "charleston_sc": "charlestoncountysc",
    "beaufort_sc": "beaufortsc",
    # NC
    "mecklenburg_nc": "mecknc",
    "new_hanover_nc": "nhcgov",
    "cabarrus_nc": "cabarruscounty",
}


def get_legistar_api_url(client_key: str, endpoint: str = "EventItems") -> str:
    """
    Build a Legistar REST API URL for a known client.

    Example:
        get_legistar_api_url("mecklenburg_nc", "EventItems")
        → "https://webapi.legistar.com/v1/mecknc/EventItems"
    """
    client = LEGISTAR_CLIENTS.get(client_key)
    if not client:
        raise ValueError(
            f"Unknown Legistar client '{client_key}'. "
            f"Known clients: {list(LEGISTAR_CLIENTS.keys())}"
        )
    return f"{LEGISTAR_API_BASE}/{client}/{endpoint}"


def fetch_legistar_events(client_key: str, top: int = 50) -> List[dict]:
    """
    Fetch recent meeting events from a Legistar API (no auth required).

    Args:
        client_key: One of the keys in LEGISTAR_CLIENTS.
        top: Number of recent events to fetch.

    Returns:
        List of event dicts from the Legistar API.
    """
    import json
    from urllib.request import urlopen, Request
    from urllib.error import URLError

    url = f"{get_legistar_api_url(client_key, 'Events')}?$top={top}&$orderby=EventDate desc"
    try:
        req = Request(url, headers={"User-Agent": "ClearCouncil/1.0 (public data access)"})
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, json.JSONDecodeError) as e:
        import logging
        logging.getLogger(__name__).warning(f"Legistar API fetch failed for {client_key}: {e}")
        return []
