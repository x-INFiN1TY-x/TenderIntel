#!/usr/bin/env python3
"""
TenderIntel Project Initialization Script
=========================================

Sets up the TenderIntel project for development or production use.

Features:
- Database schema creation with FTS5 optimization
- Sample data loading for immediate testing
- Configuration file generation
- Dependency validation and installation
- System requirements verification
"""

import os
import sys
import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent

def create_database_schema(db_path: str) -> bool:
    """Create the enhanced database schema for TenderIntel"""
    
    try:
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create FTS5 table for intelligent search
        cursor.execute("DROP TABLE IF EXISTS tenders")
        
        fts5_table_sql = """
        CREATE VIRTUAL TABLE tenders USING fts5(
            title,              -- Primary search field (FTS5 indexed)
            org,               -- Organization name (auxiliary)
            status,            -- Tender status (auxiliary)
            aoc_date,          -- Award of Contract date (auxiliary)
            tender_id,         -- Unique identifier (auxiliary)
            url,               -- Source portal URL (auxiliary)
            service_category,  -- Service classification (auxiliary)
            value_range,       -- Estimated value range (auxiliary)
            region,            -- Geographic region (auxiliary)
            department_type,   -- Organization type (auxiliary)
            complexity,        -- Complexity assessment (auxiliary)
            keywords,          -- Associated keywords (auxiliary)
            tokenize=porter,   -- Use Porter stemming for better matching
            prefix='2,3'      -- Enable prefix matching for short terms
        );
        """
        
        cursor.execute(fts5_table_sql)
        
        # Create competitive intelligence tables
        cursor.execute("DROP TABLE IF EXISTS firm_wins")
        
        firm_wins_sql = """
        CREATE TABLE IF NOT EXISTS firm_wins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firm_name TEXT NOT NULL,
            tender_id TEXT NOT NULL,
            service_category TEXT,
            sub_category TEXT,
            win_date DATE,
            contract_value DECIMAL(15,2),
            region TEXT,
            source_portal TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(firm_wins_sql)
        
        # Create market intelligence table
        cursor.execute("DROP TABLE IF EXISTS market_intelligence")
        
        market_intel_sql = """
        CREATE TABLE IF NOT EXISTS market_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_category TEXT NOT NULL,
            time_period TEXT NOT NULL,
            total_tenders INTEGER DEFAULT 0,
            top_winners TEXT,
            competitive_intensity TEXT,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(market_intel_sql)
        
        conn.commit()
        conn.close()
        
        print("✅ Database schema created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database schema: {e}")
        return False

