# Optimized ClearCouncil Sample Prompts

Based on your actual York County SC data analysis:
- **39 representatives** across 8 districts (At-Large, Districts 1-5, 7, Unknown)
- **3,795 voting records** with detailed motion/second tracking
- **Top performers**: Robert Winkler (414 votes), Allison Love (393 votes), Thomas Audette (319 votes)

## Recommended Prompts for Your Data

### 1. Representative Performance Analysis
```
"Show me Robert Winkler's voting patterns and how many motions he's made"
"Compare Allison Love's and Thomas Audette's voting records"
"Which At-Large representatives are most active in making motions?"
"How does Joel Hamilton's performance compare to other District 1 representatives?"
```

### 2. District-Based Queries
```
"What are the voting patterns for At-Large representatives?"
"Compare voting activity between District 3 and District 1"
"Which district has the most active representatives?"
"Show me all representatives from District 2 and their voting statistics"
```

### 3. Motion and Second Tracking
```
"Who makes the most motions in York County Council?"
"Which representatives frequently second motions?"
"Show the motion-to-second ratio for William 'Bump' Roddey"
"Find cases where Thomas Audette made the motion"
```

### 4. Vote Pattern Analysis
```
"Show me unanimous decisions and who typically makes those motions"
"Find split votes and analyze the voting patterns"
"Which representatives work together most often (motion/second pairs)?"
"Show voting trends for approved vs. rejected measures"
```

### 5. Council Dynamics
```
"Who are the most collaborative representatives (motion/second partnerships)?"
"Show the leadership patterns in York County Council"
"Which representatives initiate the most legislative action?"
"Analyze the efficiency of different representative combinations"
```

### 6. Time-Based Analysis (if meeting dates were populated)
```
"Show voting activity trends over the past year"
"Which representatives have been most active recently?"
"Compare council productivity across different time periods"
```

### 7. Specific Case Queries
```
"Show me details for case number 'vote_Robert Winkler_APPROVED [UNANIMOUS]_1'"
"Find all cases where William 'Bump' Roddey was the movant"
"Show voting records where Allison Love provided the second"
```

## Web Interface Test Prompts

### Dashboard Queries
```
"Show me the transparency dashboard"
"What data sources are being used?"
"Display the representative comparison tool"
"Show voting statistics by district"
```

### API Endpoint Tests
```
"Get data for representative Robert Winkler"
"Show all voting records for District 3"
"Display motion/second statistics"
"Export voting data for the top 5 representatives"
```

## Chat Interface Prompts

### General Council Information
```
"Tell me about York County Council structure"
"Who are the most active council members?"
"Explain the motion and second process"
"What districts are represented in York County?"
```

### Specific Representative Queries
```
"What can you tell me about Robert Winkler's role on the council?"
"How does Allison Love contribute to council decisions?"
"Compare the voting styles of At-Large vs. District representatives"
```

### Legislative Process Questions
```
"How does the voting process work in York County Council?"
"What does it mean when a vote is unanimous?"
"Who typically leads in making motions?"
"Explain the role of seconds in council voting"
```

## Advanced Analysis Prompts

### Statistical Analysis
```
"Calculate the success rate of motions by representative"
"Show the correlation between making motions and giving seconds"
"Which representatives have the highest approval rates?"
"Analyze voting efficiency by district representation"
```

### Comparative Analysis
```
"Compare top 3 representatives by total voting activity"
"Show district representation balance in council leadership"
"Analyze At-Large vs. District representative engagement patterns"
"Compare motion success rates across different representatives"
```

## Data Quality Verification

Your data shows:
- ✅ **Strong voting record tracking** (3,795 records)
- ✅ **Comprehensive representative coverage** (39 members)
- ✅ **Detailed motion/second tracking**
- ⚠️ **Limited case categorization** (mainly "other" category)
- ⚠️ **Missing meeting dates** in most records
- ⚠️ **No document processing** yet (0 documents)

## Recommendations for Enhanced Prompts

1. **Focus on motion/second dynamics** - Your strongest data point
2. **Leverage representative statistics** - Rich voting count data available
3. **Emphasize district comparisons** - Good district coverage
4. **Use specific representative names** - Real data for testing
5. **Avoid time-based queries** - Meeting dates not populated

## Testing Priority

1. **High Priority**: Representative-based queries, motion/second analysis
2. **Medium Priority**: District comparisons, voting patterns
3. **Low Priority**: Time-based analysis, document queries (until document processing is complete)

These prompts are optimized for your actual data structure and will provide meaningful results based on the 39 representatives and 3,795 voting records currently in your database.