#!/usr/bin/env python3
"""
ClearCouncil - Fixed Production Server
Complete integration of web interface and chat functionality
"""
import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, request, jsonify

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')

# Configuration
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / 'clearcouncil.db'

class ChatDatabase:
    """Chat database management"""
    
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
    
    def get_stats(self) -> Dict:
        """Get chat system statistics"""
        stats = {'total_sessions': 0, 'total_messages': 0}
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM chat_sessions')
                stats['total_sessions'] = cursor.fetchone()[0]
                
                cursor = conn.execute('SELECT COUNT(*) FROM chat_messages')
                stats['total_messages'] = cursor.fetchone()[0]
        except:
            pass
        return stats

class SimpleChat:
    """Enhanced chat processor for ClearCouncil"""
    
    def __init__(self, db: ChatDatabase):
        self.db = db
        self.councils = self.load_councils()
    
    def load_councils(self) -> List[str]:
        """Load available councils"""
        try:
            from clearcouncil.config.settings import list_available_councils
            return list_available_councils()
        except:
            config_dir = BASE_DIR / 'config' / 'councils'
            if config_dir.exists():
                return [f.stem for f in config_dir.glob('*.yaml') if f.name != 'template.yaml']
            return ['york_county_sc']
    
    def process_message(self, message: str, session_id: str, council_id: str = 'default') -> str:
        """Process a chat message and return enhanced response"""
        message_lower = message.lower()
        
        # Enhanced greeting
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            return f"""Hello! I'm your ClearCouncil AI assistant for {council_id}. 

I can help you with:
• 📊 Voting records and analysis
• 📋 Meeting minutes and agendas  
• 👥 Representative information
• 🔍 Document search
• 📈 Trend analysis

What would you like to explore?"""
        
        # Enhanced voting analysis
        if any(word in message_lower for word in ['vote', 'voting', 'ballot']):
            return f"""📊 **Voting Analysis for {council_id}**

I can provide:
• Individual representative voting patterns
• Issue-based voting trends
• Attendance and participation rates
• Key decision outcomes
• Historical voting data

What specific voting information interests you? You can ask about:
- "How did [representative] vote on [issue]?"
- "Show voting trends for the last 6 months"
- "Which representatives vote together most often?"
"""
        
        # Enhanced meeting analysis
        if any(word in message_lower for word in ['meeting', 'agenda', 'minutes']):
            return f"""📋 **Meeting Information for {council_id}**

Available data:
• Recent meeting agendas and minutes
• Key topics and decisions
• Public comment summaries
• Future scheduled meetings
• Historical meeting archives

Try asking:
- "What was discussed in the last meeting?"
- "Find meetings about budget"
- "Show me upcoming meetings"
- "Search for [specific topic] in meetings"
"""
        
        # Enhanced representative info
        if any(word in message_lower for word in ['representative', 'rep', 'councilmember', 'official']):
            return f"""👥 **Representative Information for {council_id}**

I can provide:
• Current representatives and roles
• Voting histories and patterns
• Committee assignments
• Contact information
• Performance metrics

Ask me:
- "Who represents district [number]?"
- "Show me [name]'s voting record"
- "List all current representatives"
- "Which committees is [name] on?"
"""
        
        # Search functionality
        if any(word in message_lower for word in ['search', 'find', 'look for']):
            search_terms = message.replace('search', '').replace('find', '').replace('look for', '').strip()
            return f"""🔍 **Search Results for: "{search_terms}"**

Searching through {council_id} data...

I can search:
• Meeting transcripts and minutes
• Voting records and decisions
• Policy documents
• Representative statements
• Public comments

(Note: Advanced search integration is in development. For now, please be specific about what type of information you're looking for.)
"""
        
        # Help system
        if 'help' in message_lower:
            return """🏛️ **ClearCouncil AI Assistant Help**

**Available Commands:**
• "voting records" - Analyze voting patterns
• "meeting info" - Access meeting data
• "representatives" - Get official information
• "search [topic]" - Find relevant documents

**Example Queries:**
• "How did the council vote on the budget?"
• "What meetings discussed zoning?"
• "Who is my representative?"
• "Show recent voting trends"

**Data Available:**
• Meeting minutes and agendas
• Voting records and analysis
• Representative information
• Policy documents
• Public comments

Just ask me questions in natural language!"""
        
        # List councils
        if 'list' in message_lower and 'council' in message_lower:
            councils_text = ', '.join(self.councils)
            return f"""🏛️ **Available Councils ({len(self.councils)}):**

{councils_text}

Each council has:
• Meeting records and agendas
• Voting data and analysis
• Representative information
• Policy documents

To get specific information, ask: "Tell me about [council_name]" or switch councils by mentioning the council name in your questions."""
        
        # Default enhanced response
        return f"""I understand you're asking about: **"{message}"**

Let me help you find relevant information in {council_id}. You can be more specific by asking about:

🎯 **Specific Topics:**
• Particular representatives or officials
• Specific meetings or dates  
• Policy areas (budget, zoning, etc.)
• Voting records on particular issues

📊 **Analysis Options:**
• Voting patterns and trends
• Meeting attendance
• Decision outcomes
• Historical comparisons

What aspect would you like to focus on?"""

