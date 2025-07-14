# Voting Analysis Guide

This guide shows you how to analyze representative voting patterns and compare representatives using ClearCouncil's new voting analysis features.

## Quick Start Examples

### 1. Analyze Your Representative's Voting Record

```bash
# Analyze District 2 representative for the last year
clearcouncil analyze-voting york_county_sc "District 2" "last year" --create-charts

# Analyze a specific representative by name for the last 6 months
clearcouncil analyze-voting york_county_sc "John Smith" "last 6 months" --download-missing
```

### 2. Compare Representatives

```bash
# Compare your district representative with others
clearcouncil analyze-voting york_county_sc "District 2" "last year" \
  --compare-with "District 1" "District 3" \
  --create-charts \
  --output-format html
```

### 3. Analyze Entire District

```bash
# See all representatives in District 2
clearcouncil analyze-district york_county_sc "District 2" "last year" --create-charts
```

### 4. Update Missing Documents

```bash
# Download and process missing documents for the last 5 months
clearcouncil update-documents york_county_sc "last 5 months"
```

### 5. Understand Municipal Terms

```bash
# Get explanations for specific terms
clearcouncil explain-terms "movant" "second" "rezoning" "ordinance"

# See all terms in a category
clearcouncil explain-terms --category voting

# See all available categories
clearcouncil explain-terms all
```

## Advanced Usage

### Time Range Options

The system understands natural language time ranges:

- `"last year"` - Past 12 months
- `"last 6 months"` - Past 6 months  
- `"past 2 years"` - Past 24 months
- `"since 2023"` - From January 1, 2023 to now
- `"2023-01-01 to 2023-12-31"` - Specific date range
- `"6 months ago"` - Around 6 months ago

### Output Formats

Choose different output formats for your analysis:

- `--output-format plain` - Simple text output (default)
- `--output-format json` - JSON data for further processing
- `--output-format csv` - CSV files for spreadsheet analysis
- `--output-format html` - Interactive HTML report with tooltips

### Visualization Options

Generate charts to visualize voting patterns:

- `--create-charts` - Creates multiple chart types:
  - Representative summary with vote breakdowns
  - Timeline showing activity over time
  - Comparison charts between representatives
  - District overview charts

Charts are saved to `data/results/charts/` as high-resolution PNG files.

## Understanding the Analysis

### What You'll Learn About Representatives

1. **Activity Level**
   - Total votes in the time period
   - Number of motions made (proposals initiated)
   - Number of seconds given (supporting others' proposals)
   - Participation rate

2. **Voting Patterns**
   - Breakdown by vote type (for/against/abstain)
   - Activity by case category (rezoning, ordinances, etc.)
   - Timeline of voting activity

3. **Comparisons**
   - How active compared to other representatives
   - Agreement rates with other representatives
   - Specialization in certain types of issues

### Municipal Terms Explained

The system automatically explains municipal government terms you might not be familiar with:

- **Movant**: The person who makes a motion (proposes an action)
- **Second**: A council member who supports a motion so it can be discussed
- **Rezoning**: Changing what can be built or done on a piece of land
- **Ordinance**: A local law passed by the council
- **Abstain**: Choosing not to vote due to conflict of interest or insufficient information

## Efficient Data Processing

### How the System Optimizes Performance

The new system is much more efficient than the old approach:

1. **Automatic Document Discovery**: Finds relevant documents by date range
2. **Parallel Processing**: Downloads and processes multiple documents simultaneously
3. **Smart Caching**: Reuses existing documents when possible
4. **Batch Operations**: Processes all documents in one operation

### Missing Document Handling

When you request analysis for a time period:

1. **Automatic Detection**: System checks what documents you already have
2. **Gap Analysis**: Identifies potential missing documents
3. **Smart Downloading**: Downloads only what's likely to be missing
4. **Recommendation**: Tells you if coverage seems adequate

Example workflow:
```bash
# Check what's missing for the last year
clearcouncil update-documents york_county_sc "last year"

# Then analyze with confidence you have complete data
clearcouncil analyze-voting york_county_sc "District 2" "last year" --create-charts
```

## Real-World Use Cases

### Citizen Engagement

**Before a council meeting:**
```bash
# See what your representative has been voting on lately
clearcouncil analyze-voting york_county_sc "District 2" "last 3 months"

# Understand any unfamiliar terms
clearcouncil explain-terms "conditional use permit" "setback" "variance"
```

**During election season:**
```bash
# Compare candidates' voting records
clearcouncil analyze-voting york_county_sc "Current Rep" "last 2 years" \
  --compare-with "Challenger Name" \
  --output-format html
```

### Research and Journalism

**Investigating voting patterns:**
```bash
# Get comprehensive data for analysis
clearcouncil analyze-district york_county_sc "District 2" "last 2 years" \
  --output-format csv \
  --create-charts

# Download missing historical documents
clearcouncil update-documents york_county_sc "since 2020"
```

### Transparency and Accountability

**Regular monitoring:**
```bash
# Monthly check on all representatives
for district in 1 2 3 4 5; do
  clearcouncil analyze-voting york_county_sc "District $district" "last month"
done
```

## File Locations

### Generated Files

- **Charts**: `data/results/charts/`
  - `{representative_name}_summary.png` - Individual summary
  - `comparison_{representative_name}.png` - Comparison charts
  - `district_{district}_overview.png` - District overviews
  - `voting_timeline.png` - Activity timeline

- **Data Files**: `data/results/`
  - `voting_analysis_{name}.csv` - Analysis data
  - `detailed_votes_{name}.csv` - Individual vote records
  - `{name}_analysis.html` - Interactive HTML reports

- **Logs**: `clearcouncil.log` - Detailed operation logs

### Configuration

- **Council Settings**: `config/councils/york_county_sc.yaml`
- **Custom Terms**: Add your own glossary terms to council config

## Troubleshooting

### Common Issues

1. **"Representative not found"**
   - Try different formats: "District 2", "John Smith", "Smith"
   - Check spelling and capitalization
   - Use `clearcouncil analyze-district` to see available representatives

2. **"No documents found"**
   - Run `clearcouncil update-documents` first
   - Check if the time range has any council meetings
   - Verify council website is accessible

3. **Missing visualizations**
   - Install visualization dependencies: `pip install matplotlib seaborn`
   - Check `data/results/charts/` directory permissions

### Getting Help

```bash
# See all available commands
clearcouncil --help

# Get help for specific commands
clearcouncil analyze-voting --help
clearcouncil explain-terms --help

# Check system status
clearcouncil list-councils
```

## Contributing

To add support for your local council:

1. Copy `config/councils/template.yaml`
2. Rename to `your_council.yaml` 
3. Update all configuration sections
4. Test with: `clearcouncil download-pdfs your_council --document-id 1`

The system will work with any council that provides PDF documents with structured data.