#!/usr/bin/env python3
"""
Simple HTTP server for ClearCouncil Chat
Uses built-in http.server module to serve the chat interface
"""

import os
import sys
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import threading
import time

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

# Load environment
env_vars = load_env()
GITHUB_TOKEN = env_vars.get('GITHUB_TOKEN', os.getenv('GITHUB_TOKEN'))

class GitHubClient:
    """Simple GitHub Models API client"""
    
    def __init__(self, token):
        self.token = token
        self.base_url = "https://models.github.ai/inference/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages, model="gpt-4o-mini"):
        """Send chat completion request"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
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

class ChatHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the chat interface"""
    
    def __init__(self, *args, **kwargs):
        self.github_client = GitHubClient(GITHUB_TOKEN) if GITHUB_TOKEN else None
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_html()
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
        else:
            self.send_404()
    
    def handle_chat(self, message):
        """Handle chat messages"""
        try:
            if not self.github_client:
                response = self.get_mock_response(message)
            else:
                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for ClearCouncil, a local government transparency tool. Help users understand local government processes, representative voting patterns, and civic engagement in York County, SC."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
                
                response = self.github_client.chat_completion(messages)
                
                # If GitHub API returns an error, fall back to mock response
                if response.startswith("Error:"):
                    response = self.get_mock_response(message)
            
            self.send_json_response({"response": response})
        except Exception as e:
            # Fallback to mock response on any error
            response = self.get_mock_response(message)
            self.send_json_response({"response": response})
    
    def get_mock_response(self, message):
        """Generate mock responses when GitHub API is not available"""
        message_lower = message.lower()
        
        if "representative" in message_lower or "who are" in message_lower:
            return """The York County Council consists of several representatives who serve different districts:

**Current Council Structure:**
- **District 1**: Representative serves the northern part of the county
- **District 2**: Representative serves the central-north area
- **District 3**: Representative serves the central area
- **District 4**: Representative serves the southern area
- **District 5**: Representative serves the western area
- **District 6**: Representative serves the eastern area

**Council Leadership:**
- **Chairman**: Elected by council members to lead meetings
- **Vice-Chairman**: Assists the chairman and fills in when needed

To find your specific representative, you can:
1. Check the York County website for current representatives
2. Contact the County Clerk's office
3. Look up your district based on your address

Would you like to know more about any specific representative or district?"""
        elif "voting" in message_lower or "vote" in message_lower:
            return "Voting records are available through council meeting minutes and roll call votes. These show how each representative voted on specific issues and ordinances."
        elif "hello" in message_lower or "help" in message_lower:
            return "Hello! I can assist you with understanding local government processes, representative voting patterns, and civic engagement in York County, SC. What would you like to know?"
        else:
            return f"Thank you for your question about: {message}. I can help you understand local government processes and representative information. Please ask me about council structure, voting records, or civic engagement."
    
    def serve_html(self):
        """Serve the HTML chat interface"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ClearCouncil Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
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
            margin-bottom: 30px;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ ClearCouncil Chat</h1>
            <p>Ask me about local government in York County, SC</p>
        </div>
        
        <div class="chat-box" id="chatBox">
            <div class="message bot-message">
                <strong>🤖 ClearCouncil Bot:</strong><br>
                Hello! I can help you understand local government processes, representative voting patterns, and civic engagement in York County, SC. What would you like to know?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" class="message-input" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
            <button class="send-button" onclick="sendMessage()">Send</button>
        </div>
        
        <div class="status" id="status">
            Ready to chat • Server running on localhost:8000
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage('user', message);
            input.value = '';
            
            // Show typing indicator
            document.getElementById('status').textContent = 'Bot is typing...';
            
            // Send message to server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').textContent = 'Ready to chat • Server running on localhost:8000';
                addMessage('bot', data.response || 'Sorry, I encountered an error.');
            })
            .catch(error => {
                document.getElementById('status').textContent = 'Error occurred';
                addMessage('bot', 'Sorry, I encountered an error. Please try again.');
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
    """Start the chat server"""
    print("🏛️ ClearCouncil Chat Server")
    print("=" * 50)
    
    # Check GitHub token
    if GITHUB_TOKEN:
        print(f"✅ GitHub Token: Found (ghp_...{GITHUB_TOKEN[-4:]})")
    else:
        print("⚠️  GitHub Token: Not found - using mock responses")
    
    # Start server
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ChatHandler)
    
    print(f"🚀 Server starting on http://localhost:8000")
    print("📱 Open your browser to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    main()