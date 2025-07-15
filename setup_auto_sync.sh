#!/bin/bash

# ClearCouncil Auto-Sync Setup Script
# This script sets up automatic synchronization for the ClearCouncil system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 Setting up ClearCouncil Auto-Sync..."

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/{PDFs,transcripts,faiss_indexes,results,logs}

# Make scripts executable
echo "🔐 Setting script permissions..."
chmod +x auto_sync.sh
chmod +x setup_complete.sh

# Test the environment
echo "🧪 Testing environment..."
if [[ ! -f "clearcouncil_env/bin/activate" ]]; then
    echo "❌ Virtual environment not found. Running setup first..."
    ./setup_complete.sh
fi

# Activate virtual environment and test basic commands
source clearcouncil_env/bin/activate

if python clearcouncil.py list-councils >/dev/null 2>&1; then
    echo "✅ Basic commands working"
else
    echo "❌ Basic commands failed"
    exit 1
fi

# Check .env file
if [[ -f ".env" ]] && grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "✅ OpenAI API key configured"
else
    echo "⚠️  OpenAI API key not configured. Please edit .env file"
fi

# Test a single document download
echo "📥 Testing document download..."
if python clearcouncil.py download-pdfs york_county_sc --document-id 2100 >/dev/null 2>&1; then
    echo "✅ Document download working"
else
    echo "❌ Document download failed"
    exit 1
fi

echo ""
echo "🎯 Auto-Sync Setup Options:"
echo ""
echo "1. Manual Run:"
echo "   ./auto_sync.sh"
echo ""
echo "2. Cron Job (runs daily at 6 AM):"
echo "   Add to crontab: 0 6 * * * /home/john/projects/clearcouncil/auto_sync.sh"
echo ""
echo "3. Systemd Service (recommended for servers):"
echo "   sudo cp clearcouncil-sync.service /etc/systemd/system/"
echo "   sudo cp clearcouncil-sync.timer /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable clearcouncil-sync.timer"
echo "   sudo systemctl start clearcouncil-sync.timer"
echo ""
echo "4. Quick Test Run (processes last 7 days):"

# Create a quick test version
cat > quick_test.sh << 'EOF'
#!/bin/bash
source clearcouncil_env/bin/activate
echo "🔍 Testing with last 7 days of data..."
python clearcouncil.py update-documents york_county_sc "last 7 days"
python clearcouncil.py analyze-voting york_county_sc "District 2" "last 7 days" --create-charts
echo "✅ Test completed! Check data/results/ for output"
EOF

chmod +x quick_test.sh
echo "   ./quick_test.sh"
echo ""

# Create a status script
cat > sync_status.sh << 'EOF'
#!/bin/bash
echo "📊 ClearCouncil Sync Status"
echo "=========================="
echo ""

if [[ -f "data/sync.log" ]]; then
    echo "📋 Last Sync:"
    tail -5 data/sync.log
    echo ""
fi

echo "📁 Data Directory Status:"
echo "  PDFs: $(find data/PDFs -name "*.pdf" 2>/dev/null | wc -l) files"
echo "  Results: $(find data/results -name "*.csv" 2>/dev/null | wc -l) CSV files"
echo "  Charts: $(find data/results -name "*.png" -o -name "*.html" 2>/dev/null | wc -l) charts"
echo ""

if [[ -f "data/results/sync_summary.txt" ]]; then
    echo "📈 Last Summary:"
    cat data/results/sync_summary.txt
fi
EOF

chmod +x sync_status.sh

echo "5. Check Status:"
echo "   ./sync_status.sh"
echo ""
echo "✅ Setup complete! Choose an option above to start syncing."
