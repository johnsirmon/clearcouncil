#!/bin/bash

# ClearCouncil Setup Script
# This script sets up the environment and installs all required dependencies

echo "🔧 Setting up ClearCouncil environment..."

# Check if virtual environment exists
if [ ! -d "clearcouncil_env" ]; then
    echo "❌ Virtual environment not found. Creating new one..."
    python3 -m venv clearcouncil_env
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source clearcouncil_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Install additional dependencies that were missing
echo "🔧 Installing additional dependencies..."
pip install -U langchain-community
pip install -U langchain-openai

echo "✅ Installation complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Get an OpenAI API key from: https://platform.openai.com/api-keys"
echo "2. Edit the .env file and add your API key:"
echo "   OPENAI_API_KEY=your_actual_api_key_here"
echo "3. Run a test command:"
echo "   source clearcouncil_env/bin/activate"
echo "   python clearcouncil.py explain-terms motion"
echo ""
echo "📊 To run voting analysis:"
echo "   python clearcouncil.py analyze-voting york_county_sc \"District 2\" \"last 6 months\" --create-charts"
