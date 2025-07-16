#!/usr/bin/env python3
"""
Enhanced Chat Integration for ClearCouncil
Integrates with existing modules for intelligent responses
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

class EnhancedChatProcessor:
    """Enhanced chat processor that integrates with ClearCouncil modules"""
    
    def __init__(self):
        self.councils = self.load_councils()
        self.vector_db = self.init_vector_db()
    
    def load_councils(self):
        """Load available councils"""
        try:
            from clearcouncil.config.settings import list_available_councils
            return list_available_councils()
        except ImportError as e:
            print(f"Warning: Could not import council settings: {e}")
            # Fallback: scan config directory
            config_dir = Path(__file__).parent / 'config' / 'councils'
            if config_dir.exists():
                return [f.stem for f in config_dir.glob('*.yaml') if f.name != 'template.yaml']
            return ['york_county_sc']
    
    def init_vector_db(self):
        """Initialize vector database if available"""
        try:
            from clearcouncil.core.database import VectorDatabase
            return VectorDatabase()
        except ImportError as e:
            print(f"Warning: Vector database not available: {e}")
            return None
    
    def search_documents(self, query: str, council_id: str = None) -> str:
        """Search through documents using vector database"""
        if not self.vector_db:
            return "Document search is currently unavailable. Please check system configuration."
        
        try:
            # This would integrate with your existing vector search
            # For now, return a placeholder
            return f"Searching documents for '{query}' in {council_id or 'all councils'}... (Vector search integration pending)"
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def get_council_info(self, council_id: str) -> str:
        """Get information about a specific council"""
        try:
            from clearcouncil.config.settings import load_council_config
            config = load_council_config(council_id)
            if config:
                return f"Council: {config.get('name', council_id)}\nLocation: {config.get('location', 'Unknown')}\nWebsite: {config.get('website', 'Not specified')}"
            else:
                return f"No configuration found for council: {council_id}"
        except ImportError:
            return f"Council information system not available for: {council_id}"
        except Exception as e:
            return f"Error loading council info: {str(e)}"
    
    def process_message(self, message: str, session_id: str, council_id: str = 'default') -> str:
        """Process message with enhanced capabilities"""
        message_lower = message.lower()
        
        # Enhanced greeting with council info
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            council_info = self.get_council_info(council_id) if council_id != 'default' else ""
            greeting = f"Hello! I'm your ClearCouncil AI assistant. I can help you find information about local government activities."
            if council_info:
                greeting += f"\n\nCurrent council: {council_id}\n{council_info}"
            greeting += "\n\nYou can ask me about:\n• Meeting minutes and agendas\n• Voting records and patterns\n• Representative information\n• Document search\n• Council policies"
            return greeting
        
        # Enhanced search capabilities
        if any(word in message_lower for word in ['search', 'find', 'look for']):
            search_query = message.replace('search', '').replace('find', '').replace('look for', '').strip()
            if search_query:
                return self.search_documents(search_query, council_id)
            return "What would you like me to search for? I can look through meeting documents, voting records, and other council materials."
        
        # Council-specific information
        if 'info' in message_lower and 'council' in message_lower:
            return self.get_council_info(council_id)
        
        # List councils
        if 'list' in message_lower and 'council' in message_lower:
            councils_list = '\n'.join([f"• {council}" for council in self.councils])
            return f"Available councils ({len(self.councils)}):\n{councils_list}\n\nTo get information about a specific council, ask 'tell me about [council_name]'."
        
        # Voting analysis
        if any(word in message_lower for word in ['vote', 'voting', 'ballot']):
            return f"I can analyze voting patterns for {council_id}. I can show you:\n• Individual representative voting records\n• Voting trends over time\n• Key decisions and their outcomes\n• Attendance patterns\n\nWhat specific voting information would you like to see?"
        
        # Meeting information
        if any(word in message_lower for word in ['meeting', 'agenda', 'minutes']):
            return f"I can help you find meeting information for {council_id}:\n• Recent meeting agendas\n• Meeting minutes and summaries\n• Upcoming scheduled meetings\n• Historical meeting data\n\nWhat specific meeting information are you looking for?"
        
        # Representatives
        if any(word in message_lower for word in ['representative', 'rep', 'councilmember', 'official']):
            return f"I can provide information about {council_id} representatives:\n• Current representatives and their roles\n• Contact information\n• Voting history\n• Committee assignments\n\nWhich representative would you like to know about?"
        
        # Help
        if 'help' in message_lower:
            return """🏛️ ClearCouncil AI Assistant Help

I can help you with:

📊 **Data Analysis:**
• Voting patterns and trends
• Meeting attendance analysis
• Policy impact assessments

📄 **Document Search:**
• Meeting minutes and agendas
• Policy documents
• Public records

👥 **Representative Information:**
• Voting histories
• Contact details
• Committee memberships

🔍 **Search Commands:**
• "search [topic]" - Find relevant documents
• "voting records for [name]" - Get voting history
• "meetings about [topic]" - Find relevant meetings
• "list councils" - Show available councils

Just ask me questions in natural language!"""
        
        # Default enhanced response
        return f"I understand you're asking about: '{message}'\n\nLet me search through {council_id} data for relevant information. You can be more specific by asking about:\n• Specific representatives or officials\n• Particular meetings or dates\n• Policy topics or keywords\n• Voting records on specific issues\n\nWhat would you like to focus on?"

# Integration function for the main server
def create_enhanced_chat():
    """Create enhanced chat processor"""
    return EnhancedChatProcessor()

if __name__ == '__main__':
    # Test the enhanced chat
    chat = EnhancedChatProcessor()
    print("Enhanced Chat System Initialized")
    print(f"Available councils: {chat.councils}")
    
    # Test interaction
    response = chat.process_message("Hello", "test", "york_county_sc")
    print(f"\nTest Response:\n{response}")
