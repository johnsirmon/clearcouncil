"""
ClearCouncil MCP Server.

Exposes ClearCouncil's local-government transparency capabilities as
Model Context Protocol (MCP) tools so that AI assistants (Claude, etc.)
can query representative data, voting records, data-source catalogs,
and the municipal glossary without requiring users to run CLI commands.

Usage:
    # stdio transport (default — works with Claude Desktop / MCP clients)
    python clearcouncil_mcp.py

    # or via the installed entry point
    clearcouncil-mcp

Environment variables (optional):
    OPENAI_API_KEY — required only for search_documents / analyze_voting tools.
    CLEARCOUNCIL_LOG_LEVEL — DEBUG | INFO | WARNING | ERROR (default: WARNING)
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("clearcouncil.mcp")

# ---------------------------------------------------------------------------
# Lazy imports – heavy dependencies are deferred so the server starts fast
# even when optional packages (FAISS, pandas, …) are not installed.
# ---------------------------------------------------------------------------

def _get_glossary():
    from ..glossary.municipal_glossary import MunicipalGlossary
    return MunicipalGlossary()


def _get_sc_lookup(force_refresh: bool = False):
    from ..representatives.lookup import SCRepresentativeLookup
    return SCRepresentativeLookup(force_refresh=force_refresh)


def _get_nc_lookup(force_refresh: bool = False):
    from ..representatives.nc_lookup import NCRepresentativeLookup
    return NCRepresentativeLookup(force_refresh=force_refresh)


def _get_data_catalog():
    from ..core.state_data_catalog import (
        SC_DATA_SOURCES,
        NC_DATA_SOURCES,
    )
    return SC_DATA_SOURCES, NC_DATA_SOURCES


def _load_council_config(council_id: str):
    from ..config.settings import load_council_config
    return load_council_config(council_id)


# ---------------------------------------------------------------------------
# MCP server setup
# ---------------------------------------------------------------------------

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The 'mcp' package is required to run the ClearCouncil MCP server.\n"
        "Install it with: pip install 'mcp>=1.23.0'"
    ) from exc

mcp = FastMCP(
    name="clearcouncil",
    instructions=(
        "ClearCouncil gives you access to local government transparency data "
        "for South Carolina and North Carolina. You can look up elected "
        "representatives, browse public data-source catalogs, explain municipal "
        "terminology, and (when documents have been processed) search council "
        "meeting minutes or analyse voting records."
    ),
)

# ---------------------------------------------------------------------------
# Tool: list_councils
# ---------------------------------------------------------------------------

@mcp.tool()
def list_councils() -> str:
    """List the council identifiers that ClearCouncil has YAML configs for.

    Returns a JSON array of objects with keys ``id`` and ``name``.
    """
    from ..config.settings import list_available_councils, load_council_config

    results: List[Dict[str, str]] = []
    for council_id in list_available_councils():
        try:
            cfg = load_council_config(council_id)
            results.append({"id": council_id, "name": cfg.name})
        except Exception:
            results.append({"id": council_id, "name": "(configuration error)"})
    return json.dumps(results, indent=2)


# ---------------------------------------------------------------------------
# Tool: explain_terms
# ---------------------------------------------------------------------------

@mcp.tool()
def explain_terms(
    terms: List[str],
    category: Optional[str] = None,
) -> str:
    """Explain one or more municipal government terms from the built-in glossary.

    Args:
        terms: List of terms to look up, e.g. ``["movant", "rezoning"]``.
               Pass ``["all"]`` to receive a category overview.
        category: Optional category name (e.g. ``"voting"``, ``"zoning"``)
                  to retrieve every term in that group.

    Returns:
        JSON object mapping each requested term to its definition, explanation,
        example, and category.  Unknown terms get ``null``.
    """
    glossary = _get_glossary()

    if category:
        terms_in_cat = glossary.get_terms_by_category(category)
        if not terms_in_cat:
            all_cats = glossary.get_all_categories()
            return json.dumps({
                "error": f"Category '{category}' not found.",
                "available_categories": all_cats,
            })
        return json.dumps(terms_in_cat, indent=2)

    if "all" in terms:
        categories = glossary.get_all_categories()
        summary: Dict[str, Any] = {}
        for cat in categories:
            cat_terms = glossary.get_terms_by_category(cat)
            summary[cat] = list(cat_terms.keys())
        return json.dumps({"categories": summary}, indent=2)

    result: Dict[str, Any] = {}
    for term in terms:
        result[term] = glossary.get_definition(term)
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Tool: lookup_sc_representative
# ---------------------------------------------------------------------------

@mcp.tool()
def lookup_sc_representative(
    query: str,
    chamber: Optional[str] = None,
    county: Optional[str] = None,
    threshold: int = 60,
) -> str:
    """Look up South Carolina representatives by name, district number, or county.

    Args:
        query: A person's name, a numeric district (e.g. ``"42"``), or a
               county name (when used together with *county*).
        chamber: Optional filter – one of ``"house"``, ``"senate"``, or
                 ``"county_council"``.
        county: Restrict the search to a specific SC county name
                (e.g. ``"York"``).
        threshold: Minimum fuzzy-match score 0-100 for name searches
                   (default 60).

    Returns:
        JSON array of representative objects with keys: name, district,
        chamber, party, counties, phone, email, address, website, county.
    """
    from ..representatives.models import Chamber

    lookup = _get_sc_lookup()
    query = query.strip()
    chamber_filter = Chamber(chamber) if chamber else None

    # District lookup
    if query.isdigit() or query.lower() in ("at-large", "at large"):
        results = lookup.find_by_district(query, chamber=chamber_filter, county=county)
        return json.dumps([r.to_dict() for r in results], indent=2)

    # County-only lookup
    if county:
        results = lookup.find_by_county(county, chamber=chamber_filter)
        return json.dumps([r.to_dict() for r in results], indent=2)

    # Name fuzzy search
    matches = lookup.find_by_name(query, threshold=threshold)
    if chamber_filter:
        matches = [(r, s) for r, s in matches if r.chamber == chamber_filter]

    return json.dumps(
        [{"score": score, **rep.to_dict()} for rep, score in matches],
        indent=2,
    )


# ---------------------------------------------------------------------------
# Tool: list_sc_representatives
# ---------------------------------------------------------------------------

@mcp.tool()
def list_sc_representatives(
    chamber: Optional[str] = None,
    county: Optional[str] = None,
    refresh: bool = False,
) -> str:
    """List South Carolina elected representatives.

    Without filters, returns a summary (counts by chamber and county).
    Provide *chamber* and/or *county* to get the full member list.

    Args:
        chamber: ``"house"``, ``"senate"``, or ``"county_council"``.
        county: SC county name (e.g. ``"Richland"``).
        refresh: When ``True``, re-fetch data from the SC Legislature website.

    Returns:
        JSON object.  If no filters are given: a summary dict.
        Otherwise: a JSON array of representative objects.
    """
    from ..representatives.models import Chamber

    lookup = _get_sc_lookup(force_refresh=refresh)
    chamber_filter = Chamber(chamber) if chamber else None

    if not chamber and not county:
        return json.dumps(lookup.get_summary(), indent=2)

    if county:
        results = lookup.find_by_county(county, chamber=chamber_filter)
    else:
        results = lookup.find_by_chamber(chamber_filter)

    return json.dumps([r.to_dict() for r in results], indent=2)


# ---------------------------------------------------------------------------
# Tool: lookup_nc_representative
# ---------------------------------------------------------------------------

@mcp.tool()
def lookup_nc_representative(
    query: str,
    chamber: Optional[str] = None,
    county: Optional[str] = None,
    threshold: int = 60,
) -> str:
    """Look up North Carolina representatives by name, district, or county.

    Args:
        query: Name, numeric district, or county search term.
        chamber: Optional filter – ``"house"``, ``"senate"``, or
                 ``"county_council"``.
        county: Restrict to a specific NC county (e.g. ``"Mecklenburg"``).
        threshold: Minimum fuzzy-match score 0-100 (default 60).

    Returns:
        JSON array of representative objects.
    """
    try:
        from ..representatives.nc_lookup import NCRepresentativeLookup
        from ..representatives.models import Chamber
    except ImportError:
        return json.dumps({"error": "NC representative data module not available."})

    lookup = NCRepresentativeLookup(force_refresh=False)
    query = query.strip()
    chamber_filter = Chamber(chamber) if chamber else None

    if query.isdigit() or query.lower() in ("at-large", "at large"):
        results = lookup.find_by_district(query, chamber=chamber_filter, county=county)
        return json.dumps([r.to_dict() for r in results], indent=2)

    if county:
        results = lookup.find_by_county(county, chamber=chamber_filter)
        return json.dumps([r.to_dict() for r in results], indent=2)

    matches = lookup.find_by_name(query, threshold=threshold)
    if chamber_filter:
        matches = [(r, s) for r, s in matches if r.chamber == chamber_filter]

    return json.dumps(
        [{"score": score, **rep.to_dict()} for rep, score in matches],
        indent=2,
    )


# ---------------------------------------------------------------------------
# Tool: list_nc_representatives
# ---------------------------------------------------------------------------

@mcp.tool()
def list_nc_representatives(
    chamber: Optional[str] = None,
    county: Optional[str] = None,
    refresh: bool = False,
) -> str:
    """List North Carolina elected representatives.

    Without filters returns a summary; with *chamber* / *county* returns
    the full member list.

    Args:
        chamber: ``"house"``, ``"senate"``, or ``"county_council"``.
        county: NC county name.
        refresh: Re-fetch from NC General Assembly website when ``True``.

    Returns:
        JSON summary or array of representative objects.
    """
    try:
        from ..representatives.nc_lookup import NCRepresentativeLookup
        from ..representatives.models import Chamber
    except ImportError:
        return json.dumps({"error": "NC representative data module not available."})

    lookup = NCRepresentativeLookup(force_refresh=refresh)
    chamber_filter = Chamber(chamber) if chamber else None

    if not chamber and not county:
        return json.dumps(lookup.get_summary(), indent=2)

    if county:
        results = lookup.find_by_county(county, chamber=chamber_filter)
    else:
        results = lookup.find_by_chamber(chamber_filter)

    return json.dumps([r.to_dict() for r in results], indent=2)


# ---------------------------------------------------------------------------
# Tool: discover_data_sources
# ---------------------------------------------------------------------------

@mcp.tool()
def discover_data_sources(
    state: Optional[str] = None,
    blocked_only: bool = False,
    api_only: bool = False,
    include_municipalities: bool = False,
) -> str:
    """Browse the SC/NC public data-source catalog.

    Returns details about county government document portals including their
    URL, portal type, known access blockers, and legally-permissible
    workarounds.

    Args:
        state: Filter by state – ``"SC"`` or ``"NC"`` (default: both).
        blocked_only: Only include entries that have known access blockers.
        api_only: Only include entries that expose a programmatic API.
        include_municipalities: Include municipal (city/town) entries when
                                ``True`` (default ``False``).

    Returns:
        JSON array of data-source entries.
    """
    from ..core.state_data_catalog import get_data_sources
    from dataclasses import asdict

    sources = get_data_sources(state=state, include_municipalities=include_municipalities)

    if blocked_only:
        from ..core.state_data_catalog import get_blocked_sources
        sources = get_blocked_sources(state=state)
    if api_only:
        from ..core.state_data_catalog import get_api_sources
        sources = get_api_sources(state=state)

    return json.dumps([asdict(s) for s in sources], indent=2)


# ---------------------------------------------------------------------------
# Tool: search_documents
# ---------------------------------------------------------------------------

@mcp.tool()
def search_documents(
    council_id: str,
    query: str,
    limit: int = 5,
) -> str:
    """Search processed council meeting documents using semantic / keyword search.

    Requires that documents have already been processed with
    ``clearcouncil process-pdfs <council_id>``.  Also requires
    ``OPENAI_API_KEY`` to be set in the environment.

    Args:
        council_id: Council identifier (see ``list_councils``).
        query: Natural-language or keyword search query.
        limit: Maximum number of results to return (default 5).

    Returns:
        JSON array of search results, each with ``content``, ``score``,
        and ``metadata`` keys.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return json.dumps({
            "error": (
                "OPENAI_API_KEY environment variable is required for "
                "document search.  Set it in your .env file."
            )
        })

    try:
        config = _load_council_config(council_id)
        from ..core.database import VectorDatabase
        db = VectorDatabase(config)
        results = db.search(query, k=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as exc:
        logger.exception("search_documents failed")
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Tool: analyze_voting
# ---------------------------------------------------------------------------

@mcp.tool()
async def analyze_voting(
    council_id: str,
    representative: str,
    time_range: str,
    compare_with: Optional[List[str]] = None,
    download_missing: bool = False,
) -> str:
    """Analyze voting patterns for a council representative.

    Requires that documents have been processed (``process-pdfs``) and
    ``OPENAI_API_KEY`` to be set.

    Args:
        council_id: Council identifier (see ``list_councils``).
        representative: Representative name or district label, e.g.
                        ``"District 2"`` or ``"John Smith"``.
        time_range: Human-readable time range, e.g. ``"last year"``,
                    ``"last 6 months"``,
                    ``"2023-01-01 to 2024-01-01"``.
        compare_with: Optional list of other representative names to include
                      in a side-by-side comparison.
        download_missing: Attempt to download missing documents when
                          ``True`` (default ``False``).

    Returns:
        JSON analysis object with voting summary, breakdown, and detailed
        vote list.
    """
    if not os.getenv("OPENAI_API_KEY"):
        return json.dumps({
            "error": (
                "OPENAI_API_KEY environment variable is required for "
                "voting analysis.  Set it in your .env file."
            )
        })

    try:
        config = _load_council_config(council_id)

        from ..analysis.batch_processor import BatchVotingProcessor
        from ..analysis.voting_analyzer import VotingAnalyzer

        batch_processor = BatchVotingProcessor(config)
        analyzer = VotingAnalyzer(config)

        _tracker, _metadata = await batch_processor.get_voting_data_for_period(
            time_range,
            download_missing=download_missing,
            representative_filter=representative,
        )

        analysis = analyzer.analyze_representative_voting(
            representative,
            time_range,
            comparison_reps=compare_with,
        )

        return json.dumps(analysis, indent=2, default=str)
    except Exception as exc:
        logger.exception("analyze_voting failed")
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    """Start the ClearCouncil MCP server (stdio transport)."""
    log_level = os.getenv("CLEARCOUNCIL_LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.WARNING))
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
