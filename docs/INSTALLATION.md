# TenderIntel Installation Guide

**Version:** 1.0.0  
**Last Updated:** October 22, 2025  
**Platform Support:** Linux, macOS, Windows (Native + WSL2), Docker

## **📋 Prerequisites**

### **System Requirements:**
- **Python:** 3.8 or higher (3.11 recommended)
- **Memory:** Minimum 4GB RAM (8GB recommended for scraping)
- **Disk Space:** 1GB for application + database + dependencies
- **OS:** Linux, macOS, Windows 10/11, or Docker

### **Required Software:**
- **Python 3.8+** with pip (automatically managed on Windows)
- **Git** (for cloning repository)
- **SQLite 3.x** (usually pre-installed, or bundled with Python)

### **Optional Software:**
- **Docker & Docker Compose** (recommended for production)
- **Tesseract OCR** (for CAPTCHA solving in scraping)
- **Google Chrome** (for web scraping automation)
- **AWS CLI** (for S3 document storage)
- **Chocolatey** (Windows package manager - auto-installed)

---

## **🚀 Quick Installation (5 minutes)**

### **Method 1: Basic Installation**

```bash
# Clone the repository
git clone https://github.com/tenderintel/tenderintel.git
cd TenderIntel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install TenderIntel
pip install -e .

# Initialize project
python scripts/setup/initialize_project.py

# Start API server
python -m tenderintel.api.server
```

**Verification:**
- API available at: `http://localhost:8002`
- Test search: `curl "http://localhost:8002/search?q=lan"`
- API docs: `http://localhost:8002/docs`

---

## **🔧 Development Installation (Complete Setup)**

### **Method 2: Development with All Features**

```bash
# Clone repository
git clone https://github.com/tenderintel/tenderintel.git
cd TenderIntel

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev,tenderx,opensearch]"

# Set up pre-commit hooks
pre-commit install

# Initialize project
make setup

# Run tests to verify
pytest

# Start development server
make run
```

**What This Installs:**
- Core dependencies: FastAPI, SQLite, Pydantic, pandas
- Development tools: pytest, black, flake8, mypy
- TenderX integration: Selenium, Tesseract, OpenCV, boto3
- OpenSearch support: opensearch-py (optional)

---

## **🐳 Docker Installation (Recommended for Production)**

### **Method 3: Docker Deployment (Cross-Platform)**

#### **Prerequisites for Docker:**
```bash
# Install Docker Desktop
# Windows/macOS: Download from docker.com
# Ubuntu: sudo apt-get install docker.io docker-compose
```

#### **Docker Installation:**
```bash
# Clone repository
git clone https://github.com/tenderintel/tenderintel.git
cd TenderIntel

# Build and start all services
docker-compose up --build -d

# Verify deployment
curl http://localhost:8002/health
curl http://localhost:8080/
```

#### **Docker Services Overview:**
- **API Server:** Port 8002 (FastAPI backend with all dependencies)
- **Frontend:** Port 8080 (Nginx-served web interface)  
- **Database:** SQLite (auto-initialized with sample data)
- **Networking:** Internal container networking

#### **Docker Commands:**
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build -d

# Clean up everything
docker-compose down -v --rmi all
```

#### **Windows Docker Setup:**
```powershell
# Windows PowerShell (run as Administrator)
# 1. Install Docker Desktop from docker.com
# 2. Enable WSL2 integration
# 3. Clone and run:
git clone https://github.com/tenderintel/tenderintel.git
cd TenderIntel
docker-compose up --build -d
```

---

## **📦 Installation Options Explained**

### **Core Installation:**
```bash
pip install -e .
```
**Includes:** FastAPI, SQLite FTS5, synonym engine, basic search

### **With TenderX Scraping:**
```bash
pip install -e ".[tenderx]"
```
**Adds:** Selenium, Tesseract OCR, CAPTCHA solving, document download

### **With OpenSearch:**
```bash
pip install -e ".[opensearch]"
```
**Adds:** OpenSearch client for production scaling (100K+ records)

### **Complete Development:**
```bash
pip install -e ".[dev,tenderx,opensearch]"
```
**Includes:** Everything + testing tools + code quality tools

---

## **⚙️ Configuration**

### **Environment Variables:**
```bash
# Database Configuration
export TENDERINTEL_DB_PATH="./data/tenders.db"

