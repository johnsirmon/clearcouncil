# ClearCouncil Integrated App - Troubleshooting Guide

## Quick Start

### Method 1: Direct Run
```bash
source .venv/bin/activate
python clearcouncil_integrated_app.py
```

### Method 2: Using Startup Script
```bash
source .venv/bin/activate  
python start_integrated_app.py
```

### Method 3: Testing Script
```bash
source .venv/bin/activate
python test_integrated_app.py
```

## Access Points

- **Main Dashboard**: http://localhost:5000
- **AI Chat**: http://localhost:5000/chat
- **Representatives**: http://localhost:5000/representatives  
- **Search**: http://localhost:5000/search
- **Transparency**: http://localhost:5000/transparency

## API Endpoints

- **Stats**: http://localhost:5000/api/stats
- **Chat**: POST http://localhost:5000/api/chat
- **Representatives**: http://localhost:5000/api/representatives
- **Search**: http://localhost:5000/api/search

## Common Issues & Solutions

### 1. "Module not found" errors
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Install missing dependencies
pip install flask requests python-dotenv
```

### 2. "Database not found" errors
```bash
# Check if database file exists
ls -la clearcouncil.db

# If missing, you may need to process data first
python clearcouncil.py list-councils
```

### 3. Chat functionality not working
```bash
# Check GitHub token
echo $GITHUB_TOKEN

# Set token if missing
export GITHUB_TOKEN=your_token_here
```

### 4. Port already in use
```bash
# Kill existing processes
pkill -f "python clearcouncil"

# Or use different port
python clearcouncil_integrated_app.py --port 5001
```

### 5. Permission errors
```bash
# Check file permissions
ls -la clearcouncil_integrated_app.py

# Make executable if needed
chmod +x clearcouncil_integrated_app.py
```

## Features Included

✅ **Dashboard**
- Real-time statistics
- Top representatives
- Voting patterns
- Quick search

✅ **AI Chat**  
- GitHub AI integration
- Contextual responses
- Session management
- Real-time messaging

✅ **Data Access**
- Representatives overview
- Voting records search
- Performance metrics
- District analysis

✅ **Transparency**
- Data source information
- Processing methods
- Quality metrics
- Limitations disclosure

## Technical Details

- **Framework**: Flask with Blueprint architecture
- **Database**: SQLite with context managers
- **AI**: GitHub Models API integration
- **Frontend**: Bootstrap 5 with responsive design
- **API**: RESTful endpoints with JSON responses

## Verification Steps

1. **Check app creation**:
   ```bash
   python -c "from clearcouncil_integrated_app import create_app; print('✅ OK')"
   ```

2. **Test database access**:
   ```bash
   python analyze_data.py
   ```

3. **Verify dependencies**:
   ```bash
   python -c "import flask, requests, sqlite3; print('✅ All deps OK')"
   ```

4. **Test routes**:
   ```bash
   python test_integrated_app.py
   ```

## If Still Not Working

Please provide:
1. **Exact error message** you see
2. **Command you're running**
3. **Your operating system**
4. **Python version**: `python --version`
5. **Virtual environment status**: `which python`

The application has been tested and verified to work correctly with the existing data structure.