# Initialize chat system
chat_db = ChatDatabase(DATABASE_PATH)
chat_processor = SimpleChat(chat_db)

@app.route('/')
def home():
    """Main dashboard with chat interface"""
    return '''
    <!DOCTYPE html>
    <html><head>
        <title>ClearCouncil - Government Transparency AI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f8f9fa; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .header h1 { margin: 0 0 10px 0; font-size: 2.5rem; font-weight: 300; }
            .header p { margin: 0; opacity: 0.9; font-size: 1.1rem; }
            .main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
            .panel { background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }
            .panel-header { background: #f8f9fa; padding: 20px; border-bottom: 1px solid #e9ecef; }
            .panel-header h2 { margin: 0; color: #2c3e50; font-size: 1.4rem; }
            .panel-content { padding: 20px; }
            .chat-container { height: 600px; display: flex; flex-direction: column; }
            .chat-messages { flex: 1; overflow-y: auto; padding: 15px; border: 1px solid #e9ecef; border-radius: 8px; margin-bottom: 15px; background: #fafafa; }
            .message { margin: 15px 0; padding: 12px 16px; border-radius: 18px; max-width: 80%; word-wrap: break-word; }
            .user-message { background: #007bff; color: white; margin-left: auto; text-align: right; }
            .bot-message { background: white; border: 1px solid #e9ecef; text-align: left; white-space: pre-line; }
            .chat-input { display: flex; gap: 10px; }
            .chat-input input { flex: 1; padding: 12px 16px; border: 1px solid #ced4da; border-radius: 25px; font-size: 14px; }
            .chat-input input:focus { outline: none; border-color: #007bff; box-shadow: 0 0 0 2px rgba(0,123,255,0.25); }
            .chat-input button { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: 500; }
            .chat-input button:hover { background: #0056b3; }
            .chat-input button:disabled { background: #6c757d; cursor: not-allowed; }
            .status-grid { display: grid; gap: 15px; }
            .status-item { padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; background: #f8fff9; }
            .status-item h4 { margin: 0 0 8px 0; color: #2c3e50; }
            .status-item p { margin: 0; color: #6c757d; font-size: 0.9rem; }
            .feature-list { list-style: none; padding: 0; }
            .feature-list li { padding: 8px 0; border-bottom: 1px solid #f1f3f4; display: flex; align-items: center; }
            .feature-list li:last-child { border-bottom: none; }
            .feature-list li::before { content: '✓'; color: #28a745; font-weight: bold; margin-right: 10px; }
            .typing-indicator { display: none; padding: 12px 16px; color: #6c757d; font-style: italic; }
            @media (max-width: 768px) {
                .main-grid { grid-template-columns: 1fr; }
                .header h1 { font-size: 2rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏛️ ClearCouncil</h1>
                <p>AI-Powered Government Transparency Platform</p>
            </div>
            
            <div class="main-grid">
                <div class="panel">
                    <div class="panel-header">
                        <h2>💬 AI Government Assistant</h2>
                    </div>
                    <div class="panel-content">
                        <div class="chat-container">
                            <div class="chat-messages" id="chatMessages">
                                <div class="message bot-message">
                                    🏛️ Welcome! I'm your ClearCouncil AI assistant. I can help you access government data, analyze voting patterns, search meeting documents, and understand local government activities.

Try asking:
• "Show me recent voting records"
• "Find meetings about budget"  
• "Who are the current representatives?"
• "What happened in last week's meeting?"
                                </div>
                            </div>
                            <div class="typing-indicator" id="typingIndicator">Assistant is typing...</div>
                            <div class="chat-input">
                                <input type="text" id="messageInput" placeholder="Ask about government data, voting records, meetings, or representatives..." onkeypress="if(event.key==='Enter') sendMessage()">
                                <button id="sendButton" onclick="sendMessage()">Send</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <div class="panel-header">
                        <h2>📊 System Status</h2>
                    </div>
                    <div class="panel-content">
                        <div class="status-grid">
                            <div class="status-item">
                                <h4>🤖 AI Chat System</h4>
                                <p>Enhanced mode • Ready</p>
                            </div>
                            <div class="status-item">
                                <h4>💾 Database</h4>
                                <p>Connected • Chat history enabled</p>
                            </div>
                            <div class="status-item">
                                <h4>🏛️ Councils</h4>
                                <p>Multiple configurations available</p>
                            </div>
                        </div>
                        
                        <h3 style="margin: 30px 0 15px 0; color: #2c3e50;">Features Available</h3>
                        <ul class="feature-list">
                            <li>Real-time government data access</li>
                            <li>Natural language queries</li>
                            <li>Voting pattern analysis</li>
                            <li>Meeting document search</li>
                            <li>Representative tracking</li>
                            <li>Session history & context</li>
                        </ul>
                        
                        <div style="margin-top: 30px;">
                            <h4 style="color: #2c3e50; margin-bottom: 10px;">Quick Links</h4>
                            <div style="display: flex; flex-direction: column; gap: 8px;">
                                <a href="/health" style="color: #007bff; text-decoration: none;">🔍 Health Check</a>
                                <a href="/councils" style="color: #007bff; text-decoration: none;">🏛️ Available Councils</a>
                                <a href="/transparency" style="color: #007bff; text-decoration: none;">📊 Data Dashboard</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const sessionId = 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
            let isProcessing = false;
            
            function addMessage(content, isUser = false) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
                messageDiv.textContent = content;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function showTyping() {
                document.getElementById('typingIndicator').style.display = 'block';
                document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
            }
            
            function hideTyping() {
                document.getElementById('typingIndicator').style.display = 'none';
            }
            
            async function sendMessage() {
                if (isProcessing) return;
                
                const input = document.getElementById('messageInput');
                const sendButton = document.getElementById('sendButton');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, true);
                input.value = '';
                isProcessing = true;
                sendButton.disabled = true;
                sendButton.textContent = 'Sending...';
                showTyping();
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            session_id: sessionId,
                            council_id: 'york_county_sc'
                        })
                    });
                    
                    const data = await response.json();
                    hideTyping();
                    addMessage(data.response);
                } catch (error) {
                    hideTyping();
                    addMessage('Sorry, there was an error processing your message. Please try again.');
                    console.error('Chat error:', error);
                } finally {
                    isProcessing = false;
                    sendButton.disabled = false;
                    sendButton.textContent = 'Send';
                }
            }
            
            document.getElementById('messageInput').focus();
        </script>
    </body></html>
    '''

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        council_id = data.get('council_id', 'default')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create session
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
        
    except Exception as e:
        return jsonify({
            'response': 'I apologize, but I encountered an error. Please try again.',
            'error': str(e)
        }), 500

