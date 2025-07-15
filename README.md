# ClearCouncil 🏛️

**A comprehensive local government transparency tool that makes understanding council decisions simple**

ClearCouncil processes PDF documents, extracts voting records, and creates interactive dashboards to help citizens understand what their representatives are voting on and how they compare to others. Features intelligent name matching, automated document processing, and comprehensive voting analysis.

## 📸 Screenshots

![ClearCouncil Dashboard](images/dashboard-transparency.png)
*Main dashboard showing data sources transparency, quality metrics, and processing information*

The dashboard provides complete transparency about data sources, including:
- **Historical Documents**: Automated collection from IQM2 Legacy System (2018-March 2025)
- **Current Documents**: CivicPlus portal integration with authentication automation (March 2025-Present)
- **Quality Metrics**: Real-time statistics on processing success rates and data coverage
- **Transparency Commitments**: Clear disclosure of limitations and upcoming improvements

## 🚀 Quick Start

### 1. Setup (One Time)
```bash
# Clone or download this repository
git clone [repository-url]
cd clearcouncil

# Install dependencies
pip install -r requirements.txt

# Set up your environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# Initialize the application
python setup_web.py
```

### 2. Using the Application

#### Command Line Interface
```bash
# See available councils
python clearcouncil.py list-councils

# Download and process council documents
python clearcouncil.py update-documents york_county_sc "last 6 months"
python clearcouncil.py process-pdfs york_county_sc

# Search documents with AI-powered search
python clearcouncil.py search york_county_sc "rezoning ordinance"

# Analyze voting patterns with fuzzy name matching
python clearcouncil.py analyze-voting york_county_sc "Love" "last year" --create-charts
python clearcouncil.py analyze-voting york_county_sc "District 2" "since 2020" --compare-with "District 1" "District 3"

# Analyze district performance
python clearcouncil.py analyze-district york_county_sc "District 1" "last 2 years" --create-charts

# Get municipal term explanations
python clearcouncil.py explain-terms

# Get help
python clearcouncil.py --help
```

#### Web Interface
```bash
# Initialize the database
python clearcouncil_web.py init-db

# Process data for web interface
python clearcouncil_web.py process-data york_county_sc

# Start the web server
python clearcouncil_web.py serve

# Open your browser to http://localhost:5000

# Alternative: Simple standalone server with transparency features
python simple_web_server.py
# Open your browser to http://localhost:5001
```

#### Web API Endpoints
```bash
# Data sources transparency information
curl http://localhost:5001/api/data-sources

# Health check and feature status
curl http://localhost:5001/api/health

# Example response includes:
# - Data quality metrics (463 documents, 39 representatives, 3,795 votes)
# - Processing methods disclosure
# - Source attribution and limitations
```

#### Automated Sync
```bash
# Set up automated document processing
chmod +x auto_sync.sh
./auto_sync.sh  # Run manual sync

# For automated scheduling, use the systemd service:
sudo cp clearcouncil-sync.service /etc/systemd/system/
sudo cp clearcouncil-sync.timer /etc/systemd/system/
sudo systemctl enable clearcouncil-sync.timer
sudo systemctl start clearcouncil-sync.timer
```

## 📊 Features

### 🔍 **Data Sources Transparency**
- **Complete Source Attribution**: Clear documentation of where all data originates
- **Historical vs Current Sources**: Dual-source tracking with IQM2 and CivicPlus systems
- **Quality Metrics Dashboard**: Real-time processing success rates and coverage statistics
- **Authentication Status**: Transparent disclosure of manual vs automated collection methods
- **Processing Method Disclosure**: Step-by-step explanation of data collection and AI processing
- **Honest Limitations**: Upfront about current challenges and planned improvements

### 🧠 Intelligent Name Matching
- **Fuzzy String Matching**: Find representatives even with misspellings, nicknames, or partial names
- **Multi-tier Search**: Exact → case-insensitive → partial → fuzzy matching
- **Smart Suggestions**: Get similar name suggestions when exact matches aren't found
- **Examples**: "Love" finds "Allison Love", "Bob" finds "Robert Winkler"

