#!/usr/bin/env python3
"""
ClearCouncil - Enhanced Production Server (Schema Fixed)
Complete integration with meeting minutes processing and improved chat functionality
"""
import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
import re

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Configuration
BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / 'clearcouncil.db'

class DocumentProcessor:
    """Process and extract meeting minutes and documents"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def process_text_document(self, file_path: Path, document_type: str = 'meeting_minutes') -> Dict:
        """Process text documents (meeting minutes, agendas, etc.)"""
        try:
            # Extract text content
            text_content = self.extract_text_content(file_path)
            
            # Store in database
            doc_id = self.store_document(
                title=file_path.stem,
                content=text_content,
                document_type=document_type,
                file_path=str(file_path)
            )
            
            # Extract meeting information if it's meeting minutes
            if document_type == 'meeting_minutes':
                meeting_info = self.extract_meeting_info(text_content)
                if meeting_info:
                    self.store_meeting(meeting_info, doc_id)
            
            return {"success": True, "document_id": doc_id, "content_length": len(text_content)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_text_content(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        try:
            # For now, handle text files and basic PDF reading
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                # Fallback for other formats
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception:
            return f"Document uploaded: {file_path.name} (content extraction in progress)"
    
    def extract_meeting_info(self, text: str) -> Optional[Dict]:
        """Extract meeting information from text"""
        try:
            info = {}
            
            # Extract date patterns
            date_patterns = [
                r'(\w+\s+\d{1,2},?\s+\d{4})',  # January 15, 2024
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # 01/15/2024
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    info['date'] = match.group(1)
                    break
            
            # Extract meeting type
            if re.search(r'regular\s+meeting', text, re.IGNORECASE):
                info['meeting_type'] = 'Regular Meeting'
            elif re.search(r'special\s+meeting', text, re.IGNORECASE):
                info['meeting_type'] = 'Special Meeting'
            else:
                info['meeting_type'] = 'Meeting'
            
            # Extract attendees
            attendee_section = re.search(r'present.*?:(.*?)(?=\n\n|\n[A-Z])', text, re.IGNORECASE | re.DOTALL)
            if attendee_section:
                info['attendees'] = attendee_section.group(1).strip()
            
            return info if info else None
            
        except Exception:
            return None
    
    def store_document(self, title: str, content: str, document_type: str, file_path: str) -> int:
        """Store document in database"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO documents (title, content, document_type, file_path, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, content, document_type, file_path, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid
    
    def store_meeting(self, meeting_info: Dict, document_id: int):
        """Store meeting information"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO meetings (date, meeting_type, attendees, document_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                meeting_info.get('date', ''),
                meeting_info.get('meeting_type', ''),
                meeting_info.get('attendees', ''),
                document_id,
                datetime.now().isoformat()
            ))
            conn.commit()

class ChatDatabase:
    """Chat database management with enhanced data access"""
    
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    message TEXT,
                    response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id)
                )
            ''')
            conn.commit()
    
    def create_session(self, session_id: str):
        """Create a new chat session"""
        with self.get_connection() as conn:
            try:
                conn.execute(
                    'INSERT INTO chat_sessions (session_id) VALUES (?)',
                    (session_id,)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # Session already exists
                pass
    
    def store_message(self, session_id: str, message: str, response: str):
        """Store a chat message and response"""
        with self.get_connection() as conn:
            conn.execute(
                'INSERT INTO chat_messages (session_id, message, response) VALUES (?, ?, ?)',
                (session_id, message, response)
            )
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """Get chat usage statistics"""
        stats = {"total_sessions": 0, "total_messages": 0}
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM chat_sessions')
                stats['total_sessions'] = cursor.fetchone()[0]
                
                cursor = conn.execute('SELECT COUNT(*) FROM chat_messages')
                stats['total_messages'] = cursor.fetchone()[0]
        except:
            pass
        return stats

class EnhancedDataAccess:
    """Enhanced data access for chat integration with correct schema"""
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict]:
        """Search through documents and meeting minutes"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT title, content, document_type, created_at
                FROM documents 
                WHERE content LIKE ? OR title LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_representative_info(self, name_query: str = None) -> List[Dict]:
        """Get representative information using correct schema"""
        with self.get_connection() as conn:
            if name_query:
                cursor = conn.execute('''
                    SELECT name, district, council_id, total_votes, motions_made
                    FROM representatives 
                    WHERE name LIKE ? OR district LIKE ?
                    ORDER BY name
                    LIMIT 10
                ''', (f'%{name_query}%', f'%{name_query}%'))
            else:
                cursor = conn.execute('''
                    SELECT name, district, council_id, total_votes, motions_made
                    FROM representatives 
                    ORDER BY name
                    LIMIT 20
                ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_voting_records(self, topic: str = None, representative: str = None) -> List[Dict]:
        """Get voting records with optional filters using correct schema"""
        with self.get_connection() as conn:
            query = '''SELECT representative_name, vote_result, case_category, 
                              zoning_request, meeting_date, case_number
                       FROM voting_records WHERE 1=1'''
            params = []
            
            if topic:
                query += ' AND (case_category LIKE ? OR zoning_request LIKE ?)'
                params.extend([f'%{topic}%', f'%{topic}%'])
            
            if representative:
                query += ' AND representative_name LIKE ?'
                params.append(f'%{representative}%')
            
            query += ' ORDER BY meeting_date DESC LIMIT 10'
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_meetings(self, limit: int = 5) -> List[Dict]:
        """Get recent meetings"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT m.date, m.meeting_type, m.attendees, d.title as document_title
                FROM meetings m
                LEFT JOIN documents d ON m.document_id = d.id
                ORDER BY m.created_at DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]

class EnhancedChat:
    """Enhanced chat processor with real data integration"""
    
    def __init__(self, db: ChatDatabase):
        self.db = db
        self.data_access = EnhancedDataAccess(db.db_path)
        self.councils = self.load_councils()
    
    def load_councils(self) -> List[str]:
        """Load available councils"""
        try:
            config_dir = BASE_DIR / 'config' / 'councils'
            if config_dir.exists():
                return [f.stem for f in config_dir.glob('*.yaml') if f.name != 'template.yaml']
            return ['york_county_sc']
        except:
            return ['york_county_sc']
    
    def process_message(self, message: str, session_id: str, council_id: str = 'default') -> str:
        """Process a chat message with real data integration"""
        message_lower = message.lower()
        
        # Enhanced greeting with real data
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            # Get actual data counts
            reps = self.data_access.get_representative_info()
            meetings = self.data_access.get_recent_meetings()
            voting_records = self.data_access.get_voting_records()
            
            return f"""Hello! I'm your ClearCouncil AI assistant for {council_id}. 

📊 **Current Data Available:**
• {len(reps)} Representatives tracked
• {len(meetings)} Recent meetings on file
• {len(voting_records)} Recent voting records
• Document search capabilities

🔍 **I can help you with:**
• "Show me my representatives"
• "What happened in recent meetings?"
• "Search for [topic] in documents"
• "How did [representative] vote on [issue]?"

What would you like to explore?"""
        
        # Representatives query
        if any(word in message_lower for word in ['representative', 'rep', 'council member', 'who represents']):
            reps = self.data_access.get_representative_info()
            if reps:
                rep_list = []
                for rep in reps[:8]:  # Show top 8
                    rep_info = f"**{rep['name']}**"
                    if rep['district']:
                        rep_info += f" - District {rep['district']}"
                    if rep['total_votes']:
                        rep_info += f" ({rep['total_votes']} votes recorded)"
                    rep_list.append(rep_info)
                
                return f"""�� **Your Representatives:**

{chr(10).join(rep_list)}

💡 *Ask me: "How did [name] vote?" or "Show votes on [topic]"*"""
            else:
                return "❌ No representative data is currently available. Please contact your administrator to load council data."
        
        # Meeting minutes query
        if any(word in message_lower for word in ['meeting', 'minutes', 'agenda']):
            meetings = self.data_access.get_recent_meetings()
            if meetings:
                meeting_list = []
                for meeting in meetings:
                    meeting_info = f"📅 **{meeting['date']}** - {meeting['meeting_type']}"
                    if meeting['document_title']:
                        meeting_info += f"\n   📄 {meeting['document_title']}"
                    if meeting['attendees']:
                        meeting_info += f"\n   👥 Attendees: {meeting['attendees'][:100]}..."
                    meeting_list.append(meeting_info)
                
                return f"""📋 **Recent Meetings:**

{chr(10).join(meeting_list)}

💡 *Upload meeting minutes using the document upload feature to add more meetings*"""
            else:
                return "❌ No meeting data is currently available. You can upload meeting minutes using the document upload feature above."
        
        # Voting records query
        if any(word in message_lower for word in ['vote', 'voting', 'ballot', 'voted']):
            # Extract potential representative name or topic
            potential_rep = self.extract_representative_name(message)
            potential_topic = self.extract_topic(message)
            
            voting_records = self.data_access.get_voting_records(
                topic=potential_topic, 
                representative=potential_rep
            )
            
            if voting_records:
                vote_list = []
                for vote in voting_records[:5]:
                    vote_info = f"📊 **Case {vote.get('case_number', 'Unknown')}** - {vote.get('case_category', 'General')}"
                    vote_info += f"\n   👤 {vote.get('representative_name', 'Unknown')}: **{vote.get('vote_result', 'Unknown')}**"
                    if vote.get('zoning_request'):
                        vote_info += f"\n   📋 Request: {vote['zoning_request'][:50]}..."
                    if vote.get('meeting_date'):
                        vote_info += f"\n   📅 {vote['meeting_date']}"
                    vote_list.append(vote_info)
                
                return f"""🗳️ **Voting Records:**

{chr(10).join(vote_list)}

💡 *Try: "How did John Smith vote on zoning?" or "Show votes on budget"*"""
            else:
                return "❌ No voting records found for your query. Try a different representative name or topic like 'zoning', 'budget', or 'development'."
        
        # Document search
        if any(word in message_lower for word in ['search', 'find', 'document', 'look for']):
            # Extract search terms
            search_terms = self.extract_search_terms(message)
            if search_terms:
                documents = self.data_access.search_documents(' '.join(search_terms))
                if documents:
                    doc_list = []
                    for doc in documents:
                        doc_info = f"📄 **{doc['title']}** ({doc['document_type']})"
                        # Show snippet of content
                        content_snippet = doc['content'][:150] + "..." if len(doc['content']) > 150 else doc['content']
                        doc_info += f"\n   {content_snippet}"
                        doc_list.append(doc_info)
                    
                    return f"""🔍 **Search Results for "{' '.join(search_terms)}":**

{chr(10).join(doc_list)}

💡 *Upload more documents above to expand the searchable archive*"""
                else:
                    return f"❌ No documents found containing '{' '.join(search_terms)}'. Try different search terms or upload relevant documents."
            else:
                return "🔍 Please specify what you'd like to search for. Example: 'Search for budget discussions'"
        
        # General help
        if any(word in message_lower for word in ['help', 'what can you do', 'commands']):
            return """🤖 **ClearCouncil AI Assistant Help**

**Available Commands:**
• "Show my representatives" - List council members with voting stats
• "Recent meetings" - Show meeting minutes and agendas  
• "Search for [topic]" - Find documents about specific topics
• "How did [name] vote?" - Get specific voting records
• "What votes happened on [topic]?" - Topic-based voting search

**Real Data Available:**
• Representative profiles with voting statistics
• Zoning and development voting records
• Uploaded meeting minutes and documents
• Searchable document archive

**Tips:**
• Be specific with names and topics
• Try keywords: "zoning", "development", "budget"
• Upload documents above to expand available data

How can I help you explore your local government data?"""
        
        # Default response with helpful suggestions
        return f"""I understand you're asking about: "{message}"

🤔 I'm not sure how to help with that specific question. Here are some things I can do with real data:

• **"Show representatives"** - {len(self.data_access.get_representative_info())} council members available
• **"Recent meetings"** - {len(self.data_access.get_recent_meetings())} meetings on file
• **"Search for zoning"** - Find zoning-related documents and votes
• **"Voting records"** - Browse actual council voting data

💡 Try asking about specific topics like "development", "zoning", or representative names."""
    
    def extract_representative_name(self, message: str) -> Optional[str]:
        """Extract potential representative name from message"""
        message_lower = message.lower()
        if 'did' in message_lower and ('vote' in message_lower or 'voted' in message_lower):
            # Try to extract name after "did" and before "vote"
            match = re.search(r'did\s+([^?]+?)\s+vote', message_lower)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_topic(self, message: str) -> Optional[str]:
        """Extract potential topic from message"""
        message_lower = message.lower()
        for preposition in ['on ', 'about ']:
            if preposition in message_lower:
                parts = message_lower.split(preposition, 1)
                if len(parts) > 1:
                    topic = parts[1].strip().split()[0]  # Get first word after preposition
                    return topic
        return None
    
    def extract_search_terms(self, message: str) -> List[str]:
        """Extract search terms from message"""
        stop_words = {'search', 'find', 'look', 'for', 'about', 'in', 'the', 'a', 'an', 'and', 'or', 'but'}
        words = message.lower().split()
        return [word for word in words if word not in stop_words and len(word) > 2]

# Initialize components
chat_db = ChatDatabase(DATABASE_PATH)
enhanced_chat = EnhancedChat(chat_db)
doc_processor = DocumentProcessor(DATABASE_PATH)

# Web Routes
@app.route('/')
def index():
    """Main page with upload and chat interface"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>ClearCouncil - Enhanced Government Transparency</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .feature-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .upload-area { border: 2px dashed #667eea; border-radius: 10px; padding: 40px; text-align: center; margin: 20px 0; cursor: pointer; transition: all 0.3s; }
        .upload-area:hover { border-color: #764ba2; background: #f8f9ff; }
        .chat-container { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .chat-header { background: #667eea; color: white; padding: 20px; }
        .chat-messages { height: 400px; overflow-y: auto; padding: 20px; border-bottom: 1px solid #eee; }
        .chat-input { display: flex; padding: 20px; }
        .chat-input input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 5px; margin-right: 10px; }
        .chat-input button { padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .message { margin-bottom: 15px; }
        .user-message { text-align: right; }
        .user-message .content { background: #667eea; color: white; padding: 10px 15px; border-radius: 15px; display: inline-block; max-width: 80%; }
        .bot-message .content { background: #f1f1f1; padding: 10px 15px; border-radius: 15px; display: inline-block; max-width: 80%; white-space: pre-line; }
        .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #764ba2; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ ClearCouncil Enhanced</h1>
            <p>Government transparency with AI-powered insights and document processing</p>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <h3>📄 Document Upload</h3>
                <p>Upload meeting minutes, agendas, and other government documents for processing and analysis.</p>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <div class="upload-area" onclick="document.getElementById('file-input').click()">
                        <input type="file" id="file-input" name="file" accept=".pdf,.txt,.doc,.docx" style="display: none" onchange="this.form.submit()">
                        <p>📁 Click to select or drag & drop files</p>
                        <small>Supported: PDF, TXT, DOC, DOCX</small>
                    </div>
                </form>
            </div>
            
            <div class="feature-card">
                <h3>💬 AI Assistant</h3>
                <div class="chat-container">
                    <div class="chat-header">
                        <strong>ClearCouncil Assistant - Connected to Real Data</strong>
                    </div>
                    <div class="chat-messages" id="chat-messages">
                        <div class="message bot-message">
                            <div class="content">Hello! I can help you explore real government data. Try asking:
• "Show my representatives"
• "Recent meetings"
• "Search for zoning decisions"</div>
                        </div>
                    </div>
                    <div class="chat-input">
                        <input type="text" id="chat-input" placeholder="Ask about representatives, meetings, or voting records..." onkeypress="if(event.key==='Enter') sendMessage()">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <h3>🏛️ Browse Councils</h3>
                <p>View available council configurations and data.</p>
                <a href="/councils" class="btn">View Councils</a>
            </div>
            
            <div class="feature-card">
                <h3>🔍 Transparency Tools</h3>
                <p>Access voting records, representative information, and meeting archives.</p>
                <a href="/transparency" class="btn">Explore Data</a>
            </div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');
        let sessionId = 'session_' + Date.now();

        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            messageDiv.innerHTML = `<div class="content">${content}</div>`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;

            addMessage(message, true);
            chatInput.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, session_id: sessionId })
                });

                const data = await response.json();
                addMessage(data.response);
            } catch (error) {
                addMessage('Sorry, there was an error processing your message.', false);
            }
        }
    </script>
</body>
</html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = app.config['UPLOAD_FOLDER'] / filename
        file.save(file_path)
        
        # Process the document
        result = doc_processor.process_text_document(file_path, 'meeting_minutes')
        
        if result['success']:
            message = f"✅ Document '{filename}' processed successfully! Content length: {result['content_length']} characters."
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': result['error']}), 500
    
    return jsonify({'error': 'File processing failed'}), 500

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Enhanced chat API with real data integration"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', f'session_{datetime.now().timestamp()}')
        
        # Create session if it doesn't exist
        chat_db.create_session(session_id)
        
        # Process message with enhanced chat
        response = enhanced_chat.process_message(message, session_id)
        
        # Store the conversation
        chat_db.store_message(session_id, message, response)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'response': f'Sorry, I encountered an error: {str(e)}',
            'error': True
        }), 500

@app.route('/councils')
def councils():
    """List available councils"""
    councils_list = enhanced_chat.councils
    return jsonify({
        'councils': councils_list,
        'count': len(councils_list)
    })

@app.route('/transparency')
def transparency():
    """Transparency dashboard with real data"""
    data_access = enhanced_chat.data_access
    
    return jsonify({
        'representatives': data_access.get_representative_info()[:10],
        'recent_meetings': data_access.get_recent_meetings(),
        'sample_voting_records': data_access.get_voting_records()[:10]
    })

@app.route('/health')
def health():
    """Enhanced health check with data status"""
    stats = chat_db.get_statistics()
    
    # Check data availability
    data_access = enhanced_chat.data_access
    representatives = data_access.get_representative_info()
    meetings = data_access.get_recent_meetings()
    documents = data_access.search_documents('', limit=1)
    
    return jsonify({
        'status': 'healthy',
        'service': 'clearcouncil-enhanced-fixed',
        'features': ['web', 'chat', 'database', 'ai-assistant', 'document-processing'],
        'data_status': {
            'representatives_count': len(representatives),
            'meetings_count': len(meetings),
            'documents_available': len(documents) > 0
        },
        'councils_available': len(enhanced_chat.councils),
        'database_connected': True,
        'statistics': stats
    })

if __name__ == '__main__':
    print("🚀 ClearCouncil Enhanced Server (Schema Fixed) Starting...")
    print("=" * 65)
    print("💬 Chat system: Enhanced with real data integration")
    print("📄 Document processing: Enabled")
    print(f"💾 Database: {DATABASE_PATH}")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"🏛️ Councils: {len(enhanced_chat.councils)} available")
    print("🌐 Server URL: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("=" * 65)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
