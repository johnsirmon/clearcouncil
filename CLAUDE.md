# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ClearCouncil is a modular local government transparency tool that democratizes access to council information through RAG (Retrieval Augmented Generation). The system processes PDF documents, YouTube transcripts, and extracts structured data to enable natural language querying about local government activities.

## New Modular Architecture

The codebase has been completely restructured with a modular, extensible architecture:

```
src/clearcouncil/
├── config/          # Configuration management for different councils
├── core/            # Core data models, database interface, exceptions
├── processors/      # Document processors (PDF, transcripts)
├── downloaders/     # Document downloaders
├── parsers/         # Structured data parsers (voting records)
└── cli/             # Command-line interface
```

### Key Components

1. **Configuration System**: Council-specific YAML configs in `config/councils/`
2. **Processors**: Modular document processing with proper error handling
3. **Vector Database**: FAISS integration with automatic index management
4. **CLI Interface**: Comprehensive command-line tool for all operations
5. **Data Models**: Proper dataclasses for documents, metadata, and voting records

## Environment Setup

### Installation Options

**Option 1: Development Installation**
```bash
pip install -e .
```

**Option 2: Quick Start (without installation)**
```bash
pip install -r requirements.txt
python clearcouncil.py --help
```

### Required Environment Variables
- `OPENAI_API_KEY` - Required for OpenAI embeddings
- Create `.env` file in project root

## CLI Usage

The new CLI provides a unified interface for all operations:

### List Available Councils
```bash
clearcouncil list-councils
```

### Process PDF Documents
```bash
clearcouncil process-pdfs york_county_sc
```

### Download Documents
```bash
# Download using configured ranges
clearcouncil download-pdfs york_county_sc

# Download specific document
clearcouncil download-pdfs york_county_sc --document-id 2280
```

### Process YouTube Transcripts
```bash
clearcouncil process-transcripts york_county_sc --video-id y7wMTwJN7rA
```

### Parse Voting Records
```bash
clearcouncil parse-voting york_county_sc --file-path data/PDFs/document.pdf
```

### Search Documents
```bash
clearcouncil search york_county_sc "rezoning ordinance" --limit 10
```

## Adding New Councils

1. Copy `config/councils/template.yaml`
2. Rename to `your_council_id.yaml`
3. Customize all configuration sections:
   - Website URLs and download patterns
   - File naming patterns (regex)
   - Storage directories
   - Parsing rules for voting data

Example:
```yaml
name: "Your City Council"
identifier: "your_city"
website:
  base_url: "https://your-city.gov"
  document_url_template: "{base_url}/documents/{id}"
```

## Development Guidelines

### Error Handling
- All components use proper exception hierarchies
- Processing results include success/error status
- Comprehensive logging throughout

### Adding New Processors
1. Inherit from `BaseProcessor`
2. Implement `process_file()` method
3. Return `Document` objects with proper metadata

### Adding New Parsers
1. Inherit from `BaseParser`
2. Implement `parse_text()` method
3. Return structured data objects

## File Structure
- `config/councils/` - Council configurations
- `data/` - All data files (PDFs, transcripts, indexes, results)
- `src/clearcouncil/` - Main package code
- `clearcouncil.py` - Quick start script

## Migration from Old Code

The old scripts have been replaced:
- `encod_langchain.py` → `clearcouncil process-pdfs`
- `get_youtube_transcripts.py` → `clearcouncil process-transcripts`
- `get_council_votes.py` → `clearcouncil parse-voting`
- `scripts/getminuteswithfilename.sh` → `clearcouncil download-pdfs`

## New Voting Analysis Features

### Advanced Voting Analysis Commands

```bash
# Analyze representative voting patterns with time ranges
clearcouncil analyze-voting york_county_sc "District 2" "last year" --create-charts

# Compare representatives
clearcouncil analyze-voting york_county_sc "John Smith" "last 6 months" \
  --compare-with "Jane Doe" "Bob Wilson" --output-format html

# Analyze entire districts
clearcouncil analyze-district york_county_sc "District 2" "last year"

# Batch download missing documents for time periods
clearcouncil update-documents york_county_sc "last 5 months"

# Explain municipal government terms
clearcouncil explain-terms "movant" "rezoning" "ordinance"
```

### Key Features

1. **Smart Time Range Parsing**: "last year", "last 6 months", "2023-01-01 to 2024-01-01"
2. **Automatic Document Discovery**: Finds and downloads missing documents
3. **Parallel Processing**: Efficient batch processing of multiple documents
4. **Interactive Visualizations**: Charts showing voting patterns and comparisons
5. **Municipal Glossary**: Built-in explanations for government terms
6. **Multiple Output Formats**: Plain text, JSON, CSV, HTML with tooltips

### Architecture Updates

- `src/clearcouncil/analysis/` - Voting analysis and time range parsing
- `src/clearcouncil/visualization/` - Chart generation with matplotlib/seaborn
- `src/clearcouncil/glossary/` - Municipal terminology system
- `config/councils/*.yaml` - Enhanced council configurations

## Testing

Run basic functionality tests:
```bash
clearcouncil list-councils
clearcouncil download-pdfs york_county_sc --document-id 2280
clearcouncil process-pdfs york_county_sc

# Test new voting analysis features
clearcouncil explain-terms "movant" "second"
clearcouncil analyze-voting york_county_sc "District 2" "last 3 months" --create-charts
```