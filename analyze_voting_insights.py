#!/usr/bin/env python3
"""
ClearCouncil Data Insights Analyzer
Analyzes voting data to find interesting patterns and insights for the main page showcase.
"""

import json
import sys
from collections import defaultdict, Counter
from datetime import datetime
import re

def load_data():
    """Load the voting data from JSON file."""
    try:
        with open('clearcouncil_data.json', 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def analyze_representatives(data):
    """Analyze representative data for insights."""
    representatives = data.get('representatives', {})
    
    insights = {
        'total_representatives': len(representatives),
        'total_votes_cast': 0,
        'total_motions_made': 0,
        'total_seconds_given': 0,
        'most_active_rep': None,
        'districts': set(),
        'voting_patterns': {},
        'leadership_activity': {},
        'vote_results': Counter(),
        'case_categories': Counter()
    }
    
    # Analyze each representative
    for rep_name, rep_data in representatives.items():
        total_votes = rep_data.get('total_votes', 0)
        motions_made = rep_data.get('motions_made', 0)
        seconds_given = rep_data.get('seconds_given', 0)
        district = rep_data.get('district', 'Unknown')
        
        insights['total_votes_cast'] += total_votes
        insights['total_motions_made'] += motions_made
        insights['total_seconds_given'] += seconds_given
        insights['districts'].add(district)
        
        # Track most active representative by total votes
        if insights['most_active_rep'] is None or total_votes > insights['most_active_rep'][1]:
            insights['most_active_rep'] = (rep_name, total_votes)
        
        # Analyze voting patterns
        voting_record = rep_data.get('voting_record', [])
        rep_patterns = {
            'motions': 0,
            'seconds': 0,
            'approvals': 0,
            'unanimous_votes': 0,
            'close_votes': 0,
            'categories': Counter()
        }
        
        for vote in voting_record:
            vote_type = vote.get('vote_type', '')
            result = vote.get('result', '')
            case_number = vote.get('case_number', '')
            category = vote.get('case_category', 'unknown')
            
            # Count vote types
            if vote_type == 'motion':
                rep_patterns['motions'] += 1
            elif vote_type == 'second':
                rep_patterns['seconds'] += 1
            
            # Count results
            if result:
                insights['vote_results'][result] += 1
                if result == 'APPROVED':
                    rep_patterns['approvals'] += 1
            
            # Analyze vote margins from case_number
            if 'UNANIMOUS' in case_number:
                rep_patterns['unanimous_votes'] += 1
            elif re.search(r'\[(\d+)\s+TO\s+(\d+)\]', case_number):
                match = re.search(r'\[(\d+)\s+TO\s+(\d+)\]', case_number)
                if match:
                    yes_votes = int(match.group(1))
                    no_votes = int(match.group(2))
                    if abs(yes_votes - no_votes) <= 1:
                        rep_patterns['close_votes'] += 1
            
            # Count categories
            rep_patterns['categories'][category] += 1
            insights['case_categories'][category] += 1
        
        insights['voting_patterns'][rep_name] = rep_patterns
        
        # Leadership activity (motions + seconds)
        leadership_score = motions_made + seconds_given
        insights['leadership_activity'][rep_name] = {
            'motions': motions_made,
            'seconds': seconds_given,
            'total_leadership': leadership_score,
            'district': district
        }
    
    insights['districts'] = list(insights['districts'])
    return insights

def find_interesting_patterns(insights):
    """Find interesting patterns and stories in the data."""
    patterns = []
    
    # Most active representative
    if insights['most_active_rep']:
        patterns.append({
            'type': 'most_active',
            'title': 'Most Active Representative',
            'description': f"{insights['most_active_rep'][0]} leads with {insights['most_active_rep'][1]} recorded votes",
            'value': insights['most_active_rep'][1],
            'representative': insights['most_active_rep'][0]
        })
    
    # Leadership analysis
    leadership_ranking = sorted(
        insights['leadership_activity'].items(),
        key=lambda x: x[1]['total_leadership'],
        reverse=True
    )[:5]
    
    if leadership_ranking:
        top_leader = leadership_ranking[0]
        patterns.append({
            'type': 'top_leader',
            'title': 'Top Leadership Activity',
            'description': f"{top_leader[0]} shows highest leadership with {top_leader[1]['motions']} motions and {top_leader[1]['seconds']} seconds",
            'value': top_leader[1]['total_leadership'],
            'representative': top_leader[0],
            'motions': top_leader[1]['motions'],
            'seconds': top_leader[1]['seconds']
        })
    
    # Vote result analysis
    total_decisions = sum(insights['vote_results'].values())
    if total_decisions > 0:
        approval_rate = (insights['vote_results'].get('APPROVED', 0) / total_decisions) * 100
        patterns.append({
            'type': 'approval_rate',
            'title': 'Overall Approval Rate',
            'description': f"{approval_rate:.1f}% of all votes result in approval",
            'value': approval_rate,
            'total_decisions': total_decisions
        })
    
    # Unanimous vote analysis
    unanimous_count = 0
    close_vote_count = 0
    for rep_pattern in insights['voting_patterns'].values():
        unanimous_count += rep_pattern.get('unanimous_votes', 0)
        close_vote_count += rep_pattern.get('close_votes', 0)
    
    if unanimous_count > 0:
        unanimous_rate = (unanimous_count / insights['total_votes_cast']) * 100
        patterns.append({
            'type': 'unanimous_rate',
            'title': 'Unanimous Decision Rate',
            'description': f"{unanimous_rate:.1f}% of votes are unanimous, showing council consensus",
            'value': unanimous_rate,
            'count': unanimous_count
        })
    
    if close_vote_count > 0:
        close_vote_rate = (close_vote_count / insights['total_votes_cast']) * 100
        patterns.append({
            'type': 'close_votes',
            'title': 'Close Vote Analysis',
            'description': f"{close_vote_count} close votes (margin of 1) show {close_vote_rate:.1f}% contentious decisions",
            'value': close_vote_rate,
            'count': close_vote_count
        })
    
    # District representation
    patterns.append({
        'type': 'representation',
        'title': 'District Representation',
        'description': f"Tracking {len(insights['districts'])} districts with {insights['total_representatives']} representatives",
        'value': len(insights['districts']),
        'districts': insights['districts']
    })
    
    # Case category analysis
    top_categories = insights['case_categories'].most_common(3)
    if top_categories:
        patterns.append({
            'type': 'top_categories',
            'title': 'Most Common Case Types',
            'description': f"Top category: {top_categories[0][0]} ({top_categories[0][1]} cases)",
            'categories': top_categories
        })
    
    return patterns

def generate_visualization_data(insights, patterns, data):
    """Generate data structures for visualizations."""
    viz_data = {
        'summary_stats': {
            'total_representatives': insights['total_representatives'],
            'total_votes': insights['total_votes_cast'],
            'total_motions': insights['total_motions_made'],
            'total_seconds': insights['total_seconds_given'],
            'districts': len(insights['districts'])
        },
        'leadership_chart': [],
        'activity_chart': [],
        'vote_results_chart': [],
        'district_chart': []
    }
    
    # Leadership activity chart data (top 10)
    leadership_ranking = sorted(
        insights['leadership_activity'].items(),
        key=lambda x: x[1]['total_leadership'],
        reverse=True
    )[:10]
    
    for rep, data in leadership_ranking:
        viz_data['leadership_chart'].append({
            'name': rep,
            'district': data['district'],
            'motions': data['motions'],
            'seconds': data['seconds'],
            'total': data['total_leadership']
        })
    
    # Most active representatives by votes (top 10)
    # Get vote counts from the original representatives data
    activity_ranking = []
    representatives = data.get('representatives', {})
    
    for name, rep_data in representatives.items():
        total_votes = rep_data.get('total_votes', 0)
        district = rep_data.get('district', 'Unknown')
        activity_ranking.append((name, total_votes, district))
    
    activity_ranking = sorted(activity_ranking, key=lambda x: x[1], reverse=True)[:10]
    
    for name, votes, district in activity_ranking:
        viz_data['activity_chart'].append({
            'name': name,
            'district': district,
            'votes': votes
        })
    
    # Vote results distribution
    for result, count in insights['vote_results'].items():
        viz_data['vote_results_chart'].append({
            'result': result,
            'count': count
        })
    
    # District representation
    district_counts = defaultdict(int)
    for rep_data in insights['voting_patterns'].values():
        # Get district from leadership_activity which has district info
        for name, leader_data in insights['leadership_activity'].items():
            if leader_data['district'] != 'Unknown':
                district_counts[leader_data['district']] += 1
                break
    
    for district, count in district_counts.items():
        viz_data['district_chart'].append({
            'district': district,
            'representatives': count
        })
    
    return viz_data

def main():
    """Main analysis function."""
    print("🔍 ClearCouncil Data Analysis Starting...")
    print("=" * 50)
    
    # Load data
    data = load_data()
    if not data:
        return
    
    # Analyze representatives
    print("📊 Analyzing representatives and voting patterns...")
    insights = analyze_representatives(data)
    
    # Find interesting patterns
    print("🎯 Finding interesting patterns...")
    patterns = find_interesting_patterns(insights)
    
    # Generate visualization data
    print("📈 Generating visualization data...")
    viz_data = generate_visualization_data(insights, patterns, data)
    
    # Print summary
    print("\n🏛️ CLEARCOUNCIL INSIGHTS SUMMARY")
    print("=" * 40)
    print(f"📊 Total Representatives: {insights['total_representatives']}")
    print(f"🗳️  Total Votes Recorded: {insights['total_votes_cast']:,}")
    print(f"📋 Total Motions Made: {insights['total_motions_made']:,}")
    print(f"✋ Total Seconds Given: {insights['total_seconds_given']:,}")
    print(f"🏘️  Districts Represented: {len(insights['districts'])}")
    
    print("\n🎯 KEY INSIGHTS:")
    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern['title']}: {pattern['description']}")
    
    print("\n📈 TOP 5 MOST ACTIVE REPRESENTATIVES:")
    activity_ranking = sorted(
        [(name, data) for name, data in insights['leadership_activity'].items()],
        key=lambda x: x[1]['total_leadership'],
        reverse=True
    )[:5]
    
    for i, (name, data) in enumerate(activity_ranking, 1):
        print(f"{i}. {name} ({data['district']}): {data['motions']} motions, {data['seconds']} seconds")
    
    # Save insights for web interface
    output_data = {
        'insights': insights,
        'patterns': patterns,
        'visualization_data': viz_data,
        'analysis_date': datetime.now().isoformat()
    }
    
    with open('voting_insights.json', 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n✅ Analysis complete! Results saved to voting_insights.json")
    print(f"📁 File size: {len(json.dumps(output_data, default=str))} characters")

if __name__ == "__main__":
    main()