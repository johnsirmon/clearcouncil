#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

from clearcouncil.analysis.batch_processor import BatchVotingProcessor
from clearcouncil.config.settings import load_council_config
from clearcouncil.web.database import DatabaseManager
import asyncio
import sqlite3

async def update_web_database_with_deduplication():
    print('🔧 Updating web database with deduplicated representatives...')
    
    # Load council config and get deduplicated data
    council_config = load_council_config('york_county_sc')
    processor = BatchVotingProcessor(council_config)
    
    print('Loading and deduplicating voting data...')
    tracker, metadata = await processor.get_voting_data_for_period('since 2018', download_missing=False)
    
    print(f'Before deduplication: {len(tracker.representatives)} representatives')
    tracker.consolidate_duplicates()
    print(f'After deduplication: {len(tracker.representatives)} representatives')
    
    # Clear and repopulate the database
    print('Clearing existing web database data...')
    conn = sqlite3.connect('clearcouncil.db')
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM representatives')
    cursor.execute('DELETE FROM voting_records')
    
    print('Inserting deduplicated representatives...')
    
    # Insert deduplicated representatives
    for name, rep in tracker.representatives.items():
        cursor.execute('''
            INSERT INTO representatives (name, district, council_id, total_votes, 
                                       motions_made, seconds_given, 
                                       first_seen, last_seen, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (
            name,
            rep.district or 'Unknown',
            'york_county_sc',
            rep.total_votes,
            rep.motions_made,
            rep.seconds_given,
            metadata.get('date_range', {}).get('start', '2018-01-01'),
            metadata.get('date_range', {}).get('end', '2024-12-31')
        ))
    
    print('Inserting voting records...')
    
    # Insert voting records
    for case_votes in tracker.votes_by_case.values():
        for vote in case_votes:
            cursor.execute('''
                INSERT INTO voting_records (representative_name, case_number, vote_type,
                                          vote_date, description, category, council_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                vote.representative,
                vote.case_number,
                vote.vote_type,
                vote.date.isoformat() if vote.date else None,
                vote.description,
                vote.category,
                'york_county_sc'
            ))
    
    conn.commit()
    
    # Verify the results
    cursor.execute('SELECT COUNT(*) FROM representatives WHERE council_id = ?', ('york_county_sc',))
    rep_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM voting_records WHERE council_id = ?', ('york_county_sc',))
    vote_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f'✅ Database updated successfully!')
    print(f'   👥 Representatives: {rep_count}')
    print(f'   📊 Voting records: {vote_count}')
    
    # Show top representatives
    print('\nTop 10 representatives by votes:')
    sorted_reps = sorted(tracker.representatives.items(), key=lambda x: x[1].total_votes, reverse=True)
    for name, rep in sorted_reps[:10]:
        print(f'   {rep.total_votes:3d} votes - {name} ({rep.district})')

if __name__ == "__main__":
    try:
        asyncio.run(update_web_database_with_deduplication())
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
