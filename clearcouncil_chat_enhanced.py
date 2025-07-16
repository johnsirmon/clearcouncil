#!/usr/bin/env python3
"""
Enhanced ClearCouncil Chat with Real Data Integration

This enhanced version integrates preloaded voting data to provide real information
about representatives, voting patterns, and council activities.
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

# Import data preloader
try:
    from data_preloader import ClearCouncilDataPreloader
    DATA_PRELOADER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Data preloader not available: {e}")
    DATA_PRELOADER_AVAILABLE = False

class EnhancedClearCouncilChatBot:
    """Enhanced chat bot with real voting data integration."""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.current_council = None
        self.voting_data = {}
        self.data_loaded = False
        
        # Initialize original chatbot
        if CHATBOT_AVAILABLE:
            self.base_chatbot = ClearCouncilChatBot(github_token)
        else:
            self.base_chatbot = None
        
        # Load preloaded data
        self.load_voting_data()
    
    def load_voting_data(self):
        """Load preloaded voting data."""
        data_file = Path("clearcouncil_data.json")
        
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    self.voting_data = json.load(f)
                self.data_loaded = True
                print(f"✅ Loaded voting data: {len(self.voting_data.get('representatives', {}))} representatives, {len(self.voting_data.get('voting_records', []))} records")
            except Exception as e:
                print(f"❌ Error loading voting data: {e}")
                self.voting_data = {}
        else:
            print("⚠️  No preloaded data file found. Run data_preloader.py first.")
    
    def set_council(self, council_id: str) -> bool:
        """Set the current council context."""
        self.current_council = council_id
        if self.base_chatbot:
            return self.base_chatbot.set_council(council_id)
        return True
    
    def get_available_councils(self) -> list:
        """Get list of available councils."""
        if self.base_chatbot:
            return self.base_chatbot.get_available_councils()
        return ["york_county_sc"]
    
    def get_representative_info(self, name: str) -> dict:
        """Get detailed information about a representative."""
        if not self.data_loaded:
            return {"error": "Voting data not loaded"}
        
        representatives = self.voting_data.get("representatives", {})
        
        # Try exact match first
        if name in representatives:
            return representatives[name]
        
        # Try fuzzy matching
        name_lower = name.lower()
        matches = []
        for rep_name in representatives.keys():
            if (name_lower in rep_name.lower() or 
                rep_name.lower() in name_lower or
                any(part in rep_name.lower() for part in name_lower.split())):
                matches.append(rep_name)
        
        if matches:
            best_match = matches[0]
            return {
                "matched_name": best_match,
                **representatives[best_match]
            }
        
        return {"error": f"Representative '{name}' not found"}
    
    def get_voting_summary(self) -> dict:
        """Get overall voting summary."""
        if not self.data_loaded:
            return {"error": "Voting data not loaded"}
        
        return self.voting_data.get("statistics", {})
    
    def search_voting_records(self, query: str, limit: int = 10) -> list:
        """Search voting records by query."""
        if not self.data_loaded:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for record in self.voting_data.get("voting_records", []):
            # Search in various fields
            searchable_fields = [
                record.get("representative", ""),
                record.get("case_category", ""),
                record.get("location", "") or "",
                record.get("owner", "") or "",
                record.get("applicant", "") or "",
                record.get("zoning_request", "") or ""
            ]
            
            if any(query_lower in field.lower() for field in searchable_fields if field):
                matches.append(record)
                
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_representatives_list(self) -> list:
        """Get list of all representatives."""
        if not self.data_loaded:
            return []
        
        representatives = self.voting_data.get("representatives", {})
        return [
            {
                "name": name,
                "district": data.get("district", "Unknown"),
                "total_votes": data.get("total_votes", 0),
                "motions_made": data.get("motions_made", 0)
            }
            for name, data in representatives.items()
        ]
    
    def process_message(self, message: str) -> str:
        """Process a chat message with real data context."""
        if not self.current_council:
            return "Please select a council first before asking questions."
        
        # Determine what kind of information the user is asking for
        message_lower = message.lower()
        
        # Handle representative-specific queries
        if any(word in message_lower for word in ['representative', 'rep', 'who is', 'about']):
            return self.handle_representative_query(message)
        
        # Handle voting records queries
        if any(word in message_lower for word in ['vote', 'voting', 'voted', 'record']):
            return self.handle_voting_query(message)
        
        # Handle summary/statistics queries
        if any(word in message_lower for word in ['summary', 'statistics', 'stats', 'overview']):
            return self.handle_summary_query(message)
        
        # Handle representatives list queries
        if any(word in message_lower for word in ['list', 'show', 'all']):
            return self.handle_list_query(message)
        
        # For other queries, use the base chatbot with enhanced context
        return self.handle_general_query(message)
    
    def handle_representative_query(self, message: str) -> str:
        """Handle queries about specific representatives."""
        # Extract representative name from message
        words = message.split()
        potential_names = []
        
        # Look for names in the message
        for i, word in enumerate(words):
            if word.lower() in ['about', 'is', 'representative', 'rep']:
                # Take the next few words as potential name
                if i + 1 < len(words):
                    potential_names.append(words[i + 1])
                if i + 2 < len(words):
                    potential_names.append(f"{words[i + 1]} {words[i + 2]}")
        
        # Also check for common representative names
        representatives = self.voting_data.get("representatives", {})
        for rep_name in representatives.keys():
            if rep_name.lower() in message.lower():
                potential_names.append(rep_name)
        
        if potential_names:
            # Try to find the representative
            for name in potential_names:
                info = self.get_representative_info(name)
                if "error" not in info:
                    return self.format_representative_info(info)
        
        # If no specific rep found, show top representatives
        top_reps = self.get_representatives_list()[:5]
        response = "Here are the most active representatives in York County SC:\\n\\n"
        
        for rep in top_reps:
            response += f"• **{rep['name']}** ({rep['district']})\\n"
            response += f"  - Total votes: {rep['total_votes']}\\n"
            response += f"  - Motions made: {rep['motions_made']}\\n\\n"
        
        response += "Ask me about a specific representative for more details!"
        return response
    
    def handle_voting_query(self, message: str) -> str:
        """Handle queries about voting records."""
        # Extract search terms
        search_terms = []
        for word in message.split():
            if len(word) > 3 and word.lower() not in ['vote', 'voting', 'voted', 'record', 'records', 'what', 'show', 'about']:
                search_terms.append(word)
        
        if search_terms:
            # Search for voting records
            query = " ".join(search_terms)
            records = self.search_voting_records(query, limit=5)
            
            if records:
                response = f"Found {len(records)} voting records related to '{query}':\\n\\n"
                for record in records:
                    response += f"• **{record['representative']}** ({record['district']})\\n"
                    response += f"  - Case: {record['case_number']}\\n"
                    response += f"  - Vote Type: {record['vote_type']}\\n"
                    response += f"  - Result: {record['result']}\\n"
                    if record.get('location'):
                        response += f"  - Location: {record['location']}\\n"
                    response += "\\n"
                
                return response
            else:
                return f"No voting records found for '{query}'. Try asking about a specific representative or case type."
        
        # General voting information
        stats = self.get_voting_summary()
        response = f"**York County SC Voting Overview:**\\n\\n"
        response += f"• Total voting records: {stats.get('total_voting_records', 0)}\\n"
        response += f"• Total representatives: {stats.get('total_representatives', 0)}\\n"
        response += f"• Average votes per representative: {stats.get('average_votes_per_representative', 0):.1f}\\n\\n"
        
        response += "**Most Active Representatives:**\\n"
        for name, votes in stats.get('most_active_representatives', [])[:5]:
            response += f"• {name}: {votes} votes\\n"
        
        return response
    
    def handle_summary_query(self, message: str) -> str:
        """Handle summary/statistics queries."""
        stats = self.get_voting_summary()
        
        response = f"**York County SC Council Summary:**\\n\\n"
        response += f"📊 **Overall Statistics:**\\n"
        response += f"• Total voting records: {stats.get('total_voting_records', 0)}\\n"
        response += f"• Total representatives: {stats.get('total_representatives', 0)}\\n"
        response += f"• Average votes per representative: {stats.get('average_votes_per_representative', 0):.1f}\\n\\n"
        
        response += f"🏆 **Most Active Representatives:**\\n"
        for name, votes in stats.get('most_active_representatives', [])[:5]:
            response += f"• {name}: {votes} votes\\n"
        
        response += f"\\n📋 **Voting Results Distribution:**\\n"
        for result, count in stats.get('results_distribution', {}).items():
            response += f"• {result}: {count} cases\\n"
        
        response += f"\\n💡 Ask me about specific representatives or voting records for more details!"
        
        return response
    
    def handle_list_query(self, message: str) -> str:
        """Handle list queries."""
        if any(word in message.lower() for word in ['representative', 'rep']):
            reps = self.get_representatives_list()
            response = f"**York County SC Representatives:**\\n\\n"
            
            for rep in reps:
                response += f"• **{rep['name']}** ({rep['district']})\\n"
                response += f"  - {rep['total_votes']} total votes\\n"
                if rep['motions_made'] > 0:
                    response += f"  - {rep['motions_made']} motions made\\n"
                response += "\\n"
            
            response += f"Ask me about any specific representative for detailed information!"
            return response
        
        return "I can show you lists of representatives, voting records, or case categories. What would you like to see?"
    
    def handle_general_query(self, message: str) -> str:
        """Handle general queries using the base chatbot with enhanced context."""
        # Build enhanced context with real data
        context_data = {
            "council_id": self.current_council,
            "data_available": self.data_loaded,
            "statistics": self.get_voting_summary() if self.data_loaded else {},
            "sample_representatives": self.get_representatives_list()[:5] if self.data_loaded else []
        }
        
        # Create enhanced system prompt
        system_prompt = f"""You are ClearCouncil AI, a helpful assistant for York County SC local government data.