# API Server Configuration  
export TENDERINTEL_API_PORT="8002"
export TENDERINTEL_API_HOST="0.0.0.0"

# AWS S3 for Document Storage (Optional)
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="ap-south-1"

# Supabase for Enhanced Features (Optional)
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

### **Configuration Files:**
- `config/synonyms.yaml` - Keyword expansion dictionary (266+ keywords)
- `config/config.yaml` - Main application configuration
- `config/dev/config.json` - Development settings
- `config/prod/` - Production configuration templates

---

## **🗄️ Database Setup**

### **Automatic Setup (Recommended):**
```bash
# Run initialization script
python scripts/setup/initialize_project.py
```

**This will:**
- Create SQLite database with FTS5 schema
- Load 3 sample tenders for testing
- Set up reference tables
- Configure FTS5 with Porter stemming

### **Manual Database Setup:**
```bash
# Create database directory
mkdir -p data

# Run schema creation
sqlite3 data/tenders.db < config/schemas/tender_schema.sql

# Verify FTS5 support
sqlite3 data/tenders.db "SELECT fts5_version();"
```

### **Import Existing Data:**
```bash
# If you have existing tender data
python scripts/data/import_tenders.py --source your_data.json --format json
```

---

## **✅ Verification & Testing**

### **Automated Verification (Recommended):**
```bash
# Run comprehensive verification script
python scripts/verify_installation.py

# This checks:
# - Python version compatibility
# - All dependencies installed
# - Database setup and integrity
# - API server functionality
# - Core feature functionality
```

### **Manual Verification Steps:**

#### **1. Basic Installation Check:**
```bash
# Check TenderIntel is installed
python -c "import tenderintel; print(tenderintel.__version__)"
# Expected output: 1.0.0

# Verify core dependencies
python -c "import fastapi, sqlite3, yaml; print('✅ Dependencies OK')"
```

#### **2. Database Verification:**
```bash
# Check database exists and has data
sqlite3 data/tenders.db "SELECT COUNT(*) FROM tenders;"
# Expected: Non-zero count (3+ sample records)

# Test FTS5 full-text search
sqlite3 data/tenders.db "SELECT title FROM tenders WHERE tenders MATCH 'network' LIMIT 3;"
# Expected: Search results with network-related tenders

# Verify FTS5 functionality
sqlite3 data/tenders.db "SELECT fts5_version();"
# Expected: FTS5 version number
```

#### **3. API Server Testing:**
```bash
# Start server (Terminal 1)
python -m uvicorn src.tenderintel.api.server:app --port 8002

# Test endpoints (Terminal 2)
curl http://localhost:8002/health
# Expected: {"status":"healthy",...}

curl "http://localhost:8002/search?q=lan"
# Expected: Search results with networking tenders

curl "http://localhost:8002/expand?q=api" 
# Expected: Keyword expansions

# Test all 18 endpoints
curl http://localhost:8002/stats
curl http://localhost:8002/filter-options
curl http://localhost:8002/competitive-intelligence/summary
```

#### **4. Frontend Testing:**
```bash
# Start frontend server (Terminal 3)
cd frontend && python -m http.server 8080

# Open in browser
# Windows: start http://localhost:8080
# macOS: open http://localhost:8080  
# Linux: xdg-open http://localhost:8080

# Verify:
# - Page loads without errors
# - Navigation works (Dashboard, Search, Intelligence, Analytics)
# - Search functionality works
# - No JavaScript errors in console (F12)
```

#### **5. Docker Verification:**
```bash
# If using Docker, verify all services
docker-compose ps
# Expected: All services "Up" status

curl http://localhost:8002/health
curl http://localhost:8080/
# Both should return 200 OK
```

#### **6. Full Test Suite:**
```bash
# Run comprehensive tests (if development installation)
pytest
# Expected: All tests pass

# Run with coverage report
pytest --cov=src/tenderintel --cov-report=html

# View coverage report
# Windows: start htmlcov\index.html
# macOS: open htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

---

## **🔥 Common Installation Issues**

### **Issue 1: Python Version**
```bash
# Error: Python 3.7 not supported
# Solution: Install Python 3.8+
python --version  # Check current version
# Install Python 3.11 from python.org
```

### **Issue 2: SQLite FTS5 Not Available**
```bash
# Error: no such module: fts5
# Solution: Reinstall Python with full SQLite support
# On Ubuntu/Debian:
sudo apt-get install libsqlite3-dev
# Rebuild Python from source
```

### **Issue 3: Tesseract Not Found**
```bash
# Error: pytesseract.pytesseract.TesseractNotFoundError
# Solution: Install Tesseract OCR
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### **Issue 4: Port Already in Use**
```bash
# Error: Address already in use: 8002
# Solution: Change port or kill existing process
# Find process: lsof -i :8002
# Kill process: kill -9 <PID>
# Or use different port: TENDERINTEL_API_PORT=8003 make run
```

