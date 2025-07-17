#!/usr/bin/env python3
"""
ClearCouncil Chat Web Application

A web-based chat interface that allows users to interact with ClearCouncil data
using GitHub's free AI models. Integrates with existing ClearCouncil logic.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import logging
import json
from datetime import datetime
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sqlite3
from contextlib import contextmanager

# Import existing ClearCouncil components
from clearcouncil.config.settings import load_council_config, list_available_councils
from clearcouncil.core.database import VectorDatabase
from clearcouncil.core.models import Document, ProcessingResult
from clearcouncil.parsers.voting_parser import VotingParser
from clearcouncil.analysis.voting_analyzer import VotingAnalyzer
from clearcouncil.analysis.time_range import TimeRangeParser
from clearcouncil.web.database import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('clearcouncil_chat.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    context_used: Optional[Dict[str, Any]] = None

class GitHubModelsClient:
    """Client for GitHub Models API."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://models.inference.ai.azure.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models."""
        try:
            response = requests.get(
                f"{self.base_url}/catalog/models",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []
    
    def chat_completion(self, messages: List[Dict], model: str = "gpt-4o-mini") -> str:
        """Send chat completion request."""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.base_url}/inference/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

class ClearCouncilChatBot:
    """Main chat bot that integrates with ClearCouncil data."""
    
    def __init__(self, github_token: str):
        self.github_client = GitHubModelsClient(github_token)
        self.vector_db = None
        self.current_council = None
        self.time_parser = TimeRangeParser()
        
    def set_council(self, council_id: str):
        """Set the current council context."""
        try:
            self.current_council = council_id
            config = load_council_config(council_id)
            self.vector_db = VectorDatabase(council_id)
            logger.info(f"Set council context to: {council_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting council {council_id}: {e}")
            return False
    
    def search_documents(self, query: str, limit: int = 5) -> List[Dict]:
        """Search documents using vector database."""
        if not self.vector_db:
            return []
        
        try:
            results = self.vector_db.search(query, limit=limit)
            return [
                {
                    "content": result.page_content,
                    "metadata": result.metadata,
                    "score": getattr(result, 'score', 0)
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_voting_data(self, representative: str, time_range: str) -> Dict:
        """Get voting data for a representative."""
        if not self.current_council:
            return {}
        
        try:
            analyzer = VotingAnalyzer(self.current_council)
            start_date, end_date = self.time_parser.parse_time_range(time_range)
            
            # Get voting records
            voting_records = analyzer.get_representative_votes(
                representative, start_date, end_date
            )
            
            return {
                "representative": representative,
                "time_range": time_range,
                "vote_count": len(voting_records),
                "voting_records": voting_records[:10]  # Limit for context
            }
        except Exception as e:
            logger.error(f"Error getting voting data: {e}")
            return {}
    
    def get_council_context(self) -> Dict:
        """Get context about the current council."""
        if not self.current_council:
            return {}
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get document count
                cursor.execute("""
                    SELECT COUNT(*) as doc_count 
                    FROM documents 
                    WHERE council_id = ?
                """, (self.current_council,))
                doc_count = cursor.fetchone()['doc_count']
                
                # Get representative count
                cursor.execute("""
                    SELECT COUNT(DISTINCT representative) as rep_count 
                    FROM voting_records 
                    WHERE council_id = ?
                """, (self.current_council,))
                rep_count = cursor.fetchone()['rep_count']
                
                # Get recent representatives
                cursor.execute("""
                    SELECT DISTINCT representative 
                    FROM voting_records 
                    WHERE council_id = ? 
                    ORDER BY date DESC 
                    LIMIT 10
                """, (self.current_council,))
                representatives = [row['representative'] for row in cursor.fetchall()]
                
                return {
                    "council_id": self.current_council,
                    "document_count": doc_count,
                    "representative_count": rep_count,
                    "recent_representatives": representatives
                }
        except Exception as e:
            logger.error(f"Error getting council context: {e}")
            return {}
    
    def process_chat_message(self, message: str, context: Dict = None) -> str:
        """Process a chat message and return response."""
        # Determine if user is asking about specific data
        context_data = {}
        
        # Check if asking about voting/representatives
        if any(keyword in message.lower() for keyword in ['vote', 'voting', 'representative', 'council']):
            context_data.update(self.get_council_context())
        
        # Check if asking about specific documents
        if any(keyword in message.lower() for keyword in ['document', 'meeting', 'minutes', 'ordinance']):
            search_results = self.search_documents(message)
            context_data['search_results'] = search_results
        
        # Build system prompt with context
        system_prompt = f"""You are ClearCouncil AI, a helpful assistant for understanding local government data.
        
Current Council: {self.current_council or 'None selected'}

Available Data Context:
{json.dumps(context_data, indent=2) if context_data else 'No specific context available'}

Guidelines:
1. Help users understand local government data and processes
2. Answer questions about voting records, representatives, and council documents
3. Provide clear, factual information based on available data
4. If you don't have specific data, explain what information would be helpful
5. Suggest specific queries or actions the user can take
6. Be concise but informative

User Message: {message}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        return self.github_client.chat_completion(messages)

# Flask App Setup
template_dir = Path(__file__).parent / "src" / "clearcouncil" / "web" / "templates"
app = Flask(__name__, template_folder=str(template_dir))
app.secret_key = os.environ.get('SECRET_KEY', 'clearcouncil-chat-secret')
CORS(app)

# Initialize chat bot
github_token = os.environ.get('GITHUB_TOKEN')
if not github_token:
    logger.warning("GITHUB_TOKEN not found. Please set it in your environment.")
    chatbot = None
else:
    chatbot = ClearCouncilChatBot(github_token)

@app.route('/')
def index():
    """Main chat interface."""
    councils = list_available_councils()
    return render_template('chat.html', councils=councils)

@app.route('/api/councils')
def get_councils():
    """Get available councils."""
    try:
        councils = list_available_councils()
        return jsonify({"councils": councils})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/set-council', methods=['POST'])
def set_council():
    """Set the current council context."""
    if not chatbot:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    data = request.get_json()
    council_id = data.get('council_id')
    
    if not council_id:
        return jsonify({"error": "Council ID required"}), 400
    
    success = chatbot.set_council(council_id)
    if success:
        session['council_id'] = council_id
        return jsonify({"success": True, "council_id": council_id})
    else:
        return jsonify({"error": "Failed to set council"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    if not chatbot:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({"error": "Message required"}), 400
    
    # Ensure council is set
    council_id = session.get('council_id')
    if council_id and chatbot.current_council != council_id:
        chatbot.set_council(council_id)
    
    try:
        response = chatbot.process_chat_message(message)
        return jsonify({
            "response": response,
            "council_id": chatbot.current_council,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({"error": "Failed to process message"}), 500

@app.route('/api/search', methods=['POST'])
def search_documents():
    """Search documents endpoint."""
    if not chatbot:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    data = request.get_json()
    query = data.get('query', '')
    limit = data.get('limit', 5)
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    try:
        results = chatbot.search_documents(query, limit)
        return jsonify({"results": results})
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return jsonify({"error": "Failed to search documents"}), 500

@app.route('/api/representatives')
def get_representatives():
    """Get representatives for current council."""
    if not chatbot or not chatbot.current_council:
        return jsonify({"error": "No council selected"}), 400
    
    try:
        context = chatbot.get_council_context()
        return jsonify({
            "representatives": context.get('recent_representatives', []),
            "count": context.get('representative_count', 0)
        })
    except Exception as e:
        logger.error(f"Error getting representatives: {e}")
        return jsonify({"error": "Failed to get representatives"}), 500

@app.route('/api/voting-data', methods=['POST'])
def get_voting_data():
    """Get voting data for a representative."""
    if not chatbot:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    data = request.get_json()
    representative = data.get('representative', '')
    time_range = data.get('time_range', 'last year')
    
    if not representative:
        return jsonify({"error": "Representative required"}), 400
    
    try:
        voting_data = chatbot.get_voting_data(representative, time_range)
        return jsonify(voting_data)
    except Exception as e:
        logger.error(f"Error getting voting data: {e}")
        return jsonify({"error": "Failed to get voting data"}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "github_token_configured": github_token is not None,
        "current_council": chatbot.current_council if chatbot else None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)