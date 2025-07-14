# Migration Guide

This guide helps you migrate from the old ClearCouncil scripts to the new modular architecture.

## What Changed

The codebase has been completely restructured for better maintainability, extensibility, and ease of use:

### Old Structure → New Structure

```
OLD:                           NEW:
├── main.py                   ├── src/clearcouncil/
├── encod_langchain.py        │   ├── config/
├── get_youtube_transcripts.py│   ├── core/
├── get_council_votes.py      │   ├── processors/
├── scripts/                  │   ├── downloaders/
│   └── getminuteswithfilename.sh│   ├── parsers/
├── requirements.txt          │   └── cli/
└── data/                     ├── config/councils/
                              ├── clearcouncil.py
                              ├── setup.py
                              └── data/
```

## Script Migration

### 1. PDF Processing (`encod_langchain.py`)

**Old Way:**
```bash
python encod_langchain.py
```

**New Way:**
```bash
clearcouncil process-pdfs york_county_sc
```

**What's Better:**
- Configurable for any council
- Better error handling and logging
- Progress tracking with tqdm
- Automatic directory creation

### 2. YouTube Transcripts (`get_youtube_transcripts.py`)

**Old Way:**
```python
# Edit video_id in file
video_id = "y7wMTwJN7rA"
python get_youtube_transcripts.py
```

**New Way:**
```bash
clearcouncil process-transcripts york_county_sc --video-id y7wMTwJN7rA
```

**What's Better:**
- No need to edit files
- Command-line arguments
- Integrated with vector database
- Better error handling

### 3. Council Votes (`get_council_votes.py`)

**Old Way:**
```python
# Edit file path in script
pdf_text = extract_information_from_pdf(r'C:\Users\...\document.pdf')
python get_council_votes.py
```

**New Way:**
```bash
clearcouncil parse-voting york_county_sc --file-path data/PDFs/document.pdf
```

**What's Better:**
- Command-line arguments (no editing files)
- Cross-platform paths
- Configurable parsing rules
- Better data models

### 4. Document Download (`scripts/getminuteswithfilename.sh`)

**Old Way:**
```bash
cd scripts
./getminuteswithfilename.sh
```

**New Way:**
```bash
# Download all documents in configured range
clearcouncil download-pdfs york_county_sc

# Download specific document
clearcouncil download-pdfs york_county_sc --document-id 2280
```

**What's Better:**
- Cross-platform (no shell scripts)
- Configurable URL patterns
- Better error handling
- Progress tracking

## Configuration Migration

### Old Hardcoded Values

The old scripts had hardcoded values scattered throughout:

```python
# In encod_langchain.py
pdf_dir = 'data/PDFs'
chunk_size=10000

# In getminuteswithfilename.sh
baseUrl="https://yorkcountysc.iqm2.com/Citizens/FileOpen.aspx?Type=12&ID="
savePath="/c/Source/clearcouncil/data/PDFs2"
```

### New Configuration System

All settings are now in `config/councils/york_county_sc.yaml`:

```yaml
name: "York County South Carolina"
website:
  base_url: "https://yorkcountysc.iqm2.com/Citizens/FileOpen.aspx"
  document_url_template: "{base_url}?Type=12&ID={id}&Inline=True"
storage:
  pdf_directory: "data/PDFs"
processing:
  chunk_size: 10000
  max_workers: 10
```

## Environment Setup Migration

### Old Setup
```bash
# Manual dependency installation
pip install requests langchain openai PyPDF2 faiss-cpu tiktoken PyYAML SQLAlchemy aiohttp dataclasses-json jsonpatch numpy pydantic tenacity
```

### New Setup
```bash
# Clean requirements
pip install -r requirements.txt

# Or install as package
pip install -e .
```

## Data Structure Migration

Your existing data files are compatible, but the new structure is more organized:

```
data/
├── PDFs/              # Same as before
├── transcripts/       # Same as before  
├── faiss_indexes/     # Same as before
└── results/           # New: CSV outputs go here
```

## Usage Examples

### Complete Workflow - Old Way
```bash
# Download documents
cd scripts && ./getminuteswithfilename.sh

# Process PDFs
cd .. && python encod_langchain.py

# Process transcript (edit file first)
python get_youtube_transcripts.py

# Parse voting (edit file first)  
python get_council_votes.py
```

### Complete Workflow - New Way
```bash
# Download documents
clearcouncil download-pdfs york_county_sc

# Process PDFs
clearcouncil process-pdfs york_county_sc

# Process transcript
clearcouncil process-transcripts york_county_sc --video-id y7wMTwJN7rA

# Parse voting records
clearcouncil parse-voting york_county_sc --file-path data/PDFs/2024-04-01*.pdf

# Search documents
clearcouncil search york_county_sc "rezoning ordinance"
```

## Adding New Councils

### Old Way
- Copy and modify each script
- Update hardcoded URLs and paths
- Create new shell scripts

### New Way
1. Copy `config/councils/template.yaml`
2. Rename to `your_council.yaml`
3. Update configuration
4. Use immediately: `clearcouncil download-pdfs your_council`

## Benefits of Migration

1. **Extensibility**: Easy to add new councils
2. **Maintainability**: Modular code with proper separation of concerns  
3. **Error Handling**: Comprehensive error reporting and logging
4. **Cross-Platform**: No shell scripts, works on Windows/Mac/Linux
5. **User-Friendly**: CLI interface with help and validation
6. **Testing**: Easier to test individual components
7. **Documentation**: Better documentation and type hints

## Troubleshooting

### Import Errors
Make sure you're in the project root and have installed dependencies:
```bash
pip install -r requirements.txt
python clearcouncil.py --help
```

### Old Files
The old Python files are still in the repository but are no longer used. You can safely remove them after confirming the new system works for your use case.

### Configuration Issues
Use the template as a starting point:
```bash
cp config/councils/template.yaml config/councils/my_council.yaml
# Edit my_council.yaml
clearcouncil list-councils  # Should show your new council
```