# TenderIntel Windows Installation Script
# PowerShell script for complete Windows setup

param(
    [switch]$SkipPython,
    [switch]$SkipTesseract,
    [switch]$SkipChrome,
    [switch]$DevMode
)

Write-Host "🎯 TenderIntel Windows Installation Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if running as Administrator
function Test-IsAdmin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to install Chocolatey if not present
function Install-Chocolatey {
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Host "📦 Installing Chocolatey package manager..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        Write-Host "✅ Chocolatey installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✅ Chocolatey already installed" -ForegroundColor Green
    }
}

# Function to check Python installation
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
            Write-Host "✅ Python already installed: $pythonVersion" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️  Python version too old: $pythonVersion" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
        return $false
    }
}

# Function to install Python
function Install-Python {
    if (!$SkipPython -and !(Test-Python)) {
        Write-Host "🐍 Installing Python 3.11..." -ForegroundColor Yellow
        choco install python311 -y
        refreshenv
        Write-Host "✅ Python installed successfully" -ForegroundColor Green
    }
}

# Function to install Tesseract OCR
function Install-Tesseract {
    if (!$SkipTesseract) {
        Write-Host "🔍 Installing Tesseract OCR..." -ForegroundColor Yellow
        choco install tesseract -y
        
        # Add Tesseract to PATH if not already there
        $tesseractPath = "C:\Program Files\Tesseract-OCR"
        if (Test-Path $tesseractPath) {
            $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
            if ($currentPath -notlike "*$tesseractPath*") {
                [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$tesseractPath", "Machine")
                Write-Host "✅ Added Tesseract to PATH" -ForegroundColor Green
            }
        }
        Write-Host "✅ Tesseract OCR installed successfully" -ForegroundColor Green
    }
}

# Function to install Chrome (for Selenium scraping)
function Install-Chrome {
    if (!$SkipChrome) {
        Write-Host "🌐 Installing Google Chrome..." -ForegroundColor Yellow
        choco install googlechrome -y
        Write-Host "✅ Google Chrome installed successfully" -ForegroundColor Green
    }
}

# Function to install Git
function Install-Git {
    if (!(Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "📚 Installing Git..." -ForegroundColor Yellow
        choco install git -y
        refreshenv
        Write-Host "✅ Git installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✅ Git already installed" -ForegroundColor Green
    }
}

# Function to create virtual environment
function Create-VirtualEnv {
    Write-Host "🏗️  Creating virtual environment..." -ForegroundColor Yellow
    
    if (Test-Path "venv") {
        Write-Host "⚠️  Virtual environment already exists, removing old one..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force venv
    }
    
    python -m venv venv
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    Write-Host "✅ Virtual environment created and activated" -ForegroundColor Green
}

# Function to install TenderIntel dependencies
function Install-Dependencies {
    Write-Host "📦 Installing TenderIntel dependencies..." -ForegroundColor Yellow
    
    # Upgrade pip first
    python -m pip install --upgrade pip setuptools wheel
    
    if ($DevMode) {
        Write-Host "🔧 Installing development dependencies..." -ForegroundColor Yellow
        python -m pip install -e ".[dev,tenderx,opensearch]"
    } else {
        Write-Host "🚀 Installing production dependencies..." -ForegroundColor Yellow
        python -m pip install -e ".[tenderx]"
    }
    
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
}

# Function to initialize project
function Initialize-Project {
    Write-Host "🔧 Initializing TenderIntel project..." -ForegroundColor Yellow
    
    python scripts\setup\initialize_project.py
    
    Write-Host "✅ Project initialized successfully" -ForegroundColor Green
}

# Function to verify installation
function Test-Installation {
    Write-Host "🧪 Verifying installation..." -ForegroundColor Yellow
    
    # Test Python import
    try {
        python -c "import tenderintel; print(f'TenderIntel v{tenderintel.__version__}')"
        Write-Host "✅ TenderIntel import successful" -ForegroundColor Green
    } catch {
        Write-Host "❌ TenderIntel import failed" -ForegroundColor Red
        return $false
    }
    
    # Test database
    if (Test-Path "data\tenders.db") {
        $recordCount = python -c "import sqlite3; conn = sqlite3.connect('data/tenders.db'); print(conn.execute('SELECT COUNT(*) FROM tenders').fetchone()[0]); conn.close()"
        Write-Host "✅ Database: $recordCount records" -ForegroundColor Green
    } else {
        Write-Host "❌ Database not found" -ForegroundColor Red
        return $false
    }
    
    # Test key dependencies
    $dependencies = @("fastapi", "sqlite3", "requests", "selenium", "pytesseract")
    foreach ($dep in $dependencies) {
        try {
            python -c "import $dep; print('$dep: OK')"
            Write-Host "✅ $dep" -ForegroundColor Green
        } catch {
            Write-Host "❌ $dep missing" -ForegroundColor Red
        }
    }
    
    return $true
}

# Function to start services
function Start-Services {
    Write-Host "🚀 Starting TenderIntel services..." -ForegroundColor Yellow
    
    # Start API server in background
    Write-Host "🔧 Starting API server on port 8002..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "-m", "uvicorn", "src.tenderintel.api.server:app", "--host", "0.0.0.0", "--port", "8002", "--reload" -WindowStyle Minimized
    
    # Wait for server to start
    Start-Sleep -Seconds 3
    
    # Start frontend server
    Write-Host "🌐 Starting frontend server on port 8080..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "-m", "http.server", "8080" -WorkingDirectory "frontend" -WindowStyle Minimized
    
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
    Write-Host "🔗 API: http://localhost:8002" -ForegroundColor Cyan
    Write-Host "🌐 Frontend: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "📚 API Docs: http://localhost:8002/docs" -ForegroundColor Cyan
}

# Main installation process
function Main {
    Write-Host "🔍 System Requirements Check" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    
    # Check if running as Administrator
    if (Test-IsAdmin) {
        Write-Host "✅ Running as Administrator" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Not running as Administrator - some features may require elevation" -ForegroundColor Yellow
    }
    
    # Install Chocolatey
    Install-Chocolatey
    
    # Install system dependencies
    Write-Host ""
    Write-Host "📦 Installing System Dependencies" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Install-Git
    Install-Python
    Install-Tesseract
    Install-Chrome
    
    # Set up Python environment
    Write-Host ""
    Write-Host "🐍 Python Environment Setup" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor Cyan
    Create-VirtualEnv
    Install-Dependencies
    Initialize-Project
    
    # Verify installation
    Write-Host ""
    Write-Host "✅ Installation Verification" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    
    if (Test-Installation) {
        Write-Host ""
        Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
        Write-Host "=======================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Next Steps:" -ForegroundColor Cyan
        Write-Host "  1. Activate virtual environment: .\venv\Scripts\Activate.ps1"
        Write-Host "  2. Start API server: python -m uvicorn src.tenderintel.api.server:app --port 8002"
        Write-Host "  3. Start frontend: cd frontend && python -m http.server 8080"
        Write-Host "  4. Test search: curl http://localhost:8002/search?q=cloud"
        Write-Host ""
        Write-Host "🔧 Development Commands:" -ForegroundColor Cyan
        Write-Host "  Run tests: pytest"
        Write-Host "  Format code: black src/ tests/"
        Write-Host "  Check lint: flake8 src/ tests/"
        Write-Host ""
        Write-Host "📚 Documentation:" -ForegroundColor Cyan
        Write-Host "  User Manual: docs\USER_MANUAL.md"
        Write-Host "  API Reference: docs\API_REFERENCE.md"
        Write-Host "  Developer Guide: docs\DEVELOPER_GUIDE.md"
        
        # Offer to start services
        $startServices = Read-Host "`n🚀 Start TenderIntel services now? (y/N)"
        if ($startServices -eq "y" -or $startServices -eq "Y") {
            Start-Services
        }
        
    } else {
        Write-Host ""
        Write-Host "❌ Installation verification failed!" -ForegroundColor Red
        Write-Host "Please check the error messages above and retry." -ForegroundColor Red
        exit 1
    }
}

# Handle script parameters and start
Write-Host "Parameters:" -ForegroundColor Gray
Write-Host "  SkipPython: $SkipPython" -ForegroundColor Gray
Write-Host "  SkipTesseract: $SkipTesseract" -ForegroundColor Gray
Write-Host "  SkipChrome: $SkipChrome" -ForegroundColor Gray
Write-Host "  DevMode: $DevMode" -ForegroundColor Gray
Write-Host ""

# Run main installation
Main

Write-Host ""
Write-Host "🎊 TenderIntel Windows setup complete!" -ForegroundColor Green
Write-Host "Thank you for using TenderIntel!" -ForegroundColor Cyan
