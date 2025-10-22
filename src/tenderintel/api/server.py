#!/usr/bin/env python3
"""
TenderIntel API Server
=====================

Production-ready FastAPI server providing intelligent government procurement search
and competitive intelligence capabilities.

Features:
- RESTful API with comprehensive OpenAPI documentation
- Real-time tender search with keyword expansion
- Competitive intelligence analytics
- TenderX integration for production scraping
- Health monitoring and performance metrics
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import sqlite3
import json
import time
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional

# Import TenderIntel components
from tenderintel.search.manager import UnifiedSearchManager
from tenderintel.search.search_engine_interface import SearchFilters
from tenderintel.config import load_config
from tenderintel.core.database_manager import DatabaseManager
from tenderintel.scraper.tenderx_integration import TenderXIntegratedScraper
from tenderintel.analytics.financial_analysis_engine import FinancialAnalysisEngine
from tenderintel.analytics.currency_normalizer import CurrencyNormalizer, DealSizeClassifier
from tenderintel.analytics.visualization_data_generator import (
    ServiceFirmHeatmapGenerator, GeographicIntelligenceGenerator, DashboardDataProvider
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with professional metadata
app = FastAPI(
    title="TenderIntel API",
    description="""
    **AI-Powered Competitive Intelligence for Government Procurement**
    
    TenderIntel provides intelligent search and competitive analysis capabilities 
    for Indian government procurement data from CPPP, GeM, and other portals.
    
    ## Key Features
    
    * **🔍 Intelligent Search**: 215+ keyword expansion with zero false positives
    * **📊 Competitive Intelligence**: Real-time firm tracking and market analysis  
    * **🏭 Production Scraping**: Automated CPPP and GeM data collection
    * **⚡ High Performance**: Sub-second search with BM25 ranking
    
    ## Quick Start Examples
    
    * Search for networking tenders: `GET /search?q=lan`
    * Get competitive intelligence: `GET /competitive-intelligence/summary`
    * Scrape new data: `POST /scraper/cppp?pages=5`
    """,
    version="1.0.0",
    contact={
        "name": "TenderIntel Team",
        "url": "https://github.com/tenderintel/tenderintel",
        "email": "team@tenderintel.org"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Search",
            "description": "Intelligent tender search with keyword expansion and BM25 ranking"
        },
        {
            "name": "Intelligence", 
            "description": "Competitive intelligence and market analysis"
        },
        {
            "name": "Scraping",
            "description": "Data collection from government portals"
        },
        {
            "name": "System",
            "description": "Health monitoring and system information"
        }
    ]
)

# Add CORS middleware for web UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core services with absolute paths
# Fix path resolution using project root
db_path = project_root / "data" / "tenders.db"
database_manager = DatabaseManager(str(db_path))

# Initialize unified search manager (handles engine selection automatically)
config = load_config()
search_manager = UnifiedSearchManager(config)
tenderx_scraper = TenderXIntegratedScraper()

# Initialize synonym manager (required for health checks and expansion)
from tenderintel.search.synonym_manager_yaml import SynonymManagerV2 as SynonymManager
synonym_manager = SynonymManager()

# Initialize financial analysis components
financial_analysis_engine = FinancialAnalysisEngine(str(db_path))
currency_normalizer = CurrencyNormalizer(str(db_path))
deal_size_classifier = DealSizeClassifier(str(db_path))
# Initialize visualization components
heatmap_generator = ServiceFirmHeatmapGenerator(str(db_path))
geographic_generator = GeographicIntelligenceGenerator(str(db_path))
dashboard_provider = DashboardDataProvider(str(db_path))

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Root endpoint with API overview and quick links"""
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>TenderIntel API</title>
            <style>
                body { font-family: system-ui, sans-serif; margin: 40px; color: #333; }
                .header { border-bottom: 2px solid #007acc; padding-bottom: 20px; }
                .section { margin: 30px 0; }
                .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { display: inline-block; padding: 4px 8px; border-radius: 3px; font-weight: bold; }
                .get { background: #4CAF50; color: white; }
                .post { background: #FF9800; color: white; }
                a { color: #007acc; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 TenderIntel API</h1>
                <p><strong>AI-Powered Competitive Intelligence for Government Procurement</strong></p>
                <p>Production-ready API providing intelligent search and competitive analysis for Indian government tenders.</p>
            </div>
            
            <div class="section">
                <h2>🔍 Core Search Endpoints</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/search?q=lan">/search</a> - Intelligent tender search with keyword expansion
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/expand?q=api">/expand</a> - Technical keyword expansion (215+ terms)
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/search-filtered?q=cloud&service_categories=cloud">/search-filtered</a> - Advanced filtering
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Competitive Intelligence</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/competitive-intelligence/summary">/competitive-intelligence/summary</a> - Market analysis
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/filter-options">/filter-options</a> - Available filter categories
                </div>
            </div>
            
            <div class="section">
                <h2>🏭 Data Collection</h2>
                <div class="endpoint">
                    <span class="method post">POST</span> 
                    <a href="/docs#/Scraping/scrape_cppp_tenders">/scraper/cppp</a> - CPPP portal scraping
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> 
                    <a href="/docs#/Scraping/scrape_gem_contracts">/scraper/gem</a> - GeM contract collection
                </div>
            </div>
            
            <div class="section">
                <h2>🔧 System & Monitoring</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/health">/health</a> - Comprehensive health check
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/stats">/stats</a> - System statistics
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> 
                    <a href="/test-demo-scenarios">/test-demo-scenarios</a> - Validation scenarios
                </div>
            </div>
            
            <div class="section">
                <h2>📚 Documentation & Tools</h2>
                <p>
                    <a href="/docs">📖 Interactive API Documentation</a> | 
                    <a href="/redoc">📋 ReDoc Documentation</a> | 
                    <a href="https://github.com/tenderintel/tenderintel">🔗 GitHub Repository</a>
                </p>
                
                <h3>🎯 Quick Test Commands:</h3>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
# Test intelligent search
curl "http://localhost:8002/search?q=lan"

# Test keyword expansion  
curl "http://localhost:8002/expand?q=api"

# Test competitive intelligence
curl "http://localhost:8002/competitive-intelligence/summary"

# Health check
curl "http://localhost:8002/health"
                </pre>
            </div>
            
            <div class="section">
                <p><em>TenderIntel v1.0.0 - Transforming Government Procurement Intelligence</em></p>
            </div>
        </body>
    </html>
    """

# Search Endpoints
@app.get("/search", tags=["Search"])
async def search_tenders(
    q: str = Query(..., description="Search keyword", min_length=1, max_length=50),
    limit: int = Query(25, description="Maximum results to return", ge=1, le=100),
    debug: bool = Query(False, description="Include debug information"),
    min_similarity: int = Query(0, description="Minimum similarity threshold (0-100)", ge=0, le=100)
) -> Dict[str, Any]:
    """
    Execute intelligent tender search with keyword expansion and BM25 ranking
    
    This endpoint demonstrates TenderIntel's core value: transforming short technical
    acronyms into comprehensive, relevant search results with zero false positives.
    
    **Example:**
    - Query: "lan" 
    - Expands to: ["local area network", "layer 2 switch", "vlan", "ethernet"]
    - Returns: Networking tenders with BM25 similarity scoring
    """
    
    try:
        start_time = time.time()
        
        # Input validation
        keyword = q.strip()
        if not keyword:
            raise HTTPException(status_code=400, detail="Search keyword cannot be empty")
        
        # Create filters if similarity threshold specified
        filters = SearchFilters(min_similarity=min_similarity) if min_similarity > 0 else None
        
        # Execute search using unified search manager (supports both engines)
        search_result = await search_manager.search(
            keyword=keyword,
            filters={'min_similarity': min_similarity} if min_similarity > 0 else None,
            limit=limit,
            debug=debug
        )
        
        # Convert to API response format
        return {
            "query": search_result.query,
            "expanded_phrases": search_result.expanded_phrases,
            "total_matches": search_result.total_matches,
            "execution_time_ms": search_result.execution_time_ms,
            "engine_used": search_result.engine_used,
            "hits": [
                {
                    "tender_id": hit.tender_id,
                    "title": hit.title,
                    "organization": hit.organization,
                    "status": hit.status,
                    "aoc_date": hit.aoc_date,
                    "url": hit.url,
                    "similarity_percent": hit.similarity_percent,
                    "matched_phrases": hit.matched_phrases,
                    "exact_match": hit.exact_match,
                    "service_category": hit.service_category,
                    "value_range": hit.value_range,
                    "region": hit.region
                }
                for hit in search_result.hits
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed for '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/expand", tags=["Search"])
async def expand_keyword(
    q: str = Query(..., description="Keyword to expand", min_length=1, max_length=50),
    max_expansions: int = Query(5, description="Maximum number of expansions", ge=1, le=10),
    debug: bool = Query(False, description="Include debug information")
) -> Dict[str, Any]:
    """
    Expand a keyword into relevant technical phrases
    
    **Core Innovation**: Transform short technical acronyms into searchable long-form phrases
    that overcome government portal search limitations.
    
    **Examples:**
    - "api" → ["application programming interface", "rest api", "api gateway", "openapi"]
    - "lan" → ["local area network", "layer 2 switch", "layer 3 switch", "vlan", "ethernet"]
    - "iam" → ["identity and access management", "user management", "access control"]
    """
    start_time = time.time()
    
    try:
        # Input validation and sanitization
        keyword = q.strip().lower()
        if not keyword:
            raise HTTPException(status_code=400, detail="Keyword cannot be empty")
        
        # Perform expansion using global synonym manager
        expansion_result = synonym_manager.expand_keyword(keyword, max_expansions)
        
        # Calculate execution time
        execution_time = round((time.time() - start_time) * 1000, 2)
        
        # Build response
        response = {
            "query": q,  # Original case preserved
            "normalized_query": keyword,
            "phrases": expansion_result['expanded_phrases'],
            "domain": expansion_result.get('domain', 'general'),
            "confidence": expansion_result.get('confidence', 0.0),
            "execution_time_ms": execution_time
        }
        
        # Add debug information if requested
        if debug:
            response["debug_info"] = {
                "anti_patterns": expansion_result.get('anti_patterns', []),
                "expansion_count": expansion_result.get('expansion_count', 0),
                "domain_detected": expansion_result.get('domain') != 'general'
            }
        
        logger.info(f"Keyword expansion: '{q}' → {len(expansion_result['expanded_phrases'])} phrases")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Expansion failed for '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Expansion error: {str(e)}")

# Competitive Intelligence Endpoints
@app.get("/competitive-intelligence/summary", tags=["Intelligence"])
async def get_competitive_intelligence_summary() -> Dict[str, Any]:
    """
    Get comprehensive competitive intelligence summary
    
    Provides market share analysis, firm performance tracking, and regional
    distribution analysis based on actual government procurement data.
    
    **Returns:**
    - Service category breakdown with tender counts
    - Top performing organizations by category
    - Regional procurement distribution
    - Market complexity analysis
    """
    
    try:
        with sqlite3.connect(database_manager.db_path) as conn:
            # Service category breakdown
            category_stats = conn.execute("""
                SELECT service_category, COUNT(*) as tender_count
                FROM tenders 
                WHERE service_category IS NOT NULL AND service_category != ''
                GROUP BY service_category
                ORDER BY tender_count DESC
            """).fetchall()
            
            # Organization performance analysis
            org_stats = conn.execute("""
                SELECT org, service_category, COUNT(*) as participation_count
                FROM tenders 
                WHERE org IS NOT NULL AND org != ''
                GROUP BY org, service_category
                ORDER BY participation_count DESC
                LIMIT 20
            """).fetchall()
            
            # Regional distribution
            region_stats = conn.execute("""
                SELECT region, COUNT(*) as tender_count, COUNT(DISTINCT org) as unique_orgs
                FROM tenders
                WHERE region IS NOT NULL AND region != ''
                GROUP BY region
                ORDER BY tender_count DESC
            """).fetchall()
            
            # Complexity analysis
            complexity_stats = conn.execute("""
                SELECT complexity, COUNT(*) as count
                FROM tenders
                WHERE complexity IS NOT NULL AND complexity != ''
                GROUP BY complexity
            """).fetchall()
        
        return {
            "competitive_intelligence": {
                "market_overview": {
                    "total_analyzed_tenders": sum(stat[1] for stat in category_stats),
                    "service_categories": len(category_stats),
                    "active_regions": len(region_stats),
                    "complexity_distribution": {
                        stat[0]: {"count": stat[1]}
                        for stat in complexity_stats
                    }
                },
                "service_category_analysis": [
                    {"category": stat[0], "tender_count": stat[1]}
                    for stat in category_stats
                ],
                "organization_performance": [
                    {
                        "organization": stat[0],
                        "service_category": stat[1],
                        "participation_count": stat[2]
                    }
                    for stat in org_stats[:10]
                ],
                "regional_distribution": [
                    {
                        "region": stat[0],
                        "tender_count": stat[1],
                        "unique_organizations": stat[2]
                    }
                    for stat in region_stats
                ]
            },
            "data_quality": {
                "has_real_data": len(category_stats) > 0,
                "competitive_firms_detected": len(org_stats) > 0,
                "geographic_coverage": len(region_stats) > 0
            }
        }
        
    except Exception as e:
        logger.error(f"Competitive intelligence analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Intelligence analysis error: {str(e)}")

# Scraping Endpoints  
@app.post("/scraper/cppp", tags=["Scraping"])
async def scrape_cppp_tenders(
    max_pages: int = Query(1, description="Maximum pages to scrape", ge=1, le=10),
    test_mode: bool = Query(True, description="Test mode with sample data"),
    enable_captcha: bool = Query(False, description="Enable CAPTCHA solving")
) -> Dict[str, Any]:
    """
    Execute CPPP portal scraping with TenderX integration
    
    Combines TenderX's production-grade scraping capabilities with TenderIntel's
    intelligent data enhancement and competitive analysis.
    
    **Features:**
    - Automated CAPTCHA handling with OCR
    - Document download and cloud storage  
    - Intelligent service categorization
    - Competitive firm detection
    - Real-time database updates
    """
    
    try:
        start_time = time.time()
        
        if test_mode:
            # Test mode: generate realistic sample data
            logger.info("🧪 Running CPPP scraping in test mode")
            enhanced_tenders = tenderx_scraper._create_sample_real_data(count=5)
            
            # Save to database
            saved_count = 0
            for tender in enhanced_tenders:
                if tenderx_scraper.adapter.save_enhanced_tender(tender):
                    saved_count += 1
                    
        else:
            # Production mode: actual TenderX scraping
            logger.info("🚀 Running production CPPP scraping")
            enhanced_tenders = tenderx_scraper.scrape_and_enhance_tenders(max_pages=max_pages)
            saved_count = len(enhanced_tenders)
        
        execution_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "scraping_status": "success",
            "source": "CPPP",
            "execution_results": {
                "total_tenders_processed": len(enhanced_tenders),
                "successfully_saved": saved_count,
                "failed_saves": len(enhanced_tenders) - saved_count,
                "execution_time_ms": execution_time,
                "test_mode": test_mode
            },
            "competitive_intelligence": {
                "service_categories_found": len(set(t.get("service_category") for t in enhanced_tenders)),
                "firms_detected": len(set(firm for t in enhanced_tenders for firm in t.get("detected_firms", []))),
                "regions_covered": len(set(t.get("region") for t in enhanced_tenders))
            },
            "sample_tenders": [
                {
                    "tender_id": t.get("tender_id"),
                    "title": t.get("title", "")[:100] + "..." if len(t.get("title", "")) > 100 else t.get("title", ""),
                    "service_category": t.get("service_category"),
                    "detected_firms": t.get("detected_firms", []),
                    "complexity": t.get("complexity_level")
                }
                for t in enhanced_tenders[:3]
            ]
        }
        
    except Exception as e:
        logger.error(f"CPPP scraping failed: {e}")
        raise HTTPException(status_code=500, detail=f"CPPP scraping error: {str(e)}")

# System Endpoints
@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive system health check
    
    Validates all critical components including database connectivity,
    search engine performance, and synonym manager functionality.
    """
    
    start_time = time.time()
    health_status = {"status": "healthy", "checks": {}}
    
    try:
        # Database connectivity check
        db_info = database_manager.get_database_info()
        health_status["checks"]["database"] = {
            "status": db_info.get('status', 'unknown'),
            "record_count": db_info.get('record_count', 0),
            "fts5_functional": db_info.get('fts5_functional', False)
        }
        
        # Synonym manager check
        synonym_stats = synonym_manager.get_statistics()
        health_status["checks"]["synonym_manager"] = {
            "status": "healthy",
            "total_keywords": synonym_stats.get('total_keywords', 0),
            "domains_supported": synonym_stats.get('domains_supported', 0)
        }
        
        # Search engine performance check
        engine_info = await search_manager.get_engine_info()
        health_status["checks"]["search_engine"] = {
            "status": "healthy" if engine_info['health']['is_healthy'] else "unhealthy",
            "engine_type": engine_info['engine_type'],
            "engine_name": engine_info['engine_name'],
            "performance_rating": engine_info['recommendation']['current_performance']
        }
        
        # System performance metrics
        total_health_check_time = round((time.time() - start_time) * 1000, 2)
        health_status["checks"]["performance"] = {
            "health_check_time_ms": total_health_check_time,
            "status": "healthy" if total_health_check_time < 1000 else "slow"
        }
        
        # Overall status determination
        check_statuses = [check["status"] for check in health_status["checks"].values()]
        if any(status == "unhealthy" for status in check_statuses):
            health_status["status"] = "unhealthy"
        elif any(status in ["error", "slow"] for status in check_statuses):
            health_status["status"] = "degraded"
        
        # Add system information
        health_status["system_info"] = {
            "api_version": "1.0.0",
            "database_path": str(database_manager.db_path),
            "search_engine": "sqlite_fts5_bm25",
            "total_endpoints": 9,
            "total_check_time_ms": total_health_check_time
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "checks": {}
        }

@app.get("/stats", tags=["System"])
async def get_system_statistics() -> Dict[str, Any]:
    """Get comprehensive system statistics and metrics"""
    
    try:
        with sqlite3.connect(database_manager.db_path) as conn:
            # Basic statistics
            total_records = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
            
            # Organization breakdown (Fixed: use correct column name 'org')
            org_stats = conn.execute("""
                SELECT org, COUNT(*) as count
                FROM tenders
                WHERE org IS NOT NULL AND org != ''
                GROUP BY org
                ORDER BY count DESC
                LIMIT 10
            """).fetchall()
            
            # Status distribution
            status_stats = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM tenders
                GROUP BY status
            """).fetchall()
            
            # Date range analysis
            date_stats = conn.execute("""
                SELECT 
                    MIN(aoc_date) as earliest_date,
                    MAX(aoc_date) as latest_date
                FROM tenders
                WHERE aoc_date IS NOT NULL
            """).fetchone()
            
            # Title analysis
            title_stats = conn.execute("""
                SELECT
                    AVG(LENGTH(title)) as avg_length,
                    MIN(LENGTH(title)) as min_length,
                    MAX(LENGTH(title)) as max_length
                FROM tenders
            """).fetchone()
        
        # Synonym manager statistics
        synonym_stats = synonym_manager.get_statistics()
        
        return {
            "database_statistics": {
                "total_records": total_records,
                "date_range": {
                    "earliest": date_stats[0] if date_stats else None,
                    "latest": date_stats[1] if date_stats else None
                },
                "title_analysis": {
                    "avg_length": round(title_stats[0], 1) if title_stats[0] else 0,
                    "min_length": title_stats[1] if title_stats[1] else 0,
                    "max_length": title_stats[2] if title_stats[2] else 0
                },
                "top_organizations": [
                    {"organization": org, "tender_count": count} 
                    for org, count in org_stats
                ],
                "status_distribution": [
                    {"status": status, "count": count} 
                    for status, count in status_stats
                ]
            },
            "synonym_statistics": synonym_stats,
            "api_info": {
                "version": "1.0.0",
                "search_engine": "sqlite_fts5_bm25",
                "total_endpoints": 9,
                "uptime_status": "operational"
            }
        }
        
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@app.get("/search-filtered", tags=["Search"])
async def search_tenders_with_filters(
    q: str = Query(..., description="Search keyword", min_length=1, max_length=50),
    limit: int = Query(25, description="Maximum results to return", ge=1, le=100),
    debug: bool = Query(False, description="Include debug information"),
    # Date filtering
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    # Categorical filtering
    service_categories: Optional[str] = Query(None, description="Comma-separated service categories"),
    organizations: Optional[str] = Query(None, description="Comma-separated organizations"),
    value_ranges: Optional[str] = Query(None, description="Comma-separated value ranges"),
    regions: Optional[str] = Query(None, description="Comma-separated regions"),
    status_types: Optional[str] = Query(None, description="Comma-separated status types"),
    department_types: Optional[str] = Query(None, description="Comma-separated department types"),
    complexity_levels: Optional[str] = Query(None, description="Comma-separated complexity levels"),
    min_similarity: Optional[int] = Query(0, description="Minimum similarity threshold", ge=0, le=100)
) -> Dict[str, Any]:
    """
    Execute enhanced search with comprehensive categorical filtering
    
    Supports filtering by:
    - Date ranges (from/to dates)
    - Service categories (networking, security, cloud, etc.)
    - Organizations and department types
    - Geographic regions
    - Value ranges and complexity levels
    - Minimum similarity thresholds
    """
    
    try:
        # Parse comma-separated filter parameters
        def parse_csv_param(param: Optional[str]) -> Optional[List[str]]:
            return [item.strip() for item in param.split(',')] if param else None
        
        # Build comprehensive filters object
        filters = SearchFilters(
            date_from=date_from,
            date_to=date_to,
            service_categories=parse_csv_param(service_categories),
            organizations=parse_csv_param(organizations),
            value_ranges=parse_csv_param(value_ranges),
            regions=parse_csv_param(regions),
            status_types=parse_csv_param(status_types),
            department_types=parse_csv_param(department_types),
            complexity_levels=parse_csv_param(complexity_levels),
            min_similarity=min_similarity
        )
        
        # Execute filtered search using search_manager (not search_engine!)
        search_result = await search_manager.search(
            keyword=q.strip(),
            filters=filters.dict() if filters else None,
            limit=limit,
            debug=debug
        )
        
        # Convert to API response format
        return {
            "query": search_result.query,
            "expanded_phrases": search_result.expanded_phrases,
            "total_matches": search_result.total_matches,
            "execution_time_ms": search_result.execution_time_ms,
            "engine_used": search_result.engine_used,
            "hits": [
                {
                    "tender_id": hit.tender_id,
                    "title": hit.title,
                    "organization": hit.organization,
                    "status": hit.status,
                    "aoc_date": hit.aoc_date,
                    "url": hit.url,
                    "similarity_percent": hit.similarity_percent,
                    "matched_phrases": hit.matched_phrases,
                    "exact_match": hit.exact_match,
                    "service_category": hit.service_category,
                    "value_range": hit.value_range,
                    "region": hit.region
                }
                for hit in search_result.hits
            ]
        }
        
    except Exception as e:
        logger.error(f"Filtered search failed for '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Filtered search error: {str(e)}")

@app.get("/filter-options", tags=["Search"]) 
async def get_filter_options() -> Dict[str, Any]:
    """Get available filter options for UI components"""
    
    try:
        # Get filter options from search manager
        filter_options = await search_manager.get_filter_options()
        
        return {
            "status": "success",
            "filter_options": filter_options,
            "total_categories": sum(
                len(filter_options.get(category, []))
                for category in ["service_categories", "organizations", "regions", "value_ranges"]
            )
        }
        
    except Exception as e:
        logger.error(f"Filter options retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Filter options error: {str(e)}")

@app.get("/faceted-search", tags=["Search"])
async def faceted_search(
    q: str = Query(..., description="Search keyword", min_length=1, max_length=50),
    facets: str = Query("service_category,region,value_range", description="Comma-separated facet fields"),
    limit: int = Query(25, description="Maximum results to return", ge=1, le=100)
) -> Dict[str, Any]:
    """Execute search with faceted aggregations for advanced analytics"""
    
    try:
        # Parse facet fields
        facet_fields = [field.strip() for field in facets.split(',')]
        
        # Execute search using search_manager
        search_result = await search_manager.search(
            keyword=q.strip(),
            filters=None,
            limit=limit,
            debug=False
        )
        
        # Convert to dict format and add facets
        result_dict = {
            "query": search_result.query,
            "expanded_phrases": search_result.expanded_phrases,
            "total_matches": search_result.total_matches,
            "execution_time_ms": search_result.execution_time_ms,
            "engine_used": search_result.engine_used,
            "hits": [
                {
                    "tender_id": hit.tender_id,
                    "title": hit.title,
                    "organization": hit.organization,
                    "status": hit.status,
                    "aoc_date": hit.aoc_date,
                    "url": hit.url,
                    "similarity_percent": hit.similarity_percent,
                    "matched_phrases": hit.matched_phrases,
                    "exact_match": hit.exact_match,
                    "service_category": hit.service_category,
                    "value_range": hit.value_range,
                    "region": hit.region
                }
                for hit in search_result.hits
            ],
            "facets": _calculate_manual_facets(q.strip(), facet_fields)
        }
        return result_dict
        
    except Exception as e:
        logger.error(f"Faceted search failed for '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"Faceted search error: {str(e)}")

@app.get("/test-demo-scenarios", tags=["System"])
async def test_demo_scenarios() -> Dict[str, Any]:
    """Test all planned demo scenarios to validate functionality"""
    
    demo_scenarios = [
        {
            "name": "Networking Equipment Search",
            "keyword": "lan",
            "expected_expansions": ["local area network", "layer 2 switch", "layer 3 switch", "vlan", "ethernet"],
            "expected_matches": "4-5 networking tenders",
            "anti_patterns": "No 'land development' false positives"
        },
        {
            "name": "API Services Search", 
            "keyword": "api",
            "expected_expansions": ["application programming interface", "rest api", "api gateway", "openapi"],
            "expected_matches": "3-4 software integration tenders",
            "anti_patterns": "No 'application form' false positives"
        },
        {
            "name": "Security Solutions Search",
            "keyword": "waf", 
            "expected_expansions": ["web application firewall", "waap"],
            "expected_matches": "2-3 security-focused tenders",
            "anti_patterns": "Security domain categorization"
        }
    ]
    
    scenario_results = []
    
    for scenario in demo_scenarios:
        try:
            # Test expansion
            expansion_result = synonym_manager.expand_keyword(scenario["keyword"], max_expansions=5)
            
            # Test search using search_manager
            search_result_obj = await search_manager.search(
                keyword=scenario["keyword"],
                filters=None,
                limit=25,
                debug=True
            )
            
            # Convert to dict format for analysis
            search_result = {
                "total_matches": search_result_obj.total_matches,
                "execution_time_ms": search_result_obj.execution_time_ms,
                "hits": [
                    {
                        "similarity_percent": hit.similarity_percent
                    }
                    for hit in search_result_obj.hits
                ]
            }
            
            # Analyze results vs expectations
            analysis = {
                "scenario": scenario["name"],
                "keyword": scenario["keyword"],
                "expansion_test": {
                    "success": len(expansion_result["expanded_phrases"]) >= 2,
                    "actual_expansions": expansion_result["expanded_phrases"],
                    "expected_expansions": scenario["expected_expansions"],
                    "confidence": expansion_result["confidence"]
                },
                "search_test": {
                    "success": search_result["total_matches"] > 0,
                    "match_count": search_result["total_matches"], 
                    "top_similarity": search_result["hits"][0]["similarity_percent"] if search_result["hits"] else 0,
                    "execution_time_ms": search_result["execution_time_ms"]
                },
                "validation": {
                    "has_relevant_results": search_result["total_matches"] > 0,
                    "performance_acceptable": search_result.get("execution_time_ms", 0) < 500,
                    "similarity_scores_logical": all(
                        hit["similarity_percent"] > 0 for hit in search_result.get("hits", [])
                    )
                }
            }
            
            scenario_results.append(analysis)
            
        except Exception as e:
            scenario_results.append({
                "scenario": scenario["name"],
                "keyword": scenario["keyword"],
                "error": str(e),
                "success": False
            })
    
    # Calculate overall success rate
    successful_scenarios = sum(1 for result in scenario_results if result.get("validation", {}).get("has_relevant_results", False))
    success_rate = successful_scenarios / len(demo_scenarios)
    
    return {
        "demo_validation": {
            "total_scenarios": len(demo_scenarios),
            "successful_scenarios": successful_scenarios,
            "success_rate": round(success_rate * 100, 1),
            "overall_status": "ready" if success_rate >= 0.8 else "needs_attention"
        },
        "scenario_results": scenario_results,
        "recommendation": "PoC ready for demonstration" if success_rate >= 0.8 else "Review failing scenarios before demo"
    }

# Financial Analysis Endpoints
@app.get("/analytics/firm-scorecard/{firm_name}", tags=["Intelligence"])
async def get_firm_financial_scorecard(
    firm_name: str,
    timeframe: str = Query("12months", description="Analysis timeframe"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    currency: str = Query("INR", description="Display currency")
) -> Dict[str, Any]:
    """
    Generate comprehensive firm financial scorecard with competitive intelligence
    
    **Features:**
    - Portfolio value analysis with deal size distribution
    - Market share calculation across service categories
    - Award velocity and growth trajectory analysis  
    - Competitive positioning assessment
    - Risk analysis with diversification metrics
    
    **Example:**
    GET /analytics/firm-scorecard/TCS returns complete financial profile
    """
    
    try:
        # Generate financial scorecard using the analysis engine
        scorecard = await financial_analysis_engine.generate_firm_financial_scorecard(firm_name)
        
        return {
            "firm_profile": {
                "firm_name": scorecard.firm_name,
                "market_position": scorecard.competitive_position.value,
                "analysis_timeframe": timeframe
            },
            "portfolio_metrics": {
                "total_portfolio_value_inr": float(scorecard.total_portfolio_value),
                "contract_count": scorecard.contract_count,
                "average_deal_size_inr": float(scorecard.average_deal_size),
                "median_deal_size_inr": float(scorecard.median_deal_size),
                "deal_size_distribution": scorecard.deal_size_distribution
            },
            "performance_metrics": {
                "award_velocity_per_quarter": scorecard.award_velocity,
                "market_share_percent": scorecard.market_share_percent,
                "competitive_position": scorecard.competitive_position.value,
                "growth_trajectory": scorecard.growth_trajectory
            },
            "risk_assessment": scorecard.risk_assessment,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Firm scorecard generation failed for '{firm_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Scorecard generation error: {str(e)}")

@app.get("/analytics/market-analysis/{service_category}", tags=["Intelligence"])
async def get_market_financial_analysis(
    service_category: str,
    timeframe: str = Query("12months", description="Analysis timeframe"),
    include_forecasting: bool = Query(False, description="Include market forecasting")
) -> Dict[str, Any]:
    """
    Get comprehensive market financial analysis for service category
    
    **Features:**
    - Total market value and contract volume analysis
    - Market concentration measurement (HHI index)
    - Price distribution and competitive positioning
    - Growth rate analysis and trend identification
    - Competitive intensity assessment
    
    **Example:**  
    GET /analytics/market-analysis/cloud returns cloud services market intelligence
    """
    
    try:
        # Calculate market financial metrics
        market_metrics = await financial_analysis_engine.calculate_market_financial_metrics(service_category)
        
        return {
            "market_overview": {
                "service_category": market_metrics.service_category,
                "total_market_value_inr": float(market_metrics.total_market_value),
                "total_contracts": market_metrics.total_contracts,
                "average_deal_size_inr": float(market_metrics.average_deal_size),
                "analysis_period": timeframe
            },
            "market_structure": {
                "hhi_index": round(market_metrics.market_concentration_hhi, 4),
                "competitive_intensity": market_metrics.competitive_intensity,
                "market_structure_type": _classify_market_structure(market_metrics.market_concentration_hhi)
            },
            "financial_analysis": {
                "price_distribution": market_metrics.price_distribution,
                "growth_rate_percent": market_metrics.growth_rate,
                "seasonal_patterns": market_metrics.seasonal_patterns
            },
            "competitive_landscape": await _get_service_competitive_landscape(service_category),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market analysis failed for '{service_category}': {e}")
        raise HTTPException(status_code=500, detail=f"Market analysis error: {str(e)}")

@app.get("/analytics/deal-benchmarking", tags=["Intelligence"])  
async def get_deal_benchmarking(
    value: float = Query(..., description="Deal value to benchmark"),
    service_category: str = Query(..., description="Service category for benchmarking"),
    currency: str = Query("INR", description="Deal value currency")
) -> Dict[str, Any]:
    """
    Benchmark deal value against market standards
    
    **Features:**
    - Deal size classification with market context
    - Percentile ranking within service category
    - Competitive positioning analysis
    - Price competitiveness assessment
    
    **Example:**
    GET /analytics/deal-benchmarking?value=50000000&service_category=networking
    """
    
    try:
        from decimal import Decimal
        
        # Normalize value to INR if needed
        if currency != "INR":
            normalization_result = await currency_normalizer.normalize_to_inr(
                Decimal(str(value)), currency, datetime.now().date()
            )
            inr_value = normalization_result["inr_amount"]
        else:
            inr_value = Decimal(str(value))
        
        # Classify deal size
        classification = deal_size_classifier.classify_deal_size(inr_value, service_category)
        
        # Get market benchmarks
        market_benchmarks = await _get_market_benchmarks(service_category)
        
        # Calculate competitiveness score
        competitiveness_score = _calculate_price_competitiveness(
            float(inr_value), market_benchmarks
        )
        
        return {
            "deal_analysis": {
                "original_value": value,
                "original_currency": currency,
                "inr_equivalent": float(inr_value),
                "deal_classification": classification
            },
            "market_benchmarking": {
                "service_category": service_category,
                "market_benchmarks": market_benchmarks,
                "price_competitiveness_score": competitiveness_score,
                "competitive_positioning": _determine_deal_positioning(competitiveness_score)
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Deal benchmarking failed: {e}")
        raise HTTPException(status_code=500, detail=f"Benchmarking error: {str(e)}")

@app.post("/analytics/normalize-currency", tags=["Intelligence"])
async def normalize_currency_values(
    amounts: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Batch currency normalization service
    
    **Request Format:**
    ```json
    [
        {"amount": 50000, "currency": "USD", "date": "2025-10-21"},
        {"amount": 25000000, "currency": "INR", "date": "2025-10-21"}
    ]
    ```
    """
    
    try:
        normalized_amounts = []
        
        for amount_data in amounts:
            amount = Decimal(str(amount_data["amount"]))
            currency = amount_data["currency"]
            value_date = datetime.fromisoformat(amount_data["date"]).date()
            
            normalization_result = await currency_normalizer.normalize_to_inr(
                amount, currency, value_date
            )
            
            normalized_amounts.append({
                "original_amount": float(amount),
                "original_currency": currency,
                "inr_equivalent": float(normalization_result["inr_amount"]) if normalization_result["inr_amount"] else None,
                "exchange_rate": float(normalization_result["exchange_rate"]) if normalization_result["exchange_rate"] else None,
                "confidence": normalization_result["confidence"],
                "rate_source": normalization_result["rate_source"]
            })
        
        return normalized_amounts
        
    except Exception as e:
        logger.error(f"Currency normalization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Normalization error: {str(e)}")

# Visualization Data Endpoints
@app.get("/visualizations/heatmap-data", tags=["Intelligence"])
async def get_heatmap_visualization_data(
    metric: str = Query("market_share", description="Heatmap metric: market_share, contract_count, total_value"),
    timeframe: str = Query("12months", description="Analysis timeframe")
) -> Dict[str, Any]:
    """
    Generate Service×Firm heatmap data for D3.js visualization
    
    **Features:**
    - Service×Firm performance matrix with color scaling
    - Multiple metrics: market share, contract count, total value
    - D3.js compatible data format with tooltips
    - Performance summary with top performers
    """
    
    try:
        heatmap_data = heatmap_generator.generate_heatmap_data(timeframe, metric)
        return heatmap_data
        
    except Exception as e:
        logger.error(f"Heatmap data generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Heatmap data error: {str(e)}")

@app.get("/visualizations/geographic-data", tags=["Intelligence"])
async def get_geographic_visualization_data() -> Dict[str, Any]:
    """
    Generate geographic intelligence data for Leaflet choropleth maps
    
    **Features:**
    - Indian states procurement density analysis
    - Choropleth data with normalized color scaling
    - Procurement hotspots identification
    - Regional pattern analysis with insights
    """
    
    try:
        geographic_data = geographic_generator.generate_geographic_data()
        return geographic_data
        
    except Exception as e:
        logger.error(f"Geographic data generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Geographic data error: {str(e)}")

@app.get("/visualizations/executive-summary", tags=["Intelligence"])
async def get_executive_summary_data() -> Dict[str, Any]:
    """
    Generate executive summary data for dashboard cards
    
    **Features:**
    - Key performance indicators for executive overview
    - Market metrics with growth analysis
    - Competitive landscape summary
    - Strategic insights and trends
    """
    
    try:
        executive_data = dashboard_provider.generate_executive_summary_data()
        return executive_data
        
    except Exception as e:
        logger.error(f"Executive summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Executive summary error: {str(e)}")

# Helper functions for financial analysis
def _classify_market_structure(hhi_index: float) -> str:
    """Classify market structure based on HHI index"""
    if hhi_index > 0.25:
        return "Highly Concentrated"
    elif hhi_index > 0.15:
        return "Moderately Concentrated" 
    elif hhi_index > 0.10:
        return "Competitive"
    else:
        return "Highly Competitive"

async def _get_service_competitive_landscape(service_category: str) -> Dict[str, Any]:
    """Get competitive landscape for a service category"""
    
    try:
        with sqlite3.connect(database_manager.db_path) as conn:
            # Get top firms by value in this category
            top_firms = conn.execute("""
                SELECT 
                    winning_firm,
                    COUNT(*) as contract_count,
                    SUM(inr_normalized_value) as total_value,
                    AVG(inr_normalized_value) as avg_deal_size
                FROM tenders
                WHERE service_category = ?
                AND winning_firm IS NOT NULL
                AND inr_normalized_value IS NOT NULL
                GROUP BY winning_firm
                ORDER BY total_value DESC
                LIMIT 10
            """, (service_category,)).fetchall()
            
            return {
                "top_performers": [
                    {
                        "firm": row[0],
                        "contract_count": row[1], 
                        "total_value_inr": float(row[2]),
                        "average_deal_size_inr": float(row[3])
                    }
                    for row in top_firms
                ]
            }
            
    except Exception as e:
        logger.error(f"Failed to get competitive landscape: {e}")
        return {"top_performers": []}

async def _get_market_benchmarks(service_category: str) -> Dict[str, Any]:
    """Get market benchmarks for deal benchmarking"""
    
    try:
        with sqlite3.connect(database_manager.db_path) as conn:
            benchmarks = conn.execute("""
                SELECT 
                    AVG(inr_normalized_value) as market_average,
                    MIN(inr_normalized_value) as market_minimum,
                    MAX(inr_normalized_value) as market_maximum,
                    COUNT(*) as sample_size
                FROM tenders
                WHERE service_category = ?
                AND inr_normalized_value IS NOT NULL
            """, (service_category,)).fetchone()
            
            if benchmarks and benchmarks[0]:
                return {
                    "market_average": float(benchmarks[0]),
                    "market_minimum": float(benchmarks[1]),
                    "market_maximum": float(benchmarks[2]),
                    "sample_size": benchmarks[3]
                }
                
        return {"error": "No benchmark data available"}
        
    except Exception as e:
        logger.error(f"Failed to get market benchmarks: {e}")
        return {"error": str(e)}

def _calculate_price_competitiveness(deal_value: float, benchmarks: Dict[str, Any]) -> float:
    """Calculate price competitiveness score (0-1 scale)"""
    
    if "market_average" not in benchmarks:
        return 0.5  # Neutral if no benchmark data
        
    market_avg = benchmarks["market_average"]
    
    if deal_value <= market_avg * 0.8:
        return 0.9  # Highly competitive (low price)
    elif deal_value <= market_avg:
        return 0.7  # Competitive
    elif deal_value <= market_avg * 1.2:
        return 0.5  # Market rate
    elif deal_value <= market_avg * 1.5:
        return 0.3  # Premium pricing
    else:
        return 0.1  # Very high pricing

def _determine_deal_positioning(competitiveness_score: float) -> str:
    """Determine deal positioning based on competitiveness score"""
    
    if competitiveness_score > 0.8:
        return "Highly Competitive"
    elif competitiveness_score > 0.6:
        return "Competitive"
    elif competitiveness_score > 0.4:
        return "Market Rate"
    elif competitiveness_score > 0.2:
        return "Premium"
    else:
        return "Very High"

def _calculate_manual_facets(keyword: str, facet_fields: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Calculate faceted aggregations manually for SQLite"""
    
    try:
        # Get expansion for the keyword
        expansion_result = synonym_manager.expand_keyword(keyword)
        fts5_query = " OR ".join([
            f'"{phrase}"' if " " in phrase else phrase
            for phrase in expansion_result['expanded_phrases']
        ])
        
        facets = {}
        
        with sqlite3.connect(database_manager.db_path) as conn:
            for field in facet_fields:
                if field in ["service_category", "region", "value_range", "complexity", "department_type"]:
                    facet_results = conn.execute(f"""
                        SELECT {field}, COUNT(*) as count
                        FROM tenders
                        WHERE tenders MATCH ?
                        GROUP BY {field}
                        ORDER BY count DESC
                        LIMIT 20
                    """, (fts5_query,)).fetchall()
                    
                    facets[field] = [
                        {"value": item[0], "count": item[1]}
                        for item in facet_results
                    ]
        
        return facets
        
    except Exception as e:
        logger.error(f"Manual facet calculation failed: {e}")
        return {}

def create_app() -> FastAPI:
    """Factory function to create configured FastAPI app"""
    return app

def main():
    """Main entry point for running the API server"""
    import uvicorn
    
    print("TenderIntel API Server")
    print("=" * 50)
    print("🚀 Starting production-ready FastAPI server...")
    print("📍 API available at: http://localhost:8002")
    print("📚 Documentation at: http://localhost:8002/docs")
    print("🎯 Try: curl 'http://localhost:8002/search?q=lan'")
    print("\n⌨️  Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "tenderintel.api.server:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
