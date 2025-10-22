#!/usr/bin/env python3
"""
Search module for TenderIntel
Provides intelligent search with synonym expansion and BM25 ranking

Supports multiple search engines with user choice flexibility:
- SQLite FTS5 (default, always available)
- OpenSearch (optional, for large-scale deployments)
"""

# Core components
from .synonym_manager import SynonymManager
from .base import (
    SearchEngine, SearchEngineType, UnifiedSearchResponse, UnifiedSearchHit,
    EngineCapabilities, EngineHealthStatus, EngineStatistics
)

# Engine implementations
from .engines import SQLiteFTS5Engine, OpenSearchEngine, OPENSEARCH_AVAILABLE

# Unified manager (recommended interface)
from .manager import UnifiedSearchManager, create_search_manager

# Legacy interface (backwards compatibility)
from .search_engine_interface import SearchFilters, SearchEngineInterface

__all__ = [
    # Recommended interface
    'UnifiedSearchManager',
    'create_search_manager',
    
    # Base classes
    'SearchEngine',
    'SearchEngineType',
    'UnifiedSearchResponse',
    'UnifiedSearchHit',
    
    # Engine implementations
    'SQLiteFTS5Engine',
    'OpenSearchEngine',
    'OPENSEARCH_AVAILABLE',
    
    # Utilities
    'SynonymManager',
    
    # Legacy (backwards compatibility)
    'SearchFilters',
    'SearchEngineInterface'
]