### **Issue 5: Permission Denied**
```bash
# Error: Permission denied: data/tenders.db
# Solution: Fix permissions
chmod 755 data/
chmod 644 data/tenders.db
```

### **Windows-Specific Issues:**

#### **Issue W1: Python Not in PATH**
```cmd
# Error: 'python' is not recognized as internal or external command
# Solution 1: Reinstall Python with PATH option
# Download Python from python.org, check "Add Python to PATH"

# Solution 2: Add Python manually to PATH
# 1. Find Python installation (usually C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\)
# 2. Add to PATH: Control Panel > System > Advanced > Environment Variables
# 3. Add both: C:\...\Python311\ and C:\...\Python311\Scripts\
```

#### **Issue W2: Execution Policy Restricted**
```powershell
# Error: cannot be loaded because running scripts is disabled
# Solution: Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Issue W3: Chocolatey Installation Fails**
```powershell
# Error: Chocolatey installation blocked
# Solution 1: Run PowerShell as Administrator
# Solution 2: Manual Chocolatey install
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
```

#### **Issue W4: Tesseract PATH Issues**
```cmd
# Error: TesseractNotFoundError even after installation
# Solution: Manually add to PATH
# 1. Find Tesseract: Usually C:\Program Files\Tesseract-OCR\
# 2. Add to PATH environment variable  
# 3. Restart Command Prompt/PowerShell
# 4. Test: tesseract --version
```

#### **Issue W5: Chrome Driver Issues**
```cmd
# Error: WebDriver Chrome issues
# Solution: Manual ChromeDriver setup
# 1. Download ChromeDriver from https://chromedriver.chromium.org/
# 2. Extract to C:\Windows\ or add to PATH
# 3. Verify Chrome version matches ChromeDriver version
```

#### **Issue W6: Virtual Environment Activation**
```cmd
# Error: venv activation not working
# Solution: Use correct activation script
# Command Prompt: venv\Scripts\activate.bat
# PowerShell: venv\Scripts\Activate.ps1
```

#### **Issue W7: Port 8080 Blocked (Windows Firewall)**
```cmd
# Error: Frontend not accessible on port 8080
# Solution: Allow through Windows Firewall
# 1. Windows Security > Firewall > Allow an app
# 2. Add Python.exe to allowed programs
# 3. Or disable Windows Firewall temporarily for testing
```

#### **Issue W8: Microsoft Visual C++ Build Tools**
```cmd
# Error: Microsoft Visual C++ 14.0 is required
# Solution: Install build tools
# Download Visual Studio Build Tools from Microsoft
# Or install via Chocolatey: choco install visualstudio2019buildtools
```

---

## **🌍 Platform-Specific Instructions**

### **macOS:**
```bash
# Install Homebrew dependencies
brew install python@3.11 tesseract

# Install TenderIntel
pip3 install -e ".[dev,tenderx]"
```

### **Ubuntu/Debian:**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3.11 python3-pip python3-venv tesseract-ocr

# Install TenderIntel
pip install -e ".[dev,tenderx]"
```

### **Windows (Multiple Options):**

#### **Option A: Automated PowerShell Setup (RECOMMENDED)**
```powershell
# Run PowerShell as Administrator
# Clone repository
git clone https://github.com/tenderintel/tenderintel.git
cd TenderIntel

# Run automated setup script
.\scripts\setup\setup_windows.ps1

# Optional: For development mode
.\scripts\setup\setup_windows.ps1 -DevMode
```

#### **Option B: Command Prompt Setup**
```cmd
# Clone repository  
git clone https://github.com/tenderintel/tenderintel.git
cd TenderIntel

# Run automated batch script
scripts\setup\setup_windows.bat
```

