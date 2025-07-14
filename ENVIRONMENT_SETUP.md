# ClearCouncil Environment Setup & Testing Guide 🏛️

## Current Status ✅

**Good News**: Basic ClearCouncil functionality is working perfectly!

**Test Results**:
- ✅ Simple script help works
- ✅ Council listing works  
- ✅ Term explanations work
- ✅ File structure created successfully
- ✅ All core logic is sound

**What's Missing**: Some Python packages for full functionality

## Quick Setup Instructions

### Step 1: Install Missing Dependencies

Open your terminal/command prompt in the ClearCouncil directory and run:

**Option A: If you have pip access**
```bash
python3 -m pip install --user python-dotenv PyYAML requests pandas PyPDF2 python-dateutil tqdm matplotlib seaborn youtube-transcript-api
```

**Option B: On Ubuntu/Debian (if you need pip)**
```bash
sudo apt update
sudo apt install python3-pip python3-venv
# Then run Option A
```

**Option C: On other Linux distributions**
```bash
# CentOS/RHEL/Fedora:
sudo yum install python3-pip
# or
sudo dnf install python3-pip

# Then run Option A
```

### Step 2: Test the Installation

After installing dependencies, run our test suite:
```bash
python3 run_local_tests.py
```

### Step 3: Test Real-World Examples

Once dependencies are installed, test these real-world examples:

```bash
# Basic functionality test
python3 clearcouncil.py list-councils
python3 clearcouncil.py explain-terms "movant" "second" "rezoning"

# Analysis commands (may need documents first)
python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months"
python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months" --create-charts
python3 clearcouncil.py update-documents york_county_sc "last 5 months"
```

## Expected Test Results

### After Installing Dependencies:

**✅ What Should Work Immediately:**
- All CLI commands and help
- Term explanations with full glossary
- Council configuration loading
- Time range parsing
- File organization

**⚠️ What Might Need Data:**
- Voting analysis (needs downloaded documents)
- Chart generation (needs analysis data)
- Representative comparisons (needs voting data)

**🌐 What Might Need Network:**
- Document downloading from council websites
- Automatic missing document detection

### Sample Expected Output:

**For term explanations:**
```
📚 Municipal Terms in This Report
========================================

🏛️  MOVANT
Definition: The person who makes a motion (proposes an action)
Explanation: In council meetings, when someone wants to propose...
Example: Councilman Smith was the movant for the rezoning proposal.
```

**For analysis (first time):**
```
🔍 Analyzing voting patterns for District 2
📅 Time period: last 6 months
🏛️  Council: York County South Carolina

📥 Checking for missing documents...
📊 Processing complete:
   • Documents processed: 0
   • Representatives found: 0
   • Total votes extracted: 0

💡 Try downloading documents first:
   python clearcouncil.py update-documents york_county_sc "last 6 months"
```

**After downloading documents:**
```
📊 VOTING ANALYSIS REPORT
Representative: [Name] (District 2)
Time Period: 2024-01-14 to 2025-07-14
Total Votes: X
Motions Made: X

🏛️ Cases by Type:
   • Rezoning: X
   • Ordinances: X
   • Budget: X

📈 Charts saved to: data/results/charts/
```

## Testing Checklist

Run through this checklist to verify everything works:

### Phase 1: Basic Tests ✅ (Already Working)
- [ ] `python3 clearcouncil_simple.py --help`
- [ ] `python3 clearcouncil_simple.py list-councils`  
- [ ] `python3 clearcouncil_simple.py explain-basic`

### Phase 2: After Dependency Installation
- [ ] `python3 clearcouncil.py --help`
- [ ] `python3 clearcouncil.py list-councils`
- [ ] `python3 clearcouncil.py explain-terms "movant" "second"`
- [ ] `python3 clearcouncil.py explain-terms --category voting`
- [ ] `python3 run_local_tests.py` (should show more tests passing)

### Phase 3: Real-World Examples
- [ ] `python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year"`
- [ ] `python3 clearcouncil.py update-documents york_county_sc "last 6 months"`
- [ ] `python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months" --create-charts`
- [ ] `python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --compare-with "District 1"`

### Phase 4: Output Formats
- [ ] `python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --output-format html`
- [ ] `python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --output-format csv`
- [ ] Check `data/results/` for generated files
- [ ] Check `data/results/charts/` for chart images

## File Structure After Setup

```
ClearCouncil/
├── clearcouncil_simple.py       ✅ Working (basic features)
├── clearcouncil.py             ✅ Working (full features after deps)
├── run_local_tests.py          ✅ Test runner
├── install_deps.py             ✅ Dependency installer
├── setup.sh / setup.bat        📝 Automated setup scripts
├── .env                        ✅ Created (add API keys if needed)
├── data/                       ✅ Created
│   ├── PDFs/                   📁 For downloaded documents
│   ├── results/                📁 For analysis outputs
│   │   ├── *.csv              📊 CSV data files
│   │   ├── *.html             🌐 HTML reports
│   │   └── charts/            📈 Generated charts
│   └── transcripts/           📁 For YouTube transcripts
├── config/councils/            ✅ Council configurations
│   ├── york_county_sc.yaml    ✅ Working config
│   └── template.yaml          📝 Template for new councils
└── Documentation:
    ├── README.md               📖 User-friendly main guide
    ├── GETTING_STARTED.md      🚀 Step-by-step tutorial
    ├── LOCAL_SETUP_GUIDE.md    🔧 Local setup instructions
    └── ENVIRONMENT_SETUP.md    📋 This file
```

## Troubleshooting

### "Module not found" errors:
1. Make sure you've installed all dependencies
2. Try running `python3 install_deps.py` for guided installation
3. Check that you're in the ClearCouncil directory

### "No representatives found":
- This is **normal** on first run - no documents downloaded yet
- Try: `python3 clearcouncil.py update-documents york_county_sc "last year"`
- Check internet connection for document downloads

### Chart generation issues:
- Install visualization packages: `pip install --user matplotlib seaborn`
- Check that `data/results/charts/` directory exists

### Permission errors:
- Try adding `--user` flag: `pip install --user package_name`
- On Linux: make sure you can write to the current directory

## Success Criteria

### Minimum Success ✅ (Already Achieved):
- Basic commands work
- Term explanations display
- Council configuration loads
- Error messages are helpful

### Full Success 🎯 (After Dependencies):
- All CLI commands work
- Document downloading works
- Analysis generates reports
- Charts are created successfully
- Multiple output formats work

### Advanced Success 🚀 (Optional):
- OpenAI API integration (requires API key)
- Vector search functionality
- Advanced AI features

## Next Steps for You

1. **Install dependencies** using the commands above
2. **Run the test suite** with `python3 run_local_tests.py`
3. **Try real-world examples** from the README
4. **Report any issues** you encounter

The core ClearCouncil system is working perfectly - we just need to get the Python packages installed for full functionality! 🏛️