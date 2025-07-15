"""Flask routes for ClearCouncil web interface."""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional

from ..config.settings import load_council_config, list_available_councils
from ..core.database import VectorDatabase
from .database import db
from .charts import InteractiveChartGenerator

logger = logging.getLogger(__name__)

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Initialize chart generator
chart_generator = InteractiveChartGenerator(db)


@main_bp.route('/')
def index():
    """Main dashboard page."""
    councils = list_available_councils()
    
    # Get default council if only one exists
    default_council = councils[0] if len(councils) == 1 else None
    
    if default_council:
        representatives = db.get_representatives(default_council)
        recent_meetings = db.get_meeting_dates(default_council)[:10]
        
        return render_template('dashboard.html',
                             councils=councils,
                             default_council=default_council,
                             representatives=representatives,
                             recent_meetings=recent_meetings)
    
    return render_template('index.html', councils=councils)


@main_bp.route('/transparency')
def data_transparency():
    """Data transparency page showing processed files and data sources."""
    councils = list_available_councils()
    council_data = {}
    
    for council_id in councils:
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get document statistics
                cursor.execute('''
                    SELECT COUNT(*) as total_docs,
                           COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed_docs,
                           MIN(processed_at) as first_processed,
                           MAX(processed_at) as last_processed
                    FROM documents 
                    WHERE council_id = ?
                ''', (council_id,))
                
                doc_stats = cursor.fetchone()
                
                # Get voting record statistics
                cursor.execute('''
                    SELECT COUNT(*) as total_votes,
                           COUNT(DISTINCT representative_name) as unique_reps,
                           MIN(meeting_date) as earliest_meeting,
                           MAX(meeting_date) as latest_meeting
                    FROM voting_records 
                    WHERE council_id = ?
                ''', (council_id,))
                
                vote_stats = cursor.fetchone()
                
                # Get recent processed documents
                cursor.execute('''
                    SELECT title, meeting_date, document_type, processed_at
                    FROM documents 
                    WHERE council_id = ? AND processing_status = 'completed'
                    ORDER BY processed_at DESC 
                    LIMIT 10
                ''', (council_id,))
                
                recent_docs = cursor.fetchall()
                
                council_data[council_id] = {
                    'name': load_council_config(council_id).name,
                    'doc_stats': doc_stats,
                    'vote_stats': vote_stats,
                    'recent_docs': recent_docs
                }
                
        except Exception as e:
            logger.error(f"Error loading transparency data for {council_id}: {e}")
            council_data[council_id] = {'error': str(e)}
    
    return render_template('transparency.html', 
                         councils=councils, 
                         council_data=council_data)


