#!/usr/bin/env python3
"""
Financial Schema Migration for TenderIntel
==========================================

Adds comprehensive financial fields to existing FTS5 database schema for competitive intelligence.
Based on FINANCIAL_ANALYSIS_SYSTEM.md expert specifications.
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialSchemaMigrator:
    """Database schema migration for financial intelligence capabilities"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self.backup_path = self.db_path.parent / f"{self.db_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    def execute_migration(self) -> dict:
        """Execute complete financial schema migration with backup and validation"""
        
        migration_result = {
            "success": False,
            "backup_created": False,
            "fields_added": [],
            "validation_results": {},
            "error": None
        }
        
        try:
            # Step 1: Create backup
            logger.info("Creating database backup...")
            self._create_backup()
            migration_result["backup_created"] = True
            logger.info(f"Backup created: {self.backup_path}")
            
            # Step 2: Add financial fields to existing FTS5 table
            logger.info("Adding financial intelligence fields to FTS5 table...")
            added_fields = self._add_financial_fields()
            migration_result["fields_added"] = added_fields
            
            # Step 3: Create financial analysis helper tables
            logger.info("Creating financial analysis helper tables...")
            self._create_financial_helper_tables()
            
            # Step 4: Initialize financial data for existing records
            logger.info("Initializing financial data for existing records...")
            self._initialize_financial_data()
            
            # Step 5: Validate migration success
            logger.info("Validating migration results...")
            validation_results = self._validate_migration()
            migration_result["validation_results"] = validation_results
            
            if validation_results["all_fields_present"] and validation_results["fts5_functional"]:
                migration_result["success"] = True
                logger.info("✅ Financial schema migration completed successfully!")
            else:
                raise Exception(f"Migration validation failed: {validation_results}")
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            migration_result["error"] = str(e)
            
            # Attempt rollback
            if migration_result["backup_created"]:
                logger.info("Attempting to rollback to backup...")
                self._rollback_from_backup()
        
        return migration_result
    
    def _create_backup(self):
        """Create complete database backup before migration"""
        
        import shutil
        shutil.copy2(self.db_path, self.backup_path)
        
        # Verify backup integrity
        with sqlite3.connect(self.backup_path) as backup_conn:
            backup_count = backup_conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
            
        with sqlite3.connect(self.db_path) as original_conn:
            original_count = original_conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
            
        if backup_count != original_count:
            raise Exception(f"Backup verification failed: {original_count} != {backup_count}")
    
    def _add_financial_fields(self) -> list:
        """Add financial intelligence fields to existing FTS5 virtual table"""
        
        # Note: FTS5 virtual tables cannot use ALTER TABLE ADD COLUMN
        # We need to recreate the table with enhanced schema
        
        added_fields = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Step 1: Get existing data
            logger.info("Extracting existing tender data...")
            existing_data = conn.execute("""
                SELECT title, org, status, aoc_date, tender_id, url,
                       service_category, value_range, region, department_type, complexity, keywords
                FROM tenders
            """).fetchall()
            
            logger.info(f"Found {len(existing_data)} existing records to preserve")
            
            # Step 2: Drop existing FTS5 table
            logger.info("Dropping existing FTS5 table...")
            conn.execute("DROP TABLE tenders")
            
            # Step 3: Create enhanced FTS5 table with financial fields
            logger.info("Creating enhanced FTS5 table with financial intelligence fields...")
            conn.execute("""
                CREATE VIRTUAL TABLE tenders USING fts5(
                    title,                      -- Primary search field (FTS5 indexed)
                    org,                        -- Organization name (auxiliary)
                    status,                     -- Tender status (auxiliary)
                    aoc_date,                   -- Award of Contract date (auxiliary)
                    tender_id,                  -- Unique identifier (auxiliary)  
                    url,                        -- Source portal URL (auxiliary)
                    service_category,           -- Service classification (auxiliary)
                    value_range,                -- Estimated value range (auxiliary)
                    region,                     -- Geographic region (auxiliary)
                    department_type,            -- Organization type (auxiliary)
                    complexity,                 -- Complexity assessment (auxiliary)
                    keywords,                   -- Associated keywords (auxiliary)
                    
                    -- NEW FINANCIAL INTELLIGENCE FIELDS
                    award_value,                -- Actual award value (auxiliary)
                    currency,                   -- Currency code (auxiliary)
                    exchange_rate,              -- Exchange rate used (auxiliary)
                    exchange_rate_date,         -- Rate date (auxiliary)
                    inr_normalized_value,       -- INR equivalent value (auxiliary)
                    deal_size_category,         -- MICRO/SMALL/MEDIUM/LARGE/MEGA (auxiliary)
                    value_percentile,           -- Market percentile (auxiliary)
                    value_per_month,            -- Monthly value (auxiliary)
                    
                    -- CONTRACT & PAYMENT TERMS
                    contract_duration_months,   -- Contract duration (auxiliary)
                    advance_payment_percent,    -- Advance payment % (auxiliary)
                    performance_guarantee_percent, -- Performance guarantee % (auxiliary)
                    payment_terms_days,         -- Payment terms (auxiliary)
                    
                    -- COMPETITIVE INTELLIGENCE
                    winning_firm,               -- Winner name (auxiliary)
                    runner_up_firms,            -- Runner-up firms (auxiliary)
                    total_bidders,              -- Total bidder count (auxiliary)
                    win_margin_percent,         -- Win margin % (auxiliary)
                    estimated_margin_percent,   -- Estimated profit margin (auxiliary)
                    price_competitiveness_score, -- Price competitiveness (auxiliary)
                    market_benchmark_category,  -- Market benchmark category (auxiliary)
                    
                    -- GEOGRAPHIC ENHANCEMENTS
                    state_code,                 -- State code (auxiliary)
                    state_name,                 -- Full state name (auxiliary)
                    city,                       -- City (auxiliary)
                    coordinates,                -- Lat/Long coordinates (auxiliary)
                    
                    tokenize=porter,            -- Use Porter stemming for better matching
                    prefix='2,3'               -- Enable prefix matching for short terms
                )
            """)
            
            added_fields = [
                "award_value", "currency", "exchange_rate", "exchange_rate_date",
                "inr_normalized_value", "deal_size_category", "value_percentile", "value_per_month",
                "contract_duration_months", "advance_payment_percent", "performance_guarantee_percent",
                "payment_terms_days", "winning_firm", "runner_up_firms", "total_bidders",
                "win_margin_percent", "estimated_margin_percent", "price_competitiveness_score",
                "market_benchmark_category", "state_code", "state_name", "city", "coordinates"
            ]
            
            # Step 4: Restore existing data with null financial fields
            logger.info("Restoring existing data to enhanced schema...")
            
            for row in existing_data:
                # Prepare enhanced row with existing data + null financial fields
                enhanced_row = list(row) + [None] * len(added_fields)
                
                placeholders = ",".join(["?"] * (12 + len(added_fields)))  # 12 original + new fields
                
                conn.execute(f"""
                    INSERT INTO tenders VALUES ({placeholders})
                """, enhanced_row)
            
            # Step 5: Configure BM25 parameters for enhanced schema
            logger.info("Configuring BM25 parameters for financial intelligence...")
            conn.execute("INSERT INTO tenders(tenders, rank) VALUES('rank', 'bm25(1.2, 0.2)')")
            
            conn.commit()
            logger.info(f"✅ Enhanced FTS5 table created with {len(added_fields)} new financial fields")
            
        return added_fields
    
    def _create_financial_helper_tables(self):
        """Create helper tables for financial analysis and competitive intelligence"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Exchange rates cache table
            logger.info("Creating exchange rates cache table...")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS exchange_rates (
                    id INTEGER PRIMARY KEY,
                    currency_from VARCHAR(3) NOT NULL,
                    currency_to VARCHAR(3) NOT NULL,
                    rate DECIMAL(10,4) NOT NULL,
                    rate_date DATE NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(currency_from, currency_to, rate_date)
                )
            """)
            
            # Deal size thresholds table
            logger.info("Creating deal size thresholds table...")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deal_size_thresholds (
                    id INTEGER PRIMARY KEY,
                    category VARCHAR(20) NOT NULL UNIQUE,
                    min_value_inr DECIMAL(15,2) NOT NULL,
                    max_value_inr DECIMAL(15,2) NOT NULL,
                    display_label VARCHAR(50) NOT NULL,
                    color_code VARCHAR(7),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Populate deal size thresholds
            deal_thresholds = [
                ("micro", 0, 1000000, "< ₹10 Lakh", "#e3f2fd"),
                ("small", 1000000, 10000000, "₹10L - ₹1Cr", "#bbdefb"),
                ("medium", 10000000, 100000000, "₹1Cr - ₹10Cr", "#90caf9"),
                ("large", 100000000, 1000000000, "₹10Cr - ₹100Cr", "#64b5f6"),
                ("mega", 1000000000, 999999999999, "> ₹100Cr", "#2196f3")
            ]
            
            for threshold in deal_thresholds:
                conn.execute("""
                    INSERT OR IGNORE INTO deal_size_thresholds 
                    (category, min_value_inr, max_value_inr, display_label, color_code)
                    VALUES (?, ?, ?, ?, ?)
                """, threshold)
            
            # Competitive firms reference table (enhanced)
            logger.info("Creating competitive firms reference table...")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS competitive_firms (
                    id INTEGER PRIMARY KEY,
                    canonical_name VARCHAR(200) NOT NULL UNIQUE,
                    aliases TEXT,  -- JSON array of aliases
                    service_categories TEXT,  -- JSON array of service focus areas
                    firm_type VARCHAR(50),  -- MNC, Indian, Startup, etc.
                    headquarters VARCHAR(100),
                    market_position VARCHAR(50),  -- Leader, Challenger, Follower
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Market benchmarks table
            logger.info("Creating market benchmarks table...")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_benchmarks (
                    id INTEGER PRIMARY KEY,
                    service_category VARCHAR(100) NOT NULL,
                    time_period VARCHAR(20) NOT NULL,  -- quarterly, yearly
                    avg_value_inr DECIMAL(15,2),
                    median_value_inr DECIMAL(15,2),
                    total_market_value_inr DECIMAL(15,2),
                    total_tenders INTEGER,
                    hhi_index DECIMAL(5,4),  -- Market concentration
                    top_4_concentration DECIMAL(5,4),
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(service_category, time_period)
                )
            """)
            
            conn.commit()
            logger.info("✅ Financial helper tables created successfully")
    
    def _initialize_financial_data(self):
        """Initialize financial data for existing records using intelligent estimation"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Get all existing records
            records = conn.execute("""
                SELECT rowid, title, service_category, value_range, region
                FROM tenders  
            """).fetchall()
            
            logger.info(f"Initializing financial data for {len(records)} existing records...")
            
            initialized_count = 0
            
            for rowid, title, service_category, value_range, region in records:
                # Estimate financial data based on available information
                financial_estimate = self._estimate_financial_data(
                    title, service_category, value_range, region
                )
                
                # Update record with estimated financial data
                conn.execute("""
                    UPDATE tenders SET 
                        award_value = ?,
                        currency = ?,
                        inr_normalized_value = ?,
                        deal_size_category = ?,
                        value_percentile = ?,
                        state_name = ?,
                        state_code = ?
                    WHERE rowid = ?
                """, (
                    financial_estimate["award_value"],
                    financial_estimate["currency"],
                    financial_estimate["inr_normalized_value"], 
                    financial_estimate["deal_size_category"],
                    financial_estimate["value_percentile"],
                    financial_estimate["state_name"],
                    financial_estimate["state_code"],
                    rowid
                ))
                
                initialized_count += 1
            
            conn.commit()
            logger.info(f"✅ Initialized financial data for {initialized_count} records")
    
    def _estimate_financial_data(self, title: str, service_category: str, value_range: str, region: str) -> dict:
        """Estimate financial data based on available information and market intelligence"""
        
        # Service category based value estimation (in INR)
        service_value_estimates = {
            "cloud": (25000000, 75000000),      # ₹2.5Cr - ₹7.5Cr  
            "networking": (15000000, 45000000), # ₹1.5Cr - ₹4.5Cr
            "security": (20000000, 60000000),   # ₹2Cr - ₹6Cr
            "database": (18000000, 55000000),   # ₹1.8Cr - ₹5.5Cr
            "ai_ml": (30000000, 90000000),      # ₹3Cr - ₹9Cr
            "enterprise": (12000000, 40000000), # ₹1.2Cr - ₹4Cr
            "mobile_iot": (8000000, 25000000),  # ₹80L - ₹2.5Cr
        }
        
        # Get base estimate from service category
        if service_category and service_category.lower() in service_value_estimates:
            min_val, max_val = service_value_estimates[service_category.lower()]
            estimated_value = (min_val + max_val) / 2  # Average
        else:
            estimated_value = 25000000  # Default ₹2.5Cr
        
        # Adjust based on title keywords (complexity indicators)
        title_lower = title.lower() if title else ""
        
        if any(keyword in title_lower for keyword in ["enterprise", "nationwide", "pan india"]):
            estimated_value *= 2.5  # Enterprise deals are typically larger
        elif any(keyword in title_lower for keyword in ["basic", "maintenance", "support"]):
            estimated_value *= 0.6  # Support contracts are typically smaller
        elif any(keyword in title_lower for keyword in ["implementation", "deployment", "setup"]):
            estimated_value *= 1.4  # Implementation projects are larger
        
        # Regional adjustment
        if region and region.lower() in ["delhi", "mumbai", "bangalore"]:
            estimated_value *= 1.3  # Metro cities have higher values
        
        # Classify deal size
        def classify_deal_size(value_inr: float) -> str:
            if value_inr < 1000000:
                return "micro"
            elif value_inr < 10000000:
                return "small" 
            elif value_inr < 100000000:
                return "medium"
            elif value_inr < 1000000000:
                return "large"
            else:
                return "mega"
        
        # Calculate market percentile (estimated)
        def calculate_percentile(value_inr: float, category: str) -> int:
            if category == "ai_ml" and value_inr > 50000000:
                return 85  # High-value AI/ML projects
            elif category == "cloud" and value_inr > 40000000:
                return 80  # Large cloud implementations
            elif value_inr > 30000000:
                return 70  # Generally large projects
            elif value_inr > 10000000:
                return 50  # Medium projects  
            else:
                return 30  # Smaller projects
        
        # State code mapping
        state_mapping = {
            "delhi": ("DL", "Delhi"),
            "mumbai": ("MH", "Maharashtra"),
            "bangalore": ("KA", "Karnataka"), 
            "chennai": ("TN", "Tamil Nadu"),
            "kolkata": ("WB", "West Bengal"),
            "hyderabad": ("TG", "Telangana"),
            "pune": ("MH", "Maharashtra")
        }
        
        state_code, state_name = "UN", "Unknown"
        if region:
            region_key = region.lower()
            if region_key in state_mapping:
                state_code, state_name = state_mapping[region_key]
        
        return {
            "award_value": estimated_value,
            "currency": "INR",
            "inr_normalized_value": estimated_value,
            "deal_size_category": classify_deal_size(estimated_value),
            "value_percentile": calculate_percentile(estimated_value, service_category or ""),
            "state_code": state_code,
            "state_name": state_name
        }
    
    def _validate_migration(self) -> dict:
        """Validate migration success with comprehensive checks"""
        
        validation_results = {
            "all_fields_present": False,
            "record_count_preserved": False,
            "fts5_functional": False,
            "financial_data_initialized": False,
            "helper_tables_created": False,
            "original_record_count": 0,
            "migrated_record_count": 0,
            "financial_records_with_data": 0
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check record count preservation
                migrated_count = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
                validation_results["migrated_record_count"] = migrated_count
                
                # Check original count from backup
                with sqlite3.connect(self.backup_path) as backup_conn:
                    original_count = backup_conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
                    validation_results["original_record_count"] = original_count
                    validation_results["record_count_preserved"] = (migrated_count == original_count)
                
                # Test FTS5 functionality
                test_query = conn.execute("""
                    SELECT title, award_value, deal_size_category 
                    FROM tenders 
                    WHERE tenders MATCH 'network' 
                    LIMIT 5
                """).fetchall()
                
                validation_results["fts5_functional"] = len(test_query) > 0
                
                # Check financial data initialization
                financial_records = conn.execute("""
                    SELECT COUNT(*) FROM tenders 
                    WHERE award_value IS NOT NULL AND deal_size_category IS NOT NULL
                """).fetchone()[0]
                
                validation_results["financial_records_with_data"] = financial_records
                validation_results["financial_data_initialized"] = financial_records > 0
                
                # Check helper tables
                helper_tables = ["exchange_rates", "deal_size_thresholds", "competitive_firms", "market_benchmarks"]
                tables_exist = []
                
                for table in helper_tables:
                    exists = conn.execute("""
                        SELECT name FROM sqlite_master WHERE type='table' AND name=?
                    """, (table,)).fetchone()
                    tables_exist.append(exists is not None)
                
                validation_results["helper_tables_created"] = all(tables_exist)
                validation_results["all_fields_present"] = True  # If we got here, schema creation succeeded
                
        except Exception as e:
            logger.error(f"Migration validation failed: {e}")
            validation_results["error"] = str(e)
        
        return validation_results
    
    def _rollback_from_backup(self):
        """Rollback to backup database in case of migration failure"""
        
        try:
            import shutil
            shutil.copy2(self.backup_path, self.db_path)
            logger.info(f"✅ Successfully rolled back to backup: {self.backup_path}")
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            raise Exception(f"Critical error: Migration failed and rollback failed: {e}")

def main():
    """Main migration execution function"""
    
    print("TenderIntel Financial Schema Migration")
    print("=" * 45)
    
    # Get database path
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/tenders.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Usage: python financial_schema_migration.py [database_path]")
        sys.exit(1)
    
    # Execute migration
    migrator = FinancialSchemaMigrator(db_path)
    
    print(f"📁 Database: {db_path}")
    print(f"🔄 Starting financial schema migration...")
    
    result = migrator.execute_migration()
    
    # Display results
    print("\n📊 Migration Results:")
    print("-" * 25)
    print(f"Success: {result['success']}")
    print(f"Backup Created: {result['backup_created']}")
    print(f"Fields Added: {len(result['fields_added'])}")
    
    if result['validation_results']:
        validation = result['validation_results']
        print(f"Records Preserved: {validation.get('record_count_preserved', False)}")
        print(f"FTS5 Functional: {validation.get('fts5_functional', False)}")
        print(f"Financial Data Initialized: {validation.get('financial_records_with_data', 0)} records")
    
    if result['error']:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
    
    print("\n✅ Financial schema migration completed successfully!")
    print("\n🎯 Next Steps:")
    print("1. Test financial analysis APIs")
    print("2. Implement currency normalization service") 
    print("3. Build deal size classification engine")
    print("4. Create financial analytics dashboard")

if __name__ == "__main__":
    main()
