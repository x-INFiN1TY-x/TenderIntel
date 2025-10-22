#!/usr/bin/env python3
"""
Search Engine Interface for Smart Tender Search PoC
Abstract interface supporting both SQLite FTS5 and OpenSearch engines
"""

from typing import Protocol, Dict, Any, List, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel
from datetime import datetime

class SearchFilters(BaseModel):
    """Enhanced filtering parameters for categorical search"""
    
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    organizations: Optional[List[str]] = None
    service_categories: Optional[List[str]] = None
    value_ranges: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    status_types: Optional[List[str]] = None
    department_types: Optional[List[str]] = None
    complexity_levels: Optional[List[str]] = None
    min_similarity: Optional[int] = 0
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        extra = "forbid"

class SearchEngineInterface(Protocol):
    """Protocol defining the interface all search engines must implement"""
    
    def execute_search(
        self,
        keyword: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 25,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Execute intelligent search with expansion, filtering, and ranking
        
        Args:
            keyword: Original search keyword
            filters: Optional categorical filters
            limit: Maximum results to return
            debug: Include debug information
            
        Returns:
            Comprehensive search results with similarity percentages
        """
        ...
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get search engine health status
        
        Returns:
            Health information and performance metrics
        """
        ...
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive search engine statistics
        
        Returns:
            Statistics about indexed data and performance
        """
        ...
    
    def get_filter_options(self) -> Dict[str, Any]:
        """
        Get available filter options for UI components
        
        Returns:
            Available categories, organizations, regions, etc.
        """
        ...

class SearchEngineAdapter:
    """Adapter pattern for managing multiple search engine implementations"""
    
    def __init__(self, engine_type: str = "sqlite", config: Optional[Dict[str, Any]] = None):
        """
        Initialize search engine adapter
        
        Args:
            engine_type: Type of search engine ('sqlite', 'opensearch')
            config: Engine-specific configuration parameters
        """
        self.engine_type = engine_type
        self.config = config or {}
        self.engine = self._initialize_engine()
    
    def _initialize_engine(self) -> SearchEngineInterface:
        """Initialize the appropriate search engine implementation"""
        
        if self.engine_type == "sqlite":
            from .sqlite_fts5_engine import SQLiteFTS5Engine
            return SQLiteFTS5Engine(self.config.get("db_path", "engine/tenders.db"))
        
        elif self.engine_type == "opensearch":
            from .opensearch_engine import OpenSearchEngine
            return OpenSearchEngine(self.config)
        
        else:
            raise ValueError(f"Unsupported engine type: {self.engine_type}")
    
    def execute_search(self, keyword: str, filters: Optional[SearchFilters] = None, limit: int = 25, debug: bool = False) -> Dict[str, Any]:
        """Delegate search to underlying engine"""
        return self.engine.execute_search(keyword, filters, limit, debug)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Delegate health check to underlying engine"""
        return self.engine.get_health_status()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Delegate statistics to underlying engine"""
        return self.engine.get_statistics()
    
    def get_filter_options(self) -> Dict[str, Any]:
        """Delegate filter options to underlying engine"""
        return self.engine.get_filter_options()
    
    def switch_engine(self, new_engine_type: str, new_config: Optional[Dict[str, Any]] = None):
        """Switch to a different search engine implementation"""
        
        logger.info(f"Switching from {self.engine_type} to {new_engine_type}")
        
        # Validate new engine type
        if new_engine_type not in ["sqlite", "opensearch"]:
            raise ValueError(f"Unsupported engine type: {new_engine_type}")
        
        # Update configuration
        self.engine_type = new_engine_type
        if new_config:
            self.config.update(new_config)
        
        # Initialize new engine
        self.engine = self._initialize_engine()
        
        logger.info(f"Successfully switched to {new_engine_type} engine")
    
    def compare_engines(self, keyword: str, engines: List[str]) -> Dict[str, Any]:
        """Compare performance and results across different engines"""
        
        comparison_results = {}
        
        for engine_type in engines:
            try:
                # Temporarily switch to comparison engine
                original_engine_type = self.engine_type
                original_config = self.config.copy()
                
                self.switch_engine(engine_type, self.config)
                
                # Execute test search
                start_time = datetime.now()
                search_result = self.execute_search(keyword, limit=10)
                end_time = datetime.now()
                
                comparison_results[engine_type] = {
                    "search_time_ms": (end_time - start_time).total_seconds() * 1000,
                    "total_matches": search_result.get("total_matches", 0),
                    "top_similarity": search_result["hits"][0]["similarity_percent"] if search_result.get("hits") else 0,
                    "status": "success"
                }
                
                # Restore original engine
                self.switch_engine(original_engine_type, original_config)
                
            except Exception as e:
                comparison_results[engine_type] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "keyword": keyword,
            "engines_compared": engines,
            "comparison_results": comparison_results,
            "comparison_time": datetime.now().isoformat()
        }

# Factory function for easy engine creation
def create_search_engine(engine_type: str = "sqlite", config: Optional[Dict[str, Any]] = None) -> SearchEngineAdapter:
    """
    Factory function to create search engine instances
    
    Args:
        engine_type: Type of search engine to create
        config: Engine-specific configuration
        
    Returns:
        Configured search engine adapter
    """
    return SearchEngineAdapter(engine_type, config)

def main():
    """Test search engine interface and adapter functionality"""
    print("Smart Tender Search PoC - Search Engine Interface")
    print("=" * 55)
    
    # Test engine adapter
    print("🔧 Testing SearchEngineAdapter...")
    
    try:
        # Create SQLite engine adapter
        sqlite_engine = create_search_engine("sqlite", {"db_path": "engine/tenders.db"})
        
        # Test health check
        health = sqlite_engine.get_health_status()
        print(f"   SQLite Engine Health: {health.get('status', 'unknown')}")
        
        # Test basic functionality  
        if health.get('status') == 'healthy':
            # Test search (if data is loaded)
            search_result = sqlite_engine.execute_search("lan", limit=3)
            print(f"   Test search results: {search_result.get('total_matches', 0)} matches")
            
            # Test filter options
            filter_options = sqlite_engine.get_filter_options()
            print(f"   Filter options available: {len(filter_options)} categories")
        
        print("✅ SearchEngineAdapter test completed successfully!")
        
    except Exception as e:
        print(f"❌ SearchEngineAdapter test failed: {e}")
        logger.error(f"Engine adapter test failed: {e}")
    
    print("\n📋 Available Engine Types:")
    print("   - sqlite: SQLite FTS5 with BM25 ranking")
    print("   - opensearch: OpenSearch with synonym_graph (Phase 2)")
    
    print("\n🎯 Usage Example:")
    print("   engine = create_search_engine('sqlite')")
    print("   results = engine.execute_search('lan')")
    print("   health = engine.get_health_status()")

if __name__ == "__main__":
    main()
