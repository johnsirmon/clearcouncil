#!/bin/bash
# ClearCouncil Project Cleanup & Organization Script

echo "🧹 ClearCouncil Project Cleanup Starting..."

# Create .claude directory structure
echo "📁 Creating Claude development structure..."
mkdir -p .claude/templates
mkdir -p .claude/scripts

# Create the prompt template
cat << 'EOF' > .claude/templates/development-prompt.md
# ClearCouncil Development Prompt Template

## Context
**Project:** ClearCouncil - Local government transparency tool
**Current State:** Production system with PDF processing, web interface, voting analysis
**Environment:** VS Code Insiders + Claude Code, Python 3.12, .venv active

## Objective
**Primary Goal:** [Describe specific goal here]
**Why:** [Brief explanation of motivation]

## Constraints & Requirements
**Must Have:**
- [ ] Maintain 100% backward compatibility
- [ ] Use existing virtual environment (.venv)
- [ ] Follow existing code patterns
- [ ] Pass existing integration tests

**Nice to Have:**
- [ ] [Optional features]

**Must NOT:**
- [ ] Break existing CLI commands
- [ ] Install packages globally
- [ ] Modify existing database schema without migration
- [ ] Change existing API contracts

## Environment Safety
**Virtual Environment:** /home/johnsirmon/projects/clearcouncil/.venv
**Current Status:** [Run ./check_env.sh to verify]
**Package Manager:** pip with requirements.txt

## Success Criteria
I'll know this worked when:
- ✅ All existing tests pass: `python quick_test.sh`
- ✅ CLI help works: `python clearcouncil.py --help`
- ✅ Web interface loads: `python clearcouncil_web.py serve`
- ✅ [Specific new functionality works]

## Questions for Learning
- What patterns should I follow from existing codebase?
- Are there better practices I should adopt?
- How does this integrate with existing architecture?

---
**Ready to proceed with the above context and constraints.**
EOF

echo "✅ Created .claude/templates/development-prompt.md"

# Create quick development scripts
cat << 'EOF' > .claude/scripts/start-dev.sh
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
EOF

chmod +x .claude/scripts/start-dev.sh
echo "✅ Created .claude/scripts/start-dev.sh"

# Identify cleanup targets
echo ""
echo "🔍 Analyzing project for cleanup opportunities..."

# Find potential unused files
echo "📄 Files that might be unused or temporary:"

# Look for common temporary/unused patterns
find . -maxdepth 2 -name "*.tmp" -o -name "*.bak" -o -name "*.old" -o -name "*~" 2>/dev/null | head -10

# Look for duplicate or test files that might be outdated
echo ""
echo "🔄 Potential duplicate or old test files:"
find . -maxdepth 2 -name "*test*" -type f | grep -v ".py$" | head -5
find . -maxdepth 2 -name "*backup*" -o -name "*copy*" -o -name "*orig*" 2>/dev/null | head -5

# Look for large files that might be unnecessary
echo ""
echo "📦 Large files (>1MB) that might need review:"
find . -type f -size +1M -not -path "./.git/*" -not -path "./.venv/*" 2>/dev/null | head -10

# Look for empty directories
echo ""
echo "📁 Empty directories:"
find . -type d -empty -not -path "./.git/*" 2>/dev/null | head -5

# Check for Python cache files
echo ""
echo "🗑️  Python cache files to clean:"
find . -name "__pycache__" -type d | wc -l | xargs echo "  __pycache__ directories:"
find . -name "*.pyc" | wc -l | xargs echo "  .pyc files:"

echo ""
echo "🧹 Cleanup Recommendations:"
echo ""
echo "SAFE TO DELETE:"
echo "  1. Python cache: find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null"
echo "  2. Compiled Python: find . -name '*.pyc' -delete"
echo "  3. Temporary files: find . -name '*.tmp' -delete"
echo ""
echo "REVIEW BEFORE DELETING:"
echo "  4. Large files shown above"
echo "  5. Duplicate test files"
echo "  6. Old backup files"
echo ""
echo "Would you like me to:"
echo "  A) Clean Python cache files automatically? [SAFE]"
echo "  B) Show detailed analysis of large files? [REVIEW]"
echo "  C) Create .gitignore improvements? [SAFE]"
echo ""
read -p "Choose option (A/B/C/N for none): " choice

case $choice in
    [Aa]* )
        echo "🧹 Cleaning Python cache files..."
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
        find . -name "*.pyc" -delete 2>/dev/null
        echo "✅ Python cache cleaned"
        ;;
    [Bb]* )
        echo "📊 Detailed large file analysis:"
        find . -type f -size +1M -not -path "./.git/*" -not -path "./.venv/*" -exec ls -lh {} \; | sort -k5 -hr
        ;;
    [Cc]* )
        echo "📝 Creating improved .gitignore..."
        # Backup existing .gitignore if it exists
        if [ -f ".gitignore" ]; then
            cp .gitignore .gitignore.backup
        fi
        
        # Add common ignores if not present
        cat << 'GITIGNORE_EOF' >> .gitignore

# Claude development files
.claude/cache/
*.claude-session

# Python cache and temporary files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.tmp
*.bak
*.swp
*~

# Virtual environments
.venv/
venv/
env/

# IDE files
.vscode/settings.json
.idea/

# OS files
.DS_Store
Thumbs.db

# Large data files (review before adding)
data/large_datasets/
*.sqlite-wal
*.sqlite-shm

GITIGNORE_EOF
        echo "✅ Enhanced .gitignore created (.gitignore.backup saved)"
        ;;
    * )
        echo "No cleanup performed."
        ;;
esac

echo ""
echo "🎯 Organization Complete!"
echo ""
echo "📁 New Structure Created:"
echo "  .claude/templates/development-prompt.md"
echo "  .claude/scripts/start-dev.sh"
echo ""
echo "🚀 Quick Start Commands:"
echo "  ./.claude/scripts/start-dev.sh  # Setup development environment"
echo "  cat .claude/templates/development-prompt.md  # View prompt template"
echo ""
echo "📖 Usage:"
echo "  1. Run ./.claude/scripts/start-dev.sh before development"
echo "  2. Copy template content when starting Claude Code sessions"
echo "  3. Customize template for specific tasks"