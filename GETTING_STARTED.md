# Getting Started with ClearCouncil 🏛️

**ClearCouncil helps you understand what your local government representatives are voting on and how they compare to others - in plain English!**

## What ClearCouncil Does

- 📊 **Analyzes** your representative's voting patterns
- 📈 **Compares** representatives to see how they differ
- 📚 **Explains** municipal government terms in simple language
- 📥 **Downloads** missing meeting documents automatically
- 📋 **Visualizes** voting data with charts and graphs

## Step-by-Step Setup (5 minutes)

### Step 1: Download ClearCouncil
1. Download all the ClearCouncil files to a folder on your computer
2. Open that folder in your file explorer
3. You should see files like `clearcouncil_simple.py`, `setup.sh`, `setup.bat`

### Step 2: Run the Setup Script

**🪟 If you're on Windows:**
1. Double-click `setup.bat`
2. Follow the prompts
3. Wait for installation to complete

**🍎 If you're on Mac:**
1. Open Terminal (press Cmd+Space, type "Terminal", press Enter)
2. Drag the ClearCouncil folder into Terminal window
3. Type `./setup.sh` and press Enter
4. Follow the prompts

**🐧 If you're on Linux:**
1. Open Terminal
2. Navigate to the ClearCouncil folder: `cd /path/to/clearcouncil`
3. Run: `./setup.sh`
4. Follow the prompts

### Step 3: Test Basic Functionality

Open your command prompt/terminal and navigate to the ClearCouncil folder, then try:

```bash
python clearcouncil_simple.py list-councils
```

You should see:
```
📋 Available Councils:
=========================
  • york_county_sc
```

**If you see an error**, don't worry! The simple script will guide you through fixing it.

## Basic Usage (No Technical Knowledge Required)

### 🔍 Understanding Municipal Terms

Start by learning the basic terms:

```bash
python clearcouncil_simple.py explain-basic
```

This shows you what terms like "movant", "second", and "rezoning" mean in plain English.

### 📋 See What Councils Are Available

```bash
python clearcouncil_simple.py list-councils
```

### 🗳️ Analyze Your Representative (Main Feature)

Once setup is complete, you can analyze any representative:

```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year"
```

**What this tells you:**
- How many times they voted
- What types of issues they voted on
- How active they are compared to others

### 📊 Compare Representatives

```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --compare-with "District 1" "District 3"
```

**What this shows:**
- Side-by-side comparison of voting activity
- Who's most active in your area
- Different representatives' focus areas

### 📈 Create Visual Charts

Add `--create-charts` to any analysis command:

```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --create-charts
```

**What you get:**
- Bar charts showing vote counts
- Timeline showing activity over time
- Comparison charts between representatives
- All saved as easy-to-share image files

## Time Periods You Can Use

ClearCouncil understands natural language for time periods:

- `"last year"` - Past 12 months
- `"last 6 months"` - Past 6 months
- `"last 3 months"` - Past 3 months
- `"since 2023"` - From January 2023 to now
- `"2023-01-01 to 2023-12-31"` - Specific dates

## Example Real-World Scenarios

### Scenario 1: "I want to see what my representative has been voting on"

```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last 6 months" --create-charts
```

**Result:** You get a detailed report showing:
- 📊 How many votes they participated in
- 🏛️ What types of issues (zoning, budget, ordinances)
- 📈 Charts showing their activity over time
- 📚 Explanations of any unfamiliar terms

### Scenario 2: "How does my representative compare to others?"

```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --compare-with "District 1" "District 3" "District 4" --output-format html
```

**Result:** You get:
- 📊 Side-by-side comparison charts
- 🌐 Interactive HTML report you can share
- 📚 Built-in explanations of municipal terms
- 📈 Visual comparisons of activity levels

### Scenario 3: "I want to understand these government terms"

```bash
python clearcouncil.py explain-terms "movant" "second" "rezoning" "ordinance" "variance"
```

**Result:** Plain English explanations like:
- **Movant**: The person who makes a motion (proposes an action)
- **Second**: Someone who supports the motion so it can be discussed
- **Rezoning**: Changing what can be built on a piece of land

