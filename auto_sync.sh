#!/bin/bash

# ClearCouncil Auto-Sync Script
# This script automatically downloads new documents, processes them, and updates the database

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
COUNCIL_ID="york_county_sc"
VENV_PATH="./clearcouncil_env"
LOG_FILE="./data/sync.log"
LOCK_FILE="./data/sync.lock"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to cleanup on exit
cleanup() {
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
    fi
}

# Set up cleanup trap
trap cleanup EXIT

# Check if another sync is running
if [[ -f "$LOCK_FILE" ]]; then
    log "ERROR: Another sync process is already running (lock file exists)"
    exit 1
fi

# Create lock file
echo $$ > "$LOCK_FILE"

log "Starting ClearCouncil auto-sync for $COUNCIL_ID"

# Activate virtual environment
if [[ -f "$VENV_PATH/bin/activate" ]]; then
    source "$VENV_PATH/bin/activate"
    log "Activated virtual environment"
else
    log "ERROR: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    log "ERROR: .env file not found. Please create it with your OPENAI_API_KEY"
    exit 1
fi

# Create necessary directories
mkdir -p data/{PDFs,transcripts,faiss_indexes,results}

# Step 1: Update documents for the last 6 months
log "Step 1: Downloading missing documents for the last 6 months..."
if python clearcouncil.py update-documents "$COUNCIL_ID" "last 6 months" 2>> "$LOG_FILE"; then
    log "Document update completed successfully"
else
    log "WARNING: Document update had some issues, but continuing..."
fi

# Step 2: Process new PDFs
log "Step 2: Processing PDFs and creating embeddings..."
if python clearcouncil.py process-pdfs "$COUNCIL_ID" 2>> "$LOG_FILE"; then
    log "PDF processing completed successfully"
else
    log "ERROR: PDF processing failed"
    exit 1
fi

# Step 3: Generate analysis for key districts
log "Step 3: Generating voting analysis for key districts..."

# Array of districts to analyze
DISTRICTS=("District 1" "District 2" "District 3" "District 4" "District 5" "District 6" "District 7")

for district in "${DISTRICTS[@]}"; do
    log "Analyzing $district for last 6 months..."
    if python clearcouncil.py analyze-voting "$COUNCIL_ID" "$district" "last 6 months" --create-charts --output-format csv 2>> "$LOG_FILE"; then
        log "Analysis completed for $district"
    else
        log "WARNING: Analysis failed for $district, continuing with others..."
    fi
done

# Step 4: Generate district overview
log "Step 4: Generating district overviews..."
for district in "${DISTRICTS[@]}"; do
    log "Generating district overview for $district..."
    if python clearcouncil.py analyze-district "$COUNCIL_ID" "$district" "last year" --create-charts 2>> "$LOG_FILE"; then
        log "District overview completed for $district"
    else
        log "WARNING: District overview failed for $district"
    fi
done

# Step 5: Generate summary report
log "Step 5: Creating summary statistics..."
RESULTS_DIR="./data/results"
if [[ -d "$RESULTS_DIR" ]]; then
    TOTAL_CSVS=$(find "$RESULTS_DIR" -name "*.csv" | wc -l)
    TOTAL_CHARTS=$(find "$RESULTS_DIR" -name "*.png" -o -name "*.html" | wc -l)
    log "Summary: Generated $TOTAL_CSVS CSV files and $TOTAL_CHARTS charts"
    
    # Create a simple index file
    cat > "$RESULTS_DIR/sync_summary.txt" << EOF
ClearCouncil Sync Summary
Generated: $(date)
Council: $COUNCIL_ID
CSV Files: $TOTAL_CSVS
Charts: $TOTAL_CHARTS

Recent files:
$(find "$RESULTS_DIR" -type f -mmin -60 | head -10)
EOF
    
    log "Created sync summary at $RESULTS_DIR/sync_summary.txt"
fi

log "Auto-sync completed successfully!"

# Optional: Clean up old log files (keep last 30 days)
find ./data -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true

log "Cleanup completed"
