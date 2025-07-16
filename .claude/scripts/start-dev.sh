#!/bin/bash
# Quick development environment setup

echo "🚀 Starting ClearCouncil development environment..."

# Activate virtual environment
source .venv/bin/activate

# Run environment safety check
./check_env.sh

# Show current status
echo ""
echo "📊 Development Status:"
echo "Project: $(pwd)"
echo "Python: $(which python)"
echo "Virtual Env: $VIRTUAL_ENV"
echo ""
echo "🎯 Ready for development!"
echo "Use: claude (to start Claude Code)"
echo "Template: .claude/templates/development-prompt.md"
