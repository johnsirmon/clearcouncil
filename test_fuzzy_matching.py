#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/john/projects/clearcouncil/src')

from clearcouncil.analysis.batch_processor import BatchVotingProcessor
from clearcouncil.config.settings import load_council_config
import asyncio

async def test_fuzzy_matching():
    """Test fuzzy matching for representative names."""
    council_config = load_council_config('york_county_sc')
    processor = BatchVotingProcessor(council_config)
    
    print("🔍 Testing fuzzy matching for representative names...")
    
    # Get voting data
    representative_tracker, metadata = await processor.get_voting_data_for_period(
        'since 2018',
        download_missing=False
    )
    
    # Test cases for fuzzy matching
    test_cases = [
        "Allison Love",      # Exact match
        "allison love",      # Case insensitive
        "Alison Love",       # Slight misspelling
        "Allisson Love",     # Double 's'
        "Love",              # Last name only
        "A. Love",           # Initial + last name
        "Robert Winkler",    # Another exact match
        "Bob Winkler",       # Common nickname
        "R. Winkler",        # Initial + last name
        "Winkler",           # Last name only
        "District 2",        # District search
        "NonExistent Person" # Should not be found
    ]
    
    print(f"\n📊 Testing with {len(representative_tracker.representatives)} representatives found")
    print("\n🎯 Test Results:")
    print("=" * 60)
    
    for test_name in test_cases:
        rep = representative_tracker.get_representative(test_name, fuzzy_threshold=70)
        
        if rep:
            print(f"✅ '{test_name}' -> Found: '{rep.name}' (District: {rep.district})")
        else:
            # Get suggestions
            similar = representative_tracker.get_similar_representatives(test_name, limit=3)
            if similar:
                suggestions = ", ".join([f"'{name}' ({score}%)" for name, score in similar])
                print(f"❌ '{test_name}' -> Not found. Similar: {suggestions}")
            else:
                print(f"❌ '{test_name}' -> Not found. No similar names.")
    
    print("\n📋 All available representatives:")
    for i, name in enumerate(sorted(representative_tracker.representatives.keys()), 1):
        print(f"{i:2d}. {name}")

if __name__ == "__main__":
    asyncio.run(test_fuzzy_matching())
