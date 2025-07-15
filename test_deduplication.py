#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

from clearcouncil.analysis.batch_processor import BatchVotingProcessor
from clearcouncil.config.settings import load_council_config
import asyncio

async def test_deduplication():
    print('🔧 Testing deduplication process...')
    council_config = load_council_config('york_county_sc')
    processor = BatchVotingProcessor(council_config)
    
    # Get voting data
    print('Loading voting data...')
    tracker, metadata = await processor.get_voting_data_for_period('since 2018', download_missing=False)
    
    print(f'Before deduplication: {len(tracker.representatives)} representatives')
    
    # Show some examples before deduplication
    print('\nSample representatives before deduplication:')
    sample_names = list(tracker.representatives.keys())[:10]
    for name in sample_names:
        rep = tracker.representatives[name]
        print(f'  {rep.total_votes:3d} votes - {name}')
    
    # Apply deduplication
    print('\nApplying deduplication...')
    tracker.consolidate_duplicates()
    
    print(f'After deduplication: {len(tracker.representatives)} representatives')
    
    # Show top representatives after deduplication
    print('\nTop 15 representatives after deduplication:')
    sorted_reps = sorted(tracker.representatives.items(), key=lambda x: x[1].total_votes, reverse=True)
    for name, rep in sorted_reps[:15]:
        print(f'{rep.total_votes:3d} votes - {name} ({rep.district})')

if __name__ == "__main__":
    try:
        asyncio.run(test_deduplication())
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
