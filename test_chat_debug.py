#!/usr/bin/env python3
"""Test script to debug chat functionality"""

import sys
import os
sys.path.append('.')

# Set up environment
os.environ['GITHUB_TOKEN'] = os.getenv('GITHUB_TOKEN', 'your-token-here')

from enhanced_chat_server import EnhancedChatHandler, DataManager, GitHubClient

print("🔍 Testing Enhanced Chat Components")
print("=" * 50)

# Test 1: DataManager
print("\n1️⃣ Testing DataManager...")
dm = DataManager()
status = dm.get_data_status()
print(f"Status: {status}")

if status['status'] == 'loaded':
    context = dm.get_context_for_question("who are my representatives")
    print(f"Context generated: {context[:200]}...")
    
    # Test 2: GitHubClient
    print("\n2️⃣ Testing GitHubClient...")
    gc = GitHubClient(os.getenv('GITHUB_TOKEN', 'your-token-here'))
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant for ClearCouncil. Context: " + context[:500]},
        {"role": "user", "content": "who are my representatives"}
    ]
    
    response = gc.chat_completion(messages)
    print(f"Chat response: {response}")
    
    # Test 3: Enhanced Chat Handler
    print("\n3️⃣ Testing EnhancedChatHandler...")
    handler = EnhancedChatHandler()
    full_response = handler.process_message("who are my representatives")
    print(f"Enhanced response: {full_response}")
    
else:
    print("❌ Data not loaded - check data loading process")

print("\n✅ Testing complete!")
