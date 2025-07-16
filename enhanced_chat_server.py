#!/usr/bin/env python3
"""
Enhanced ClearCouncil Chat Server with Real Data Integration

This server integrates with the ClearCouncil database to provide real-time
access to voting records, representative information, and council data.
"""

import os
import sys
import json
import requests
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
from typing import Dict, List, Any, Optional

# Load environment variables
def load_env():
    env_vars = {}
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

env_vars = load_env()
GITHUB_TOKEN = env_vars.get('GITHUB_TOKEN', os.getenv('GITHUB_TOKEN'))

class DataManager:
    """Manages ClearCouncil data loading and querying"""
    
    def __init__(self, db_path: str = "clearcouncil.db"):
        self.db_path = db_path
        self.data = None
        self.last_loaded = None
        self.loading_status = "not_loaded"
        
    def get_data_status(self) -> Dict:
        """Get current data loading status"""
        if not Path(self.db_path).exists():
            return {
                "status": "no_database",
                "message": "Database not found. Please run data processing first.",
                "representatives_count": 0,
                "voting_records_count": 0,
                "last_loaded": None
            }
        
        if self.data is None:
            try:
                self.load_data()
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error loading data: {str(e)}",
                    "representatives_count": 0,
                    "voting_records_count": 0,
                    "last_loaded": None
                }
        
        return {
            "status": "loaded",
            "message": "Data loaded successfully",
            "representatives_count": len(self.data.get("representatives", {})),
            "voting_records_count": sum(len(rep.get("voting_record", [])) for rep in self.data.get("representatives", {}).values()),
            "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None
        }
    
    def load_data(self) -> Dict:
        """Load data from database"""
        self.loading_status = "loading"
        
        try:
            # Check if JSON file exists and is recent
            json_file = Path("clearcouncil_data.json")
            if json_file.exists():
                # Load from JSON file
                with open(json_file, 'r') as f:
                    self.data = json.load(f)
                    self.last_loaded = datetime.fromtimestamp(json_file.stat().st_mtime)
                    self.loading_status = "loaded"
                    return {"status": "success", "message": "Data loaded from existing file"}
            else:
                # Need to run data preloader
                self.loading_status = "needs_processing"
                return {"status": "needs_processing", "message": "Data needs to be processed first"}
                
        except Exception as e:
            self.loading_status = "error"
            return {"status": "error", "message": f"Error loading data: {str(e)}"}
    
    def process_data(self) -> Dict:
        """Process data using the data preloader"""
        self.loading_status = "processing"
        
        try:
            # Run the data preloader
            import subprocess
            result = subprocess.run([sys.executable, "data_preloader.py"], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Reload the data
                return self.load_data()
            else:
                self.loading_status = "error"
                return {"status": "error", "message": f"Data processing failed: {result.stderr}"}
                
        except subprocess.TimeoutExpired:
            self.loading_status = "error"
            return {"status": "error", "message": "Data processing timed out"}
        except Exception as e:
            self.loading_status = "error"
            return {"status": "error", "message": f"Error processing data: {str(e)}"}
    
    def get_context_for_question(self, question: str) -> str:
        """Get relevant context for a user question"""
        try:
            if not self.data:
                return "No data loaded. Please load data first."
            
            question_lower = question.lower()
            context_parts = []
            
            # Add basic stats
            rep_count = len(self.data.get("representatives", {}))
            total_votes = sum(len(rep.get("voting_record", [])) for rep in self.data.get("representatives", {}).values())
            context_parts.append(f"Council data: {rep_count} representatives, {total_votes} total voting records")
            
            # If asking about specific representative
            if "representative" in question_lower or "council member" in question_lower or "who are" in question_lower:
                representatives = self.data.get("representatives", {})
                rep_list = []
                for name, rep_data in list(representatives.items())[:10]:  # Limit to first 10
                    try:
                        district = rep_data.get("district", "Unknown")
                        votes = rep_data.get("total_votes", 0)
                        rep_list.append(f"{name} ({district}): {votes} votes")
                    except Exception as e:
                        rep_list.append(f"{name}: Error getting details")
                
                context_parts.append(f"Representatives: {', '.join(rep_list)}")
            
            # If asking about voting records
            if "voting" in question_lower or "vote" in question_lower:
                # Get some sample voting records
                sample_records = []
                try:
                    for rep_name, rep_data in list(self.data.get("representatives", {}).items())[:3]:
                        records = rep_data.get("voting_record", [])[:2]  # First 2 records
                        for record in records:
                            case_num = record.get("case_number", "Unknown")
                            result = record.get("result", "Unknown")
                            vote_type = record.get("vote_type", "Unknown")
                            sample_records.append(f"{rep_name}: {case_num} - {vote_type} - {result}")
                    
                    if sample_records:
                        context_parts.append(f"Sample voting records: {'; '.join(sample_records[:5])}")
                except Exception as e:
                    context_parts.append(f"Sample voting records: Error loading - {str(e)}")
            
            # If asking about specific person
            try:
                for rep_name in self.data.get("representatives", {}):
                    if rep_name.lower() in question_lower:
                        rep_data = self.data["representatives"][rep_name]
                        district = rep_data.get("district", "Unknown")
                        votes = rep_data.get("total_votes", 0)
                        motions = rep_data.get("motions_made", 0)
                        seconds = rep_data.get("seconds_given", 0)
                        
                        context_parts.append(f"{rep_name} details: District {district}, {votes} votes, {motions} motions, {seconds} seconds")
                        
                        # Add recent voting activity
                        recent_votes = rep_data.get("voting_record", [])[:3]
                        if recent_votes:
                            vote_details = []
                            for vote in recent_votes:
                                case_num = vote.get("case_number", "Unknown")
                                result = vote.get("result", "Unknown")
                                vote_details.append(f"{case_num}: {result}")
                            context_parts.append(f"Recent votes: {'; '.join(vote_details)}")
                        break
            except Exception as e:
                context_parts.append(f"Error getting specific representative info: {str(e)}")
            
            return "\n".join(context_parts)
        except Exception as e:
            return f"Error generating context: {str(e)}"

class GitHubClient:
    """GitHub Models API client"""
    
    def __init__(self, token):
        self.token = token
        self.base_url = "https://models.github.ai/inference/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages, model="gpt-4o-mini"):
        """Send chat completion request with context"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error: {str(e)}"

class EnhancedChatHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP request handler with real data integration"""
    
    # Class-level variables to avoid re-initialization
    _github_client = None
    _data_manager = None
    
    def __init__(self, *args, **kwargs):
        # Initialize class-level variables once
        if EnhancedChatHandler._github_client is None:
            EnhancedChatHandler._github_client = GitHubClient(GITHUB_TOKEN) if GITHUB_TOKEN else None
        if EnhancedChatHandler._data_manager is None:
            EnhancedChatHandler._data_manager = DataManager()
        
        self.github_client = EnhancedChatHandler._github_client
        self.data_manager = EnhancedChatHandler._data_manager
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_html()
        elif parsed_path.path == '/data/status':
            self.handle_data_status()
        elif parsed_path.path == '/chat':
            query_params = parse_qs(parsed_path.query)
            message = query_params.get('message', [''])[0]
            if message:
                self.handle_chat(message)
            else:
                self.send_json_response({"error": "No message provided"})
        else:
            self.send_404()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/chat':
            self.handle_chat_post()
        elif self.path == '/data/process':
            self.handle_data_process()
        else:
            self.send_404()
    
    def handle_chat_post(self):
        """Handle chat POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            if message:
                self.handle_chat(message)
            else:
                self.send_json_response({"error": "No message provided"})
        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"})
    
    def handle_data_status(self):
        """Handle data status requests"""
        status = self.data_manager.get_data_status()
        self.send_json_response(status)
    
    def handle_data_process(self):
        """Handle data processing requests"""
        result = self.data_manager.process_data()
        self.send_json_response(result)
    
    def handle_chat(self, message):
        """Handle chat messages with real data context"""
        try:
            # Get relevant context from real data
            context = self.data_manager.get_context_for_question(message)
            print(f"DEBUG: Context generated: {context[:200]}...")  # Debug output
            
            if not self.github_client:
                response = self.get_enhanced_mock_response(message, context)
            else:
                # Create system message with context
                system_content = f"""You are a helpful assistant for ClearCouncil, a local government transparency tool for York County, SC. 

You have access to real council data. Use this context to answer questions accurately:

{context}

Help users understand local government processes, representative voting patterns, and civic engagement. Always base your responses on the actual data provided in the context above."""

                messages = [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": message}
                ]
                
                response = self.github_client.chat_completion(messages)
                print(f"DEBUG: GitHub API response: {response[:100]}...")  # Debug output
                
                # If GitHub API returns an error, fall back to enhanced mock
                if response.startswith("Error:"):
                    print("DEBUG: GitHub API error, falling back to mock")
                    response = self.get_enhanced_mock_response(message, context)
            
            self.send_json_response({"response": response})
        except Exception as e:
            print(f"DEBUG: Exception in handle_chat: {str(e)}")
            # Fallback to enhanced mock response
            try:
                context = self.data_manager.get_context_for_question(message)
                response = self.get_enhanced_mock_response(message, context)
                self.send_json_response({"response": response})
            except Exception as e2:
                print(f"DEBUG: Exception in fallback: {str(e2)}")
                self.send_json_response({"response": f"I apologize, but I encountered an error processing your question: {str(e)}. The system is experiencing technical difficulties."})
    
    def get_enhanced_mock_response(self, message: str, context: str) -> str:
        """Generate enhanced mock responses using real data"""
        message_lower = message.lower()
        
        if "representative" in message_lower or "who are" in message_lower:
            if "No data loaded" in context:
                return "I need to load the council data first to show you the current representatives. Please use the 'Load Data' button to process the latest council information."
            
            # Extract representative info from context
            lines = context.split('\n')
            rep_info = ""
            for line in lines:
                if "Representatives:" in line:
                    rep_info = line.replace("Representatives: ", "")
                    break
            
            if rep_info:
                return f"Based on the current council data, here are the representatives:\n\n{rep_info.replace(', ', '\n- ')}\n\nThis information is from the actual council database. Would you like to know more about any specific representative?"
            else:
                return "I have council data loaded but couldn't find representative information in the expected format. Please try reloading the data."
        
        elif "voting" in message_lower or "vote" in message_lower:
            if "No data loaded" in context:
                return "I need to load the council data first to show you voting records. Please use the 'Load Data' button to process the latest voting information."
            
            # Extract voting info from context
            lines = context.split('\n')
            vote_info = ""
            for line in lines:
                if "voting records" in line.lower():
                    vote_info = line
                    break
            
            return f"Based on the current council database:\n\n{vote_info}\n\nI can provide detailed voting analysis for any representative. Just ask about a specific person or topic!"
        
        elif "hello" in message_lower or "help" in message_lower:
            data_status = "loaded" if "No data loaded" not in context else "not loaded"
            status_msg = "✅ Council data is loaded and ready!" if data_status == "loaded" else "⚠️ Council data needs to be loaded first."
            
            return f"Hello! I'm your ClearCouncil assistant for York County, SC.\n\n{status_msg}\n\nI can help you with:\n- Information about your representatives\n- Voting records and patterns\n- Council meeting outcomes\n- Civic engagement guidance\n\nWhat would you like to know about your local government?"
        
        else:
            if "No data loaded" in context:
                return f"I'd be happy to help you with: {message}\n\nHowever, I need to load the council data first to give you accurate information. Please use the 'Load Data' button to process the latest council information, then ask your question again."
            
            return f"Thank you for your question about: {message}\n\nBased on the current council data:\n{context}\n\nI can provide more specific information if you ask about representatives, voting records, or specific council matters."
    
    def serve_html(self):
        """Serve the enhanced HTML chat interface"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ClearCouncil Chat - Enhanced</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
        }
        .data-status {
            background-color: #ecf0f1;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }
        .data-status.loaded {
            border-left-color: #27ae60;
            background-color: #d5f4e6;
        }
        .data-status.error {
            border-left-color: #e74c3c;
            background-color: #fadbd8;
        }
        .data-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .data-button {
            padding: 8px 16px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        .data-button:hover {
            background-color: #2980b9;
        }
        .data-button:disabled {
            background-color: #bdc3c7;
            cursor: not-allowed;
        }
        .chat-box {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            background-color: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
        }
        .user-message {
            background-color: #3498db;
            color: white;
            text-align: right;
        }
        .bot-message {
            background-color: #ecf0f1;
            color: #2c3e50;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        .message-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .send-button {
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .send-button:hover {
            background-color: #2980b9;
        }
        .status {
            text-align: center;
            margin-top: 10px;
            color: #7f8c8d;
            font-size: 12px;
        }
        .loading {
            opacity: 0.7;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ ClearCouncil Chat - Enhanced</h1>
            <p>Ask me about local government in York County, SC</p>
        </div>
        
        <div class="data-status" id="dataStatus">
            <div><strong>📊 Data Status:</strong> <span id="statusText">Checking...</span></div>
            <div id="statusDetails"></div>
        </div>
        
        <div class="data-controls">
            <button class="data-button" id="refreshStatus" onclick="refreshDataStatus()">🔄 Refresh Status</button>
            <button class="data-button" id="loadData" onclick="loadData()">📥 Load Data</button>
            <button class="data-button" id="processData" onclick="processData()">⚙️ Process Data</button>
        </div>
        
        <div class="chat-box" id="chatBox">
            <div class="message bot-message">
                <strong>🤖 ClearCouncil Bot:</strong><br>
                Hello! I'm your enhanced ClearCouncil assistant. I can provide real information about York County government once the data is loaded. Please check the data status above and load the council data if needed.
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" class="message-input" placeholder="Ask about representatives, voting records, or council matters..." onkeypress="handleKeyPress(event)">
            <button class="send-button" onclick="sendMessage()">Send</button>
        </div>
        
        <div class="status" id="status">
            Ready to chat • Enhanced server running on localhost:8000
        </div>
    </div>

    <script>
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            refreshDataStatus();
        });
        
        function refreshDataStatus() {
            document.getElementById('statusText').textContent = 'Checking...';
            
            fetch('/data/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('dataStatus');
                    const statusText = document.getElementById('statusText');
                    const statusDetails = document.getElementById('statusDetails');
                    
                    statusText.textContent = data.message;
                    
                    if (data.status === 'loaded') {
                        statusDiv.className = 'data-status loaded';
                        statusDetails.innerHTML = `
                            <div>📊 Representatives: ${data.representatives_count}</div>
                            <div>🗳️ Voting Records: ${data.voting_records_count}</div>
                            <div>📅 Last Updated: ${data.last_loaded ? new Date(data.last_loaded).toLocaleString() : 'Unknown'}</div>
                        `;
                    } else if (data.status === 'error') {
                        statusDiv.className = 'data-status error';
                        statusDetails.innerHTML = `<div>❌ Error: ${data.message}</div>`;
                    } else {
                        statusDiv.className = 'data-status';
                        statusDetails.innerHTML = `<div>⚠️ Data not loaded. Please process or load data first.</div>`;
                    }
                })
                .catch(error => {
                    document.getElementById('statusText').textContent = 'Error checking status';
                    console.error('Error:', error);
                });
        }
        
        function loadData() {
            document.getElementById('statusText').textContent = 'Loading data...';
            refreshDataStatus();
        }
        
        function processData() {
            const button = document.getElementById('processData');
            button.disabled = true;
            button.textContent = '⚙️ Processing...';
            document.getElementById('statusText').textContent = 'Processing data...';
            
            fetch('/data/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                button.disabled = false;
                button.textContent = '⚙️ Process Data';
                refreshDataStatus();
                
                if (data.status === 'success') {
                    addMessage('bot', '✅ Data processing completed successfully! You can now ask questions about current council data.');
                } else {
                    addMessage('bot', `❌ Data processing failed: ${data.message}`);
                }
            })
            .catch(error => {
                button.disabled = false;
                button.textContent = '⚙️ Process Data';
                addMessage('bot', '❌ Error processing data. Please try again.');
                console.error('Error:', error);
            });
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage('user', message);
            input.value = '';
            
            document.getElementById('status').textContent = 'Bot is typing...';
            
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').textContent = 'Ready to chat • Enhanced server running on localhost:8000';
                addMessage('bot', data.response || 'Sorry, I encountered an error.');
            })
            .catch(error => {
                document.getElementById('status').textContent = 'Error occurred';
                addMessage('bot', 'Sorry, I encountered an error. Please try again.');
                console.error('Error:', error);
            });
        }
        
        function addMessage(sender, message) {
            const chatBox = document.getElementById('chatBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            const prefix = sender === 'user' ? '👤 You:' : '🤖 ClearCouncil Bot:';
            messageDiv.innerHTML = `<strong>${prefix}</strong><br>${message}`;
            
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_404(self):
        """Send 404 response"""
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def main():
    """Start the enhanced chat server"""
    print("🏛️ Enhanced ClearCouncil Chat Server")
    print("=" * 60)
    
    # Check GitHub token
    if GITHUB_TOKEN:
        print(f"✅ GitHub Token: Found (ghp_...{GITHUB_TOKEN[-4:]})")
    else:
        print("⚠️  GitHub Token: Not found - using enhanced mock responses")
    
    # Check database
    if Path("clearcouncil.db").exists():
        print("✅ Database: Found")
    else:
        print("⚠️  Database: Not found - data processing may be needed")
    
    # Check data file
    if Path("clearcouncil_data.json").exists():
        print("✅ Data File: Found")
    else:
        print("⚠️  Data File: Not found - data processing needed")
    
    # Start server
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, EnhancedChatHandler)
    
    print(f"\n🚀 Enhanced server starting on http://localhost:8000")
    print("📱 Open your browser to: http://localhost:8000")
    print("📊 Features: Real council data, voting records, representative info")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    main()