#!/usr/bin/env python3
"""
Comprehensive Test Suite for Financial Analysis System
=====================================================

Tests for currency normalization, deal classification, market analysis, and API endpoints.
Based on expert specifications from FINANCIAL_ANALYSIS_SYSTEM.md
"""

import pytest
import asyncio
import sqlite3
import json
from decimal import Decimal
from datetime import datetime, date
from pathlib import Path
import sys
import os

# Add src to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from tenderintel.analytics.currency_normalizer import CurrencyNormalizer, DealSizeClassifier
from tenderintel.analytics.financial_analysis_engine import FinancialAnalysisEngine

class TestFinancialAnalysisSystem:
    """Comprehensive test suite for financial analysis capabilities"""
    
    @pytest.fixture
    async def setup_test_database(self, tmp_path):
        """Create test database with sample financial data"""
        
        test_db = tmp_path / "test_tenders.db"
        
        with sqlite3.connect(test_db) as conn:
            # Create enhanced FTS5 table
            conn.execute("""
                CREATE VIRTUAL TABLE tenders USING fts5(
                    title, org, status, aoc_date, tender_id, url,
                    service_category, value_range, region, department_type, complexity, keywords,
                    award_value, currency, exchange_rate, exchange_rate_date, inr_normalized_value,
                    deal_size_category, value_percentile, value_per_month,
                    contract_duration_months, advance_payment_percent, performance_guarantee_percent,
                    payment_terms_days, winning_firm, runner_up_firms, total_bidders,
                    win_margin_percent, estimated_margin_percent, price_competitiveness_score,
                    market_benchmark_category, state_code, state_name, city, coordinates,
                    tokenize=porter, prefix='2,3'
                )
            """)
            
            # Create helper tables
            conn.execute("""
                CREATE TABLE exchange_rates (
                    id INTEGER PRIMARY KEY,
                    currency_from VARCHAR(3), currency_to VARCHAR(3),
                    rate DECIMAL(10,4), rate_date DATE, source VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE deal_size_thresholds (
                    id INTEGER PRIMARY KEY,
                    category VARCHAR(20) UNIQUE, min_value_inr DECIMAL(15,2),
                    max_value_inr DECIMAL(15,2), display_label VARCHAR(50), color_code VARCHAR(7)
                )
            """)
            
            # Insert test thresholds
            thresholds = [
                ("micro", 0, 1000000, "< ₹10 Lakh", "#e3f2fd"),
                ("small", 1000000, 10000000, "₹10L - ₹1Cr", "#bbdefb"),
                ("medium", 10000000, 100000000, "₹1Cr - ₹10Cr", "#90caf9"),
                ("large", 100000000, 1000000000, "₹10Cr - ₹100Cr", "#64b5f6"),
                ("mega", 1000000000, 999999999999, "> ₹100Cr", "#2196f3")
            ]
            
            for threshold in thresholds:
                conn.execute("""
                    INSERT INTO deal_size_thresholds 
                    (category, min_value_inr, max_value_inr, display_label, color_code)
                    VALUES (?, ?, ?, ?, ?)
                """, threshold)
            
            # Insert sample tender data with financial information
            sample_tenders = [
                ("LAN Infrastructure Setup", "Ministry of IT", "Published AOC", "2025-01-15", "T001", 
                 "https://test.gov.in/T001", "networking", "medium", "Delhi", "Government", "medium",
                 "lan,ethernet,switch", 45000000.0, "INR", 1.0, "2025-01-15", 45000000.0, "medium",
                 75, 3750000.0, 12, None, None, None, "Cisco Systems India", "HPE India,Juniper",
                 8, None, 12.5, 0.8, "competitive", "DL", "Delhi", None, None),
                
                ("API Gateway Development", "National Informatics Centre", "Published AOC", "2025-02-03",
                 "T002", "https://test.gov.in/T002", "cloud", "medium", "Delhi", "Government", "high",
                 "api,rest,gateway", 28000000.0, "INR", 1.0, "2025-02-03", 28000000.0, "medium",
                 60, 1555556.0, 18, None, None, None, "Tata Consultancy Services", "Infosys,HCL",
                 12, None, 15.0, 0.7, "competitive", "DL", "Delhi", None, None),
                
                ("Security Analytics Platform", "Department of Telecom", "Published AOC", "2025-02-18",
                 "T003", "https://test.gov.in/T003", "security", "large", "Delhi", "Government", "high",
                 "security,analytics,firewall", 125000000.0, "INR", 1.0, "2025-02-18", 125000000.0, "large",
                 85, 5208333.0, 24, None, None, None, "Fortinet India", "Palo Alto,Check Point",
                 6, None, 18.0, 0.6, "premium", "DL", "Delhi", None, None)
            ]
            
            for tender in sample_tenders:
                conn.execute(f"""
                    INSERT INTO tenders VALUES ({','.join(['?'] * len(tender))})
                """, tender)
            
            conn.commit()
        
        return test_db
    
    @pytest.mark.asyncio
    async def test_currency_normalization(self, setup_test_database):
        """Test currency normalization with various currencies and scenarios"""
        
        test_db = await setup_test_database
        normalizer = CurrencyNormalizer(str(test_db))
        
        # Test INR (direct)
        inr_result = await normalizer.normalize_to_inr(
            Decimal("25000000"), "INR", date(2025, 10, 21)
        )
        assert inr_result["inr_amount"] == Decimal("25000000")
        assert inr_result["exchange_rate"] == Decimal("1.0")
        assert inr_result["confidence"] == 1.0
        
        # Test USD conversion (using approximation)
        usd_result = await normalizer.normalize_to_inr(
            Decimal("50000"), "USD", date(2025, 10, 21)
        )
        assert usd_result["inr_amount"] is not None
        assert usd_result["inr_amount"] > Decimal("4000000")  # Reasonable conversion
        assert usd_result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_deal_size_classification(self, setup_test_database):
        """Test deal size classification accuracy and market percentiles"""
        
        test_db = await setup_test_database
        classifier = DealSizeClassifier(str(test_db))
        
        # Test classification boundaries
        test_cases = [
            (Decimal("500000"), "micro"),
            (Decimal("5000000"), "small"),  
            (Decimal("50000000"), "medium"),
            (Decimal("500000000"), "large"),
            (Decimal("2000000000"), "mega")
        ]
        
        for value, expected_category in test_cases:
            result = classifier.classify_deal_size(value, "networking")
            assert result["deal_size_category"] == expected_category
            assert result["classification_confidence"] > 0.9
            assert "display_label" in result
    
    @pytest.mark.asyncio  
    async def test_firm_financial_scorecard(self, setup_test_database):
        """Test firm financial scorecard generation with comprehensive metrics"""
        
        test_db = await setup_test_database
        engine = FinancialAnalysisEngine(str(test_db))
        
        # Test scorecard for firm with data
        scorecard = await engine.generate_firm_financial_scorecard("Tata Consultancy Services")
        
        assert scorecard.firm_name == "Tata Consultancy Services"
        assert scorecard.contract_count > 0
        assert scorecard.total_portfolio_value > Decimal("0")
        assert scorecard.market_share_percent >= 0.0
        assert scorecard.competitive_position in ["leader", "challenger", "follower", "niche"]
        
        # Verify financial metrics calculation
        assert scorecard.average_deal_size > Decimal("0")
        assert "deal_distribution" in scorecard.deal_size_distribution or scorecard.deal_size_distribution == {}
        assert scorecard.award_velocity >= 0.0
    
    @pytest.mark.asyncio
    async def test_market_financial_analysis(self, setup_test_database):
        """Test market financial analysis with HHI calculation and competitive assessment"""
        
        test_db = await setup_test_database
        engine = FinancialAnalysisEngine(str(test_db))
        
        # Test market analysis for networking category
        market_analysis = await engine.calculate_market_financial_metrics("networking")
        
        assert market_analysis.service_category == "networking"
        assert market_analysis.total_contracts >= 0
        assert market_analysis.total_market_value >= Decimal("0")
        assert 0.0 <= market_analysis.market_concentration_hhi <= 1.0
        assert market_analysis.competitive_intensity in ["low", "moderate", "high", "very_high", "unknown"]
        
        # Verify price distribution analysis
        if market_analysis.price_distribution:
            assert "mean" in market_analysis.price_distribution
            assert "median" in market_analysis.price_distribution
    
    @pytest.mark.asyncio
    async def test_batch_currency_normalization(self, setup_test_database):
        """Test batch currency normalization performance and accuracy"""
        
        test_db = await setup_test_database
        normalizer = CurrencyNormalizer(str(test_db))
        
        # Test batch normalization
        batch_result = await normalizer.batch_normalize_tenders()
        
        assert "total_tenders" in batch_result
        assert "success_rate" in batch_result
        assert batch_result["successful_normalizations"] >= 0
        assert batch_result["failed_normalizations"] >= 0
        
        # Verify normalization details
        if batch_result["normalization_details"]:
            detail = batch_result["normalization_details"][0]
            assert "tender_id" in detail
            assert "inr_amount" in detail
            assert "confidence" in detail
    
    def test_deal_size_boundary_conditions(self, setup_test_database):
        """Test deal size classification boundary conditions"""
        
        test_db = setup_test_database
        classifier = DealSizeClassifier(str(test_db))
        
        # Test exact boundary values
        boundary_tests = [
            (Decimal("999999"), "micro"),  # Just under 1M
            (Decimal("1000000"), "small"),  # Exactly 1M  
            (Decimal("9999999"), "small"),  # Just under 10M
            (Decimal("10000000"), "medium")  # Exactly 10M
        ]
        
        for value, expected in boundary_tests:
            result = classifier.classify_deal_size(value)
            assert result["deal_size_category"] == expected
    
    def test_market_concentration_calculation(self, setup_test_database):
        """Test HHI index calculation for market concentration analysis"""
        
        test_db = setup_test_database
        
        # Create test scenario with known market shares
        firms = ["FirmA", "FirmA", "FirmB", "FirmC"]  # FirmA: 50%, FirmB: 25%, FirmC: 25%
        values = [Decimal("40"), Decimal("40"), Decimal("20"), Decimal("20")]
        
        engine = FinancialAnalysisEngine(str(test_db))
        hhi = engine._calculate_hhi_index(firms, values)
        
        # Expected HHI = 0.5^2 + 0.25^2 + 0.25^2 = 0.375
        expected_hhi = 0.375
        assert abs(hhi - expected_hhi) < 0.01  # Allow small floating point variance

