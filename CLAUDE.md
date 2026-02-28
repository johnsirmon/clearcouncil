# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Self-Improvement Workflow

This project uses the [self-improving-agent](https://clawhub.ai/pskoett/self-improving-agent) pattern to capture learnings and continuously improve agent behavior.

### When to Log

| Situation | File |
|-----------|------|
| Command or operation fails unexpectedly | `.learnings/ERRORS.md` |
| User corrects the agent ("No, that's wrong…", "Actually…") | `.learnings/LEARNINGS.md` (category: `correction`) |
| User requests a capability that doesn't exist | `.learnings/FEATURE_REQUESTS.md` |
| External API or tool fails | `.learnings/ERRORS.md` |
| Knowledge is outdated or incorrect | `.learnings/LEARNINGS.md` (category: `knowledge_gap`) |
| A better approach is found for a recurring task | `.learnings/LEARNINGS.md` (category: `best_practice`) |

### ID Format

`TYPE-YYYYMMDD-XXX` — e.g. `LRN-20260223-001`, `ERR-20260223-A3F`, `FEAT-20260223-002`

### Promotion

When a learning is broadly applicable, promote it to permanent project memory:

| Learning Type | Promote To |
|---------------|------------|
| Project facts, conventions, gotchas | `CLAUDE.md` (this file) |
| Agent workflows, automation rules | `.github/copilot-instructions.md` |
| User-facing feature patterns | `README.md` |

After promoting, update the original entry's `**Status**` to `promoted` and add `**Promoted**: CLAUDE.md` (or relevant target).

## Project Overview

ClearCouncil is a modular local government transparency tool that democratizes access to council information through RAG (Retrieval Augmented Generation). The system processes PDF documents, YouTube transcripts, and extracts structured data to enable natural language querying about local government activities.

## Development Commands

### Setup and Installation
```bash
# Development installation
pip install -e .

# Quick start without installation
pip install -r requirements.txt
python clearcouncil.py --help

# Web interface setup
python setup_web.py

# Chat interface setup
python setup_chat.py

# Alternative setup using platform-specific scripts
./setup.sh      # Linux/Mac
setup.bat       # Windows
```

### Web Interface Commands
```bash
# Start web server
python clearcouncil_web.py serve --host 0.0.0.0 --port 5000

# Process data for web interface
python clearcouncil_web.py process-data york_county_sc

# Check processing status
python clearcouncil_web.py status york_county_sc

# Initialize database
python clearcouncil_web.py init-db

# List available councils
python clearcouncil_web.py list-councils

# Alternative: Simple standalone server with transparency features
python simple_web_server.py
# Runs on port 5001 with data sources transparency dashboard
```

### Chat Interface Commands
```bash
# Start AI chat interface
python clearcouncil_chat.py
# Runs on port 5002 with GitHub AI models

# Enhanced chat with integrated features
python clearcouncil_chat_enhanced.py

# Integrated server with chat and web features
python clearcouncil_enhanced_server.py

# Test chat functionality
python test_chat_basic.py
```

### Running Tests
```bash
# Run comprehensive test suite
python run_local_tests.py

# Test web interface integration
python test_web_integration.py

# Quick functionality test
./quick_test.sh

# Test specific components
python tests/test_fuzzy_matching.py
python tests/test_rep_extraction.py
python tests/test_voting_parser.py
python test_deduplication.py

# Test basic functionality only
python clearcouncil_simple.py --help
python clearcouncil_simple.py list-councils

# Run specific CLI tests
python clearcouncil.py list-councils
python clearcouncil.py explain-terms "movant" "second"

# Test chat functionality
python test_chat_basic.py
python test_enhanced_chat.py

# Test web server
python test_web_server.py

# Test GitHub API integration
python test_github_api.py
```

**Important**: There are no formal unit tests or linting configured. The project uses integration testing via various test scripts and `quick_test.sh` for quick functionality checks. Test files include:
- `test_fuzzy_matching.py` - Tests intelligent name matching
- `test_rep_extraction.py` - Tests representative extraction
- `test_voting_parser.py` - Tests voting record parsing
- `test_deduplication.py` - Tests deduplication functionality
- `test_chat_basic.py` - Tests basic chat functionality
- `test_enhanced_chat.py` - Tests enhanced chat features
- `test_web_server.py` - Tests web server functionality
- `test_github_api.py` - Tests GitHub API integration

## Architecture

### Modular Structure
```
src/clearcouncil/
├── config/          # YAML-based council configurations
├── core/            # Data models, database interface, exceptions
├── processors/      # Document processors (PDF, transcripts)
├── downloaders/     # Document downloaders with connection testing
├── parsers/         # Structured data parsers (voting records)
├── analysis/        # Voting analysis and time range parsing
├── visualization/   # Chart generation with matplotlib/seaborn
├── glossary/        # Municipal terminology system
├── cli/             # Command-line interface with async support
└── web/             # Web interface with Flask app, database, and charts
```

### Key Components

1. **Configuration System**: Council-specific YAML configs in `config/councils/` with template-based setup
2. **Data Models**: Dataclasses for `Document`, `DocumentMetadata`, `VotingRecord`, and `ProcessingResult`
3. **Vector Database**: FAISS integration with automatic index management and embedding support
4. **Processing Pipeline**: Multi-threaded document processing with proper error handling
5. **CLI Interface**: Comprehensive command-line tool with subcommands and async operations
6. **Web Interface**: Modern Flask application with interactive dashboards and API endpoints
7. **Database Layer**: Optimized SQLite database with proper indexing for fast queries

### Core Data Flow

1. **Document Processing**: PDF/transcript → chunks → vector embeddings → FAISS index
2. **Analysis Pipeline**: Time range parsing → document discovery → voting extraction → visualization
3. **Configuration**: YAML configs → dataclasses → runtime settings
4. **Web Processing**: PDF → SQLite database → interactive charts → web dashboard

### Web Interface Architecture

The web interface (`src/clearcouncil/web/`) provides a modern, interactive frontend:

- **Flask Application** (`app.py`): Main web server with blueprints for routes and API
- **Database Layer** (`database.py`): Optimized SQLite schema with proper indexing
- **Interactive Charts** (`charts.py`): Plotly-based charts replacing static matplotlib
- **Data Processor** (`data_processor.py`): Enhanced pipeline for parallel PDF processing
- **CLI Integration** (`cli_integration.py`): Web commands integrated with existing CLI

**Key Features**:
- **Interactive Dashboards**: Real-time filtering with dropdowns for representatives and time periods
- **Data Sources Transparency**: Complete visibility into data origins and processing methods
- **Comparison Tools**: Side-by-side analysis of multiple representatives
- **Export Capabilities**: CSV, PDF, and HTML exports with shareable links
- **Mobile Responsive**: Bootstrap 5 design optimized for all devices
- **API Endpoints**: RESTful API for programmatic access to data
- **Quality Metrics**: Real-time statistics on processing success rates and data coverage

## Environment Setup

### Required Environment Variables
- `OPENAI_API_KEY` - Required for OpenAI embeddings (not needed for basic commands)
- `GITHUB_TOKEN` - Required for GitHub AI models in chat interface (free alternative)
- Create `.env` file in project root

### Environment File Template
```bash
# For OpenAI-based features (legacy)
OPENAI_API_KEY=your_openai_key_here

# For GitHub AI models (free alternative)
GITHUB_TOKEN=your_github_token_here

# Optional: Custom model endpoints
GITHUB_API_BASE_URL=https://models.inference.ai.azure.com
```

### Directory Structure
The system auto-creates these directories:
- `data/PDFs/` - Downloaded council documents
- `data/transcripts/` - YouTube transcripts
- `data/faiss_indexes/` - Vector database indexes
- `data/results/` - Analysis results and exports
- `data/results/charts/` - Generated visualizations

## CLI Usage

### Entry Points
- `clearcouncil.py` - Main CLI (requires full dependencies)
- `clearcouncil_simple.py` - Simplified CLI with graceful dependency handling
- `clearcouncil_web.py` - Web interface launcher
- `simple_web_server.py` - Standalone transparency dashboard server
- `clearcouncil_chat.py` - AI chat interface with GitHub models
- `clearcouncil_chat_enhanced.py` - Enhanced chat with additional features
- `clearcouncil_enhanced_server.py` - Enhanced server with integrated chat

### Core Commands
```bash
# Council management
clearcouncil list-councils
clearcouncil download-pdfs york_county_sc --document-id 2280

# Document processing
clearcouncil process-pdfs york_county_sc
clearcouncil process-transcripts york_county_sc --video-id y7wMTwJN7rA

# Analysis and search
clearcouncil search york_county_sc "rezoning ordinance" --limit 10
clearcouncil analyze-voting york_county_sc "District 2" "last year" --create-charts
clearcouncil analyze-district york_county_sc "District 2" "last year"

# Utilities
clearcouncil explain-terms "movant" "rezoning" "ordinance"
clearcouncil update-documents york_county_sc "last 5 months"
```

### Advanced Features
- **Time Range Parsing**: Natural language like "last year", "last 6 months", "2023-01-01 to 2024-01-01"
- **Fuzzy Name Matching**: Intelligent name matching with `fuzzywuzzy` and Levenshtein distance
- **Parallel Processing**: Multi-threaded document processing and downloads
- **Multiple Output Formats**: Plain text, JSON, CSV, HTML with tooltips
- **Chart Generation**: Matplotlib/seaborn visualizations saved to `data/results/charts/`
- **Municipal Glossary**: Built-in explanations for government terms
- **Data Deduplication**: Advanced representative deduplication and canonical name mapping
- **Automated Sync**: Systemd integration for scheduled updates

## Development Guidelines

### Adding New Councils
1. Copy `config/councils/template.yaml`
2. Rename to `your_council_id.yaml`
3. Configure website URLs, file patterns, and parsing rules
4. Test with `clearcouncil list-councils`

### Adding New Components

**Processors**: Inherit from `BaseProcessor` in `src/clearcouncil/processors/base_processor.py`
- Implement `process_file()` method
- Return `ProcessingResult` objects
- Use proper logging and error handling

**Parsers**: Inherit from `BaseParser` in `src/clearcouncil/parsers/base_parser.py`
- Implement `parse_text()` method
- Return structured data objects
- Handle malformed input gracefully

**Analysis**: Add to `src/clearcouncil/analysis/` with async support
- Use time range parsing from `time_range.py`
- Integrate with visualization system
- Support multiple output formats

### Error Handling
- All components use `ClearCouncilError` exception hierarchy
- Processing results include success/error status with timing
- Comprehensive logging to `clearcouncil.log`
- Graceful degradation for missing dependencies

### Code Conventions
- Use dataclasses for structured data
- Async/await for I/O operations
- Type hints throughout
- Configuration-driven rather than hardcoded values

## Architecture Notes

### Vector Database Integration
The system uses FAISS for document embeddings with automatic index management. Vector stores are saved with date-based filenames and loaded automatically on startup.

### Async Processing
The CLI supports both sync and async commands. Voting analysis commands use async for parallel document processing and downloads.

### Configuration Management
Council configurations are YAML-based with validation through dataclasses. The system supports multiple councils with different document patterns and parsing rules.

### Testing Strategy
- Integration tests via various test scripts in root directory
- Component-specific tests in `tests/` directory
- Quick functionality checks with `quick_test.sh`
- Web interface integration tests in `tests/test_web_integration.py`
- Chat functionality tests with `test_chat_basic.py` and `test_enhanced_chat.py`
- GitHub API integration tests with `test_github_api.py`
- Deduplication testing with `test_deduplication.py`
- No formal unit tests or CI/CD pipeline
- Testing focuses on end-to-end functionality

## Automation and Maintenance

### Automated Sync Setup
```bash
# Set up automated document processing
chmod +x auto_sync.sh
./auto_sync.sh  # Run manual sync

# For automated scheduling using systemd
sudo cp clearcouncil-sync.service /etc/systemd/system/
sudo cp clearcouncil-sync.timer /etc/systemd/system/
sudo systemctl enable clearcouncil-sync.timer
sudo systemctl start clearcouncil-sync.timer

# Check sync status
./sync_status.sh
```

### Utility Scripts
- `auto_sync.sh` - Automated document sync
- `setup_auto_sync.sh` - Setup automated scheduling
- `sync_status.sh` - Check sync status
- `quick_test.sh` - Quick functionality test
- `update_web_database.py` - Database deduplication
- `extract_representatives.py` - Representative extraction utility
- `check_representatives.py` - Representative validation
- `debug_pdf_content.py` - PDF content debugging
- `setup_chat.py` - Chat application setup
- `install_chat_deps.py` - Chat dependency installation
- `start_chat_server.py` - Chat server startup
- `data_preloader.py` - Data preloading utility

## Migration Notes

Legacy scripts have been replaced:
- `encod_langchain.py` → `clearcouncil process-pdfs`
- `get_youtube_transcripts.py` → `clearcouncil process-transcripts`
- `get_council_votes.py` → `clearcouncil parse-voting`
- `scripts/getminuteswithfilename.sh` → `clearcouncil download-pdfs`