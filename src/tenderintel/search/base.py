#!/usr/bin/env python3
"""
Abstract Base Classes for TenderIntel Search Engines
Defines the interface that both SQLite FTS5 and OpenSearch must implement
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SearchEngineType(Enum):
    """Available search engine types"""
    SQLITE = "sqlite"
    OPENSEARCH = "opensearch"


@dataclass
class EngineCapabilities:
    """
    Declares what a search engine can do
    
    Used to inform users about engine features and limitations
    """
    name: str
    supports_fuzzy: bool
    supports_highlighting: bool
    supports_nested_aggregations: bool
    supports_distributed_search: bool
    max_recommended_records: int
    max_concurrent_users: int
    setup_complexity: str  # 'simple', 'moderate', 'complex'
    operational_overhead: str  # 'low', 'medium', 'high'
    features: List[str] = field(default_factory=list)


@dataclass
class EngineHealthStatus:
    """Engine health information"""
    is_healthy: bool
    status: str  # 'green', 'yellow', 'red'
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineStatistics:
    """Engine usage statistics and metrics"""
    record_count: int
    index_size_mb: float
    avg_query_time_ms: float
    queries_per_minute: float
    last_updated: datetime
    additional_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedSearchHit:
    """
    Single search result - identical structure from both engines
    
    This ensures users get the same experience regardless of engine choice
    """
    # Core fields
    tender_id: str
    title: str
    organization: str
    status: str
    aoc_date: str
    url: str
    
    # Scoring (normalized to 0-100% for user-friendly display)
    raw_score: float
    similarity_percent: int  # 0-100, normalized per-query
    
    # Search metadata
    matched_phrases: List[str]
    highlight_snippets: Optional[Dict[str, List[str]]] = None
    exact_match: bool = False
    
    # Financial data
    award_value: Optional[float] = None
    currency: Optional[str] = None
    inr_normalized_value: Optional[float] = None
    deal_size_category: Optional[str] = None
    
    # Competitive intelligence
    service_category: Optional[str] = None
    detected_firms: Optional[List[str]] = None
    region: Optional[str] = None
    department_type: Optional[str] = None
    complexity: Optional[str] = None
    keywords: Optional[List[str]] = None
    
    # Value range (for aggregations)
    value_range: Optional[str] = None


@dataclass
class UnifiedSearchResponse:
    """
    Search response - identical structure from both engines
    
    Ensures API consistency regardless of which engine is used
    """
    query: str
    expanded_phrases: List[str]
    total_matches: int
    max_score: float
    hits: List[UnifiedSearchHit]
    execution_time_ms: float
    engine_used: str
    
    # Optional fields
    domain: Optional[str] = None
    confidence: Optional[float] = None
    aggregations: Optional[Dict[str, Any]] = None
    filters_applied: Optional[Dict[str, Any]] = None
    
    # Engine-specific debug info (doesn't break compatibility)
    engine_debug: Optional[Dict[str, Any]] = None


class SearchEngine(ABC):
    """
    Abstract search engine interface
    
    Both SQLite FTS5 and OpenSearch engines must implement this interface
    to ensure feature parity and consistent user experience.
    """
    
    @property
    @abstractmethod
    def engine_type(self) -> SearchEngineType:
        """Return engine type identifier"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> EngineCapabilities:
        """Return engine capabilities and limitations"""
        pass
    
    @abstractmethod
    async def health_check(self) -> EngineHealthStatus:
        """
        Check if engine is healthy and ready to serve requests
        
        Returns:
            EngineHealthStatus with health information
        """
        pass
    
    @abstractmethod
    async def get_statistics(self) -> EngineStatistics:
        """
        Get current engine statistics and metrics
        
        Returns:
            EngineStatistics with usage information
        """
        pass
    
    @abstractmethod
    async def execute_search(
        self,
        keyword: str,
        expanded_phrases: List[str],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 25,
        offset: int = 0,
        include_aggregations: bool = False,
        debug: bool = False
    ) -> UnifiedSearchResponse:
        """
        Execute search query with expansion and filtering
        
        Args:
            keyword: Original user keyword
            expanded_phrases: Pre-expanded synonyms/variants from SynonymManager
            filters: Optional filters (year, org, status, service_category, etc.)
            limit: Maximum results to return
            offset: Pagination offset
            include_aggregations: Whether to compute aggregations
            debug: Include debug information in response
        
        Returns:
            UnifiedSearchResponse with normalized scoring (0-100% similarity)
        """
        pass
    
    @abstractmethod
    async def get_service_firm_aggregation(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get Service×Firm matrix data for competitive intelligence
        
        Args:
            filters: Optional filters to apply
        
        Returns:
            Dict with keys: 'matrix', 'services', 'firms', 'totals'
        """
        pass
    
    @abstractmethod
    async def get_geographic_aggregation(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get geographic distribution data for choropleth visualization
        
        Args:
            filters: Optional filters to apply
        
        Returns:
            Dict with state-wise procurement data
        """
        pass
    
    @abstractmethod
    async def get_financial_statistics(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get financial analysis data (deal sizes, value distributions, etc.)
        
        Args:
            filters: Optional filters to apply
        
        Returns:
            Dict with financial metrics and distributions
        """
        pass
    
    @abstractmethod
    async def get_filter_options(self) -> Dict[str, Any]:
        """
        Get available filter options for UI components
        
        Returns:
            Dict with all available categories, orgs, regions, etc. for dropdowns
        """
        pass
    
    async def sync_from_source(
        self, 
        source_data: AsyncIterator[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Sync data from external source (for OpenSearch sync from SQLite)
        
        This is optional - only OpenSearch needs to implement this.
        SQLite can return a "not supported" message.
        
        Args:
            source_data: Async iterator of source records
        
        Returns:
            Sync statistics (records_synced, errors, time_taken, etc.)
        """
        return {
            'supported': False,
            'message': f'{self.engine_type.value} does not support external sync'
        }


# SQLite FTS5 Capabilities (Production-grade for most deployments)
SQLITE_CAPABILITIES = EngineCapabilities(
    name="SQLite FTS5",
    supports_fuzzy=True,  # Via Python implementation
    supports_highlighting=True,  # Via post-processing
    supports_nested_aggregations=True,  # Via complex SQL
    supports_distributed_search=False,  # Single-node only
    max_recommended_records=100_000,  # Excellent up to 100K
    max_concurrent_users=20,  # Good for small to medium teams
    setup_complexity='simple',  # Just a database file
    operational_overhead='low',  # No external services
    features=[
        'keyword_search', 'phrase_matching', 'proximity_search',
        'bm25_ranking', 'synonym_expansion', 'categorical_filtering',
        'service_firm_matrix', 'geographic_analysis', 'financial_statistics',
        'competitive_intelligence', 'multi_field_search', 'date_filtering'
    ]
)


# OpenSearch Capabilities (For large-scale deployments)
OPENSEARCH_CAPABILITIES = EngineCapabilities(
    name="OpenSearch",
    supports_fuzzy=True,  # Native fuzzy queries
    supports_highlighting=True,  # Native highlighting
    supports_nested_aggregations=True,  # Advanced aggregations
    supports_distributed_search=True,  # Multi-node clusters
    max_recommended_records=10_000_000,  # Scales to millions
    max_concurrent_users=1000,  # High concurrency
    setup_complexity='complex',  # Requires cluster setup
    operational_overhead='high',  # External service management
    features=[
        'keyword_search', 'phrase_matching', 'proximity_search',
        'bm25_ranking', 'synonym_expansion', 'categorical_filtering',
        'service_firm_matrix', 'geographic_analysis', 'financial_statistics',
        'competitive_intelligence', 'multi_field_search', 'date_filtering',
        'distributed_search', 'real_time_suggestions', 'ml_ranking',
        'geo_spatial_search', 'advanced_analytics', 'cluster_management'
    ]
)


def get_engine_capabilities(engine_type: SearchEngineType) -> EngineCapabilities:
    """
    Get capabilities for specified engine type
    
    Args:
        engine_type: Type of search engine
    
    Returns:
        EngineCapabilities for that engine
    """
    if engine_type == SearchEngineType.SQLITE:
        return SQLITE_CAPABILITIES
    elif engine_type == SearchEngineType.OPENSEARCH:
        return OPENSEARCH_CAPABILITIES
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")


def compare_engine_capabilities() -> Dict[str, Any]:
    """
    Compare capabilities of both engines
    
    Useful for documentation and user decision-making
    
    Returns:
        Comparison dictionary
    """
    sqlite_cap = SQLITE_CAPABILITIES
    opensearch_cap = OPENSEARCH_CAPABILITIES
    
    return {
        'sqlite': {
            'name': sqlite_cap.name,
            'max_records': f"{sqlite_cap.max_recommended_records:,}",
            'max_users': sqlite_cap.max_concurrent_users,
            'setup': sqlite_cap.setup_complexity,
            'ops_overhead': sqlite_cap.operational_overhead,
            'distributed': sqlite_cap.supports_distributed_search,
            'feature_count': len(sqlite_cap.features)
        },
        'opensearch': {
            'name': opensearch_cap.name,
            'max_records': f"{opensearch_cap.max_recommended_records:,}",
            'max_users': opensearch_cap.max_concurrent_users,
            'setup': opensearch_cap.setup_complexity,
            'ops_overhead': opensearch_cap.operational_overhead,
            'distributed': opensearch_cap.supports_distributed_search,
            'feature_count': len(opensearch_cap.features)
        },
        'recommendation': (
            'SQLite FTS5 is recommended for most deployments (<100K records, <20 users). '
            'OpenSearch is for large-scale deployments (100K+ records, 20+ concurrent users).'
        )
    }


def main():
    """Test base classes and capabilities"""
    print("TenderIntel Search Engine Base Classes")
    print("=" * 50)
    
    # Test engine capabilities
    print("\n📊 Engine Capabilities Comparison:")
    comparison = compare_engine_capabilities()
    
    print("\nSQLite FTS5:")
    for key, value in comparison['sqlite'].items():
        print(f"   {key}: {value}")
    
    print("\nOpenSearch:")
    for key, value in comparison['opensearch'].items():
        print(f"   {key}: {value}")
    
    print(f"\n💡 Recommendation:")
    print(f"   {comparison['recommendation']}")
    
    # Show feature lists
    print("\n✨ SQLite Features:")
    for feature in SQLITE_CAPABILITIES.features[:10]:
        print(f"   • {feature.replace('_', ' ').title()}")
    print(f"   ... and {len(SQLITE_CAPABILITIES.features) - 10} more")
    
    print("\n✨ OpenSearch Additional Features:")
    opensearch_only = set(OPENSEARCH_CAPABILITIES.features) - set(SQLITE_CAPABILITIES.features)
    for feature in opensearch_only:
        print(f"   • {feature.replace('_', ' ').title()}")
    
    print("\n✅ Base classes test completed!")


if __name__ == "__main__":
    main()
