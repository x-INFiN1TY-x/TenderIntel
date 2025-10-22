#!/usr/bin/env python3
"""
Unified Search Manager for TenderIntel
Single interface that handles engine selection, fallback, and transparent routing
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import (
    SearchEngine, SearchEngineType, UnifiedSearchResponse,
    EngineHealthStatus, EngineStatistics
)
from .engines import SQLiteFTS5Engine, OpenSearchEngine, OPENSEARCH_AVAILABLE
from .synonym_manager import SynonymManager

logger = logging.getLogger(__name__)


class UnifiedSearchManager:
    """
    Unified search interface - handles engine selection transparently
    
    This is the ONLY class the rest of the application interacts with.
    Users and API never directly touch SQLite or OpenSearch engines.
    
    Features:
    - Automatic engine initialization based on config
    - Graceful fallback to SQLite if OpenSearch unavailable
    - Intelligent recommendations based on usage patterns
    - Transparent routing - same API regardless of engine
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize unified search manager
        
        Args:
            config: Complete application configuration
        """
        self.config = config
        self.search_config = config.get('search', {})
        
        # Shared synonym manager (engine-agnostic)
        # Note: SynonymManager doesn't take config args yet
        self.synonym_manager = SynonymManager()
        
        # Current active engine
        self.current_engine: Optional[SearchEngine] = None
        
        # Initialize engine with fallback logic
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """
        Initialize search engine based on configuration with graceful fallback
        
        Priority:
        1. Try requested engine (from config)
        2. If that fails, fall back to SQLite
        3. SQLite should always succeed (it's always available)
        """
        
        requested_engine = self.search_config.get('engine', 'sqlite').lower()
        
        logger.info(f"Initializing search engine: {requested_engine}")
        
        try:
            if requested_engine == 'opensearch':
                self.current_engine = self._try_initialize_opensearch()
            else:
                self.current_engine = self._initialize_sqlite()
        except Exception as e:
            logger.error(f"Failed to initialize {requested_engine} engine: {e}")
            logger.info("Falling back to SQLite FTS5")
            self.current_engine = self._initialize_sqlite()
    
    def _try_initialize_opensearch(self) -> SearchEngine:
        """
        Try to initialize OpenSearch with comprehensive checks
        
        Returns:
            OpenSearch engine if successful, SQLite engine as fallback
        """
        
        # Check 1: Is OpenSearch library installed?
        if not OPENSEARCH_AVAILABLE:
            logger.warning(
                "OpenSearch requested but opensearch-py not installed.\n"
                "  Install with: pip install tenderintel[opensearch]\n"
                "  Falling back to SQLite FTS5"
            )
            return self._initialize_sqlite()
        
        # Check 2: Is OpenSearch enabled in config?
        opensearch_config = self.search_config.get('opensearch', {})
        if not opensearch_config.get('enabled', False):
            logger.warning(
                "OpenSearch library installed but not enabled in config.\n"
                "  Set search.opensearch.enabled=true in config.yaml\n"
                "  Using SQLite FTS5"
            )
            return self._initialize_sqlite()
        
        # Check 3: Are hosts configured?
        if not opensearch_config.get('hosts'):
            logger.error(
                "OpenSearch enabled but no hosts configured.\n"
                "  Add search.opensearch.hosts to config.yaml\n"
                "  Falling back to SQLite FTS5"
            )
            return self._initialize_sqlite()
        
        # Check 4: Can we connect to cluster?
        try:
            engine = OpenSearchEngine(opensearch_config)
            
            # Test connection with timeout
            health = asyncio.run(
                asyncio.wait_for(engine.health_check(), timeout=5.0)
            )
            
            if not health.is_healthy:
                logger.warning(
                    f"OpenSearch cluster unhealthy: {health.status}\n"
                    f"  Message: {health.message}\n"
                    f"  Falling back to SQLite FTS5"
                )
                return self._initialize_sqlite()
            
            logger.info(f"✓ OpenSearch engine initialized successfully")
            logger.info(f"  Cluster status: {health.status}")
            logger.info(f"  Details: {health.details}")
            return engine
            
        except asyncio.TimeoutError:
            logger.warning(
                "OpenSearch health check timeout (5s).\n"
                "  Check if OpenSearch cluster is running.\n"
                "  Falling back to SQLite FTS5"
            )
            return self._initialize_sqlite()
        except Exception as e:
            logger.warning(
                f"OpenSearch connection failed: {e}\n"
                f"  Falling back to SQLite FTS5"
            )
            return self._initialize_sqlite()
    
    def _initialize_sqlite(self) -> SearchEngine:
        """
        Initialize SQLite engine - should always succeed
        
        Returns:
            SQLite FTS5 engine
        """
        sqlite_config = self.search_config.get('sqlite', {})
        
        try:
            engine = SQLiteFTS5Engine(sqlite_config)
            
            logger.info("✓ SQLite FTS5 engine initialized successfully")
            logger.info(f"  Database: {sqlite_config.get('database_path', 'data/tenders.db')}")
            logger.info(f"  Tokenizer: {sqlite_config.get('fts5_tokenizer', 'porter unicode61')}")
            
            return engine
            
        except Exception as e:
            logger.critical(f"Failed to initialize SQLite engine: {e}")
            raise RuntimeError(
                f"Cannot initialize search engine. SQLite initialization failed: {e}"
            )
    
    # ===== Public API - Same Regardless of Engine =====
    
    async def search(
        self,
        keyword: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 25,
        offset: int = 0,
        debug: bool = False
    ) -> UnifiedSearchResponse:
        """
        Execute search - user doesn't know which engine is used
        
        This method signature never changes, regardless of engine.
        
        Args:
            keyword: Search keyword
            filters: Optional filters (year, organization, status, etc.)
            limit: Maximum results
            offset: Pagination offset
            debug: Include debug information
        
        Returns:
            UnifiedSearchResponse with consistent structure
        """
        
        # Step 1: Expand keyword (engine-agnostic)
        expansion = self.synonym_manager.expand_keyword(keyword)
        
        # Step 2: Execute on current engine
        result = await self.current_engine.execute_search(
            keyword=keyword,
            expanded_phrases=expansion['expanded_phrases'],
            filters=filters,
            limit=limit,
            offset=offset,
            debug=debug
        )
        
        # Step 3: Add expansion metadata
        result.domain = expansion.get('domain')
        result.confidence = expansion.get('confidence')
        
        return result
    
    async def get_service_firm_heatmap(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get Service×Firm matrix data - works with both engines
        
        Args:
            filters: Optional filters to apply
        
        Returns:
            Matrix data for heatmap visualization
        """
        return await self.current_engine.get_service_firm_aggregation(filters)
    
    async def get_geographic_data(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get geographic distribution - works with both engines
        
        Args:
            filters: Optional filters to apply
        
        Returns:
            State-wise data for choropleth visualization
        """
        return await self.current_engine.get_geographic_aggregation(filters)
    
    async def get_financial_data(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get financial statistics - works with both engines
        
        Args:
            filters: Optional filters to apply
        
        Returns:
            Financial metrics and distributions
        """
        return await self.current_engine.get_financial_statistics(filters)
    
    async def get_filter_options(self) -> Dict[str, Any]:
        """
        Get available filter options - works with both engines
        
        Returns:
            Available categories, organizations, regions for UI dropdowns
        """
        return await self.current_engine.get_filter_options()
    
    async def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about current engine and recommendations
        
        Returns:
            Engine type, capabilities, health, statistics, and recommendations
        """
        
        # Get engine health and statistics
        health = await self.current_engine.health_check()
        stats = await self.current_engine.get_statistics()
        
        # Get recommendation based on usage
        recommendation = self._get_recommendation(stats)
        
        return {
            'engine_type': self.current_engine.engine_type.value,
            'engine_name': self.current_engine.capabilities.name,
            'capabilities': {
                'max_records': self.current_engine.capabilities.max_recommended_records,
                'max_users': self.current_engine.capabilities.max_concurrent_users,
                'setup_complexity': self.current_engine.capabilities.setup_complexity,
                'operational_overhead': self.current_engine.capabilities.operational_overhead,
                'supports_distributed': self.current_engine.capabilities.supports_distributed_search,
                'features': self.current_engine.capabilities.features
            },
            'health': {
                'is_healthy': health.is_healthy,
                'status': health.status,
                'message': health.message,
                'details': health.details
            },
            'statistics': {
                'record_count': stats.record_count,
                'index_size_mb': stats.index_size_mb,
                'avg_query_time_ms': stats.avg_query_time_ms,
                'last_updated': stats.last_updated.isoformat()
            },
            'recommendation': recommendation
        }
    
    def _get_recommendation(self, stats: EngineStatistics) -> Dict[str, Any]:
        """
        Provide engine recommendation based on usage patterns
        
        Args:
            stats: Current engine statistics
        
        Returns:
            Recommendation dictionary with actionable guidance
        """
        
        current_type = self.current_engine.engine_type
        
        # For SQLite engine
        if current_type == SearchEngineType.SQLITE:
            # Check if dataset is growing large
            if stats.record_count > 100_000:
                return {
                    'should_consider_opensearch': True,
                    'reason': 'Dataset exceeds 100K records',
                    'urgency': 'medium',
                    'message': (
                        f"Your dataset has {stats.record_count:,} records. "
                        "OpenSearch can provide better performance for large datasets. "
                        "Current SQLite performance is acceptable but may degrade further."
                    ),
                    'current_performance': 'acceptable',
                    'action': 'Consider OpenSearch: pip install tenderintel[opensearch]'
                }
            
            # Check if query latency is elevated
            if stats.avg_query_time_ms > 500:
                return {
                    'should_optimize': True,
                    'reason': 'Query latency elevated',
                    'urgency': 'medium',
                    'message': (
                        f"Search latency ({stats.avg_query_time_ms:.0f}ms) is higher than optimal. "
                        "First, try optimizing SQLite. If issues persist, consider OpenSearch."
                    ),
                    'current_performance': 'suboptimal',
                    'suggested_actions': [
                        'Run ANALYZE command on database',
                        'Check for missing indexes',
                        'Increase cache_size in config',
                        'Enable WAL mode if not already enabled',
                        'Consider OpenSearch if optimizations insufficient'
                    ]
                }
            
            # Performance is good
            return {
                'should_consider_opensearch': False,
                'reason': 'Current engine optimal for workload',
                'message': (
                    f"SQLite FTS5 performing excellently for your workload "
                    f"({stats.record_count:,} records, {stats.avg_query_time_ms:.1f}ms avg latency). "
                    "No need to consider OpenSearch at this time."
                ),
                'current_performance': 'excellent',
                'action': None
            }
        
        # For OpenSearch engine
        else:
            return {
                'engine_status': 'optimal',
                'message': 'OpenSearch providing excellent performance for your workload',
                'current_performance': 'excellent'
            }
    
    def get_engine_type(self) -> str:
        """
        Get current engine type
        
        Returns:
            Engine type string: 'sqlite' or 'opensearch'
        """
        return self.current_engine.engine_type.value
    
    def is_opensearch_active(self) -> bool:
        """
        Check if OpenSearch is the active engine
        
        Returns:
            True if OpenSearch is active, False otherwise
        """
        return self.current_engine.engine_type == SearchEngineType.OPENSEARCH
    
    async def reload_engine(self) -> Dict[str, Any]:
        """
        Reload engine based on current configuration
        
        Useful after configuration changes.
        
        Returns:
            Result of reload operation
        """
        old_engine_type = self.current_engine.engine_type.value
        
        try:
            self._initialize_engine()
            new_engine_type = self.current_engine.engine_type.value
            
            return {
                'success': True,
                'old_engine': old_engine_type,
                'new_engine': new_engine_type,
                'message': f'Engine reloaded: {old_engine_type} → {new_engine_type}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Engine reload failed: {e}'
            }


def create_search_manager(config: Optional[Dict[str, Any]] = None) -> UnifiedSearchManager:
    """
    Factory function to create search manager
    
    Args:
        config: Optional configuration (uses defaults if None)
    
    Returns:
        Configured UnifiedSearchManager
    """
    if config is None:
        from ..config import get_default_config
        config = get_default_config()
    
    return UnifiedSearchManager(config)


def main():
    """Test unified search manager"""
    print("TenderIntel Unified Search Manager")
    print("=" * 50)
    
    from ..config import get_default_config
    
    # Test with default config (SQLite)
    print("\n1. Testing with default config (SQLite)...")
    config = get_default_config()
    manager = UnifiedSearchManager(config)
    
    print(f"   Active engine: {manager.get_engine_type()}")
    print(f"   Is OpenSearch: {manager.is_opensearch_active()}")
    
    # Test engine info
    print("\n2. Testing engine info...")
    engine_info = asyncio.run(manager.get_engine_info())
    print(f"   Engine: {engine_info['engine_name']}")
    print(f"   Health: {engine_info['health']['status']}")
    print(f"   Records: {engine_info['statistics']['record_count']:,}")
    print(f"   Performance: {engine_info['recommendation']['current_performance']}")
    
    # Test search (if database exists)
    print("\n3. Testing search...")
    try:
        result = asyncio.run(manager.search("lan", limit=3))
        print(f"   Search executed successfully")
        print(f"   Engine used: {result.engine_used}")
        print(f"   Total matches: {result.total_matches}")
        print(f"   Execution time: {result.execution_time_ms:.2f}ms")
    except Exception as e:
        print(f"   Search test skipped: {e}")
    
    # Test OpenSearch config (will fall back to SQLite)
    print("\n4. Testing OpenSearch config (expect fallback)...")
    opensearch_config = get_default_config()
    opensearch_config['search']['engine'] = 'opensearch'
    opensearch_config['search']['opensearch']['enabled'] = True
    
    manager2 = UnifiedSearchManager(opensearch_config)
    print(f"   Requested: opensearch")
    print(f"   Active engine: {manager2.get_engine_type()}")
    print(f"   Fallback worked: {manager2.get_engine_type() == 'sqlite'}")
    
    print("\n✅ Unified search manager test completed!")


if __name__ == "__main__":
    main()
