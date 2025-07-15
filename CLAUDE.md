# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
```

### Running Tests
```bash
# Run comprehensive test suite
python run_local_tests.py

# Test web interface integration
python test_web_integration.py

# Test basic functionality only
python clearcouncil_simple.py --help
python clearcouncil_simple.py list-councils

# Run specific CLI tests
python clearcouncil.py list-councils
python clearcouncil.py explain-terms "movant" "second"
```

**Important**: There are no formal unit tests or linting configured. The project uses `run_local_tests.py` for integration testing, `test_web_integration.py` for web interface testing, and `TEST_WORKFLOW.md` for manual testing procedures.

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
- **Comparison Tools**: Side-by-side analysis of multiple representatives
- **Export Capabilities**: CSV, PDF, and HTML exports with shareable links
- **Mobile Responsive**: Bootstrap 5 design optimized for all devices
- **API Endpoints**: RESTful API for programmatic access to data

## Environment Setup

### Required Environment Variables
- `OPENAI_API_KEY` - Required for OpenAI embeddings (not needed for basic commands)
- Create `.env` file in project root

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
- **Parallel Processing**: Multi-threaded document processing and downloads
- **Multiple Output Formats**: Plain text, JSON, CSV, HTML with tooltips
- **Chart Generation**: Matplotlib/seaborn visualizations saved to `data/results/charts/`
- **Municipal Glossary**: Built-in explanations for government terms

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
- Integration tests via `run_local_tests.py`
- Manual testing procedures in `TEST_WORKFLOW.md`
- No formal unit tests or CI/CD pipeline
- Testing focuses on end-to-end functionality

## Migration Notes

Legacy scripts have been replaced:
- `encod_langchain.py` → `clearcouncil process-pdfs`
- `get_youtube_transcripts.py` → `clearcouncil process-transcripts`
- `get_council_votes.py` → `clearcouncil parse-voting`
- `scripts/getminuteswithfilename.sh` → `clearcouncil download-pdfs`