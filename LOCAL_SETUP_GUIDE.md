# Local Setup Guide for ClearCouncil 🏛️

## Option 1: Quick Local Setup (Recommended)

### Step 1: Install Python Dependencies Locally

Open your terminal/command prompt in the ClearCouncil directory and run:

**Windows:**
```cmd
python -m pip install --user python-dotenv PyYAML requests pandas PyPDF2 python-dateutil tqdm matplotlib seaborn youtube-transcript-api
```

**Mac/Linux:**
```bash
python3 -m pip install --user python-dotenv PyYAML requests pandas PyPDF2 python-dateutil tqdm matplotlib seaborn youtube-transcript-api
```

If pip isn't available, install it first:
**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

**CentOS/RHEL:**
```bash
sudo yum install python3-pip
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python
```

### Step 2: Create Environment File

Create a `.env` file in the ClearCouncil directory:
```bash
# On Windows
echo # OpenAI API Key (optional for basic features) > .env
echo # OPENAI_API_KEY=your_key_here >> .env

# On Mac/Linux  
echo "# OpenAI API Key (optional for basic features)" > .env
echo "# OPENAI_API_KEY=your_key_here" >> .env
```

### Step 3: Test Basic Functionality

```bash
# Test simple commands (should work immediately)
python clearcouncil_simple.py list-councils
python clearcouncil_simple.py explain-basic

# Test full functionality (after installing dependencies)
python clearcouncil.py list-councils
python clearcouncil.py explain-terms "movant" "second" "rezoning"
```

## Option 2: Virtual Environment Setup (Best Practice)

### Step 1: Create Virtual Environment

**Windows:**
```cmd
python -m venv clearcouncil_env
clearcouncil_env\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv clearcouncil_env
source clearcouncil_env/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install python-dotenv PyYAML requests pandas PyPDF2 python-dateutil tqdm matplotlib seaborn youtube-transcript-api
```

### Step 3: Test Everything

```bash
python clearcouncil.py --help
python clearcouncil.py list-councils
python clearcouncil.py explain-terms "movant" "second"
```

## Option 3: Using the Automated Setup Scripts

### Windows:
1. Double-click `setup.bat`
2. Follow the prompts
3. Wait for installation to complete

### Mac/Linux:
```bash
chmod +x setup.sh
./setup.sh
```

## Testing the Real-World Examples

Once dependencies are installed, test these examples:

### Example 1: Basic Analysis
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months"
```

### Example 2: With Charts
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months" --create-charts
```

### Example 3: Representative Comparison
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --compare-with "District 1" "District 3"
```

### Example 4: Download Missing Documents
```bash
python clearcouncil.py update-documents york_county_sc "last 5 months"
```

### Example 5: HTML Output
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --output-format html --create-charts
```

## Expected Results

### First Time (No Documents):
```
📥 Checking for missing documents...
📊 Processing complete:
   • Documents processed: 0
   • Representatives found: 0
   • Total votes extracted: 0

💡 Try downloading documents first:
   python clearcouncil.py update-documents york_county_sc "last year"
```

### After Downloading Documents:
```
📊 VOTING ANALYSIS REPORT
Representative: Found Representative Name (District 2)
Time Period: [Date Range]
Total Votes: X
Motions Made: X
Seconds Given: X

📈 Charts saved to: data/results/charts/
```

## Troubleshooting

### "Module not found" errors:
- Make sure you've installed all dependencies
- Try running the setup script again
- Check that you're in the correct directory

### "No representatives found":
- This is normal on first run
- Try downloading documents first
- Check if the council website is accessible

### Chart generation fails:
- Make sure matplotlib and seaborn are installed
- Check that the data/results/charts/ directory exists

## File Locations After Setup

```
ClearCouncil/
├── clearcouncil_simple.py      # Basic functionality
├── clearcouncil.py            # Full functionality  
├── setup.sh / setup.bat       # Automated setup
├── .env                       # API keys (created)
├── data/
│   ├── PDFs/                  # Downloaded documents
│   ├── results/               # Analysis results
│   └── results/charts/        # Generated charts
└── clearcouncil.log           # Operation logs
```