#!/bin/bash

# Environment Safety Check Script for ClearCouncil
# This script ensures we're using the project's virtual environment

echo "🔍 Environment Safety Check..."

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ No virtual environment active!"
    echo "🔧 Attempting to activate .venv..."
    
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        if [[ "$VIRTUAL_ENV" != "" ]]; then
            echo "✅ Virtual environment activated: $VIRTUAL_ENV"
        else
            echo "❌ Failed to activate virtual environment"
            echo "Please run: source .venv/bin/activate"
            exit 1
        fi
    else
        echo "❌ No .venv directory found"
        echo "Please create virtual environment: python -m venv .venv"
        exit 1
    fi
else
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
fi

# Verify pip will install to virtual environment
pip_location=$(pip show pip 2>/dev/null | grep Location | cut -d' ' -f2)
if [[ "$pip_location" == *"$VIRTUAL_ENV"* ]]; then
    echo "✅ Pip will install to virtual environment"
else
    echo "❌ ERROR: Pip will install to system Python!"
    echo "Pip location: $pip_location"
    echo "Virtual env: $VIRTUAL_ENV"
    exit 1
fi

# Display current environment info
echo ""
echo "📊 Current Environment Info:"
echo "   Python: $(which python)"
echo "   Pip: $(which pip)"
echo "   Virtual Env: $VIRTUAL_ENV"
echo "   Python Version: $(python --version 2>/dev/null || echo 'Not available')"

echo ""
echo "✅ Environment safety check passed!"