### Scenario 4: "Get me caught up on the last few months"

```bash
python clearcouncil.py update-documents york_county_sc "last 5 months"
```

**Result:** 
- 📥 Automatically downloads any missing meeting documents
- 📊 Processes them to extract voting data
- ✅ Tells you what new information was found

## Output Formats

Choose how you want to see results:

### Plain Text (Default)
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year"
```
**Good for:** Quick reading in terminal

### HTML Report (Interactive)
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --output-format html
```
**Good for:** Sharing with others, interactive tooltips

### CSV Data (Spreadsheet)
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --output-format csv
```
**Good for:** Your own analysis in Excel or Google Sheets

### JSON Data (Technical)
```bash
python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --output-format json
```
**Good for:** Programmers who want to build on the data

## Understanding the Results

### Representative Analysis Report

When you analyze a representative, you'll see:

```
📊 VOTING ANALYSIS REPORT
==================================================
Representative: John Smith (District 2)
Time Period: 2023-07-14 to 2024-07-14
Total Votes: 45
Motions Made: 8
Seconds Given: 12

📋 Voting Activity Breakdown:
   • Motions Made: 8
   • Seconds Given: 12
   • Votes For: 20
   • Votes Against: 3
   • Abstentions: 2

🏛️  Cases by Type:
   • Rezoning: 15
   • Ordinance: 12
   • Budget: 8
   • Other: 10
```

**What this means:**
- **Total Votes**: How many voting actions they took
- **Motions Made**: How many times they proposed something new
- **Seconds Given**: How many times they supported others' proposals
- **Cases by Type**: What kinds of issues they dealt with

### Charts and Visualizations

Charts are saved in `data/results/charts/` as PNG files:
- `John_Smith_summary.png` - Overview of their activity
- `comparison_John_Smith.png` - Comparison with other representatives
- `voting_timeline.png` - Activity over time

## Troubleshooting

### "Module not found" or "Import error"
**Solution:** Run the setup script again:
- Windows: Double-click `setup.bat`
- Mac/Linux: Run `./setup.sh`

### "No documents found"
**Solution:** Download documents first:
```bash
python clearcouncil.py update-documents york_county_sc "last year"
```

### "Representative not found"
**Try different formats:**
- `"District 2"` (if you know the district)
- `"John Smith"` (if you know the name)
- `"Smith"` (just the last name)

### Charts not generating
**Solution:** Install visualization packages:
```bash
pip install matplotlib seaborn --user
```

### Need API key for advanced features
1. Go to https://platform.openai.com/api-keys
2. Create an account and get an API key
3. Open the `.env` file in the ClearCouncil folder
4. Add your key: `OPENAI_API_KEY=your_key_here`

## Getting Help

### Built-in Help
```bash
python clearcouncil.py --help
python clearcouncil.py analyze-voting --help
```

### Check What's Working
```bash
python clearcouncil_simple.py list-councils
python clearcouncil_simple.py explain-basic
```

### Common Commands Quick Reference

| What you want to do | Command |
|---------------------|---------|
| See available councils | `python clearcouncil_simple.py list-councils` |
| Learn basic terms | `python clearcouncil_simple.py explain-basic` |
| Analyze your rep | `python clearcouncil.py analyze-voting york_county_sc "District 2" "last year"` |
| Compare reps | `python clearcouncil.py analyze-voting york_county_sc "District 2" "last year" --compare-with "District 1"` |
| Make charts | `Add --create-charts to any analyze command` |
| Get missing docs | `python clearcouncil.py update-documents york_county_sc "last 6 months"` |
| Explain terms | `python clearcouncil.py explain-terms "movant" "second"` |

## Next Steps

Once you're comfortable with the basics:

1. **Explore different time periods** - Try "last 3 months", "since 2022", etc.
2. **Compare multiple representatives** - See how your district compares to others
3. **Create charts** - Visual data is easier to understand and share
4. **Try different output formats** - HTML reports are great for sharing
5. **Learn more terms** - Understanding the language helps you follow local politics

**Remember:** ClearCouncil is designed to make local government more accessible. Don't worry if you don't understand everything at first - that's exactly what this tool is meant to help with!