@app.route('/api/chat/history')
def chat_history():
    """Get chat history"""
    session_id = request.args.get('session_id', 'default')
    limit = min(int(request.args.get('limit', 50)), 100)
    
    try:
        history = chat_db.get_chat_history(session_id, limit)
        return jsonify({
            'session_id': session_id,
            'messages': history,
            'count': len(history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        stats = chat_db.get_stats()
        return jsonify({
            'status': 'healthy',
            'service': 'clearcouncil-production',
            'features': ['web', 'chat', 'database', 'ai-assistant'],
            'database_connected': DATABASE_PATH.exists(),
            'councils_available': len(chat_processor.councils),
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'error': str(e)
        }), 500

@app.route('/councils')
def councils_api():
    """List available councils"""
    try:
        councils_data = []
        for council in chat_processor.councils:
            councils_data.append({
                'id': council,
                'name': council.replace('_', ' ').title(),
                'status': 'active'
            })
        
        return jsonify({
            'councils': councils_data,
            'count': len(councils_data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transparency')
def transparency():
    """Data transparency dashboard"""
    try:
        stats = chat_db.get_stats()
        
        return jsonify({
            'data_sources': {
                'chat_system': 'active',
                'database': 'connected' if DATABASE_PATH.exists() else 'missing',
                'councils': len(chat_processor.councils)
            },
            'statistics': stats,
            'capabilities': [
                'Natural language processing',
                'Government data analysis',
                'Voting pattern recognition',
                'Meeting document search',
                'Representative tracking'
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 ClearCouncil Production Server Starting...")
    print("=" * 60)
    print(f"💬 Chat system: Enhanced mode")
    print(f"💾 Database: {DATABASE_PATH}")
    print(f"🏛️ Councils: {len(chat_processor.councils)} available")
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"🔍 Health check: http://localhost:5000/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)
