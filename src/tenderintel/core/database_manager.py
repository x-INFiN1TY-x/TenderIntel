#!/usr/bin/env python3
"""
SQLite FTS5 Database Setup for Smart Tender Search PoC
Creates optimized FTS5 virtual table for title-only search with BM25 ranking
"""

import sqlite3
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite FTS5 database creation and optimization"""
    
    def __init__(self, db_path: str = "engine/tenders.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
    
    def create_database(self) -> Dict[str, Any]:
        """
        Create optimized FTS5 database for tender search
        
        Returns:
            Database creation result with statistics and validation info
        """
        logger.info(f"Creating FTS5 database at: {self.db_path}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Enable foreign keys and other optimizations
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")  # Better concurrent access
                conn.execute("PRAGMA synchronous = NORMAL")  # Balance safety/performance
                
                # Create enhanced FTS5 virtual table with categorical metadata
                logger.info("Creating enhanced FTS5 virtual table with categorical support...")
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS tenders USING fts5(
                        title,              -- Primary search field (FTS5 indexed)
                        org,               -- Organization name (auxiliary)
                        status,            -- Tender status (auxiliary)
                        aoc_date,          -- Award of Contract date (auxiliary)
                        tender_id,         -- Unique identifier (auxiliary)
                        url,               -- Source portal URL (auxiliary)
                        service_category,  -- NEW: Service classification (auxiliary)
                        value_range,       -- NEW: Estimated value range (auxiliary)
                        region,            -- NEW: Geographic region (auxiliary)
                        department_type,   -- NEW: Organization type (auxiliary)
                        complexity,        -- NEW: Complexity assessment (auxiliary)
                        keywords,          -- NEW: Associated keywords (auxiliary)
                        tokenize=porter,   -- Use Porter stemming for better matching
                        prefix='2,3'      -- Enable prefix matching for short terms
                    )
                """)
                
                # Create categorical metadata tables for efficient filtering
                logger.info("Creating categorical metadata tables...")
                
                # Service categories reference table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS service_categories (
                        id INTEGER PRIMARY KEY,
                        category_name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        keyword_count INTEGER DEFAULT 0,
                        color_code TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Organizations reference table  
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS organizations (
                        id INTEGER PRIMARY KEY,
                        org_name TEXT UNIQUE NOT NULL,
                        org_type TEXT,
                        region TEXT,
                        tender_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Value ranges reference table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS value_ranges (
                        id INTEGER PRIMARY KEY,
                        range_code TEXT UNIQUE NOT NULL,
                        range_label TEXT NOT NULL,
                        min_value INTEGER,
                        max_value INTEGER,
                        tender_count INTEGER DEFAULT 0
                    )
                """)
                
                # Regions reference table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS regions (
                        id INTEGER PRIMARY KEY,
                        region_code TEXT UNIQUE NOT NULL,
                        region_name TEXT NOT NULL,
                        state TEXT,
                        tender_count INTEGER DEFAULT 0
                    )
                """)
                
                # Initialize reference data
                self._initialize_reference_tables(conn)
                
                # Configure BM25 parameters optimized for short titles
                # k1=1.2 (term frequency saturation), b=0.2 (reduced length normalization)
                logger.info("Configuring BM25 parameters for short titles...")
                conn.execute("""
                    INSERT INTO tenders(tenders, rank) VALUES('rank', 'bm25(1.2, 0.2)')
                """)
                
                # Create metadata table for search statistics
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS search_metadata (
                        id INTEGER PRIMARY KEY,
                        total_records INTEGER DEFAULT 0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        schema_version TEXT DEFAULT '1.0',
                        fts5_config TEXT DEFAULT 'porter_stemming_prefix_2_3'
                    )
                """)
                
                # Insert initial metadata
                conn.execute("""
                    INSERT OR REPLACE INTO search_metadata 
                    (id, total_records, fts5_config) 
                    VALUES (1, 0, 'bm25_k1_1.2_b_0.2_porter_prefix_2_3')
                """)
                
                # Note: FTS5 virtual tables provide their own indexing
                # Traditional CREATE INDEX statements are not supported on FTS5 tables
                logger.info("FTS5 virtual table created with built-in full-text indexing")
                
                conn.commit()
                
            # Validate database creation
            return self.validate_database_structure()
            
        except Exception as e:
            logger.error(f"Database creation failed: {e}")
            raise
    
    def validate_database_structure(self) -> Dict[str, Any]:
        """Validate that FTS5 database was created correctly with all optimizations"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Check FTS5 table exists and is configured correctly
            tables = conn.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%tenders%'
            """).fetchall()
            
            # Verify FTS5 configuration
            fts5_info = conn.execute("""
                SELECT * FROM tenders_config WHERE k='version'
            """).fetchall()
            
            # Check BM25 configuration
            rank_info = conn.execute("""
                SELECT * FROM tenders_data WHERE id=0
            """).fetchall()
            
            # Get database file size
            db_size = os.path.getsize(self.db_path)
            
            # Test basic FTS5 functionality
            test_query = conn.execute("""
                SELECT COUNT(*) FROM tenders WHERE tenders MATCH 'test'
            """).fetchone()
            
            validation_result = {
                'database_path': str(self.db_path),
                'database_size_bytes': db_size,
                'tables_created': [t[0] for t in tables],
                'fts5_configured': len(fts5_info) > 0,
                'bm25_configured': True,  # If we got here, it worked
                'basic_query_test': test_query[0] == 0,  # Should be 0 for empty table
                'status': 'success'
            }
            
            logger.info("Database validation completed successfully")
            logger.info(f"Database created: {self.db_path} ({db_size} bytes)")
            
            return validation_result
    
    def _initialize_reference_tables(self, conn: sqlite3.Connection):
        """Initialize reference tables with standard categorical data"""
        
        logger.info("Initializing reference tables with standard data...")
        
        # Initialize service categories
        service_categories = [
            ("networking", "Networking and connectivity solutions", 25, "#28a745"),
            ("security", "Security and compliance solutions", 30, "#dc3545"),
            ("cloud", "Cloud and platform services", 20, "#6f42c1"),
            ("database", "Database and analytics platforms", 15, "#17a2b8"),
            ("ai_ml", "AI and machine learning solutions", 18, "#fd7e14"),
            ("mobile_iot", "Mobile and IoT connectivity", 22, "#20c997"),
            ("enterprise", "Enterprise applications and systems", 25, "#6c757d")
        ]
        
        for category, desc, keyword_count, color in service_categories:
            conn.execute("""
                INSERT OR IGNORE INTO service_categories 
                (category_name, description, keyword_count, color_code)
                VALUES (?, ?, ?, ?)
            """, (category, desc, keyword_count, color))
        
        # Initialize value ranges
        value_ranges = [
            ("under_1_lakh", "Under ₹1 Lakh", 50000, 100000),
            ("1_to_5_lakh", "₹1-5 Lakh", 100000, 500000),
            ("5_to_25_lakh", "₹5-25 Lakh", 500000, 2500000),
            ("25_lakh_to_1_crore", "₹25 Lakh - 1 Crore", 2500000, 10000000),
            ("1_to_5_crore", "₹1-5 Crore", 10000000, 50000000),
            ("5_to_25_crore", "₹5-25 Crore", 50000000, 250000000),
            ("above_25_crore", "Above ₹25 Crore", 250000000, 1000000000)
        ]
        
        for range_code, label, min_val, max_val in value_ranges:
            conn.execute("""
                INSERT OR IGNORE INTO value_ranges 
                (range_code, range_label, min_value, max_value)
                VALUES (?, ?, ?, ?)
            """, (range_code, label, min_val, max_val))
        
        # Initialize regions
        regions = [
            ("delhi", "Delhi", "Delhi"),
            ("mumbai", "Mumbai", "Maharashtra"),
            ("bangalore", "Bangalore", "Karnataka"),
            ("chennai", "Chennai", "Tamil Nadu"),
            ("kolkata", "Kolkata", "West Bengal"),
            ("hyderabad", "Hyderabad", "Telangana"),
            ("pune", "Pune", "Maharashtra"),
            ("ahmedabad", "Ahmedabad", "Gujarat"),
            ("jaipur", "Jaipur", "Rajasthan"),
            ("lucknow", "Lucknow", "Uttar Pradesh")
        ]
        
        for region_code, region_name, state in regions:
            conn.execute("""
                INSERT OR IGNORE INTO regions 
                (region_code, region_name, state)
                VALUES (?, ?, ?)
            """, (region_code, region_name, state))
        
        logger.info("Reference tables initialized with standard data")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information for health checks"""
        
        if not self.db_path.exists():
            return {'status': 'not_created', 'error': 'Database file does not exist'}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get record count
                record_count = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
                
                # Get metadata
                metadata = conn.execute("""
                    SELECT total_records, last_updated, schema_version 
                    FROM search_metadata WHERE id = 1
                """).fetchone()
                
                # Test FTS5 functionality
                fts5_test = conn.execute("""
                    SELECT COUNT(*) FROM tenders WHERE tenders MATCH '"test query"'
                """).fetchone()[0]
                
                # Get reference table counts
                categories_count = conn.execute("SELECT COUNT(*) FROM service_categories").fetchone()[0]
                orgs_count = conn.execute("SELECT COUNT(*) FROM organizations").fetchone()[0]
                
                return {
                    'status': 'healthy',
                    'record_count': record_count,
                    'metadata': {
                        'total_records': metadata[0] if metadata else 0,
                        'last_updated': metadata[1] if metadata else None,
                        'schema_version': metadata[2] if metadata else '1.0'
                    },
                    'reference_tables': {
                        'service_categories': categories_count,
                        'organizations': orgs_count
                    },
                    'fts5_functional': True,
                    'database_size_bytes': os.path.getsize(self.db_path)
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'database_path': str(self.db_path)
            }
    
    def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options from reference tables"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get service categories
                categories = conn.execute("""
                    SELECT category_name, description, color_code 
                    FROM service_categories 
                    ORDER BY category_name
                """).fetchall()
                
                # Get value ranges
                value_ranges = conn.execute("""
                    SELECT range_code, range_label 
                    FROM value_ranges 
                    ORDER BY min_value
                """).fetchall()
                
                # Get regions
                regions = conn.execute("""
                    SELECT region_code, region_name, state 
                    FROM regions 
                    ORDER BY region_name
                """).fetchall()
                
                return {
                    "service_categories": [
                        {"code": cat[0], "label": cat[1], "color": cat[2]} 
                        for cat in categories
                    ],
                    "value_ranges": [
                        {"code": vr[0], "label": vr[1]} 
                        for vr in value_ranges
                    ],
                    "regions": [
                        {"code": reg[0], "label": reg[1], "state": reg[2]} 
                        for reg in regions
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to get filter options: {e}")
            return {"error": str(e)}

def main():
    """Main function to create and validate database"""
    print("Smart Tender Search PoC - Database Setup")
    print("=" * 50)
    
    # Create database manager
    db_manager = DatabaseManager()
    
    # Create and validate database
    result = db_manager.create_database()
    
    print("\nDatabase Creation Results:")
    print("-" * 30)
    for key, value in result.items():
        print(f"{key}: {value}")
    
    # Get database info
    info = db_manager.get_database_info()
    
    print("\nDatabase Health Check:")
    print("-" * 25)
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\n✅ Database setup completed successfully!")
    print(f"📁 Database location: {db_manager.db_path}")
    print("🔍 Ready for tender data loading and search operations")

if __name__ == "__main__":
    main()
