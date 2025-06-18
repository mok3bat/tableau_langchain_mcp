@echo off
REM Tableau LangChain MCP Server - Quick Start Script for Windows

echo 🚀 Tableau LangChain MCP Server - Quick Start
echo =============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not found
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Found Python %PYTHON_VERSION%

REM Check virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  You're not in a virtual environment. It's recommended to create one:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo.
    set /p CONTINUE="Continue anyway? (y/N): "
    if /i not "%CONTINUE%"=="y" (
        echo Exiting. Please set up a virtual environment first.
        pause
        exit /b 1
    )
) else (
    echo ✓ Virtual environment active: %VIRTUAL_ENV%
)

REM Install dependencies
echo.
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully

REM Install package in development mode
echo.
echo 🔧 Installing package in development mode...
python -m pip install -e .

if errorlevel 1 (
    echo ❌ Failed to install package
    pause
    exit /b 1
)

echo ✓ Package installed successfully

REM Set up environment file
echo.
echo ⚙️  Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo ✓ Created .env file from template
    echo 📝 Please edit .env with your Tableau and OpenAI credentials
) else (
    echo ℹ .env file already exists
)

REM Run tests
echo.
echo 🧪 Running tests...
python simple_test.py

if errorlevel 1 (
    echo.
    echo ⚠️  Setup completed with some issues. Please check the test output above.
    pause
    exit /b 1
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file with your credentials:
echo    - Tableau Server details and Connected App credentials
echo    - OpenAI API key
echo    - Datasource LUID
echo.
echo 2. Test your configuration:
echo    python simple_test.py
echo.
echo 3. Add to your MCP client configuration:
echo    See README.md for configuration examples
echo.
echo 4. Start using your MCP server!
echo.
pause
