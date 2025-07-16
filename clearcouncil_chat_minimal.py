#!/usr/bin/env python3
"""
ClearCouncil Chat - Minimal Version

A simplified version of the chat application that works with basic dependencies.
This version demonstrates the core functionality without requiring the full stack.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Any, Optional

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Try to import ClearCouncil components
try:
    from clearcouncil.config.settings import list_available_councils, load_council_config
    CLEARCOUNCIL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ClearCouncil components not fully available: {e}")
    CLEARCOUNCIL_AVAILABLE = False

# Try to import requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("Warning: requests module not available")
    REQUESTS_AVAILABLE = False

class MockGitHubClient:
    """Mock GitHub client for testing without actual API calls."""
    
    def __init__(self):
        self.available = False
    
    def get_available_models(self) -> List[Dict]:
        return [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
        ]
    
    def chat_completion(self, messages: List[Dict], model: str = "gpt-4o-mini") -> str:
        # Mock response for testing
        user_message = messages[-1].get("content", "")
        
        # Simple rule-based responses for testing
        if "representative" in user_message.lower():
            return "Based on the available data, I can help you find information about representatives. However, this is a mock response for testing purposes."
        elif "vote" in user_message.lower() or "voting" in user_message.lower():
            return "I can analyze voting patterns and records. This is a mock response - in the real version, I would search through your council's voting data."
        elif "document" in user_message.lower():
            return "I can search through council documents and minutes. This is a mock response for testing purposes."
        elif "help" in user_message.lower():
            return """I'm ClearCouncil AI! I can help you with:
            
• Finding information about representatives
• Analyzing voting patterns and records  
• Searching through council documents
• Explaining municipal terms and processes
• Comparing representatives or districts

Try asking me something like:
- "Show me representatives for this council"
- "What documents are available?"
- "How did John Smith vote on recent issues?"

Note: This is a test version with mock responses."""
        else:
            return f"I received your message: '{user_message}'. This is a mock response for testing. In the real version, I would use GitHub's AI models to provide intelligent responses about your council data."

class GitHubModelsClient:
    """Real GitHub Models API client."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://models.github.ai"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.available = False
        self._test_connection()
    
    def _test_connection(self):
        """Test if the GitHub API is accessible."""
        if not REQUESTS_AVAILABLE:
            return
        
        try:
            # Test with a simple chat completion
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.base_url}/inference/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            self.available = response.status_code == 200
        except Exception:
            self.available = False
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models."""
        if not self.available or not REQUESTS_AVAILABLE:
            return []
        
        try:
            # For GitHub Models, we'll return some known models
            return [
                {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
            ]
        except Exception:
            return []
    
    def chat_completion(self, messages: List[Dict], model: str = "gpt-4o-mini") -> str:
        """Send chat completion request."""
        if not self.available or not REQUESTS_AVAILABLE:
            return "GitHub Models API not available. Please check your connection and token."
        
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
            return f"Sorry, I encountered an error: {str(e)}"

class ClearCouncilChatBot:
    """Simplified chat bot for testing."""
    
    def __init__(self, github_token: str):
        self.current_council = None
        
        # Try to initialize GitHub client
        if github_token and github_token != 'your_github_token_here':
            self.github_client = GitHubModelsClient(github_token)
            if not self.github_client.available:
                print("GitHub API not available, using mock client")
                self.github_client = MockGitHubClient()
        else:
            print("No GitHub token provided, using mock client")
            self.github_client = MockGitHubClient()
    
    def set_council(self, council_id: str) -> bool:
        """Set the current council context."""
        if not CLEARCOUNCIL_AVAILABLE:
            print(f"ClearCouncil modules not available, mocking council: {council_id}")
            self.current_council = council_id
            return True
        
        try:
            config = load_council_config(council_id)
            self.current_council = council_id
            print(f"Successfully set council to: {council_id}")
            return True
        except Exception as e:
            print(f"Error setting council {council_id}: {e}")
            return False
    
    def get_available_councils(self) -> List[str]:
        """Get list of available councils."""
        if not CLEARCOUNCIL_AVAILABLE:
            return ["york_county_sc", "test_council"]
        
        try:
            return list_available_councils()
        except Exception as e:
            print(f"Error getting councils: {e}")
            return []
    
    def get_council_info(self) -> Dict:
        """Get information about the current council."""
        if not self.current_council:
            return {"error": "No council selected"}
        
        return {
            "council_id": self.current_council,
            "status": "connected",
            "mock_data": True if not CLEARCOUNCIL_AVAILABLE else False
        }
    
    def process_message(self, message: str) -> str:
        """Process a chat message."""
        if not self.current_council:
            return "Please select a council first before asking questions."
        
        # Build context
        context_info = self.get_council_info()
        
        system_prompt = f"""You are ClearCouncil AI, a helpful assistant for local government transparency.

Current Council: {self.current_council}
Context: {json.dumps(context_info, indent=2)}

You help citizens understand:
- Local government processes
- Representative voting patterns  
- Council meeting minutes and documents
- Municipal terminology

Be helpful, factual, and encourage civic engagement.

User message: {message}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        return self.github_client.chat_completion(messages)

def test_chat_functionality():
    """Test the chat functionality."""
    print("🤖 Testing ClearCouncil Chat Functionality")
    print("=" * 50)
    
    # Load environment
    env_file = Path(".env")
    github_token = None
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('GITHUB_TOKEN='):
                    github_token = line.split('=', 1)[1].strip()
                    break
    
    print(f"🔑 GitHub Token: {'✅ Found' if github_token else '❌ Not found'}")
    if github_token:
        print(f"   Token: {github_token[:12]}...")  # Show first 12 chars
    
    # Initialize chatbot
    chatbot = ClearCouncilChatBot(github_token)
    
    # Test getting councils
    print("\n📋 Testing council listing...")
    councils = chatbot.get_available_councils()
    print(f"Available councils: {councils}")
    
    # Test setting council
    if councils:
        print(f"\n🏛️ Testing council selection...")
        test_council = councils[0]
        success = chatbot.set_council(test_council)
        print(f"Set council '{test_council}': {'✅ Success' if success else '❌ Failed'}")
        
        # Test getting council info
        print(f"\n📊 Testing council info...")
        info = chatbot.get_council_info()
        print(f"Council info: {json.dumps(info, indent=2)}")
        
        # Test chat messages
        print(f"\n💬 Testing chat messages...")
        
        test_messages = [
            "Hello, what can you help me with?",
            "Show me information about representatives",
            "What voting records are available?",
            "Help me understand this council's structure"
        ]
        
        for msg in test_messages:
            print(f"\n👤 User: {msg}")
            response = chatbot.process_message(msg)
            print(f"🤖 Bot: {response}")
            print("-" * 40)
    
    # Test API connectivity
    print(f"\n🔗 API Status:")
    print(f"GitHub Client Available: {chatbot.github_client.available if hasattr(chatbot.github_client, 'available') else 'Mock'}")
    print(f"ClearCouncil Modules: {'✅ Available' if CLEARCOUNCIL_AVAILABLE else '❌ Limited'}")
    print(f"Requests Module: {'✅ Available' if REQUESTS_AVAILABLE else '❌ Not Available'}")

def main():
    """Main function for testing."""
    try:
        test_chat_functionality()
        print("\n🎉 Test completed successfully!")
        print("\nTo use the full web interface:")
        print("1. Install missing dependencies: pip install flask flask-cors python-dotenv")
        print("2. Add your GitHub token to .env file")
        print("3. Run: python clearcouncil_chat.py")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()