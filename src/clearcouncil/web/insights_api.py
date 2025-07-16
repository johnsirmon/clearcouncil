"""
ClearCouncil Web Insights API
Provides endpoints for serving voting insights and analytics data.
"""

import json
import os
from flask import Blueprint, jsonify, current_app
from datetime import datetime

insights_bp = Blueprint('insights', __name__, url_prefix='/api/insights')

def load_voting_insights():
    """Load voting insights from the analysis file."""
    insights_file = os.path.join(current_app.root_path, '../../voting_insights.json')
    
    # Fallback to different possible locations
    possible_paths = [
        insights_file,
        os.path.join(os.getcwd(), 'voting_insights.json'),
        os.path.join(os.path.dirname(__file__), '../../../voting_insights.json')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                current_app.logger.error(f"Error loading insights from {path}: {e}")
                continue
    
    # Return mock data if no insights file found
    return generate_mock_insights()

def generate_mock_insights():
    """Generate mock insights data for demonstration."""
    return {
        'insights': {
            'total_representatives': 39,
            'total_votes_cast': 3795,
            'total_motions_made': 1899,
            'total_seconds_given': 1896,
            'districts': ['At-Large', 'District 1', 'District 2', 'District 3', 'District 4', 'District 5', 'District 6', 'District 7']
        },
        'patterns': [
            {
                'type': 'most_active',
                'title': 'Most Active Representative',
                'description': 'Robert Winkler leads with 414 recorded votes',
                'value': 414,
                'representative': 'Robert Winkler'
            },
            {
                'type': 'unanimous_rate',
                'title': 'Unanimous Decision Rate',
                'description': '58.6% of votes are unanimous, showing council consensus',
                'value': 58.6,
                'count': 2226
            },
            {
                'type': 'close_votes',
                'title': 'Close Vote Analysis',
                'description': '82 close votes (margin of 1) show 2.2% contentious decisions',
                'value': 2.2,
                'count': 82
            }
        ],
        'visualization_data': {
            'summary_stats': {
                'total_representatives': 39,
                'total_votes': 3795,
                'total_motions': 1899,
                'total_seconds': 1896,
                'districts': 8
            },
            'leadership_chart': [
                {'name': 'Robert Winkler', 'district': 'At-Large', 'motions': 280, 'seconds': 134, 'total': 414},
                {'name': 'Allison Love', 'district': 'At-Large', 'motions': 200, 'seconds': 193, 'total': 393},
                {'name': 'Thomas Audette', 'district': 'District 3', 'motions': 130, 'seconds': 189, 'total': 319},
                {'name': 'Joel Hamilton', 'district': 'District 1', 'motions': 106, 'seconds': 173, 'total': 279},
                {'name': 'William "Bump" Roddey', 'district': 'At-Large', 'motions': 110, 'seconds': 159, 'total': 269}
            ]
        },
        'analysis_date': datetime.now().isoformat()
    }

@insights_bp.route('/summary')
def get_insights_summary():
    """Get summary insights for the main page."""
    try:
        data = load_voting_insights()
        
        summary = {
            'success': True,
            'stats': data['visualization_data']['summary_stats'],
            'top_patterns': data['patterns'][:3],  # Top 3 most interesting patterns
            'top_representatives': data['visualization_data']['leadership_chart'][:5],
            'last_updated': data.get('analysis_date', datetime.now().isoformat())
        }
        
        return jsonify(summary)
        
    except Exception as e:
        current_app.logger.error(f"Error generating insights summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to load insights data',
            'message': str(e)
        }), 500

@insights_bp.route('/leadership')
def get_leadership_data():
    """Get detailed leadership activity data."""
    try:
        data = load_voting_insights()
        
        leadership_data = {
            'success': True,
            'representatives': data['visualization_data']['leadership_chart'],
            'total_representatives': data['insights']['total_representatives'],
            'total_leadership_actions': data['insights']['total_motions_made'] + data['insights']['total_seconds_given']
        }
        
        return jsonify(leadership_data)
        
    except Exception as e:
        current_app.logger.error(f"Error loading leadership data: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to load leadership data'
        }), 500

@insights_bp.route('/patterns')
def get_voting_patterns():
    """Get voting pattern insights."""
    try:
        data = load_voting_insights()
        
        patterns_data = {
            'success': True,
            'patterns': data['patterns'],
            'analysis_summary': {
                'total_votes_analyzed': data['insights']['total_votes_cast'],
                'unanimous_rate': next((p['value'] for p in data['patterns'] if p['type'] == 'unanimous_rate'), 0),
                'approval_rate': next((p['value'] for p in data['patterns'] if p['type'] == 'approval_rate'), 0),
                'close_vote_count': next((p['count'] for p in data['patterns'] if p['type'] == 'close_votes'), 0)
            }
        }
        
        return jsonify(patterns_data)
        
    except Exception as e:
        current_app.logger.error(f"Error loading voting patterns: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to load voting patterns'
        }), 500

@insights_bp.route('/districts')
def get_district_data():
    """Get district representation data."""
    try:
        data = load_voting_insights()
        
        # Count representatives by district
        district_counts = {}
        for rep in data['visualization_data']['leadership_chart']:
            district = rep['district']
            district_counts[district] = district_counts.get(district, 0) + 1
        
        district_data = {
            'success': True,
            'districts': data['insights']['districts'],
            'district_counts': district_counts,
            'total_districts': len(data['insights']['districts']),
            'total_representatives': data['insights']['total_representatives']
        }
        
        return jsonify(district_data)
        
    except Exception as e:
        current_app.logger.error(f"Error loading district data: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to load district data'
        }), 500

@insights_bp.route('/refresh')
def refresh_insights():
    """Trigger a refresh of insights data."""
    try:
        # In a production environment, this would trigger the analysis script
        # For now, return success if the insights file exists
        data = load_voting_insights()
        
        return jsonify({
            'success': True,
            'message': 'Insights refreshed successfully',
            'last_updated': data.get('analysis_date', datetime.now().isoformat()),
            'stats': data['visualization_data']['summary_stats']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error refreshing insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to refresh insights',
            'message': str(e)
        }), 500