#### **Option C: Manual Windows Setup**
```cmd
# 1. Install Python 3.11 from python.org (check "Add to PATH")
# 2. Install Git from git-scm.com
# 3. Install Tesseract OCR from GitHub releases
# 4. Install Google Chrome (for scraping)

# Clone and setup
git clone https://github.com/tenderintel/tenderintel.git
cd TenderIntel
python -m venv venv
venv\Scripts\activate
pip install -e ".[tenderx]"
python scripts\setup\initialize_project.py
```

#### **Option D: WSL2 (Linux-like experience)**
```bash
# Install WSL2 with Ubuntu (run in PowerShell as Admin)
wsl --install -d Ubuntu-22.04

# Inside WSL2, follow Ubuntu instructions above
sudo apt-get update && sudo apt-get install python3.11 python3-pip tesseract-ocr
git clone https://github.com/tenderintel/tenderintel.git
cd TenderIntel && pip install -e ".[dev,tenderx]"
```

---

## **🚀 Production Deployment**

### **Option 1: Systemd Service (Linux)**

Create `/etc/systemd/system/tenderintel.service`:
```ini
[Unit]
Description=TenderIntel API Server
After=network.target

[Service]
Type=simple
User=tenderintel
WorkingDirectory=/opt/tenderintel
Environment="PATH=/opt/tenderintel/venv/bin"
ExecStart=/opt/tenderintel/venv/bin/gunicorn tenderintel.api.server:app --workers 4 --bind 0.0.0.0:8002
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable tenderintel
sudo systemctl start tenderintel
sudo systemctl status tenderintel
```

### **Option 2: Docker Production**

```bash
# Build production image
docker build -f docker/Dockerfile.prod -t tenderintel:1.0.0 .

# Run with environment variables
docker run -d \
  -p 8002:8002 \
  -v /path/to/data:/app/data \
  -e TENDERINTEL_DB_PATH=/app/data/tenders.db \
  --name tenderintel \
  tenderintel:1.0.0
```

### **Option 3: Cloud Deployment (AWS/GCP/Azure)**

See `docs/DEPLOYMENT.md` for detailed cloud deployment instructions.

---

## **🎯 Quick Start After Installation**

### **Verify Everything Works:**
```bash
# Run automated verification (all platforms)
python scripts/verify_installation.py
# Expected: All checks pass

# Or manually test the core functionality
curl "http://localhost:8002/health"        # System health
curl "http://localhost:8002/search?q=cloud" # Search test
curl "http://localhost:8002/expand?q=lan"   # Keyword expansion
```

### **Start Using TenderIntel:**
```bash
# 1. Start both services:
# Terminal 1: python -m uvicorn src.tenderintel.api.server:app --port 8002
# Terminal 2: cd frontend && python -m http.server 8080

# 2. Open in browser: http://localhost:8080
# 3. Navigate to Search page
# 4. Try searching for: "cloud", "api", "security", "network"
# 5. Test the 8 filter categories
# 6. Try exporting results to CSV
```

---

## **📚 Next Steps After Installation**

1. **Verify Installation:** `python scripts/verify_installation.py`
2. **Read User Manual:** `docs/USER_MANUAL.md`  
3. **Explore API:** Visit `http://localhost:8002/docs` for interactive documentation
4. **Try Examples:** Check `examples/` directory for usage patterns
5. **Test Frontend:** Open `http://localhost:8080` and try the Advanced Search
6. **Join Community:** GitHub Discussions for questions and feedback

---

## **🆘 Getting Help**

### **Documentation:**
- **Full Installation Guide:** This file (`docs/INSTALLATION.md`)
- **User Manual:** `docs/USER_MANUAL.md` - How to use TenderIntel
- **API Reference:** `docs/API_REFERENCE.md` - All 18 endpoints
- **Developer Guide:** `docs/DEVELOPER_GUIDE.md` - Architecture & customization

### **Community & Support:**
- **GitHub Issues:** Report bugs and request features
- **GitHub Discussions:** Ask questions and get help
- **Email:** team@tenderintel.org for direct support

### **Quick Links:**
- 🔗 **Frontend:** http://localhost:8080 (after setup)
- 🔗 **API:** http://localhost:8002 (after setup)  
- 🔗 **API Docs:** http://localhost:8002/docs (interactive documentation)
- 🔗 **Health Check:** http://localhost:8002/health (system status)

**Installation successful?** 

**🚀 Quick Test:** `curl "http://localhost:8002/search?q=cloud"`  
**🌐 Open Frontend:** http://localhost:8080  
**📖 API Docs:** http://localhost:8002/docs