### 📈 Advanced Voting Analysis
- **Individual Representative Tracking**: Detailed voting history and patterns
- **District Comparisons**: Compare performance across different districts
- **Time-based Analysis**: Track changes over specific periods
- **Voting Pattern Insights**: Identify trends, agreements, and disagreements
- **Automated Chart Generation**: Visual representations of voting data

### 🌐 Interactive Web Dashboard
- **Data Sources Transparency Section**: Complete visibility into data origins and processing
- **Representative Analysis**: View detailed voting records and patterns with advanced deduplication
- **Interactive Charts**: Filter by time period and representative
- **Search Functionality**: Find specific topics or cases with AI-powered search
- **Comparison Tools**: Compare representatives side-by-side
- **Mobile Responsive**: Works on phones, tablets, and desktops
- **Real-time Updates**: Stay current with latest council decisions
- **Quality Metrics**: Live statistics showing 39 unique representatives (down from 1,017 duplicates)
- **Processing Transparency**: Clear disclosure of AI extraction methods and success rates

### 🤖 AI-Powered Processing
- **Document Processing**: Intelligent extraction from PDF documents
- **Vector Search**: Find relevant content using AI embeddings
- **Municipal Glossary**: Built-in explanations of government terms
- **Automated Categorization**: Smart classification of voting records

### 🔄 Automated Operations
- **Scheduled Downloads**: Automatic document fetching with systemd integration
- **Batch Processing**: Handle multiple documents efficiently
- **Background Updates**: Keep data current without manual intervention
- **Error Recovery**: Robust handling of failed operations

### 🎯 **Data Quality & Deduplication**
- **Advanced Deduplication**: Reduced representative duplicates from 1,017 to 39 unique entries
- **Fuzzy Name Matching**: Intelligent consolidation of similar names and variations
- **Vote Record Consolidation**: Merged 3,795 voting records under correct representative names
- **Quality Metrics Tracking**: 99.3% processing success rate with transparency reporting
- **Canonical Name Mapping**: Consistent representative identification across all documents
- **Historical Data Preservation**: Original documents maintained for verification and audit trails

### 📊 Data Export & Visualization
- **Multiple Formats**: Export data as CSV, JSON, or interactive charts
- **Custom Time Ranges**: Analyze any period from days to years
- **Comprehensive Reports**: Detailed summaries with statistics
- **Shareable Visualizations**: Generate charts for presentations or reports

## 🏛️ Currently Supported

- **York County, South Carolina** (fully configured with comprehensive data quality)
  - **463 documents processed** from official government sources
  - **39 unique representatives tracked** (after intelligent deduplication from 1,017 entries)
  - **3,795 voting records analyzed** with 99.3% processing success rate
  - **6+ years of historical coverage** (2018-2025) with dual-source tracking
  - **Daily automated updates** from IQM2 Legacy System and CivicPlus Portal

- **Easy Configuration**: Add new councils by copying and editing YAML config files

## 📁 Project Structure