@main_bp.route('/council/<council_id>')
def council_overview(council_id):
    """Council overview page."""
    try:
        config = load_council_config(council_id)
        representatives = db.get_representatives(council_id)
        meeting_dates = db.get_meeting_dates(council_id)
        categories = db.get_case_categories(council_id)
        
        # Get council overview chart
        council_chart = chart_generator.create_council_overview_chart(council_id)
        
        return render_template('council_overview.html',
                             council=config,
                             representatives=representatives,
                             meeting_dates=meeting_dates,
                             categories=categories,
                             council_chart=council_chart)
    
    except Exception as e:
        logger.error(f"Error loading council overview: {e}")
        flash(f"Error loading council data: {str(e)}", 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/representative/<int:rep_id>')
def representative_detail(rep_id):
    """Representative detail page."""
    try:
        # Get representative info
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM representatives WHERE id = ?', (rep_id,))
            representative = dict(cursor.fetchone())
        
        if not representative:
            flash('Representative not found', 'error')
            return redirect(url_for('main.index'))
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Create dashboard
        dashboard = chart_generator.create_representative_dashboard(
            rep_id, representative['council_id'], start_date, end_date
        )
        
        # Get voting records for table
        voting_records = db.get_voting_records(
            representative['council_id'], rep_id, start_date, end_date
        )
        
        # Get available date range
        all_dates = db.get_meeting_dates(representative['council_id'])
        min_date = min(all_dates) if all_dates else None
        max_date = max(all_dates) if all_dates else None
        
        return render_template('representative_detail.html',
                             representative=representative,
                             dashboard=dashboard,
                             voting_records=voting_records,
                             min_date=min_date,
                             max_date=max_date,
                             start_date=start_date,
                             end_date=end_date)
    
    except Exception as e:
        logger.error(f"Error loading representative detail: {e}")
        flash(f"Error loading representative data: {str(e)}", 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/compare')
def compare_representatives():
    """Compare representatives page."""
    council_id = request.args.get('council_id')
    if not council_id:
        flash('Please select a council first', 'error')
        return redirect(url_for('main.index'))
    
    try:
        config = load_council_config(council_id)
        representatives = db.get_representatives(council_id)
        
        # Get selected representatives from query parameters
        selected_reps = request.args.getlist('representatives')
        selected_rep_ids = [int(rep_id) for rep_id in selected_reps if rep_id.isdigit()]
        
        comparison_chart = None
        if len(selected_rep_ids) >= 2:
            # Get date range
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            comparison_chart = chart_generator.create_comparison_chart(
                selected_rep_ids, council_id, start_date, end_date
            )
        
        # Get available date range
        all_dates = db.get_meeting_dates(council_id)
        min_date = min(all_dates) if all_dates else None
        max_date = max(all_dates) if all_dates else None
        
        return render_template('compare_representatives.html',
                             council=config,
                             representatives=representatives,
                             selected_rep_ids=selected_rep_ids,
                             comparison_chart=comparison_chart,
                             min_date=min_date,
                             max_date=max_date)
    
    except Exception as e:
        logger.error(f"Error loading comparison page: {e}")
        flash(f"Error loading comparison data: {str(e)}", 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/search')
def search():
    """Search page."""
    council_id = request.args.get('council_id')
    query = request.args.get('q', '')
    
    if not council_id:
        flash('Please select a council first', 'error')
        return redirect(url_for('main.index'))
    
    results = []
    if query:
        try:
            config = load_council_config(council_id)
            vector_db = VectorDatabase(config)
            results = vector_db.search(query, k=20)
        except Exception as e:
            logger.error(f"Search error: {e}")
            flash(f"Search error: {str(e)}", 'error')
    
    return render_template('search.html',
                         council_id=council_id,
                         query=query,
                         results=results)


@main_bp.route('/upload')
def upload_documents():
    """Upload documents page."""
    return render_template('upload.html')


@main_bp.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')


# API Routes
@api_bp.route('/councils')
def get_councils():
    """Get list of available councils."""
    try:
        councils = list_available_councils()
        council_data = []
        
        for council_id in councils:
            try:
                config = load_council_config(council_id)
                council_data.append({
                    'id': council_id,
                    'name': config.name,
                    'description': config.description
                })
            except Exception as e:
                logger.error(f"Error loading council {council_id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'councils': council_data
        })
    
    except Exception as e:
        logger.error(f"Error getting councils: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/council/<council_id>/representatives')
def get_representatives(council_id):
    """Get representatives for a council."""
    try:
        representatives = db.get_representatives(council_id)
        return jsonify({
            'success': True,
            'representatives': representatives
        })
    
    except Exception as e:
        logger.error(f"Error getting representatives: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/council/<council_id>/meeting-dates')
def get_meeting_dates(council_id):
    """Get meeting dates for a council."""
    try:
        dates = db.get_meeting_dates(council_id)
        return jsonify({
            'success': True,
            'dates': dates
        })
    
    except Exception as e:
        logger.error(f"Error getting meeting dates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/council/<council_id>/categories')
def get_categories(council_id):
    """Get case categories for a council."""
    try:
        categories = db.get_case_categories(council_id)
        return jsonify({
            'success': True,
            'categories': categories
        })
    
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/representative/<int:rep_id>/stats')
def get_representative_stats(rep_id):
    """Get statistics for a representative."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        stats = db.get_representative_stats(rep_id, start_date, end_date)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        logger.error(f"Error getting representative stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/representative/<int:rep_id>/dashboard')
def get_representative_dashboard(rep_id):
    """Get dashboard data for a representative."""
    try:
        # Get representative info
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM representatives WHERE id = ?', (rep_id,))
            representative = dict(cursor.fetchone())
        
        if not representative:
            return jsonify({
                'success': False,
                'error': 'Representative not found'
            }), 404
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Create dashboard
        dashboard = chart_generator.create_representative_dashboard(
            rep_id, representative['council_id'], start_date, end_date
        )
        
        return jsonify({
            'success': True,
            'dashboard': dashboard
        })
    
    except Exception as e:
        logger.error(f"Error getting representative dashboard: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/council/<council_id>/voting-records')
def get_voting_records(council_id):
    """Get voting records for a council."""
    try:
        representative_id = request.args.get('representative_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        records = db.get_voting_records(
            council_id, representative_id, start_date, end_date, category
        )
        
        return jsonify({
            'success': True,
            'records': records
        })
    
    except Exception as e:
        logger.error(f"Error getting voting records: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/search')
def api_search():
    """Search API endpoint."""
    try:
        council_id = request.args.get('council_id')
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not council_id or not query:
            return jsonify({
                'success': False,
                'error': 'Council ID and query are required'
            }), 400
        
        config = load_council_config(council_id)
        vector_db = VectorDatabase(config)
        results = vector_db.search(query, k=limit)
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Search API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/upload-document', methods=['POST'])
def upload_document():
    """Upload document API endpoint."""
    try:
        # This would handle document upload
        # For now, return a placeholder response
        return jsonify({
            'success': False,
            'error': 'Document upload not yet implemented'
        }), 501
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500