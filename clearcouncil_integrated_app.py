#!/usr/bin/env python3
"""
ClearCouncil Integrated Web Application
Combines main web app with chat functionality in a comprehensive design
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, session, flash, redirect, url_for
from flask import Blueprint, current_app, g
from werkzeug.exceptions import abort
import requests
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed, using environment variables directly")

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///clearcouncil.db')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITHUB_API_BASE = "https://models.inference.ai.azure.com"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = Path.cwd() / 'uploads'

# Database utility functions
def get_db_connection():
    """Get database connection with row factory for dict-like access"""
    conn = sqlite3.connect('clearcouncil.db')
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

# Data access functions
def get_representatives_summary():
    """Get summary statistics for representatives"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_reps,
                COUNT(DISTINCT district) as total_districts,
                SUM(total_votes) as total_votes,
                AVG(total_votes) as avg_votes_per_rep
            FROM representatives
        ''')
        return dict(cursor.fetchone())

def get_top_representatives(limit=5):
    """Get top representatives by vote count"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, district, total_votes, motions_made, seconds_given
            FROM representatives 
            ORDER BY total_votes DESC 
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_voting_patterns():
    """Get voting pattern statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                vote_type,
                COUNT(*) as count,
                COUNT(DISTINCT representative_name) as unique_reps
            FROM voting_records 
            WHERE vote_type IS NOT NULL
            GROUP BY vote_type
        ''')
        return [dict(row) for row in cursor.fetchall()]

