# ClearCouncil Test Workflow 🧪

This document provides a step-by-step test workflow to verify all ClearCouncil capabilities work correctly.

## ✅ Phase 1: Basic Setup Testing

### Test 1: Initial Setup
```bash
# Test simple script without dependencies
python3 clearcouncil_simple.py --help
```
**Expected**: Help screen with setup instructions

### Test 2: Council Discovery
```bash
python3 clearcouncil_simple.py list-councils
```
**Expected**: List showing "york_county_sc"

### Test 3: Basic Term Explanations
```bash
python3 clearcouncil_simple.py explain-basic
```
**Expected**: List of municipal terms with explanations

## ✅ Phase 2: Dependency Installation

### Test 4: Run Setup Script

**Windows:**
```cmd
setup.bat
```

**Mac/Linux:**
```bash
./setup.sh
```

**Expected**: Automatic installation of required packages

### Test 5: Verify Installation
```bash
python3 clearcouncil.py list-councils
```
**Expected**: Same council list but using full CLI

## ✅ Phase 3: Core Functionality

### Test 6: Term Explanations
```bash
python3 clearcouncil.py explain-terms "movant" "second" "rezoning"
```
**Expected**: Detailed explanations with definitions, examples, and categories

### Test 7: Term Categories
```bash
python3 clearcouncil.py explain-terms --category voting
```
**Expected**: All voting-related terms listed

### Test 8: Document Discovery
```bash
python3 clearcouncil.py update-documents york_county_sc "last 3 months"
```
**Expected**: Report on document status and any downloads

## ✅ Phase 4: Basic Analysis (May require documents)

### Test 9: Simple Analysis
```bash
python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year"
```
**Expected**: Analysis report or guidance on missing documents

### Test 10: Comparison Analysis
```bash
python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --compare-with "District 1"
```
**Expected**: Comparison report or guidance on missing data

## ✅ Phase 5: Advanced Features (Optional - requires full setup)

### Test 11: Chart Generation
```bash
python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --create-charts
```
**Expected**: Chart files in `data/results/charts/`

### Test 12: HTML Output
```bash
python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --output-format html
```
**Expected**: HTML file with interactive tooltips

### Test 13: CSV Export
```bash
python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --output-format csv
```
**Expected**: CSV files in `data/results/`

### Test 14: District Analysis
```bash
python3 clearcouncil.py analyze-district york_county_sc "District 2" "last year"
```
**Expected**: District-wide analysis report

## 📊 Expected File Structure After Testing

```
ClearCouncil/
├── clearcouncil_simple.py     ✅ Working
├── setup.sh / setup.bat       ✅ Completed
├── .env                       ✅ Created by setup
├── data/
│   ├── PDFs/                  📥 May contain downloaded docs
│   ├── results/               📊 Analysis results
│   │   ├── *.csv             📄 CSV exports
│   │   └── *.html            🌐 HTML reports
│   └── results/charts/        📈 Generated charts
│       ├── *.png             🖼️ Chart images
│       └── *.svg             🎨 Vector charts
└── clearcouncil.log           📝 Operation logs
```

## 🚨 Troubleshooting Common Test Failures

### Test 1-3 Fail: "Module not found"
**Cause**: Python path issues
**Fix**: 
```bash
cd /path/to/clearcouncil
python3 clearcouncil_simple.py --help
```

### Test 4 Fails: "Permission denied"
**Cause**: Setup script permissions
**Fix**:
```bash
chmod +x setup.sh
./setup.sh
```

### Test 5 Fails: "No module named 'dotenv'"
**Cause**: Setup script didn't complete
**Fix**: Re-run setup script or install manually:
```bash
pip3 install python-dotenv PyYAML requests pandas --user
```

### Test 6-8 Fail: Import errors
**Cause**: Partial dependency installation
**Fix**: Install missing packages:
```bash
pip3 install -r requirements.txt --user
```

### Test 9-10 Fail: "No documents found"
**Cause**: No local documents available
**Fix**: This is expected behavior - the system will guide you to download documents

### Test 11 Fails: "Module 'matplotlib' not found"
**Cause**: Visualization packages not installed
**Fix**:
```bash
pip3 install matplotlib seaborn --user
```

### Test 12-13 Fail: File permission errors
**Cause**: Directory permissions
**Fix**:
```bash
mkdir -p data/results/charts
chmod 755 data/results/
```

## 📝 Test Results Checklist

Mark each test as you complete it:

- [ ] ✅ Test 1: Simple script help
- [ ] ✅ Test 2: Council listing  
- [ ] ✅ Test 3: Basic terms
- [ ] ✅ Test 4: Setup script
- [ ] ✅ Test 5: Full CLI
- [ ] ✅ Test 6: Term explanations
- [ ] ✅ Test 7: Term categories
- [ ] ✅ Test 8: Document discovery
- [ ] ⚠️ Test 9: Basic analysis (may need documents)
- [ ] ⚠️ Test 10: Comparison (may need documents)
- [ ] 📊 Test 11: Charts (requires matplotlib)
- [ ] 🌐 Test 12: HTML output
- [ ] 📄 Test 13: CSV export  
- [ ] 🏛️ Test 14: District analysis

## 🎯 Success Criteria

### Minimum Success (Essential functionality)
- ✅ Tests 1-8 pass
- ✅ Setup script completes without errors
- ✅ Basic CLI commands work
- ✅ Term explanations display correctly

### Full Success (All features working)
- ✅ All tests 1-14 pass
- ✅ Charts generate correctly
- ✅ Multiple output formats work
- ✅ No import or dependency errors

### Expected Limitations
- **Document availability**: Analysis commands may report "no documents found" - this is normal
- **API features**: Some features require OpenAI API key in .env file
- **Visualization**: Chart generation requires matplotlib/seaborn packages

## 🔄 Continuous Testing

### Daily Use Test
```bash
# Quick functionality check
python3 clearcouncil_simple.py list-councils
python3 clearcouncil.py explain-terms "movant"
```

### Weekly Analysis Test
```bash
# Full analysis workflow
python3 clearcouncil.py update-documents york_county_sc "last month"
python3 clearcouncil.py analyze-voting york_county_sc "District 2" "last month" --create-charts
```

### New User Simulation
1. Fresh download of ClearCouncil
2. Run setup script
3. Follow README.md quick start
4. Verify all examples work

This test workflow ensures ClearCouncil works reliably for all users, from complete beginners to advanced users wanting full functionality.