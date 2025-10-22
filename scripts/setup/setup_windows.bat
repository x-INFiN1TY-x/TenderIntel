@echo off
REM TenderIntel Windows Installation Script (Batch)
REM For users who prefer Command Prompt over PowerShell

echo.
echo ================================================================
echo   TenderIntel Windows Installation Script (Command Prompt)
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
) else (
    echo ✅ Python found
    python --version
)

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git not found. Please install Git from https://git-scm.com
    pause
    exit /b 1
) else (
    echo ✅ Git found
)

echo.
echo 📦 Setting up TenderIntel...
echo ================================

REM Create virtual environment
echo 🏗️  Creating virtual environment...
if exist venv (
    echo ⚠️  Removing existing virtual environment...
    rmdir /s /q venv
)
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install TenderIntel
echo 📦 Installing TenderIntel with dependencies...
python -m pip install -e ".[tenderx]"

REM Initialize project
echo 🔧 Initializing project...
python scripts\setup\initialize_project.py

echo.
echo ✅ Installation completed!
echo ========================

REM Verify installation
echo 🧪 Verifying installation...
python -c "import tenderintel; print('TenderIntel version:', tenderintel.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ Installation verification failed
    pause
    exit /b 1
)

REM Check database
if exist data\tenders.db (
    echo ✅ Database created successfully
) else (
    echo ❌ Database not found
)

echo.
echo 🎉 TenderIntel is ready to use!
echo ================================
echo.
echo 📋 Quick Start Commands:
echo   1. Start API server:
echo      python -m uvicorn src.tenderintel.api.server:app --port 8002
echo.
echo   2. Start frontend (in new Command Prompt):
echo      cd frontend
echo      python -m http.server 8080
echo.
echo   3. Open in browser:
echo      API: http://localhost:8002
echo      Frontend: http://localhost:8080
echo      Docs: http://localhost:8002/docs
echo.
echo   4. Test search:
echo      curl "http://localhost:8002/search?q=cloud"
echo.
echo 📚 Documentation:
echo   docs\INSTALLATION.md - Complete installation guide
echo   docs\USER_MANUAL.md - User guide
echo   docs\API_REFERENCE.md - API documentation
echo.

REM Ask if user wants to start services
set /p startServices="🚀 Start TenderIntel services now? (y/N): "
if /i "%startServices%"=="y" (
    echo.
    echo 🚀 Starting services...
    
    REM Start API server in new window
    start "TenderIntel API" cmd /k "venv\Scripts\activate && python -m uvicorn src.tenderintel.api.server:app --host 0.0.0.0 --port 8002 --reload"
    
    REM Wait a moment
    timeout /t 3 /nobreak >nul
    
    REM Start frontend in new window
    start "TenderIntel Frontend" cmd /k "cd frontend && python -m http.server 8080"
    
    echo ✅ Services started!
    echo 🔗 API: http://localhost:8002
    echo 🌐 Frontend: http://localhost:8080
    echo.
    echo Press any key to open browser...
    pause >nul
    start http://localhost:8080
) else (
    echo.
    echo 💡 To start services later, run:
    echo    venv\Scripts\activate
    echo    python -m uvicorn src.tenderintel.api.server:app --port 8002
)

echo.
echo 🎊 Setup complete! Thank you for using TenderIntel!
echo.
pause
