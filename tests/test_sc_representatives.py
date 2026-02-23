#!/usr/bin/env python3
"""
Tests for the South Carolina representative lookup module.

Run with:
    python tests/test_sc_representatives.py
"""

import sys
import os

# Ensure src is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from clearcouncil.representatives.models import Chamber, SCRepresentative
from clearcouncil.representatives.county_councils import (
    get_county_council,
    list_supported_counties,
    YORK_COUNTY_COUNCIL,
)
from clearcouncil.representatives.sc_legislature import (
    _get_static_senate_members,
    _get_static_house_members,
    _normalise_name,
)
from clearcouncil.representatives.lookup import SCRepresentativeLookup


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _ok(condition: bool, message: str) -> bool:
    if condition:
        print(f"  ✅ PASS: {message}")
    else:
        print(f"  ❌ FAIL: {message}")
    return condition


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

def test_sc_representative_model():
    print("\n--- test_sc_representative_model ---")
    rep = SCRepresentative(
        name="Joel Hamilton",
        district="1",
        chamber=Chamber.COUNTY_COUNCIL,
        county="York",
        counties=["York"],
    )
    assert _ok(rep.name == "Joel Hamilton", "name is correct")
    assert _ok(rep.district == "1", "district is correct")
    assert _ok(rep.chamber == Chamber.COUNTY_COUNCIL, "chamber is correct")
    d = rep.to_dict()
    assert _ok(d["name"] == "Joel Hamilton", "to_dict name")
    assert _ok(d["chamber"] == "county_council", "to_dict chamber value")


# ---------------------------------------------------------------------------
# Static data tests
# ---------------------------------------------------------------------------

def test_static_senate_data():
    print("\n--- test_static_senate_data ---")
    members = _get_static_senate_members()
    assert _ok(len(members) == 46, f"46 senate districts loaded (got {len(members)})")
    districts = {m.district for m in members}
    assert _ok("1" in districts, "district 1 present")
    assert _ok("46" in districts, "district 46 present")
    # All should be SENATE chamber
    assert _ok(all(m.chamber == Chamber.SENATE for m in members), "all chamber=SENATE")


def test_static_house_data():
    print("\n--- test_static_house_data ---")
    members = _get_static_house_members()
    assert _ok(len(members) > 0, f"house data loaded ({len(members)} members)")
    assert _ok(all(m.chamber == Chamber.HOUSE for m in members), "all chamber=HOUSE")
    # All members should have non-empty names and districts
    assert _ok(
        all(m.name and m.district for m in members),
        "all members have name and district",
    )


def test_normalise_name():
    print("\n--- test_normalise_name ---")
    assert _ok(_normalise_name("Smith, John") == "John Smith", "Last, First -> First Last")
    assert _ok(_normalise_name("Johnson, Mary Beth") == "Mary Beth Johnson", "multi first name")
    assert _ok(_normalise_name("Joel Hamilton") == "Joel Hamilton", "already normal")
    assert _ok(_normalise_name("  Padded  ") == "Padded", "strips whitespace")


# ---------------------------------------------------------------------------
# County council tests
# ---------------------------------------------------------------------------

def test_york_county_council():
    print("\n--- test_york_county_council ---")
    members = get_county_council("York")
    assert _ok(len(members) > 0, f"York County council loaded ({len(members)} members)")
    assert _ok(
        all(m.chamber == Chamber.COUNTY_COUNCIL for m in members),
        "all chamber=COUNTY_COUNCIL",
    )
    names = [m.name for m in members]
    assert _ok("Joel Hamilton" in names, "Joel Hamilton present")
    assert _ok("Allison Love" in names, "Allison Love present")


def test_county_case_insensitive():
    print("\n--- test_county_case_insensitive ---")
    members_lower = get_county_council("york")
    members_upper = get_county_council("YORK")
    members_title = get_county_council("York")
    assert _ok(
        len(members_lower) == len(members_upper) == len(members_title),
        "case-insensitive county lookup",
    )


def test_list_supported_counties():
    print("\n--- test_list_supported_counties ---")
    counties = list_supported_counties()
    assert _ok("York" in counties, "York in supported counties")
    assert _ok("Charleston" in counties, "Charleston in supported counties")
    assert _ok("Greenville" in counties, "Greenville in supported counties")
    assert _ok(len(counties) >= 10, f"at least 10 counties supported (got {len(counties)})")


def test_unsupported_county_returns_empty():
    print("\n--- test_unsupported_county_returns_empty ---")
    members = get_county_council("Atlantis")
    assert _ok(members == [], "unsupported county returns empty list")


# ---------------------------------------------------------------------------
# Lookup service tests
# ---------------------------------------------------------------------------