def search_voting_records(query, limit=20):
    """Search voting records by representative name or case details"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                representative_name,
                district,
                case_number,
                vote_type,
                case_category,
                meeting_date
            FROM voting_records 
            WHERE 
                representative_name LIKE ? OR 
                case_number LIKE ? OR
                case_category LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        return [dict(row) for row in cursor.fetchall()]

# Chat functionality
class ChatManager:
    """Manages chat interactions with GitHub AI models"""
    
    def __init__(self, github_token=None):
        self.github_token = github_token or Config.GITHUB_TOKEN
        self.api_base = Config.GITHUB_API_BASE
        self.model = "gpt-4o-mini"  # Default model
        
    def send_message(self, message, context=None):
        """Send message to AI and get response"""
        if not self.github_token:
            return {"error": "GitHub token not configured"}
            
        # Build system context with council data
        system_context = self._build_system_context(context)
        
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_context},
                {"role": "user", "content": message}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result["choices"][0]["message"]["content"],
                    "model": self.model
                }
            else:
                return {"error": f"API Error: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def _build_system_context(self, context=None):
        """Build system context with council data"""
        base_context = """You are ClearCouncil AI, an assistant for analyzing local government data. 
        You have access to York County SC council data including representatives, voting records, and meeting information.
        
        Available data:
        - 39 representatives across 8 districts
        - 3,795 voting records with motion/second tracking
        - Representative performance metrics
        
        Top representatives by activity:
        - Robert Winkler (At-Large): 414 votes
        - Allison Love (At-Large): 393 votes  
        - Thomas Audette (District 3): 319 votes
        
        Answer questions about council activities, voting patterns, representative performance, and local government processes.
        Be helpful, accurate, and cite specific data when available."""
        
        if context:
            base_context += f"\n\nAdditional context: {context}"
            
        return base_context

# Create Flask application
def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure upload directory exists
    app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
    
    # Initialize chat manager
    chat_manager = ChatManager()
    
    # Register blueprints
    app.register_blueprint(create_main_blueprint(chat_manager))
    app.register_blueprint(create_api_blueprint(chat_manager), url_prefix='/api')
    
    # Context processors
    @app.context_processor
    def inject_common_data():
        """Inject common data into templates"""
        return {
            'current_year': datetime.now().year,
            'app_version': '3.0.0-integrated'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template_string(ERROR_TEMPLATE, 
                                    error_code=404, 
                                    error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return render_template_string(ERROR_TEMPLATE, 
                                    error_code=500, 
                                    error_message="Internal server error"), 500
    
    return app

def create_main_blueprint(chat_manager):
    """Create main application blueprint"""
    bp = Blueprint('main', __name__)
    
    @bp.route('/')
    def index():
        """Main dashboard with overview and chat interface"""
        summary = get_representatives_summary()
        top_reps = get_top_representatives(5)
        voting_patterns = get_voting_patterns()
        
        return render_template_string(DASHBOARD_TEMPLATE, 
                                    summary=summary,
                                    top_representatives=top_reps,
                                    voting_patterns=voting_patterns)
    
    @bp.route('/representatives')
    def representatives():
        """Representatives overview page"""
        reps = get_top_representatives(20)
        return render_template_string(REPRESENTATIVES_TEMPLATE, 
                                    representatives=reps)
    
    @bp.route('/search')
    def search():
        """Search interface for voting records"""
        query = request.args.get('q', '')
        results = []
        
        if query:
            results = search_voting_records(query)
            
        return render_template_string(SEARCH_TEMPLATE,
                                    query=query,
                                    results=results)
    
    @bp.route('/chat')
    def chat_interface():
        """Dedicated chat interface"""
        return render_template_string(CHAT_TEMPLATE)
    
    @bp.route('/transparency')
    def transparency():
        """Data transparency and sources page"""
        return render_template_string(TRANSPARENCY_TEMPLATE)
    
    return bp

def create_api_blueprint(chat_manager):
    """Create API blueprint for AJAX endpoints"""
    bp = Blueprint('api', __name__)
    
    @bp.route('/chat', methods=['POST'])
    def chat_message():
        """Handle chat messages"""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
            
        message = data['message']
        context = data.get('context', '')
        
        # Get AI response
        response = chat_manager.send_message(message, context)
        
        # Store chat session if needed
        session_id = session.get('chat_session_id')
        if not session_id:
            session_id = datetime.now().isoformat()
            session['chat_session_id'] = session_id
        
        return jsonify({
            'response': response.get('response', response.get('error', 'Unknown error')),
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
    
    @bp.route('/representatives')
    def api_representatives():
        """API endpoint for representatives data"""
        limit = request.args.get('limit', 10, type=int)
        reps = get_top_representatives(limit)
        return jsonify({'representatives': reps})
    
    @bp.route('/search')
    def api_search():
        """API endpoint for search"""
        query = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
            
        results = search_voting_records(query, limit)
        return jsonify({'results': results, 'query': query})
    
    @bp.route('/stats')
    def api_stats():
        """API endpoint for summary statistics"""
        summary = get_representatives_summary()
        voting_patterns = get_voting_patterns()
        
        return jsonify({
            'summary': summary,
            'voting_patterns': voting_patterns
        })
    
    return bp

# HTML Templates with modern design
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ClearCouncil - Local Government Transparency{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --success-color: #10b981;
            --bg-light: #f8fafc;
            --text-dark: #1f2937;
        }
        
        body {
            background: linear-gradient(135deg, var(--bg-light) 0%, #e0e7ff 100%);
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
        }
        
        .navbar {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .card {
            border: none;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            background: rgba(255,255,255,0.9);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
        }
        
        .chat-container {
            height: 400px;
            border-radius: 16px;
            background: rgba(255,255,255,0.95);
            border: 1px solid rgba(37, 99, 235, 0.2);
        }
        
        .chat-messages {
            height: 300px;
            overflow-y: auto;
            padding: 16px;
        }
        
        .chat-message {
            margin-bottom: 12px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
        }
        
        .chat-message.user {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
            margin-left: auto;
        }
        
        .chat-message.assistant {
            background: rgba(243, 244, 246, 0.8);
            color: var(--text-dark);
        }
        
        .stats-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(243, 244, 246, 0.9));
            border-left: 4px solid var(--primary-color);
        }
        
        .stats-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
        }
        
        .fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{{ url_for('main.index') }}">
                <i class="fas fa-landmark me-2"></i>ClearCouncil
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.index') }}">
                            <i class="fas fa-tachometer-alt me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.representatives') }}">
                            <i class="fas fa-users me-1"></i>Representatives
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.search') }}">
                            <i class="fas fa-search me-1"></i>Search
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.chat_interface') }}">
                            <i class="fas fa-comments me-1"></i>AI Chat
                        </a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.transparency') }}">
                            <i class="fas fa-eye me-1"></i>Transparency
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    <footer class="bg-dark text-light py-4 mt-5">
        <div class="container text-center">
            <p class="mb-0">
                <i class="fas fa-landmark me-2"></i>ClearCouncil v{{ app_version }} - 
                Making local government transparent and accessible
            </p>
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Add fade-in animation to cards
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    card.classList.add('fade-in');
                }, index * 100);
            });
        });
        
        // Chat functionality
        async function sendChatMessage() {
            const input = document.getElementById('chatInput');
            const messages = document.getElementById('chatMessages');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addChatMessage(message, 'user');
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                addChatMessage(data.response, 'assistant');
                
            } catch (error) {
                addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            }
        }
        
        function addChatMessage(message, sender) {
            const messages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;
            messageDiv.innerHTML = `
                <div class="fw-semibold mb-1">${sender === 'user' ? 'You' : 'ClearCouncil AI'}</div>
                <div>${message}</div>
            `;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        // Enter key support for chat
        document.addEventListener('DOMContentLoaded', function() {
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                chatInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendChatMessage();
                    }
                });
            }
        });
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>
'''

DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container-xl">
    <!-- Hero Section -->
    <div class="row mb-5">
        <div class="col-12">
            <div class="card text-center py-5">
                <div class="card-body">
                    <h1 class="display-4 fw-bold text-primary mb-3">
                        <i class="fas fa-landmark me-3"></i>ClearCouncil Dashboard
                    </h1>
                    <p class="lead mb-4">Transparent access to York County SC council data with AI-powered insights</p>
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="input-group input-group-lg">
                                <input type="text" class="form-control" id="quickSearch" 
                                       placeholder="Ask AI about council activities or search records...">
                                <button class="btn btn-primary" onclick="handleQuickSearch()">
                                    <i class="fas fa-search me-1"></i>Search
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Statistics Overview -->
    <div class="row mb-5">
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100">
                <div class="card-body text-center">
                    <div class="stats-number">{{ summary.total_reps }}</div>
                    <div class="stats-label">Representatives</div>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100">
                <div class="card-body text-center">
                    <div class="stats-number">{{ summary.total_districts }}</div>
                    <div class="stats-label">Districts</div>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100">
                <div class="card-body text-center">
                    <div class="stats-number">{{ "%.0f"|format(summary.total_votes) }}</div>
                    <div class="stats-label">Total Votes</div>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card stats-card h-100">
                <div class="card-body text-center">
                    <div class="stats-number">{{ "%.1f"|format(summary.avg_votes_per_rep) }}</div>
                    <div class="stats-label">Avg Votes/Rep</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Main Content Grid -->
    <div class="row">
        <!-- Left Column: Top Representatives -->
        <div class="col-lg-6 mb-4">
            <div class="card h-100">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="fas fa-trophy me-2"></i>Most Active Representatives</h5>
                </div>
                <div class="card-body">
                    {% for rep in top_representatives %}
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <div class="fw-semibold">{{ rep.name }}</div>
                            <small class="text-muted">{{ rep.district }}</small>
                        </div>
                        <div class="text-end">
                            <div class="fw-bold text-primary">{{ rep.total_votes }} votes</div>
                            <small class="text-muted">{{ rep.motions_made }} motions, {{ rep.seconds_given }} seconds</small>
                        </div>
                    </div>
                    {% endfor %}
                    <div class="mt-3">
                        <a href="{{ url_for('main.representatives') }}" class="btn btn-outline-primary btn-sm">
                            View All Representatives <i class="fas fa-arrow-right ms-1"></i>
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Right Column: AI Chat Interface -->
        <div class="col-lg-6 mb-4">
            <div class="card h-100">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="fas fa-robot me-2"></i>AI Assistant</h5>
                </div>
                <div class="card-body p-0">
                    <div class="chat-container">
                        <div class="chat-messages" id="chatMessages">
                            <div class="chat-message assistant">
                                <div class="fw-semibold mb-1">ClearCouncil AI</div>
                                <div>Hello! I can help you analyze York County council data. Ask me about representatives, voting patterns, or specific council activities.</div>
                            </div>
                        </div>
                        <div class="p-3 border-top">
                            <div class="input-group">
                                <input type="text" class="form-control" id="chatInput" 
                                       placeholder="Ask about council activities...">
                                <button class="btn btn-success" onclick="sendChatMessage()">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Voting Patterns -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0"><i class="fas fa-chart-pie me-2"></i>Voting Activity Patterns</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        {% for pattern in voting_patterns %}
                        <div class="col-md-6 mb-3">
                            <div class="d-flex justify-content-between align-items-center p-3 bg-light rounded">
                                <div>
                                    <h6 class="mb-1 text-capitalize">{{ pattern.vote_type }}s</h6>
                                    <small class="text-muted">{{ pattern.unique_reps }} representatives involved</small>
                                </div>
                                <div class="fs-4 fw-bold text-info">{{ pattern.count }}</div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function handleQuickSearch() {
    const query = document.getElementById('quickSearch').value.trim();
    if (query) {
        // If it looks like a question, use chat; otherwise use search
        if (query.includes('?') || query.toLowerCase().startsWith('what') || 
            query.toLowerCase().startsWith('who') || query.toLowerCase().startsWith('how')) {
            document.getElementById('chatInput').value = query;
            sendChatMessage();
            document.getElementById('quickSearch').value = '';
        } else {
            window.location.href = '/search?q=' + encodeURIComponent(query);
        }
    }
}

document.getElementById('quickSearch').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        handleQuickSearch();
    }
});
</script>
{% endblock %}
''')

REPRESENTATIVES_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container-xl">
    <div class="row mb-4">
        <div class="col-12">
            <h2><i class="fas fa-users me-3"></i>Representatives Overview</h2>
            <p class="text-muted">Comprehensive view of York County council representatives and their activity</p>
        </div>
    </div>
    
    <div class="row">
        {% for rep in representatives %}
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">{{ rep.name }}</h5>
                    <p class="text-muted mb-3">{{ rep.district }}</p>
                    
                    <div class="row text-center">
                        <div class="col-4">
                            <div class="fw-bold text-primary">{{ rep.total_votes }}</div>
                            <small class="text-muted">Total Votes</small>
                        </div>
                        <div class="col-4">
                            <div class="fw-bold text-success">{{ rep.motions_made }}</div>
                            <small class="text-muted">Motions</small>
                        </div>
                        <div class="col-4">
                            <div class="fw-bold text-warning">{{ rep.seconds_given }}</div>
                            <small class="text-muted">Seconds</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
''')

SEARCH_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container-xl">
    <div class="row mb-4">
        <div class="col-12">
            <h2><i class="fas fa-search me-3"></i>Search Voting Records</h2>
            <p class="text-muted">Search through voting records by representative name, case details, or category</p>
        </div>
    </div>
    
    <div class="row mb-4">
        <div class="col-12">
            <form method="GET" action="{{ url_for('main.search') }}">
                <div class="input-group input-group-lg">
                    <input type="text" class="form-control" name="q" value="{{ query }}" 
                           placeholder="Search by representative name, case number, or category...">
                    <button class="btn btn-primary" type="submit">
                        <i class="fas fa-search me-1"></i>Search
                    </button>
                </div>
            </form>
        </div>
    </div>
    
    {% if query %}
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Search Results for "{{ query }}" ({{ results|length }} found)</h5>
                </div>
                <div class="card-body">
                    {% if results %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Representative</th>
                                    <th>District</th>
                                    <th>Case Number</th>
                                    <th>Vote Type</th>
                                    <th>Category</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for result in results %}
                                <tr>
                                    <td class="fw-semibold">{{ result.representative_name }}</td>
                                    <td>{{ result.district or 'N/A' }}</td>
                                    <td><small>{{ result.case_number }}</small></td>
                                    <td>
                                        <span class="badge bg-{{ 'primary' if result.vote_type == 'movant' else 'secondary' }}">
                                            {{ result.vote_type|title }}
                                        </span>
                                    </td>
                                    <td>{{ result.case_category or 'N/A' }}</td>
                                    <td>{{ result.meeting_date or 'N/A' }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-4">
                        <i class="fas fa-search fa-3x text-muted mb-3"></i>
                        <h5>No results found</h5>
                        <p class="text-muted">Try different search terms or check the spelling.</p>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
''')

CHAT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0"><i class="fas fa-robot me-2"></i>ClearCouncil AI Assistant</h4>
                    <small>Ask questions about York County council data and activities</small>
                </div>
                <div class="card-body p-0">
                    <div style="height: 500px;" class="chat-container">
                        <div class="chat-messages" id="chatMessages">
                            <div class="chat-message assistant">
                                <div class="fw-semibold mb-1">ClearCouncil AI</div>
                                <div>
                                    Welcome! I have access to comprehensive York County SC council data. I can help you with:
                                    <ul class="mt-2 mb-0">
                                        <li>Representative performance and statistics</li>
                                        <li>Voting patterns and analysis</li>
                                        <li>Council procedures and processes</li>
                                        <li>District comparisons</li>
                                        <li>Motion and second tracking</li>
                                    </ul>
                                    What would you like to know?
                                </div>
                            </div>
                        </div>
                        <div class="p-3 border-top">
                            <div class="input-group">
                                <input type="text" class="form-control" id="chatInput" 
                                       placeholder="Ask about representatives, voting patterns, or council activities...">
                                <button class="btn btn-primary" onclick="sendChatMessage()">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''')

TRANSPARENCY_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container-xl">
    <div class="row mb-4">
        <div class="col-12">
            <h2><i class="fas fa-eye me-3"></i>Data Transparency & Sources</h2>
            <p class="text-muted">Complete visibility into our data sources, processing methods, and limitations</p>
        </div>
    </div>
    
    <div class="row">
        <div class="col-lg-6 mb-4">
            <div class="card h-100">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0"><i class="fas fa-database me-2"></i>Data Quality Metrics</h5>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-6 mb-3">
                            <div class="h4 text-info">39</div>
                            <small>Representatives Tracked</small>
                        </div>
                        <div class="col-6 mb-3">
                            <div class="h4 text-info">3,795</div>
                            <small>Voting Records</small>
                        </div>
                        <div class="col-6 mb-3">
                            <div class="h4 text-success">99.3%</div>
                            <small>Processing Success Rate</small>
                        </div>
                        <div class="col-6 mb-3">
                            <div class="h4 text-success">96.2%</div>
                            <small>Deduplication Accuracy</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-lg-6 mb-4">
            <div class="card h-100">
                <div class="card-header bg-warning text-dark">
                    <h5 class="mb-0"><i class="fas fa-exclamation-triangle me-2"></i>Current Limitations</h5>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled">
                        <li class="mb-2">
                            <i class="fas fa-clock text-warning me-2"></i>
                            Post-March 2025 documents require manual collection
                        </li>
                        <li class="mb-2">
                            <i class="fas fa-file-pdf text-warning me-2"></i>
                            Some older PDFs have formatting issues
                        </li>
                        <li class="mb-2">
                            <i class="fas fa-calendar text-warning me-2"></i>
                            Historical coverage limited to 2018+
                        </li>
                        <li class="mb-2">
                            <i class="fas fa-tags text-warning me-2"></i>
                            Limited case categorization available
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="fas fa-cogs me-2"></i>Processing Methods</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <h6><i class="fas fa-download me-2"></i>Data Collection</h6>
                            <p class="text-muted">Automated daily downloads from official York County government sources with connection testing and retry logic.</p>
                        </div>
                        <div class="col-md-6 mb-3">
                            <h6><i class="fas fa-brain me-2"></i>AI Processing</h6>
                            <p class="text-muted">AI-powered document parsing with 95%+ accuracy for extracting voting records and representative information.</p>
                        </div>
                        <div class="col-md-6 mb-3">
                            <h6><i class="fas fa-filter me-2"></i>Deduplication</h6>
                            <p class="text-muted">Advanced fuzzy matching and name normalization to ensure accurate representative tracking across documents.</p>
                        </div>
                        <div class="col-md-6 mb-3">
                            <h6><i class="fas fa-check-circle me-2"></i>Quality Control</h6>
                            <p class="text-muted">Manual verification and error correction processes to maintain data accuracy and completeness.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''')

ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error {{ error_code }} - ClearCouncil</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container">
        <div class="row justify-content-center mt-5">
            <div class="col-md-6 text-center">
                <div class="card">
                    <div class="card-body py-5">
                        <h1 class="display-1 text-muted">{{ error_code }}</h1>
                        <h4 class="mb-3">{{ error_message }}</h4>
                        <a href="/" class="btn btn-primary">Return to Dashboard</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app = create_app()
    print("🏛️ ClearCouncil Integrated Application Starting...")
    print("✅ Features included:")
    print("   • Main dashboard with statistics")
    print("   • Integrated AI chat functionality") 
    print("   • Representatives overview")
    print("   • Voting records search")
    print("   • Data transparency reporting")
    print("   • Modern responsive design")
    print("   • RESTful API endpoints")
    print(f"🌐 Access at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)