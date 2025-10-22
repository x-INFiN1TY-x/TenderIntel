"""
TenderIntel Data Models
======================

Pydantic models for type-safe data handling and API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date

class TenderRecord(BaseModel):
    """Represents a government tender record with competitive intelligence"""
    
    tender_id: str = Field(..., description="Unique tender identifier")
    title: str = Field(..., description="Tender title/description")
    organization: str = Field(..., description="Issuing organization")
    department: Optional[str] = Field(None, description="Department/division")
    status: str = Field(..., description="Current tender status")
    published_date: Optional[date] = Field(None, description="Publication date")
    closing_date: Optional[date] = Field(None, description="Closing date")
    aoc_date: Optional[date] = Field(None, description="Award of Contract date")
    tender_value: Optional[float] = Field(None, description="Estimated/awarded value")
    url: str = Field(..., description="Source portal URL")
    
    # Competitive intelligence fields
    service_category: Optional[str] = Field(None, description="Primary service category")
    sub_category: Optional[str] = Field(None, description="Detailed subcategory")
    detected_firms: List[str] = Field(default_factory=list, description="Detected competitor firms")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    complexity_level: Optional[str] = Field(None, description="Complexity assessment")
    region: Optional[str] = Field(None, description="Geographic region")
    technology_stack: List[str] = Field(default_factory=list, description="Technology stack")
    
    # Search metadata
    similarity_percent: Optional[int] = Field(None, description="Search similarity percentage")
    matched_phrases: List[str] = Field(default_factory=list, description="Matched search phrases")

class SearchResult(BaseModel):
    """Search result with metadata and competitive intelligence"""
    
    query: str = Field(..., description="Original search query")
    phrases: List[str] = Field(..., description="Expanded search phrases")
    domain: str = Field(..., description="Detected domain")
    confidence: float = Field(..., description="Expansion confidence score")
    total_matches: int = Field(..., description="Total number of matches")
    execution_time_ms: float = Field(..., description="Search execution time")
    hits: List[TenderRecord] = Field(..., description="Search results")
    
    # Advanced search metadata
    filters_applied: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")
    fts5_query: Optional[str] = Field(None, description="Generated FTS5 query")
    engine_type: str = Field(default="sqlite_fts5", description="Search engine type")

class CompetitiveIntelligence(BaseModel):
    """Competitive intelligence analysis results"""
    
    market_overview: Dict[str, Any] = Field(..., description="Market overview metrics")
    service_category_analysis: List[Dict[str, Any]] = Field(..., description="Service category breakdown")
    organization_performance: List[Dict[str, Any]] = Field(..., description="Organization performance metrics")
    regional_distribution: List[Dict[str, Any]] = Field(..., description="Regional distribution analysis")
    data_quality: Dict[str, Any] = Field(..., description="Data quality assessment")

class MarketAnalysis(BaseModel):
    """Market analysis with trends and insights"""
    
    service_category: str = Field(..., description="Service category analyzed")
    total_tenders: int = Field(..., description="Total tenders in category")
    top_performers: List[str] = Field(..., description="Top performing firms")
    market_concentration: float = Field(..., description="Market concentration index")
    average_value: Optional[float] = Field(None, description="Average tender value")
    growth_trend: Optional[str] = Field(None, description="Growth trend direction")
    competitive_intensity: str = Field(..., description="Competition level")

class HealthStatus(BaseModel):
    """System health check results"""
    
    status: str = Field(..., description="Overall system status")
    checks: Dict[str, Any] = Field(..., description="Individual component checks")
    system_info: Dict[str, Any] = Field(..., description="System information")

class ScrapingResult(BaseModel):
    """Results from portal scraping operations"""
    
    scraping_status: str = Field(..., description="Scraping operation status")
    source: str = Field(..., description="Data source portal")
    execution_results: Dict[str, Any] = Field(..., description="Execution metrics")
    competitive_intelligence: Dict[str, Any] = Field(..., description="Intelligence summary")
    sample_tenders: List[Dict[str, Any]] = Field(..., description="Sample processed tenders")