class TestFinancialAPIEndpoints:
    """Test financial analysis API endpoints with various scenarios"""
    
    @pytest.mark.asyncio
    async def test_firm_scorecard_api(self, setup_test_database):
        """Test firm financial scorecard API endpoint"""
        
        # This would require FastAPI TestClient setup
        # For now, test the underlying engine directly
        test_db = await setup_test_database
        engine = FinancialAnalysisEngine(str(test_db))
        
        scorecard = await engine.generate_firm_financial_scorecard("Cisco Systems India")
        
        # Verify scorecard structure
        assert hasattr(scorecard, 'firm_name')
        assert hasattr(scorecard, 'total_portfolio_value') 
        assert hasattr(scorecard, 'market_share_percent')
        assert hasattr(scorecard, 'competitive_position')
    
    @pytest.mark.asyncio
    async def test_market_analysis_api(self, setup_test_database):
        """Test market financial analysis API endpoint"""
        
        test_db = await setup_test_database
        engine = FinancialAnalysisEngine(str(test_db))
        
        market_metrics = await engine.calculate_market_financial_metrics("networking")
        
        # Verify market analysis structure
        assert market_metrics.service_category == "networking"
        assert market_metrics.total_market_value >= Decimal("0")
        assert market_metrics.total_contracts >= 0
        assert 0.0 <= market_metrics.market_concentration_hhi <= 1.0
    
    def test_currency_normalization_edge_cases(self):
        """Test currency normalization with edge cases and error conditions"""
        
        # Test with non-existent database (should handle gracefully)
        normalizer = CurrencyNormalizer("non_existent.db")
        
        # Test supported currencies list
        supported = normalizer.get_supported_currencies()
        assert "INR" in supported
        assert "USD" in supported
        assert "EUR" in supported
        assert isinstance(supported, list)
    
    def test_deal_classification_service_context(self, setup_test_database):
        """Test deal classification with service category context"""
        
        test_db = setup_test_database
        classifier = DealSizeClassifier(str(test_db))
        
        # Same value should have different percentiles in different categories
        test_value = Decimal("50000000")
        
        networking_result = classifier.classify_deal_size(test_value, "networking")
        cloud_result = classifier.classify_deal_size(test_value, "cloud")
        
        # Both should classify as medium
        assert networking_result["deal_size_category"] == "medium"
        assert cloud_result["deal_size_category"] == "medium"
        
        # Should have classification confidence
        assert networking_result["classification_confidence"] > 0.9
        assert cloud_result["classification_confidence"] > 0.9