```
clearcouncil/
├── clearcouncil.py              # Main CLI application
├── clearcouncil_web.py          # Web interface launcher
├── simple_web_server.py         # Standalone transparency dashboard server
├── auto_sync.sh                 # Automated sync script
├── setup_web.py                 # Web setup script
├── update_web_database.py       # Database deduplication script
├── requirements.txt             # Python dependencies (with fuzzy matching)
├── images/                      # Screenshots and documentation images
│   ├── README.md               # Image documentation
│   └── dashboard-transparency.png  # Main dashboard screenshot
├── config/                      # Council configurations
│   └── councils/
│       ├── template.yaml        # Template for new councils
│       └── york_county_sc.yaml  # York County configuration
├── src/clearcouncil/            # Main source code
│   ├── web/                     # Web interface components
│   │   ├── app.py              # Flask application
│   │   ├── routes.py           # Web routes
│   │   ├── database.py         # Web database layer
│   │   ├── charts.py           # Chart generation
│   │   ├── data_sources_api.py # Data transparency API
│   │   └── templates/          # HTML templates
│   │       ├── dashboard.html  # Main dashboard with transparency section
│   │       └── data_sources.html  # Data sources transparency template
│   ├── cli/                     # Command line interface
│   │   ├── main.py             # CLI entry point
│   │   └── voting_commands.py  # Voting analysis commands
│   ├── analysis/                # Data analysis modules
│   │   ├── voting_analyzer.py  # Core voting analysis
│   │   ├── batch_processor.py  # Bulk processing
│   │   ├── representative_tracker.py  # Rep tracking with advanced deduplication
│   │   └── time_range.py       # Time period parsing
│   ├── core/                    # Core functionality
│   │   ├── database.py         # Vector database
│   │   ├── models.py           # Data models
│   │   ├── data_sources.py     # Data source management and transparency
│   │   └── exceptions.py       # Custom exceptions
│   ├── visualization/           # Chart and graph generation
│   │   └── voting_charts.py    # Voting visualization tools
│   ├── processors/              # Document processors
│   │   ├── pdf_processor.py    # PDF handling
│   │   └── transcript_processor.py  # YouTube transcript processing
│   ├── parsers/                 # Data parsers
│   │   ├── voting_parser.py    # Extract voting records
│   │   └── base_parser.py      # Base parsing functionality
│   ├── downloaders/             # Document downloaders
│   │   ├── pdf_downloader.py   # Automated PDF fetching
│   │   └── base_downloader.py  # Base download functionality
│   ├── glossary/                # Municipal term explanations
│   │   ├── municipal_glossary.py  # Government term definitions
│   │   └── tooltip_generator.py   # Interactive explanations
│   └── core/                    # Core functionality
│       ├── database.py         # Vector database
│       ├── models.py           # Data models
│       └── exceptions.py       # Custom exceptions
├── data/                        # Data storage
│   ├── PDFs/                    # Downloaded documents
│   ├── results/                 # Analysis results and charts
│   ├── faiss_indexes/           # Vector database indexes
│   └── transcripts/             # YouTube transcripts
├── tests/                       # Test files
│   ├── test_fuzzy_matching.py  # Fuzzy name matching tests
│   ├── test_voting_parser.py   # Parser validation
│   ├── test_web_integration.py # Web interface tests
│   └── test_rep_extraction.py  # Representative extraction tests
└── systemd/                     # System service files
    ├── clearcouncil-sync.service  # Systemd service
    └── clearcouncil-sync.timer    # Automated scheduling
```

## 🔧 Adding Your Council

1. Copy `config/councils/template.yaml`
2. Rename to `your_council_id.yaml`
3. Update the configuration:
   - Website URLs
   - Document download patterns
   - File naming conventions
   - Storage directories

## 🛠️ Requirements

- **Python 3.8+** with virtual environment support
- **OpenAI API key** (for embeddings and AI-powered search)
- **2GB+ disk space** for documents and analysis results
- **Internet connection** for document downloads and API calls
- **Optional**: systemd for automated scheduling (Linux systems)

## 🔧 Dependencies

### Core Libraries
- **LangChain** - AI document processing and embeddings
- **OpenAI** - GPT-powered search and analysis
- **FAISS** - Vector database for semantic search
- **Flask** - Web interface framework

### Analysis & Visualization
- **fuzzywuzzy** - Intelligent name matching with Levenshtein distance
- **pandas/numpy** - Data manipulation and analysis
- **matplotlib/seaborn/plotly** - Chart generation and visualization
- **PyMuPDF** - PDF document processing

### Additional Features
- **youtube-transcript-api** - YouTube meeting transcript processing
- **python-dateutil** - Smart date/time parsing
- **aiohttp** - Asynchronous HTTP requests for faster processing

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Technical documentation and project overview
- **[VOTING_ANALYSIS_GUIDE.md](VOTING_ANALYSIS_GUIDE.md)** - Advanced voting analysis features
- **[LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)** - Detailed setup instructions
- **[GIT_LARGE_FILES_GUIDE.md](GIT_LARGE_FILES_GUIDE.md)** - Managing large files with Git LFS

## 🚨 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Add your API key to the `.env` file: `OPENAI_API_KEY=your_key_here`
- Get one from https://platform.openai.com/api-keys

**"No documents found" or "Representative not found"**
- Try fuzzy matching: `python clearcouncil.py analyze-voting york_county_sc "Love" "last year"`
- Update documents first: `python clearcouncil.py update-documents york_county_sc "last 6 months"`
- Check council configuration in `config/councils/`

**"Database locked" errors**
- The improved database handling should prevent this
- If it persists, try processing fewer files at once with `--max-workers 2`

