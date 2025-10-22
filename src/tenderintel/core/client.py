"""
TenderIntel Client
=================

Main client interface for TenderIntel competitive intelligence platform.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import sqlite3

from .models import TenderRecord, SearchResult, CompetitiveIntelligence, MarketAnalysis
from ..search.synonym_manager import SynonymManager
from ..search.sqlite_fts5_engine import SQLiteFTS5Engine


class TenderIntelClient:
    """
    Main client interface for TenderIntel
    
    Provides high-level methods for tender search, competitive intelligence,
    and market analysis.
    
    Example:
        >>> client = TenderIntelClient()
        >>> results = client.search("api gateway")
        >>> intel = client.get_competitive_intelligence("networking")
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize TenderIntel client
        
        Args:
            db_path: Path to SQLite database (defaults to data/tenders.db)
        """
        self.db_path = db_path or "data/tenders.db"
        self.synonym_manager = SynonymManager()
        self.search_engine = SQLiteFTS5Engine(self.db_path)
    
    def search(self, keyword: str, limit: int = 25, expand: bool = True) -> SearchResult:
        """
        Execute intelligent tender search
        
        Args:
            keyword: Search term (e.g., "lan", "api", "security")
            limit: Maximum results to return
            expand: Enable keyword expansion
            
        Returns:
            SearchResult with relevant tenders and metadata
        """
        result = self.search_engine.execute_search(
            keyword=keyword,
            limit=limit,
            debug=False
        )
        
        # Convert to SearchResult model
        return SearchResult(**result)
    
    def expand_keyword(self, keyword: str, max_expansions: int = 5) -> List[str]:
        """
        Expand keyword into technical phrases
        
        Args:
            keyword: Term to expand
            max_expansions: Maximum phrases to return
            
        Returns:
            List of expanded phrases
        """
        result = self.synonym_manager.expand_keyword(keyword, max_expansions)
        return result['expanded_phrases']
    
    def get_competitive_intelligence(self, service_category: Optional[str] = None) -> CompetitiveIntelligence:
        """
        Get competitive intelligence analysis
        
        Args:
            service_category: Filter by specific category
            
        Returns:
            CompetitiveIntelligence with market analysis
        """
        # Implementation would call the actual intelligence analysis
        # For now, return empty structure
        return CompetitiveIntelligence(
            market_overview={},
            service_category_analysis=[],
            organization_performance=[],
            regional_distribution=[],
            data_quality={}
        )
    
    def analyze_market_share(self, service_category: str) -> MarketAnalysis:
        """
        Analyze market share for specific service category
        
        Args:
            service_category: Service category to analyze
            
        Returns:
            MarketAnalysis with trends and insights
        """
        return MarketAnalysis(
            service_category=service_category,
            total_tenders=0,
            top_performers=[],
            market_concentration=0.0,
            competitive_intensity="medium"
        )
