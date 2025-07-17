#!/bin/bash
# ClearCouncil Environment Activation Script
# This script activates the virtual environment and provides helpful commands

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏛️  ClearCouncil Environment Activation${NC}"
echo -e "${BLUE}=======================================${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run: python3 -m venv .venv${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}✅ Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if environment variables are set
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Environment file found${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found. Some features may not work.${NC}"
    echo -e "${YELLOW}   Create one with: GITHUB_TOKEN=your_token_here${NC}"
fi

# Display helpful commands
echo -e "\n${BLUE}🚀 Available Commands:${NC}"
echo -e "${GREEN}Web Interface:${NC}"
echo -e "  python clearcouncil_web.py serve --host 0.0.0.0 --port 5000"
echo -e "  python simple_web_server.py"
echo -e "\n${GREEN}Chat Interface:${NC}"
echo -e "  python clearcouncil_chat.py"
echo -e "  python clearcouncil_chat_enhanced.py"
echo -e "\n${GREEN}CLI Commands:${NC}"
echo -e "  python clearcouncil.py list-councils"
echo -e "  python clearcouncil.py download-pdfs york_county_sc --document-id 2280"
echo -e "  python clearcouncil_web.py process-data york_county_sc"
echo -e "  python clearcouncil_web.py status york_county_sc"
echo -e "\n${GREEN}Testing:${NC}"
echo -e "  ./quick_test.sh"
echo -e "  python test_web_server.py"
echo -e "  python test_chat_basic.py"

echo -e "\n${BLUE}📚 Documentation:${NC}"
echo -e "  CLAUDE.md - Full project documentation"
echo -e "  README.md - Getting started guide"

echo -e "\n${GREEN}🎯 Environment activated! Ready to use ClearCouncil.${NC}"

# Start a new shell with the virtual environment activated
exec "$SHELL"