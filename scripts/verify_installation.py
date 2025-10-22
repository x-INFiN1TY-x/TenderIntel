#!/usr/bin/env python3
"""
TenderIntel Installation Verification Script
===========================================

Comprehensive verification of TenderIntel installation across all platforms.
Checks dependencies, database, API functionality, and system requirements.
"""

import sys
import os
import subprocess
import sqlite3
import platform
import importlib
import requests
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any

class Colors:
    """ANSI color codes for cross-platform colored output"""
    if platform.system() == "Windows":
        # Try to enable ANSI colors on Windows
        try:
            import colorama
            colorama.init()
        except ImportError:
            pass
    
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
    print("=" * len(title))

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def check_python_version() -> bool:
    """Check Python version compatibility"""
    print_section("Python Version Check")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print_success(f"Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} is too old. Requires Python 3.8+")
        return False

def check_dependencies() -> bool:
    """Check if all required dependencies are installed"""
    print_section("Dependency Check")
    
    required_deps = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("sqlite3", "SQLite database (built-in)"),
        ("requests", "HTTP client library"),
        ("pandas", "Data analysis library"),
        ("pydantic", "Data validation library"),
    ]
    
    optional_deps = [
        ("selenium", "Web scraping automation"),
        ("pytesseract", "OCR for CAPTCHA solving"),
        ("boto3", "AWS SDK for S3 storage"),
        ("opensearch_py", "OpenSearch client (optional)"),
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required dependencies
    for module, description in required_deps:
        try:
            importlib.import_module(module)
            print_success(f"{module}: {description}")
        except ImportError:
            missing_required.append((module, description))
            print_error(f"{module}: {description} - MISSING")
    
    # Check optional dependencies
    for module, description in optional_deps:
        try:
            importlib.import_module(module)
            print_success(f"{module}: {description}")
        except ImportError:
            missing_optional.append((module, description))
            print_warning(f"{module}: {description} - OPTIONAL")
    
    if missing_required:
        print_error(f"\n{len(missing_required)} required dependencies missing!")
        print("Install with: pip install -e \".[tenderx]\"")
        return False
    
    if missing_optional:
        print_warning(f"\n{len(missing_optional)} optional dependencies missing")
        print("For full functionality: pip install -e \".[dev,tenderx,opensearch]\"")
    
    return True

def check_system_tools() -> bool:
    """Check system-level tools"""
    print_section("System Tools Check")
    
    tools = [
        ("git", "Git version control"),
        ("curl", "HTTP testing tool"),
    ]
    
    missing = []
    
    for tool, description in tools:
        try:
            result = subprocess.run([tool, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print_success(f"{tool}: {description} - {version}")
            else:
                missing.append((tool, description))
                print_error(f"{tool}: {description} - MISSING")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing.append((tool, description))
            print_error(f"{tool}: {description} - MISSING")
    
    # Check Tesseract (optional)
    try:
        result = subprocess.run(["tesseract", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_success(f"tesseract: OCR engine - {version}")
        else:
            print_warning("tesseract: OCR engine - OPTIONAL (needed for CAPTCHA)")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_warning("tesseract: OCR engine - OPTIONAL (for CAPTCHA solving)")
    
    return len(missing) == 0

def check_database() -> bool:
    """Check database setup and integrity"""
    print_section("Database Verification")
    
    db_paths = ["data/tenders.db", "engine/tenders.db"]
    db_found = False
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print_success(f"Database found: {db_path}")
            db_found = True
            
            try:
                # Test database connection
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if tenders table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tenders'")
                if cursor.fetchone():
                    print_success("Tenders table exists")
                    
                    # Check record count
                    cursor.execute("SELECT COUNT(*) FROM tenders")
                    count = cursor.fetchone()[0]
                    print_success(f"Records in database: {count}")
                    
                    # Test FTS5 functionality
                    try:
                        cursor.execute("SELECT fts5_version()")
                        fts5_version = cursor.fetchone()[0]
                        print_success(f"FTS5 version: {fts5_version}")
                    except sqlite3.OperationalError:
                        # Try alternative FTS5 check for virtual tables
                        try:
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tenders' AND sql LIKE '%fts5%'")
                            if cursor.fetchone():
                                print_success("FTS5 virtual table detected and working")
                            else:
                                print_error("FTS5 not available - search functionality may be limited")
                                return False
                        except sqlite3.OperationalError:
                            print_error("FTS5 not available - search functionality may be limited")
                            return False
                    
                else:
                    print_error("Tenders table not found")
                    return False
                
                conn.close()
                break
                
            except Exception as e:
                print_error(f"Database error: {e}")
                return False
    
    if not db_found:
        print_error("No database found. Run: python scripts/setup/initialize_project.py")
        return False
    
    return True

def check_tenderintel_import() -> bool:
    """Check if TenderIntel can be imported and basic functionality works"""
    print_section("TenderIntel Package Check")
    
    try:
        import tenderintel
        print_success(f"TenderIntel version: {tenderintel.__version__}")
        
        # Test core modules
        from tenderintel.search.synonym_manager import SynonymManager
        from tenderintel.core.database_manager import DatabaseManager
        from tenderintel.api import server
        
        print_success("Core modules importable")
        
        # Test synonym manager
        try:
            sm = SynonymManager()
            expansions = sm.expand_keyword("lan")
            if expansions and len(expansions.get('expanded_phrases', [])) > 0:
                print_success(f"Synonym expansion working: 'lan' → {len(expansions['expanded_phrases'])} phrases")
            else:
                print_warning("Synonym expansion returned no results")
        except Exception as e:
            print_error(f"Synonym manager error: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print_error(f"TenderIntel import failed: {e}")
        print("Solution: pip install -e .")
        return False
    except Exception as e:
        print_error(f"TenderIntel functionality error: {e}")
        return False

def check_api_server() -> bool:
    """Check if API server can start and respond"""
    print_section("API Server Check")
    
    # Check if server is already running
    try:
        response = requests.get("http://localhost:8002/health", timeout=2)
        if response.status_code == 200:
            health_data = response.json()
            print_success("API server already running and healthy")
            print_info(f"Database records: {health_data.get('checks', {}).get('database', {}).get('record_count', 'Unknown')}")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print_info("Starting API server for testing...")
    
    # Start server in background for testing
    try:
        import subprocess
        import sys
        
        # Start server in background
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "src.tenderintel.api.server:app", 
            "--host", "127.0.0.1", "--port", "8002"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        for i in range(30):  # 30 second timeout
            try:
                response = requests.get("http://localhost:8002/health", timeout=1)
                if response.status_code == 200:
                    health_data = response.json()
                    print_success("API server started successfully")
                    print_success(f"Health status: {health_data.get('status', 'unknown')}")
                    
                    # Test basic search
                    try:
                        search_response = requests.get("http://localhost:8002/search?q=test&limit=1", timeout=5)
                        if search_response.status_code == 200:
                            search_data = search_response.json()
                            print_success(f"Search functionality working: {search_data.get('total_matches', 0)} results")
                        else:
                            print_warning("Search endpoint returned non-200 status")
                    except Exception as e:
                        print_warning(f"Search test failed: {e}")
                    
                    # Clean up
                    server_process.terminate()
                    server_process.wait(timeout=5)
                    return True
                    
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        # Server didn't start in time
        server_process.terminate()
        server_process.wait(timeout=5)
        print_error("API server failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print_error(f"Failed to start API server: {e}")
        return False

def generate_report(results: Dict[str, bool]) -> None:
    """Generate final verification report"""
    print_section("Installation Verification Report")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print(f"📊 Results: {passed_checks}/{total_checks} checks passed")
    print("")
    
    for check_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{status:>6}{Colors.RESET} | {check_name}")
    
    print("")
    
    if passed_checks == total_checks:
        print_success("🎉 All verification checks passed!")
        print_success("TenderIntel is ready for use!")
        print("")
        print("🚀 Quick Start:")
        print("  1. Start API: python -m uvicorn src.tenderintel.api.server:app --port 8002")
        print("  2. Start frontend: cd frontend && python -m http.server 8080")  
        print("  3. Open: http://localhost:8080")
        return True
    else:
        failed_count = total_checks - passed_checks
        print_error(f"❌ {failed_count} verification checks failed!")
        print("Please review the errors above and fix the issues.")
        return False

def main():
    """Main verification function"""
    print(f"{Colors.BOLD}🎯 TenderIntel Installation Verification{Colors.RESET}")
    print(f"{Colors.BOLD}======================================{Colors.RESET}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("")
    
    # Run all verification checks
    results = {}
    
    try:
        results["Python Version"] = check_python_version()
        results["Dependencies"] = check_dependencies()
        results["System Tools"] = check_system_tools()
        results["Database"] = check_database()
        results["TenderIntel Package"] = check_tenderintel_import()
        results["API Server"] = check_api_server()
        
    except KeyboardInterrupt:
        print("\n\n❌ Verification interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Verification failed with error: {e}")
        return False
    
    # Generate final report
    success = generate_report(results)
    
    if success:
        print("\n📚 Documentation:")
        print("  📖 User Guide: docs/USER_MANUAL.md")
        print("  🔧 API Reference: docs/API_REFERENCE.md")
        print("  👨‍💻 Developer Guide: docs/DEVELOPER_GUIDE.md")
        print("\n🤝 Community:")
        print("  🐛 Issues: https://github.com/tenderintel/tenderintel/issues")
        print("  💬 Discussions: https://github.com/tenderintel/tenderintel/discussions")
        return True
    else:
        print("\n🆘 Getting Help:")
        print("  📖 Installation Guide: docs/INSTALLATION.md")
        print("  🐛 Report Issues: https://github.com/tenderintel/tenderintel/issues")
        print("  📧 Email: team@tenderintel.org")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1)
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎊 TenderIntel verification complete!{Colors.RESET}")
    print(f"{Colors.CYAN}Ready for competitive intelligence analysis!{Colors.RESET}")
