#!/usr/bin/env python3
"""
ClearCouncil Chat Server - Basic HTTP Server Version

A web server that works with Python's built-in HTTP server modules,
providing the ClearCouncil chat interface without requiring Flask.
"""

import sys
import os
import json
import urllib.parse
import urllib.request
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime
import html
import threading
import time

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import existing ClearCouncil components
try:
    from clearcouncil.config.settings import list_available_councils, load_council_config
    CLEARCOUNCIL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ClearCouncil components not available: {e}")
    CLEARCOUNCIL_AVAILABLE = False

# Import the chat bot from our minimal version
try:
    from clearcouncil_chat_minimal import ClearCouncilChatBot
    CHATBOT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ChatBot not available: {e}")
    CHATBOT_AVAILABLE = False

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True

class ClearCouncilChatHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the ClearCouncil chat interface."""
    
    # Class-level chatbot instance
    chatbot = None
    
    def log_message(self, format, *args):
        """Custom logging to reduce noise."""
        pass  # Suppress default logging
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.serve_chat_page()
        elif self.path == '/health':
            self.serve_health_check()
        elif self.path == '/api/councils':
            self.serve_councils()
        elif self.path.startswith('/api/'):
            self.serve_api_error("GET not supported for this endpoint")
        else:
            self.serve_404()
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/chat':
            self.handle_chat()
        elif self.path == '/api/set-council':
            self.handle_set_council()
        else:
            self.serve_api_error("Endpoint not found")
    
    def get_chatbot(self):
        """Get or create the chatbot instance."""
        if ClearCouncilChatHandler.chatbot is None:
            # Load GitHub token from environment
            env_file = Path(".env")
            github_token = None
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('GITHUB_TOKEN='):
                            github_token = line.split('=', 1)[1].strip()
                            break
            
            print(f"🔑 GitHub token loaded: {'✅ Yes' if github_token else '❌ No'}")
            
            if CHATBOT_AVAILABLE:
                ClearCouncilChatHandler.chatbot = ClearCouncilChatBot(github_token)
            else:
                ClearCouncilChatHandler.chatbot = None
        
        return ClearCouncilChatHandler.chatbot
    
    def serve_chat_page(self):
        """Serve the main chat interface."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClearCouncil AI Chat</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: #007bff;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 1.5em;
        }
        .status {
            background: #e9ecef;
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }
        .status-item {
            margin: 5px 0;
            font-size: 0.9em;
        }
        .status-connected {
            color: #28a745;
        }
        .status-disconnected {
            color: #dc3545;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background: #e9ecef;
            color: #333;
            margin-right: auto;
        }
        .system-message {
            background: #fff3cd;
            color: #856404;
            margin: 10px auto;
            text-align: center;
            font-style: italic;
        }
        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #dee2e6;
        }
        .input-row {
            display: flex;
            gap: 10px;
        }
        .council-select {
            width: 200px;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            font-size: 0.9em;
        }
        .message-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            font-size: 1em;
        }
        .send-button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        .send-button:hover {
            background: #0056b3;
        }
        .send-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        .quick-actions {
            margin-top: 10px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .quick-action {
            padding: 5px 10px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 15px;
            font-size: 0.8em;
            cursor: pointer;
        }
        .quick-action:hover {
            background: #e9ecef;
        }
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ ClearCouncil AI Chat</h1>
            <p>Chat with your local government data using free GitHub AI</p>
        </div>
        
        <div class="status">
            <div class="status-item">
                <strong>Connection:</strong> 
                <span id="connectionStatus" class="status-disconnected">Checking...</span>
            </div>
            <div class="status-item">
                <strong>Council:</strong> 
                <span id="councilStatus" class="status-disconnected">None selected</span>
            </div>
            <div class="status-item">
                <strong>AI Model:</strong> 
                <span>GitHub GPT-4o-mini (Free)</span>
            </div>
        </div>
        
        <div id="chatContainer" class="chat-container">
            <div class="message bot-message">
                <strong>🤖 ClearCouncil AI</strong><br>
                Welcome! I'm your AI assistant for local government transparency. 
                <br><br>
                <strong>To get started:</strong><br>
                1. Select a council from the dropdown below<br>
                2. Ask me questions about representatives, voting records, or documents<br>
                3. Use the quick actions for common queries<br>
                <br>
                <em>Examples:</em><br>
                • "Show me voting records for John Smith"<br>
                • "What happened in the last council meeting?"<br>
                • "Explain how local government works"
            </div>
        </div>
        
        <div class="input-container">
            <div class="input-row">
                <select id="councilSelect" class="council-select">
                    <option value="">Select council...</option>
                </select>
                <input type="text" id="messageInput" class="message-input" 
                       placeholder="Ask me about your council data..." disabled>
                <button id="sendButton" class="send-button" onclick="sendMessage()" disabled>Send</button>
            </div>
            
            <div class="quick-actions">
                <div class="quick-action" onclick="quickAction('What representatives are available?')">
                    📊 Show Representatives
                </div>
                <div class="quick-action" onclick="quickAction('What voting records are available?')">
                    🗳️ Voting Records
                </div>
                <div class="quick-action" onclick="quickAction('Explain how local government works')">
                    📚 How Government Works
                </div>
                <div class="quick-action" onclick="quickAction('What documents are available?')">
                    📄 Documents
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentCouncil = '';
        let isLoading = false;
        
        // Initialize the app
        document.addEventListener('DOMContentLoaded', function() {
            checkConnection();
            loadCouncils();
            setupEventListeners();
        });
        
        function setupEventListeners() {
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            document.getElementById('councilSelect').addEventListener('change', function() {
                setCouncil(this.value);
            });
        }
        
        async function checkConnection() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                const statusElement = document.getElementById('connectionStatus');
                if (data.status === 'healthy') {
                    statusElement.textContent = 'Connected';
                    statusElement.className = 'status-connected';
                } else {
                    statusElement.textContent = 'Connection issues';
                    statusElement.className = 'status-disconnected';
                }
            } catch (error) {
                console.error('Connection check failed:', error);
                document.getElementById('connectionStatus').textContent = 'Connection failed';
            }
        }
        
        async function loadCouncils() {
            try {
                const response = await fetch('/api/councils');
                const data = await response.json();
                
                const select = document.getElementById('councilSelect');
                select.innerHTML = '<option value="">Select council...</option>';
                
                if (data.councils) {
                    data.councils.forEach(council => {
                        const option = document.createElement('option');
                        option.value = council;
                        option.textContent = council.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                        select.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error loading councils:', error);
                addMessage('system', 'Error loading councils. Please refresh the page.');
            }
        }
        
        async function setCouncil(councilId) {
            if (!councilId) {
                currentCouncil = '';
                document.getElementById('councilStatus').textContent = 'None selected';
                document.getElementById('councilStatus').className = 'status-disconnected';
                document.getElementById('messageInput').disabled = true;
                document.getElementById('sendButton').disabled = true;
                return;
            }
            
            try {
                const response = await fetch('/api/set-council', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ council_id: councilId })
                });
                
                const data = await response.json();
                if (data.success) {
                    currentCouncil = councilId;
                    document.getElementById('councilStatus').textContent = councilId.replace('_', ' ').toUpperCase();
                    document.getElementById('councilStatus').className = 'status-connected';
                    document.getElementById('messageInput').disabled = false;
                    document.getElementById('sendButton').disabled = false;
                    
                    addMessage('system', `✅ Connected to ${councilId.replace('_', ' ').toUpperCase()}. You can now ask questions!`);
                } else {
                    addMessage('system', `❌ Failed to connect to ${councilId}: ${data.error}`);
                }
            } catch (error) {
                console.error('Error setting council:', error);
                addMessage('system', '❌ Error connecting to council. Please try again.');
            }
        }
        
        async function sendMessage() {
            if (isLoading) return;
            
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            if (!currentCouncil) {
                addMessage('system', '⚠️ Please select a council first.');
                return;
            }
            
            // Add user message
            addMessage('user', message);
            input.value = '';
            
            // Show loading
            isLoading = true;
            document.getElementById('sendButton').disabled = true;
            document.getElementById('sendButton').textContent = 'Sending...';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.response) {
                    addMessage('bot', data.response);
                } else {
                    addMessage('system', `❌ Error: ${data.error}`);
                }
            } catch (error) {
                console.error('Error sending message:', error);
                addMessage('system', '❌ Error sending message. Please try again.');
            } finally {
                isLoading = false;
                document.getElementById('sendButton').disabled = false;
                document.getElementById('sendButton').textContent = 'Send';
            }
        }
        
        function addMessage(role, content) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            
            let messageClass = '';
            let prefix = '';
            
            switch (role) {
                case 'user':
                    messageClass = 'user-message';
                    prefix = '<strong>👤 You</strong><br>';
                    break;
                case 'bot':
                    messageClass = 'bot-message';
                    prefix = '<strong>🤖 ClearCouncil AI</strong><br>';
                    break;
                case 'system':
                    messageClass = 'system-message';
                    prefix = '';
                    break;
            }
            
            messageDiv.className = `message ${messageClass}`;
            messageDiv.innerHTML = prefix + content.replace(/\\n/g, '<br>');
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function quickAction(message) {
            if (!currentCouncil) {
                addMessage('system', '⚠️ Please select a council first.');
                return;
            }
            
            document.getElementById('messageInput').value = message;
            sendMessage();
        }
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(html_content)))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def serve_health_check(self):
        """Serve health check endpoint."""
        health_data = {
            "status": "healthy",
            "chatbot_available": CHATBOT_AVAILABLE,
            "clearcouncil_available": CLEARCOUNCIL_AVAILABLE
        }
        
        self.send_json_response(health_data)
    
    def serve_councils(self):
        """Serve councils list endpoint."""
        try:
            if CLEARCOUNCIL_AVAILABLE:
                councils = list_available_councils()
            else:
                councils = ["york_county_sc", "test_council"]
            
            self.send_json_response({"councils": councils})
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)
    
    def handle_chat(self):
        """Handle chat message."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '')
            if not message:
                self.send_json_response({"error": "Message required"}, status=400)
                return
            
            chatbot = self.get_chatbot()
            if chatbot:
                response = chatbot.process_message(message)
            else:
                response = "Sorry, the chatbot is not available. Please check the server configuration."
            
            self.send_json_response({
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)
    
    def handle_set_council(self):
        """Handle set council request."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            council_id = data.get('council_id')
            if not council_id:
                self.send_json_response({"error": "Council ID required"}, status=400)
                return
            
            chatbot = self.get_chatbot()
            if chatbot:
                success = chatbot.set_council(council_id)
            else:
                success = False
            
            if success:
                self.send_json_response({
                    "success": True,
                    "council_id": council_id
                })
            else:
                self.send_json_response({"error": "Failed to set council"}, status=500)
                
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)
    
    def serve_api_error(self, message):
        """Serve API error response."""
        self.send_json_response({"error": message}, status=404)
    
    def serve_404(self):
        """Serve 404 page."""
        self.send_response(404)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>404 Not Found</h1><p>The requested resource was not found.</p>")
    
    def send_json_response(self, data, status=200):
        """Send JSON response."""
        json_data = json.dumps(data, indent=2)
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(json_data)))
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))

def main():
    """Start the ClearCouncil chat server."""
    port = int(os.environ.get('PORT', 5002))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🏛️ ClearCouncil AI Chat Server")
    print(f"=" * 50)
    print(f"🌐 Starting server on http://{host}:{port}")
    print(f"📊 ClearCouncil modules: {'✅ Available' if CLEARCOUNCIL_AVAILABLE else '❌ Limited'}")
    print(f"🤖 ChatBot: {'✅ Available' if CHATBOT_AVAILABLE else '❌ Limited'}")
    print(f"🔑 GitHub token: {'✅ Configured' if os.path.exists('.env') else '❌ Not found'}")
    print(f"")
    print(f"📱 Open in browser: http://localhost:{port}")
    print(f"❌ Press Ctrl+C to stop")
    print(f"=" * 50)
    
    try:
        server = ThreadedHTTPServer((host, port), ClearCouncilChatHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()