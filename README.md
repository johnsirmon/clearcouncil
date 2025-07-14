# ClearCouncil 🏛️

**Understanding Local Government Made Simple**

ClearCouncil helps everyday citizens understand what their local government representatives are voting on and how they compare to others - all explained in plain English!

## 🎯 What ClearCouncil Does

- **📊 Analyze Representatives**: See what your district representative has been voting on
- **📈 Compare Performance**: Compare representatives to understand different approaches
- **📚 Explain Terms**: Get plain English explanations of government jargon
- **📥 Auto-Download**: Automatically find and download missing meeting documents
- **📋 Create Visuals**: Generate charts and graphs to visualize voting patterns
- **⏰ Time Analysis**: Look at any time period - "last year", "last 6 months", etc.

## 🚀 Quick Start (5 Minutes)

### Step 1: Download and Setup

1. **Download** all ClearCouncil files to a folder on your computer
2. **Run the setup script**:
   - **Windows**: Double-click `setup.bat`
   - **Mac/Linux**: Open Terminal, navigate to folder, run `./setup.sh`
3. **Wait** for automatic installation (2-3 minutes)

### Step 2: Try It Out

Open your command prompt/terminal in the ClearCouncil folder and try:

```bash
# See what councils are available
python clearcouncil_simple.py list-councils

# Learn basic government terms
python clearcouncil_simple.py explain-basic

# Analyze your representative (after setup completes)
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --create-charts
```

## 📋 Real-World Examples

### "What has my representative been voting on?"
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months" --create-charts
```
**You get**: Detailed report with charts showing vote counts, types of issues, and activity timeline

### "How does my rep compare to others?"
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --compare-with "District 1" "District 3"
```
**You get**: Side-by-side comparison showing who's most active and in what areas

### "I don't understand these government terms"
```bash
python clearcouncil.py explain-terms "movant" "second" "rezoning" "ordinance"
```
**You get**: Plain English explanations like "Movant = the person who proposes an action"

### "Get me caught up on recent activity"
```bash
python clearcouncil.py update-documents york_county_sc "last 5 months"
```
**You get**: Automatic download and processing of any missing meeting documents

## 🎨 What You'll See

### Text Reports
```
📊 VOTING ANALYSIS REPORT
Representative: John Smith (District 2)
Time Period: Last 12 months
Total Votes: 45
Motions Made: 8

🏛️ Cases by Type:
   • Rezoning: 15
   • Budget: 12  
   • Ordinances: 18
```

### Visual Charts
- Bar charts comparing representatives
- Timeline showing activity over months
- Pie charts breaking down vote types
- All saved as shareable image files

### Interactive HTML Reports
- Click on any government term for instant explanation
- Sidebar glossary with definitions
- Professional formatting for sharing

## 🛠️ No Technical Skills Required

ClearCouncil is designed for **anyone** to use:

- ✅ **Simple Commands**: Just type what you want to know
- ✅ **Plain English**: All results explained in everyday language  
- ✅ **Automatic Setup**: Setup script handles all technical details
- ✅ **Smart Time Parsing**: Understands "last year", "last 6 months", etc.
- ✅ **Error Guidance**: If something goes wrong, you get clear instructions
- ✅ **Multiple Formats**: Choose text, charts, HTML, or spreadsheet output

## 📊 Key Features

### 🔍 Smart Analysis
- **Time Ranges**: "last year", "last 6 months", "since 2023", or specific dates
- **Natural Language**: Ask questions the way you naturally think
- **Auto-Discovery**: Finds relevant documents automatically
- **Missing Data**: Identifies and downloads missing meeting documents

### 📈 Visual Insights  
- **Representative Summaries**: Complete voting activity overview
- **Comparison Charts**: Side-by-side representative analysis
- **Activity Timelines**: See voting patterns over time
- **District Overviews**: All representatives in your area

### 📚 Educational
- **25+ Municipal Terms**: Built-in glossary of government language
- **Plain English**: Everything explained in everyday terms
- **Interactive Tooltips**: Hover over terms for instant definitions
- **Examples**: Real-world examples for every concept

### ⚡ Efficient Processing
- **Parallel Processing**: Handles multiple documents simultaneously
- **Smart Caching**: Reuses existing data when possible
- **Batch Operations**: Process months of data in one command
- **Progress Tracking**: See exactly what's happening

## 🏛️ Currently Supports

- **York County, South Carolina** (fully configured)
- **Any Council** with PDF meeting documents (easily configurable)

### Adding Your Council
1. Copy `config/councils/template.yaml`
2. Rename to `your_council.yaml`
3. Update website URLs and document patterns
4. Start analyzing immediately

## 📁 File Organization

After setup, your folder contains:
```
ClearCouncil/
├── clearcouncil_simple.py    # Easy starter script
├── setup.bat / setup.sh      # Automatic setup
├── data/
│   ├── PDFs/                 # Downloaded documents  
│   ├── results/              # Analysis results
│   └── results/charts/       # Generated visualizations
├── config/councils/          # Council configurations
└── GETTING_STARTED.md        # Detailed user guide
```

## 🚨 Troubleshooting

### Setup Issues
- **Windows**: Make sure Python is installed and "Add to PATH" was checked
- **Mac/Linux**: Install Python 3.8+ from python.org
- **Permission errors**: Try running setup as administrator

### Analysis Issues  
- **"No documents found"**: Run `python clearcouncil.py update-documents york_county_sc "last year"`
- **"Representative not found"**: Try "District 2" instead of names, or vice versa
- **Missing charts**: Run `pip install matplotlib seaborn --user`

### Quick Fixes
```bash
# Test basic functionality
python clearcouncil_simple.py list-councils

# Re-run setup if needed
./setup.sh  # or setup.bat on Windows

# Get help for any command
python clearcouncil.py --help
python clearcouncil.py analyze-voting --help
```

## 📖 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete step-by-step guide
- **[VOTING_ANALYSIS_GUIDE.md](VOTING_ANALYSIS_GUIDE.md)** - Advanced analysis features
- **[MIGRATION.md](MIGRATION.md)** - For users upgrading from old scripts
- **[CLAUDE.md](CLAUDE.md)** - Technical documentation

## 🎯 Use Cases

### 👥 For Citizens
- Track your representative's voting record
- Compare candidates during elections
- Understand local government decisions
- Stay informed about district activities

### 📰 For Journalists & Researchers
- Analyze voting patterns across time
- Compare representatives' focus areas
- Export data for detailed analysis
- Generate shareable visualizations

### 🏛️ For Transparency Organizations
- Monitor government accountability
- Create public reports
- Track policy trends
- Educate citizens about local politics

## 🤝 Contributing

We welcome contributions! Whether you're:
- 🐛 **Reporting bugs** - Help us improve
- 💡 **Suggesting features** - Tell us what you need
- 🏛️ **Adding councils** - Help expand coverage
- 📖 **Improving docs** - Make it easier for others

## 📜 License

MIT License - Use it, modify it, share it!

---

**🏛️ Making local government accessible to everyone, one vote at a time.**

*ClearCouncil: Because understanding your local government shouldn't require a law degree.*
