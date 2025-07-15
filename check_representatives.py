#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/john/projects/clearcouncil/src')

from clearcouncil.analysis.batch_processor import BatchVotingProcessor
from clearcouncil.analysis.voting_analyzer import VotingAnalyzer
from clearcouncil.config.settings import load_council_config
from datetime import datetime
import asyncio

async def main():
    council_config = load_council_config('york_county_sc')
    processor = BatchVotingProcessor(council_config)
    
    print("🔍 Processing voting data to find representatives...")
    
    # Get voting data using the async method
    representative_tracker, metadata = await processor.get_voting_data_for_period(
        'since 2018',
        download_missing=False  # Don't download, just use existing data
    )
    
    # Get list of all representatives from the tracker
    representatives = list(representative_tracker.representatives.keys())
    
    print(f"\n📊 Found {len(representatives)} representatives:")
    for i, rep in enumerate(representatives, 1):
        print(f"{i:2d}. {rep}")
    
    # Look for Love variations
    love_reps = [rep for rep in representatives if 'love' in rep.lower()]
    if love_reps:
        print(f"\n💕 Representatives with 'Love' in name:")
        for rep in love_reps:
            print(f"   - {rep}")
    else:
        print("\n❌ No representatives found with 'Love' in name")
        
    # Let's also search for similar sounding names
    similar_names = []
    search_terms = ['love', 'lov', 'allison', 'alison', 'alisson']
    for rep in representatives:
        for term in search_terms:
            if term in rep.lower():
                similar_names.append(rep)
                break
    
    if similar_names:
        print(f"\n🔍 Representatives with similar names:")
        for rep in similar_names:
            print(f"   - {rep}")

if __name__ == "__main__":
    asyncio.run(main())
