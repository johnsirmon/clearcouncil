#!/usr/bin/env python3
"""
ClearCouncil - Integrated Web Server with Chat
Combines web interface with chat functionality
"""
import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, request, jsonify, send_from_directory

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-in-production'

# Configuration
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / 'clearcouncil.db'

class ChatDatabase:
    """Simple chat database management"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_chat_tables()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_chat_tables(self):
        """Initialize chat-related database tables"""
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    council_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    message TEXT,
                    response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
                )
            ''')
            conn.commit()
    
    def create_session(self, session_id: str, council_id: str = 'default'):
        """Create a new chat session"""
        with self.get_connection() as conn:
            conn.execute(
                'INSERT OR REPLACE INTO chat_sessions (session_id, council_id) VALUES (?, ?)',
                (session_id, council_id)
            )
            conn.commit()
    
    def save_message(self, session_id: str, message: str, response: str):
        """Save a chat message and response"""
        with self.get_connection() as conn:
            conn.execute(
                'INSERT INTO chat_messages (session_id, message, response) VALUES (?, ?, ?)',
                (session_id, message, response)
            )
            conn.commit()
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a session"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT message, response, timestamp FROM chat_messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?',
                (session_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

class SimpleChat:
    """Simple chat processor for ClearCouncil"""
    
    def __init__(self, db: ChatDatabase):
        self.db = db
        self.councils = self.load_councils()
    
    def load_councils(self) -> List[str]:
        """Load available councils"""
        try:
            # Try to load from clearcouncil modules
            from clearcouncil.config.settings import list_available_councils
            return list_available_councils()
        except:
            # Fallback: scan config directory
            config_dir = BASE_DIR / 'config' / 'councils'
            if config_dir.exists():
                return [f.stem for f in config_dir.glob('*.yaml') if f.name != 'template.yaml']
            return ['york_county_sc']  # Default
    
    def process_message(self, message: str, session_id: str, council_id: str = 'default') -> str:
        """Process a chat message and return response"""
        
        # Simple rule-based responses for now
        message_lower = message.lower()
        
        # Handle greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            return f"Hello! I'm your ClearCouncil assistant. I can help you find information about local government activities. What would you like to know about {council_id}?"
        
        # Handle council questions
        if 'council' in message_lower or 'government' in message_lower:
            return f"I can help you with information about {council_id}. You can ask about meetings, voting records, representatives, or documents."
        
        # Handle voting questions
        if any(word in message_lower for word in ['vote', 'voting', 'ballot', 'election']):
            return "I can help you analyze voting patterns and records. What specific voting information are you looking for?"
        
        # Handle meeting questions
        if any(word in message_lower for word in ['meeting', 'agenda', 'minutes']):
            return "I can search through meeting documents and agendas. What specific meeting or topic are you interested in?"
        
        # Handle help requests
        if 'help' in message_lower:
            return """I can help you with:
            • Finding meeting minutes and agendas
            • Analyzing voting records
            • Information about representatives
            • Council policies and decisions
            
            Just ask me a question about your local government!"""
        
        # Handle list requests
        if 'list' in message_lower and 'council' in message_lower:
            councils_text = ', '.join(self.councils)
            return f"Available councils: {councils_text}"
        
        # Default response with search capability
        return f"I understand you're asking about: '{message}'. Let me search through the {council_id} data for relevant information. (Note: Full search functionality is being developed - this is a basic response system for now.)"

# Initialize chat system
chat_db = ChatDatabase(DATABASE_PATH)
chat_processor = SimpleChat(chat_db)

# Web Routes
@app.route('/')
def home():
    """Main dashboard with chat interface"""
    return """
    <!DOCTYPE html>
    <html><head>
        <title>ClearCouncil - Government Transparency with AI Chat</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .chat-container { height: 500px; display: flex; flex-direction: column; }
            .chat-messages { flex: 1; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #e3f2fd; text-align: right; }
            .bot-message { background: #f5f5f5; text-align: left; }
            .chat-input { display: flex; gap: 10px; }
            .chat-input input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .chat-input button { padding: 10px 20px; background: #2c3e50; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            ul li { margin: 5px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏛️ ClearCouncil</h1>
                <p>Government Transparency Platform with AI Assistant</p>
            </div>
            
            <div class="main-content">
                <div class="panel">
                    <h2>💬 AI Chat Assistant</h2>
                    <div class="chat-container">
                        <div class="chat-messages" id="chatMessages">
                            <div class="message bot-message">
                                Hello! I'm your ClearCouncil AI assistant. I can help you find information about local government activities, voting records, and meeting minutes. What would you like to know?
                            </div>
                        </div>
                        <div class="chat-input">
                            <input type="text" id="messageInput" placeholder="Ask me about council meetings, voting records, or representatives..." onkeypress="if(event.key==='Enter') sendMessage()">
                            <button onclick="sendMessage()">Send</button>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📊 System Status</h2>
                    <div class="status success">
                        <strong>✅ Chat System:</strong> Online and ready
                    </div>
                    <div class="status success">
                        <strong>✅ Database:</strong> Connected
                    </div>
                    <div class="status success">
                        <strong>✅ Web Server:</strong> Running on port 5000
                    </div>
                    
                    <h3>🚀 Quick Actions</h3>
                    <ul>
                        <li><a href="/health">🔍 Health Check</a></li>
                        <li><a href="/councils">🏛️ Available Councils</a></li>
                        <li><a href="/api/chat/history">📝 Chat History</a></li>
                        <li><a href="/transparency">📊 Data Sources</a></li>
                    </ul>
                </div>
            </div>
        </div>
        
        <script>
            const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            
            function addMessage(content, isUser = false) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
                messageDiv.textContent = content;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                // Add user message
                addMessage(message, true);
                input.value = '';
                
                try {
                    // Send to server
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            session_id: sessionId,
                            council_id: 'default'
                        })
                    });
                    
                    const data = await response.json();
                    addMessage(data.response);
                } catch (error) {
                    addMessage('Sorry, there was an error processing your message. Please try again.');
                }
            }
        </script>
    </body></html>
    """

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Handle chat messages"""
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    council_id = data.get('council_id', 'default')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Create session if it doesn't exist
    chat_db.create_session(session_id, council_id)
    
    # Process message
    response = chat_processor.process_message(message, session_id, council_id)
    
    # Save to database
    chat_db.save_message(session_id, message, response)
    
    return jsonify({
        'response': response,
        'session_id': session_id,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat/history')
def chat_history():
    """Get chat history"""
    session_id = request.args.get('session_id', 'default')
    limit = int(request.args.get('limit', 50))
    
    history = chat_db.get_chat_history(session_id, limit)
    return jsonify({
        'session_id': session_id,
        'messages': history
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'clearcouncil-integrated',
        'features': ['web', 'chat', 'database'],
        'chat_enabled': True,
        'database_connected': DATABASE_PATH.exists()
    })

@app.route('/councils')
def councils():
    """List available councils"""
    try:
        councils = chat_processor.councils
        return jsonify({
            'councils': councils,
            'count': len(councils)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transparency')
def transparency():
    """Data transparency dashboard"""
    stats = {'chat_sessions': 0, 'messages': 0, 'councils': len(chat_processor.councils)}
    
    try:
        with chat_db.get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM chat_sessions')
            stats['chat_sessions'] = cursor.fetchone()[0]
            
            cursor = conn.execute('SELECT COUNT(*) FROM chat_messages')
            stats['messages'] = cursor.fetchone()[0]
    except:
        pass
    
    return jsonify({
        'data_sources': {
            'chat_system': 'active',
            'database': 'connected' if DATABASE_PATH.exists() else 'missing',
            'councils': stats['councils']
        },
        'statistics': stats
    })

if __name__ == '__main__':
    print("🚀 ClearCouncil Integrated Server Starting...")
    print("=" * 50)
    print(f"💬 Chat system: Enabled")
    print(f"💾 Database: {DATABASE_PATH}")
    print(f"🏛️ Councils: {len(chat_processor.councils)}")
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"💬 Chat interface: http://localhost:5000")
    print(f"🔍 Health check: http://localhost:5000/health")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