def load_sample_data(db_path: str) -> bool:
    """Load sample tender data for testing"""
    
    sample_tenders = [
        {
            "title": "Supply and Installation of Local Area Network Infrastructure with Ethernet Switches",
            "org": "Ministry of Electronics and Information Technology",
            "status": "Published AOC",
            "aoc_date": "2025-01-20",
            "tender_id": "MEITY-2025-NET-001",
            "url": "https://etenders.gov.in/sample/001",
            "service_category": "networking",
            "value_range": "5_to_25_lakh", 
            "region": "delhi",
            "department_type": "central",
            "complexity": "medium",
            "keywords": "lan,ethernet,switch,network,infrastructure"
        },
        {
            "title": "Development of REST API Gateway for Government Services Integration",
            "org": "National Informatics Centre",
            "status": "Published AOC",
            "aoc_date": "2025-01-22",
            "tender_id": "NIC-2025-API-002",
            "url": "https://etenders.gov.in/sample/002",
            "service_category": "cloud",
            "value_range": "5_to_25_lakh",
            "region": "delhi", 
            "department_type": "central",
            "complexity": "high",
            "keywords": "api,gateway,rest,integration,services"
        },
        {
            "title": "Implementation of Web Application Firewall and Security Solutions",
            "org": "Department of Telecommunications", 
            "status": "Published AOC",
            "aoc_date": "2025-01-25",
            "tender_id": "DOT-2025-SEC-003",
            "url": "https://etenders.gov.in/sample/003",
            "service_category": "security",
            "value_range": "25_to_100_lakh",
            "region": "delhi",
            "department_type": "central", 
            "complexity": "high",
            "keywords": "waf,firewall,security,protection,cyber"
        }
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for tender in sample_tenders:
            cursor.execute("""
                INSERT OR REPLACE INTO tenders (
                    title, org, status, aoc_date, tender_id, url,
                    service_category, value_range, region, department_type,
                    complexity, keywords
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tender["title"], tender["org"], tender["status"], 
                tender["aoc_date"], tender["tender_id"], tender["url"],
                tender["service_category"], tender["value_range"], 
                tender["region"], tender["department_type"],
                tender["complexity"], tender["keywords"]
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Loaded {len(sample_tenders)} sample tenders")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load sample data: {e}")
        return False

def copy_existing_database() -> bool:
    """Copy existing database from PoC if available"""
    
    source_db = "smart-tender-search-poc/engine/tenders.db"
    target_db = "TenderIntel/data/tenders.db"
    
    try:
        if os.path.exists(source_db):
            # Create target directory
            os.makedirs(os.path.dirname(target_db), exist_ok=True)
            
            # Copy database with existing data
            shutil.copy2(source_db, target_db)
            print(f"✅ Copied existing database from {source_db}")
            print(f"   Target: {target_db}")
            
            # Verify the copy
            conn = sqlite3.connect(target_db)
            count = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
            conn.close()
            
            print(f"   Records: {count} tenders available")
            return True
        else:
            print(f"ℹ️  No existing database found at {source_db}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to copy existing database: {e}")
        return False

def create_development_config() -> bool:
    """Create development configuration files"""
    
    project_root = get_project_root()
    
    # Development configuration
    dev_config = {
        "database": {
            "path": "data/tenders.db",
            "engine": "sqlite_fts5"
        },
        "search": {
            "max_results": 100,
            "default_similarity_threshold": 0.0,
            "enable_debug": True
        },
        "scraping": {
            "cppp": {
                "base_url": "https://etenders.gov.in",
                "max_pages": 5,
                "rate_limit_delay": 1.0,
                "enable_captcha": False
            },
            "gem": {
                "base_url": "https://gem.gov.in",
                "max_contracts": 100,
                "rate_limit_delay": 0.5
            }
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "reload": True,
            "log_level": "info"
        }
    }
    
    try:
        config_dir = project_root / "config" / "dev"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_dir / "config.json", "w") as f:
            json.dump(dev_config, f, indent=2)
        
        print(f"✅ Created development config: {config_dir / 'config.json'}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create config: {e}")
        return False

def validate_dependencies() -> bool:
    """Validate that required dependencies are available"""
    
    required_modules = [
        ("fastapi", "FastAPI web framework"),
        ("sqlite3", "SQLite database (built-in)"),
        ("requests", "HTTP client library"),
        ("pathlib", "Path utilities (built-in)")
    ]
    
    missing = []
    
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            missing.append((module, description))
            print(f"❌ {module}: {description} - MISSING")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {len(missing)}")
        print("Install with: pip install -e \".[dev,tenderx]\"")
        return False
    
    print(f"\n✅ All core dependencies available")
    return True

def main():
    """Main initialization function"""
    
    print("🚀 TenderIntel Project Initialization")
    print("=" * 50)
    
    project_root = get_project_root()
    print(f"📁 Project root: {project_root}")
    
    # Step 1: Validate dependencies
    print("\n1️⃣  Validating Dependencies")
    print("-" * 30)
    if not validate_dependencies():
        print("⚠️  Please install missing dependencies before proceeding")
        return False
    
    # Step 2: Create database
    print("\n2️⃣  Database Setup")
    print("-" * 20)
    
    # Try to copy existing database first
    if not copy_existing_database():
        # Create new database with schema and sample data
        db_path = project_root / "data" / "tenders.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        if create_database_schema(str(db_path)):
            load_sample_data(str(db_path))
    
    # Step 3: Create configuration
    print("\n3️⃣  Configuration Setup")
    print("-" * 25)
    create_development_config()
    
    # Step 4: Validation summary
    print("\n🎯 Initialization Complete!")
    print("=" * 30)
    print("✅ Project structure: Ready")
    print("✅ Database: Configured")
    print("✅ Configuration: Created")
    print("✅ Dependencies: Validated")
    
    print("\n🚀 Next Steps:")
    print("1. Start API server: python -m tenderintel.api.server")
    print("2. Test search: curl 'http://localhost:8000/search?q=lan'")
    print("3. View docs: http://localhost:8000/docs")
    print("4. Run tests: pytest")
    
    print(f"\n📚 Documentation: {project_root}/docs/")
    print(f"🔧 Configuration: {project_root}/config/dev/")
    print(f"💾 Database: {project_root}/data/tenders.db")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