def run_financial_validation_suite():
    """Run comprehensive financial analysis validation suite"""
    
    print("TenderIntel Financial Analysis Validation Suite")
    print("=" * 55)
    
    # Test database path
    test_db_path = "data/tenders.db"
    
    if not os.path.exists(test_db_path):
        print(f"❌ Test database not found: {test_db_path}")
        print("Please run financial schema migration first.")
        return False
    
    validation_results = {
        "schema_validation": False,
        "currency_normalization": False, 
        "deal_classification": False,
        "financial_analysis": False,
        "api_integration": False,
        "performance_validation": False
    }
    
    try:
        # 1. Schema Validation
        print("\n🗃️  Validating Enhanced Database Schema...")
        schema_valid = validate_financial_schema(test_db_path)
        validation_results["schema_validation"] = schema_valid
        print(f"   Schema Validation: {'✅ PASS' if schema_valid else '❌ FAIL'}")
        
        # 2. Currency Normalization Validation
        print("\n💱 Validating Currency Normalization...")
        currency_valid = asyncio.run(validate_currency_normalization(test_db_path))
        validation_results["currency_normalization"] = currency_valid
        print(f"   Currency Normalization: {'✅ PASS' if currency_valid else '❌ FAIL'}")
        
        # 3. Deal Classification Validation  
        print("\n📊 Validating Deal Size Classification...")
        classification_valid = validate_deal_classification(test_db_path)
        validation_results["deal_classification"] = classification_valid
        print(f"   Deal Classification: {'✅ PASS' if classification_valid else '❌ FAIL'}")
        
        # 4. Financial Analysis Engine Validation
        print("\n🏢 Validating Financial Analysis Engine...")
        analysis_valid = asyncio.run(validate_financial_analysis_engine(test_db_path))
        validation_results["financial_analysis"] = analysis_valid
        print(f"   Financial Analysis Engine: {'✅ PASS' if analysis_valid else '❌ FAIL'}")
        
        # 5. API Integration Validation
        print("\n🔌 Validating API Integration...")
        api_valid = validate_api_integration()
        validation_results["api_integration"] = api_valid
        print(f"   API Integration: {'✅ PASS' if api_valid else '❌ FAIL'}")
        
        # 6. Performance Validation
        print("\n⚡ Validating Performance...")
        performance_valid = asyncio.run(validate_performance(test_db_path))
        validation_results["performance_validation"] = performance_valid
        print(f"   Performance Validation: {'✅ PASS' if performance_valid else '❌ FAIL'}")
        
    except Exception as e:
        print(f"❌ Validation suite failed: {e}")
        return False
    
    # Summary
    passed_tests = sum(1 for result in validation_results.values() if result)
    total_tests = len(validation_results)
    success_rate = passed_tests / total_tests * 100
    
    print(f"\n📊 Validation Summary:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"✅ Financial analysis system validation PASSED")
        print(f"🚀 Ready for Week 2: Advanced Visualizations")
        return True
    else:
        print(f"❌ Financial analysis system validation FAILED")
        print(f"🔧 Requires fixes before proceeding to visualizations")
        return False

def validate_financial_schema(db_path: str) -> bool:
    """Validate that financial schema migration was successful"""
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Check if financial fields exist
            schema = conn.execute("PRAGMA table_info(tenders)").fetchall()
            field_names = [row[1] for row in schema]
            
            required_fields = [
                "award_value", "currency", "inr_normalized_value", "deal_size_category",
                "winning_firm", "state_code", "state_name"
            ]
            
            missing_fields = [field for field in required_fields if field not in field_names]
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            
            # Check helper tables exist
            helper_tables = ["exchange_rates", "deal_size_thresholds"]
            for table in helper_tables:
                exists = conn.execute("""
                    SELECT name FROM sqlite_master WHERE type='table' AND name=?
                """, (table,)).fetchone()
                
                if not exists:
                    print(f"   ❌ Missing helper table: {table}")
                    return False
            
            return True
            
    except Exception as e:
        print(f"   ❌ Schema validation error: {e}")
        return False

async def validate_currency_normalization(db_path: str) -> bool:
    """Validate currency normalization functionality"""
    
    try:
        normalizer = CurrencyNormalizer(db_path)
        
        # Test basic normalization
        test_result = await normalizer.normalize_to_inr(
            Decimal("100"), "USD", date(2025, 10, 21)
        )
        
        if not test_result["inr_amount"] or test_result["confidence"] < 0.5:
            return False
        
        # Test supported currencies
        supported = normalizer.get_supported_currencies()
        if len(supported) < 5:  # Should support at least 5 major currencies
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Currency normalization error: {e}")
        return False

def validate_deal_classification(db_path: str) -> bool:
    """Validate deal size classification accuracy"""
    
    try:
        classifier = DealSizeClassifier(db_path)
        
        # Test known classifications
        test_values = [
            (Decimal("500000"), "micro"),
            (Decimal("25000000"), "medium"),
            (Decimal("250000000"), "large")
        ]
        
        for value, expected in test_values:
            result = classifier.classify_deal_size(value)
            if result["deal_size_category"] != expected:
                print(f"   ❌ Classification error: {value} → {result['deal_size_category']} (expected {expected})")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Deal classification error: {e}")
        return False

async def validate_financial_analysis_engine(db_path: str) -> bool:
    """Validate financial analysis engine comprehensive functionality"""
    
    try:
        engine = FinancialAnalysisEngine(db_path)
        
        # Test firm scorecard generation
        scorecard = await engine.generate_firm_financial_scorecard("Test Firm")
        if not hasattr(scorecard, 'firm_name'):
            return False
        
        # Test market analysis
        market_metrics = await engine.calculate_market_financial_metrics("networking")
        if not hasattr(market_metrics, 'service_category'):
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Financial analysis engine error: {e}")
        return False

def validate_api_integration() -> bool:
    """Validate API integration with financial analysis components"""
    
    try:
        # Check if financial analysis components can be imported
        from tenderintel.analytics.financial_analysis_engine import FinancialAnalysisEngine
        from tenderintel.analytics.currency_normalizer import CurrencyNormalizer
        
        # Basic instantiation test
        engine = FinancialAnalysisEngine("test.db")
        normalizer = CurrencyNormalizer("test.db")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ API integration error: {e}")
        return False

async def validate_performance(db_path: str) -> bool:
    """Validate performance requirements for financial analysis"""
    
    try:
        engine = FinancialAnalysisEngine(db_path)
        
        # Test performance of financial analysis operations
        start_time = datetime.now()
        
        # This should complete within reasonable time
        scorecard = await engine.generate_firm_financial_scorecard("Test Firm")
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Should complete within 1 second for small datasets
        if processing_time > 1000:
            print(f"   ⚠️  Performance warning: {processing_time:.0f}ms (target: <1000ms)")
            return False
        
        print(f"   ⚡ Performance: {processing_time:.1f}ms")
        return True
        
    except Exception as e:
        print(f"   ❌ Performance validation error: {e}")
        return False

if __name__ == "__main__":
    success = run_financial_validation_suite()
    sys.exit(0 if success else 1)
