# ClearCouncil 🏛️

**A local government transparency tool that makes understanding council decisions simple**

ClearCouncil processes PDF documents and creates interactive dashboards to help citizens understand what their representatives are voting on and how they compare to others.

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

# Process council documents
python clearcouncil.py process-pdfs york_county_sc

# Search documents
python clearcouncil.py search york_county_sc "rezoning ordinance"

# Analyze voting patterns
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --create-charts

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
```

## 📊 Features

### Interactive Web Dashboard
- **Representative Analysis**: View detailed voting records and patterns
- **Interactive Charts**: Filter by time period and representative
- **Search Functionality**: Find specific topics or cases
- **Comparison Tools**: Compare representatives side-by-side
- **Mobile Responsive**: Works on phones, tablets, and desktops

### Command Line Tools
- **Document Processing**: Extract voting records from PDF files
- **Data Analysis**: Generate reports and visualizations
- **Batch Operations**: Process multiple files efficiently
- **Search**: Find specific content across all documents

### Data Management
- **Optimized Database**: Fast queries with proper indexing
- **Parallel Processing**: Handle multiple documents simultaneously
- **Vector Search**: Find relevant content using AI embeddings
- **Automatic Updates**: Keep data current with new documents

## 🏛️ Currently Supported

- **York County, South Carolina** (fully configured)
- **Easy Configuration**: Add new councils by copying and editing YAML config files

## 📁 Project Structure

```
clearcouncil/
├── clearcouncil.py              # Main CLI application
├── clearcouncil_web.py          # Web interface launcher
├── setup_web.py                 # Web setup script
├── requirements.txt             # Python dependencies
├── config/                      # Council configurations
│   └── councils/
│       └── york_county_sc.yaml  # Example council config
├── src/clearcouncil/            # Main source code
│   ├── web/                     # Web interface
│   ├── cli/                     # Command line interface
│   ├── processors/              # Document processors
│   ├── parsers/                 # Data parsers
│   └── core/                    # Core functionality
├── data/                        # Data storage
│   ├── PDFs/                    # Downloaded documents
│   ├── results/                 # Analysis results
│   └── faiss_indexes/           # Vector database
└── tests/                       # Test files
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

- Python 3.8+
- OpenAI API key (for embeddings and search)
- 2GB+ disk space for documents
- Internet connection for document downloads

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Technical documentation and project overview
- **[VOTING_ANALYSIS_GUIDE.md](VOTING_ANALYSIS_GUIDE.md)** - Advanced voting analysis features
- **[LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)** - Detailed setup instructions
- **[GIT_LARGE_FILES_GUIDE.md](GIT_LARGE_FILES_GUIDE.md)** - Managing large files with Git LFS

## 🚨 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Add your API key to the `.env` file
- Get one from https://platform.openai.com/api-keys

**"No documents found"**
- Run `python clearcouncil.py download-pdfs york_county_sc` first
- Check that the council configuration is correct

**"Database locked" errors**
- The improved database handling should prevent this
- If it persists, try processing fewer files at once

### Getting Help

```bash
# Check if everything is working
python tests/test_web_integration.py

# Get help for any command
python clearcouncil.py --help
python clearcouncil_web.py --help

# Test basic functionality
python clearcouncil.py list-councils
```

## 🎯 Use Cases

### For Citizens
- Track your representative's voting record
- Understand local government decisions
- Compare candidates during elections
- Stay informed about district activities

### For Journalists & Researchers
- Analyze voting patterns over time
- Export data for detailed analysis
- Generate shareable visualizations
- Monitor government accountability

### For Transparency Organizations
- Create public reports
- Track policy trends
- Educate citizens about local politics
- Monitor government accountability

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