**Fuzzy matching not working**
- Ensure fuzzywuzzy is installed: `pip install fuzzywuzzy python-Levenshtein`
- Check the test: `python tests/test_fuzzy_matching.py`

**Web interface not loading**
- Initialize database: `python clearcouncil_web.py init-db`
- Process data: `python clearcouncil_web.py process-data york_county_sc`
- Try the simple server: `python simple_web_server.py` (runs on port 5001)
- Check logs in `clearcouncil_web.log`

**Data transparency information missing**
- Verify web server is running: check `http://localhost:5001/api/health`
- Test data sources API: `curl http://localhost:5001/api/data-sources`
- Check representative deduplication: run `python update_web_database.py`

### Getting Help

```bash
# Test if everything is working
python tests/test_web_integration.py
python tests/test_fuzzy_matching.py

# Check representative extraction
python extract_representatives.py

# Get help for any command
python clearcouncil.py --help
python clearcouncil_web.py --help

# Test basic functionality
python clearcouncil.py list-councils

# Debug PDF content extraction
python debug_pdf_content.py path/to/pdf/file.pdf

# Check sync status
./sync_status.sh
```

### Performance Optimization

**For large datasets:**
- Use `--max-workers` to control parallel processing
- Process documents in batches using time ranges
- Use `--download-missing false` to skip downloads when analyzing

**For faster searching:**
- Build FAISS indexes with `process-pdfs` command
- Use specific time ranges instead of "all time"
- Cache results with automated sync script

## 🎯 Use Cases

### For Citizens
- **Track Your Representative**: Monitor voting patterns with intelligent name search and deduplication
- **Understand Decisions**: Get context for complex municipal issues with built-in glossary
- **Compare Candidates**: Side-by-side analysis during elections with visual comparisons
- **Stay Informed**: Automated updates keep you current with district activities
- **Access History**: Search years of voting records instantly with AI-powered search
- **Verify Data Sources**: Complete transparency about where information comes from and how it's processed

### For Journalists & Researchers
- **Investigative Reporting**: Deep-dive analysis with exportable data and clean representative records
- **Trend Analysis**: Track policy changes over time with comprehensive time-range analysis
- **Data Journalism**: Generate shareable charts and export raw data for stories
- **Accountability Reporting**: Monitor government transparency with automated tracking and source attribution
- **Source Documentation**: Direct links to original documents for fact-checking and verification
- **Quality Assurance**: Access to processing success rates and data quality metrics for accurate reporting

### For Transparency Organizations
- **Public Education**: Create accessible reports with automated chart generation
- **Government Monitoring**: Track policy trends across multiple districts and time periods
- **Civic Engagement**: Help citizens understand local politics with plain-language explanations
- **Data Advocacy**: Use comprehensive analytics to support transparency initiatives
- **Community Outreach**: Mobile-responsive interface for public meetings and events

### For Government Officials
- **Historical Reference**: Quick access to past decisions and voting patterns
- **Constituent Services**: Answer citizen questions with detailed voting history
- **Policy Research**: Analyze the impact of past decisions with trend analysis
- **Transparency Compliance**: Provide easy public access to voting records
- **Inter-district Coordination**: Compare approaches across different districts

## 🔬 Advanced Features

### Municipal Glossary Integration
- Built-in explanations for government terms and procedures
- Interactive tooltips for complex municipal concepts
- Context-aware definitions based on document content

### Intelligent Document Processing
- Automatic extraction of voting records from various PDF formats
- Smart categorization of meeting types and document contents
- Handles complex table structures and multi-column layouts

### Time-Range Analysis
- Flexible date parsing: "last year", "since 2020", "Q1 2023"
- Comparative analysis across different time periods
- Trend identification and pattern recognition

### Automated Scheduling
- Systemd integration for hands-off operation
- Configurable sync intervals and retry logic
- Email notifications for process completion or errors
- Automatic cleanup of old logs and temporary files

## 🤝 Contributing

We welcome contributions! Whether you're:
- 🐛 Reporting bugs
- 💡 Suggesting features
- 🏛️ Adding councils
- 📖 Improving documentation

## 📜 License

MIT License - Use it, modify it, share it!

---

**🏛️ Making local government accessible to everyone, one vote at a time.**

*ClearCouncil: Because understanding your local government shouldn't require a law degree.*