Real Council Data Available:
{json.dumps(context_data, indent=2)}

You have access to real voting records from York County SC including:
- 39 representatives with detailed voting histories
- 3,795 voting records with case details
- Representative activity patterns and statistics

Guidelines:
1. Use the real data provided above to answer questions
2. When asked about representatives, reference actual names and statistics
3. For voting queries, mention specific vote counts and patterns
4. Be helpful and factual about local government processes
5. Encourage civic engagement with real, actionable information

User message: {message}"""
        
        if self.base_chatbot and hasattr(self.base_chatbot, 'github_client'):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            return self.base_chatbot.github_client.chat_completion(messages)
        else:
            return "I'm ready to help with York County SC council information, but the AI connection is not available. Please check your GitHub token configuration."
    
    def format_representative_info(self, info: dict) -> str:
        """Format representative information for display."""
        name = info.get("matched_name", info.get("name", "Unknown"))
        district = info.get("district", "Unknown")
        total_votes = info.get("total_votes", 0)
        motions_made = info.get("motions_made", 0)
        seconds_given = info.get("seconds_given", 0)
        
        response = f"**{name}** ({district})\\n\\n"
        response += f"📊 **Voting Activity:**\\n"
        response += f"• Total votes: {total_votes}\\n"
        response += f"• Motions made: {motions_made}\\n"
        response += f"• Seconds given: {seconds_given}\\n\\n"
        
        # Add voting breakdown if available
        vote_breakdown = info.get("vote_breakdown", {})
        if vote_breakdown:
            response += f"🗳️ **Vote Breakdown:**\\n"
            for vote_type, count in vote_breakdown.items():
                if count > 0:
                    response += f"• {vote_type.title()}: {count}\\n"
            response += "\\n"
        
        # Add case categories if available
        case_categories = info.get("case_categories", {})
        if case_categories:
            response += f"📋 **Case Categories:**\\n"
            for category, count in sorted(case_categories.items(), key=lambda x: x[1], reverse=True)[:5]:
                response += f"• {category}: {count} cases\\n"
        
        return response

# Use the enhanced chatbot in the server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True

class ClearCouncilChatHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the enhanced ClearCouncil chat interface."""
    
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
        elif self.path == '/api/representatives':
            self.serve_representatives()
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
        """Get or create the enhanced chatbot instance."""
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
            
            # Use enhanced chatbot
            ClearCouncilChatHandler.chatbot = EnhancedClearCouncilChatBot(github_token)
        
        return ClearCouncilChatHandler.chatbot
    
    def serve_representatives(self):
        """Serve representatives list endpoint."""
        try:
            chatbot = self.get_chatbot()
            if chatbot and chatbot.data_loaded:
                representatives = chatbot.get_representatives_list()
                self.send_json_response({
                    "representatives": representatives,
                    "count": len(representatives)
                })
            else:
                self.send_json_response({
                    "representatives": [],
                    "count": 0,
                    "error": "Voting data not loaded"
                })
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)
    
    def serve_health_check(self):
        """Serve enhanced health check endpoint."""
        # Load GitHub token to check if it's available
        env_file = Path(".env")
        github_token = None
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('GITHUB_TOKEN='):
                        github_token = line.split('=', 1)[1].strip()
                        break
        
        # Check if chatbot is working
        chatbot_working = False
        data_loaded = False
        
        if CHATBOT_AVAILABLE and github_token:
            try:
                chatbot = self.get_chatbot()
                if chatbot:
                    if hasattr(chatbot, 'base_chatbot') and chatbot.base_chatbot:
                        chatbot_working = getattr(chatbot.base_chatbot.github_client, 'available', False)
                    data_loaded = chatbot.data_loaded
            except Exception as e:
                print(f"Chatbot check error: {e}")
        
        health_data = {
            "status": "healthy",
            "chatbot_available": CHATBOT_AVAILABLE,
            "clearcouncil_available": CLEARCOUNCIL_AVAILABLE,
            "github_token_configured": github_token is not None,
            "ai_working": chatbot_working,
            "data_loaded": data_loaded,
            "components": {
                "chatbot": "✅ Available" if CHATBOT_AVAILABLE else "❌ Not available",
                "clearcouncil": "✅ Available" if CLEARCOUNCIL_AVAILABLE else "❌ Limited",
                "github_token": "✅ Configured" if github_token else "❌ Not configured",
                "ai_api": "✅ Working" if chatbot_working else "❌ Not working",
                "voting_data": "✅ Loaded" if data_loaded else "❌ Not loaded"
            }
        }
        
        self.send_json_response(health_data)
    
    def serve_councils(self):
        """Serve councils list endpoint."""
        try:
            if CLEARCOUNCIL_AVAILABLE:
                councils = list_available_councils()
            else:
                councils = ["york_county_sc"]
            
            self.send_json_response({"councils": councils})
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)
    
    def handle_chat(self):
        """Handle enhanced chat message."""
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
                "timestamp": datetime.now().isoformat(),
                "data_loaded": chatbot.data_loaded if chatbot else False
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
                    "council_id": council_id,
                    "data_loaded": chatbot.data_loaded if chatbot else False
                })
            else:
                self.send_json_response({"error": "Failed to set council"}, status=500)
                
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=500)
    
    def serve_chat_page(self):
        """Serve the enhanced chat interface page."""
        # Use the same HTML from the basic version for now
        # The enhanced functionality is in the backend
        from clearcouncil_chat_server import ClearCouncilChatHandler as BaseHandler
        base_handler = BaseHandler()
        base_handler.send_response = self.send_response
        base_handler.send_header = self.send_header
        base_handler.end_headers = self.end_headers
        base_handler.wfile = self.wfile
        base_handler.serve_chat_page()
    
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
    """Start the enhanced ClearCouncil chat server."""
    port = int(os.environ.get('PORT', 5003))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🏛️ Enhanced ClearCouncil AI Chat Server")
    print(f"=" * 50)
    print(f"🌐 Starting server on http://{host}:{port}")
    print(f"📊 ClearCouncil modules: {'✅ Available' if CLEARCOUNCIL_AVAILABLE else '❌ Limited'}")
    print(f"🤖 ChatBot: {'✅ Available' if CHATBOT_AVAILABLE else '❌ Limited'}")
    print(f"📋 Data Preloader: {'✅ Available' if DATA_PRELOADER_AVAILABLE else '❌ Limited'}")
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