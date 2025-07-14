@echo off
REM ClearCouncil Setup Script for Windows
REM This script helps set up ClearCouncil for non-technical users

echo 🏛️  ClearCouncil Setup Script
echo ================================
echo.

REM Check if we're in the right directory
if not exist "clearcouncil.py" (
    echo ❌ Error: Please run this script from the clearcouncil directory
    echo    Make sure you can see the clearcouncil.py file in the current folder
    pause
    exit /b 1
)

REM Check Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo ✅ Found Python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
        echo ✅ Found Python 3
    ) else (
        echo ❌ Python is not installed or not in PATH
        echo    Please install Python 3.8 or higher from https://python.org
        echo    Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
)

REM Check pip installation
echo 🔍 Checking pip installation...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ pip is available
) else (
    echo ❌ pip is not available
    echo    Please reinstall Python with pip included
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing required packages...
echo    This may take a few minutes...

REM Create basic requirements
echo python-dotenv^>=1.0.0> requirements_basic.txt
echo PyYAML^>=6.0.1>> requirements_basic.txt
echo requests^>=2.31.0>> requirements_basic.txt
echo pandas^>=1.5.0>> requirements_basic.txt
echo PyPDF2^>=3.0.1>> requirements_basic.txt
echo youtube-transcript-api^>=0.6.0>> requirements_basic.txt
echo python-dateutil^>=2.8.0>> requirements_basic.txt
echo tqdm^>=4.65.0>> requirements_basic.txt

REM Install basic packages
%PYTHON_CMD% -m pip install -r requirements_basic.txt --user
if %errorlevel% == 0 (
    echo ✅ Basic packages installed successfully
) else (
    echo ⚠️  Some packages failed to install. ClearCouncil may have limited functionality.
)

REM Install visualization packages
echo 📊 Installing visualization packages ^(optional^)...
echo matplotlib^>=3.5.0> requirements_viz.txt
echo seaborn^>=0.11.0>> requirements_viz.txt

%PYTHON_CMD% -m pip install -r requirements_viz.txt --user
if %errorlevel% == 0 (
    echo ✅ Visualization packages installed
) else (
    echo ⚠️  Visualization packages failed to install. Charts will not be available.
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 🔑 Creating .env file for API keys...
    echo # OpenAI API Key ^(required for AI features^)> .env
    echo # Get your key from: https://platform.openai.com/api-keys>> .env
    echo # OPENAI_API_KEY=your_api_key_here>> .env
    echo.>> .env
    echo # Add other API keys here as needed>> .env
    echo ✅ Created .env file
    echo    📝 Note: You'll need to add your OpenAI API key to use AI features
) else (
    echo ✅ .env file already exists
)

REM Create data directories
echo 📁 Creating data directories...
mkdir data\PDFs 2>nul
mkdir data\transcripts 2>nul
mkdir data\faiss_indexes 2>nul
mkdir data\results 2>nul
mkdir data\results\charts 2>nul
echo ✅ Data directories created

REM Test basic functionality
echo 🧪 Testing basic functionality...
%PYTHON_CMD% clearcouncil.py list-councils >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ ClearCouncil is working!
) else (
    echo ⚠️  Basic test failed. Some features may not work.
)

REM Cleanup
del requirements_basic.txt 2>nul
del requirements_viz.txt 2>nul

echo.
echo 🎉 Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. If you want AI features, add your OpenAI API key to the .env file
echo 2. Try running: %PYTHON_CMD% clearcouncil.py list-councils
echo 3. See README.md for usage examples
echo.
echo For help: %PYTHON_CMD% clearcouncil.py --help
echo.
pause