def test_lookup_find_by_name_exact():
    print("\n--- test_lookup_find_by_name_exact ---")
    lookup = SCRepresentativeLookup()
    results = lookup.find_by_name("Joel Hamilton", threshold=80)
    assert _ok(len(results) > 0, "found at least one result for 'Joel Hamilton'")
    best_name, best_score = results[0][0].name, results[0][1]
    assert _ok(best_score >= 80, f"best match score >= 80 (got {best_score})")
    assert _ok("Hamilton" in best_name, f"best match includes 'Hamilton' (got '{best_name}')")


def test_lookup_find_by_name_fuzzy():
    print("\n--- test_lookup_find_by_name_fuzzy ---")
    lookup = SCRepresentativeLookup()
    # Slight misspelling of "Allison Love"
    results = lookup.find_by_name("Alison Love", threshold=50)
    assert _ok(len(results) > 0, "fuzzy match found for 'Alison Love'")


def test_lookup_find_by_district_senate():
    print("\n--- test_lookup_find_by_district_senate ---")
    lookup = SCRepresentativeLookup()
    results = lookup.find_by_district("13", chamber=Chamber.SENATE)
    assert _ok(len(results) > 0, "found senator for district 13")
    assert _ok(
        all(r.chamber == Chamber.SENATE for r in results),
        "all results are SENATE chamber",
    )


def test_lookup_find_by_district_county():
    print("\n--- test_lookup_find_by_district_county ---")
    lookup = SCRepresentativeLookup()
    results = lookup.find_by_district("1", chamber=Chamber.COUNTY_COUNCIL, county="York")
    assert _ok(len(results) > 0, "found York County district 1")
    assert _ok(results[0].county == "York", "result is from York County")


def test_lookup_find_by_county():
    print("\n--- test_lookup_find_by_county ---")
    lookup = SCRepresentativeLookup()
    results = lookup.find_by_county("York")
    assert _ok(len(results) > 0, "found representatives for York County")
    # Should include state legislators AND county council
    chambers = {r.chamber for r in results}
    assert _ok(Chamber.COUNTY_COUNCIL in chambers, "York results include county council")


def test_lookup_find_by_county_state_only():
    print("\n--- test_lookup_find_by_county_state_only ---")
    lookup = SCRepresentativeLookup()
    house_results = lookup.find_by_county("York", chamber=Chamber.HOUSE)
    assert _ok(len(house_results) > 0, "York County has SC House members")
    assert _ok(
        all(r.chamber == Chamber.HOUSE for r in house_results),
        "all results are HOUSE chamber",
    )


def test_lookup_find_by_chamber():
    print("\n--- test_lookup_find_by_chamber ---")
    lookup = SCRepresentativeLookup()
    senate = lookup.find_by_chamber(Chamber.SENATE)
    assert _ok(len(senate) >= 46, f"at least 46 SC Senate members (got {len(senate)})")
    county_council = lookup.find_by_chamber(Chamber.COUNTY_COUNCIL)
    assert _ok(len(county_council) > 0, "county council members found")


def test_lookup_summary():
    print("\n--- test_lookup_summary ---")
    lookup = SCRepresentativeLookup()
    summary = lookup.get_summary()
    assert _ok("sc_house_members" in summary, "summary has sc_house_members")
    assert _ok("sc_senate_members" in summary, "summary has sc_senate_members")
    assert _ok("county_councils" in summary, "summary has county_councils")
    assert _ok(summary["sc_senate_members"] >= 46, "at least 46 senate members in summary")
    assert _ok(len(summary["supported_counties"]) >= 10, "at least 10 supported counties")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_all_tests():
    test_fns = [
        test_sc_representative_model,
        test_static_senate_data,
        test_static_house_data,
        test_normalise_name,
        test_york_county_council,
        test_county_case_insensitive,
        test_list_supported_counties,
        test_unsupported_county_returns_empty,
        test_lookup_find_by_name_exact,
        test_lookup_find_by_name_fuzzy,
        test_lookup_find_by_district_senate,
        test_lookup_find_by_district_county,
        test_lookup_find_by_county,
        test_lookup_find_by_county_state_only,
        test_lookup_find_by_chamber,
        test_lookup_summary,
    ]

    print("\n🔍 Running SC Representatives tests...\n")
    passed = 0
    failed = 0
    errors = 0

    for fn in test_fns:
        try:
            fn()
            passed += 1
        except AssertionError as exc:
            failed += 1
            print(f"  ⛔ AssertionError in {fn.__name__}: {exc}")
        except Exception as exc:
            errors += 1
            print(f"  💥 Exception in {fn.__name__}: {exc}")

    total = len(test_fns)
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed, {errors} errors")
    if failed + errors == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")
    return failed + errors == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
