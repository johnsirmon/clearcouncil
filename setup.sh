#!/bin/bash

# ClearCouncil Setup Script
# This script helps set up ClearCouncil for non-technical users

echo "🏛️  ClearCouncil Setup Script"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "clearcouncil.py" ]; then
    echo "❌ Error: Please run this script from the clearcouncil directory"
    echo "   Make sure you can see the clearcouncil.py file in the current folder"
    exit 1
fi

# Check Python installation
echo "🔍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Found Python 3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Found Python"
else
    echo "❌ Python is not installed or not in PATH"
    echo "   Please install Python 3.8 or higher from https://python.org"
    exit 1
fi

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo "✅ Python version $PYTHON_VERSION is compatible"
else
    echo "❌ Python version $PYTHON_VERSION is too old. Please install Python 3.8 or higher"
    exit 1
fi

# Check pip installation
echo "🔍 Checking pip installation..."
if $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "✅ pip is available"
else
    echo "❌ pip is not available"
    echo "   Please install pip or use a Python distribution that includes it"
    exit 1
fi

# Install dependencies
echo "📦 Installing required packages..."
echo "   This may take a few minutes..."

# Create a simple requirements file with essential packages only
cat > requirements_basic.txt << EOF
python-dotenv>=1.0.0
PyYAML>=6.0.1
requests>=2.31.0
pandas>=1.5.0
PyPDF2>=3.0.1
youtube-transcript-api>=0.6.0
python-dateutil>=2.8.0
tqdm>=4.65.0
EOF

# Try to install basic requirements
if $PYTHON_CMD -m pip install -r requirements_basic.txt --user; then
    echo "✅ Basic packages installed successfully"
else
    echo "⚠️  Some packages failed to install. ClearCouncil may have limited functionality."
    echo "    You can still try to run basic commands."
fi

# Try to install optional visualization packages
echo "📊 Installing visualization packages (optional)..."
cat > requirements_viz.txt << EOF
matplotlib>=3.5.0
seaborn>=0.11.0
EOF

if $PYTHON_CMD -m pip install -r requirements_viz.txt --user; then
    echo "✅ Visualization packages installed"
else
    echo "⚠️  Visualization packages failed to install. Charts will not be available."
    echo "    Basic analysis will still work."
fi

# Try to install AI/ML packages
echo "🤖 Installing AI/ML packages (optional)..."
cat > requirements_ai.txt << EOF
langchain>=0.0.340
openai>=1.0.0
faiss-cpu>=1.7.4
tiktoken>=0.5.0
EOF

if $PYTHON_CMD -m pip install -r requirements_ai.txt --user; then
    echo "✅ AI/ML packages installed"
else
    echo "⚠️  AI/ML packages failed to install. Vector search will not be available."
    echo "    Document analysis will still work."
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file for API keys..."
    cat > .env << EOF
# OpenAI API Key (required for AI features)
# Get your key from: https://platform.openai.com/api-keys
# OPENAI_API_KEY=your_api_key_here

# Add other API keys here as needed
EOF
    echo "✅ Created .env file"
    echo "   📝 Note: You'll need to add your OpenAI API key to use AI features"
else
    echo "✅ .env file already exists"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/{PDFs,transcripts,faiss_indexes,results,results/charts}
echo "✅ Data directories created"

# Test basic functionality
echo "🧪 Testing basic functionality..."
if $PYTHON_CMD clearcouncil.py list-councils &> /dev/null; then
    echo "✅ ClearCouncil is working!"
else
    echo "⚠️  Basic test failed. Some features may not work."
fi

# Cleanup temporary files
rm -f requirements_basic.txt requirements_viz.txt requirements_ai.txt

echo ""
echo "🎉 Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. If you want AI features, add your OpenAI API key to the .env file"
echo "2. Try running: $PYTHON_CMD clearcouncil.py list-councils"
echo "3. See README.md for usage examples"
echo ""
echo "For help: $PYTHON_CMD clearcouncil.py --help"
echo ""