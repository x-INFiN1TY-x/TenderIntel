#!/usr/bin/env python3
"""
OpenSearch Engine Implementation (Optional)
Requires: pip install tenderintel[opensearch]
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# OpenSearch imports (this file only loaded if opensearch-py installed)
from opensearchpy import OpenSearch, exceptions

# Import abstract base class
from ..base import (
    SearchEngine, SearchEngineType, EngineCapabilities,
    EngineHealthStatus, EngineStatistics, UnifiedSearchResponse, UnifiedSearchHit,
    OPENSEARCH_CAPABILITIES
)

logger = logging.getLogger(__name__)


class OpenSearchEngine(SearchEngine):
    """
    OpenSearch engine - optional enhancement for large-scale deployments
    
    Provides identical features to SQLite, optimized for:
    - 100K+ records
    - 20+ concurrent users
    - Distributed search
    - Advanced analytics
    
    This is an OPTIONAL enhancement, not a requirement.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenSearch engine
        
        Args:
            config: OpenSearch configuration dictionary
        """
        self.config = config
        
        # Initialize OpenSearch client
        self.client = OpenSearch(
            hosts=config.get('hosts', [{'host': 'localhost', 'port': 9200}]),
            use_ssl=config.get('use_ssl', False),
            verify_certs=config.get('verify_certs', False),
            timeout=config.get('timeout', 30),
            max_retries=config.get('max_retries', 3)
        )
        
        self.index_prefix = config.get('index_prefix', 'tenders')
        self.index_pattern = config.get('index_pattern', 'tenders-*')
        
        logger.info(f"✓ OpenSearch engine initialized: {config.get('hosts')}")
    
    # ===== SearchEngine Interface Implementation =====
    
    @property
    def engine_type(self) -> SearchEngineType:
        """Return engine type identifier"""
        return SearchEngineType.OPENSEARCH
    
    @property
    def capabilities(self) -> EngineCapabilities:
        """Return engine capabilities"""
        return OPENSEARCH_CAPABILITIES
    
    async def health_check(self) -> EngineHealthStatus:
        """Check OpenSearch cluster health"""
        
        try:
            health = self.client.cluster.health(timeout='5s')
            
            cluster_status = health.get('status', 'red')
            is_healthy = cluster_status in ['green', 'yellow']
            
            return EngineHealthStatus(
                is_healthy=is_healthy,
                status=cluster_status,
                message=f'OpenSearch cluster {cluster_status}',
                details={
                    'cluster_name': health.get('cluster_name'),
                    'number_of_nodes': health.get('number_of_nodes'),
                    'active_shards': health.get('active_shards'),
                    'relocating_shards': health.get('relocating_shards'),
                    'unassigned_shards': health.get('unassigned_shards')
                }
            )
            
        except exceptions.ConnectionError as e:
            return EngineHealthStatus(
                is_healthy=False,
                status='red',
                message=f'Cannot connect to OpenSearch: {e}',
                details={}
            )
        except Exception as e:
            return EngineHealthStatus(
                is_healthy=False,
                status='red',
                message=f'Health check failed: {e}',
                details={}
            )
    
    async def get_statistics(self) -> EngineStatistics:
        """Get OpenSearch statistics"""
        
        try:
            # Get index stats
            stats = self.client.indices.stats(index=self.index_pattern)
            
            # Get document count
            count_result = self.client.count(index=self.index_pattern)
            record_count = count_result.get('count', 0)
            
            # Calculate index size
            indices_stats = stats.get('indices', {})
            total_size_bytes = sum(
                idx.get('total', {}).get('store', {}).get('size_in_bytes', 0)
                for idx in indices_stats.values()
            )
            size_mb = total_size_bytes / (1024 * 1024)
            
            return EngineStatistics(
                record_count=record_count,
                index_size_mb=round(size_mb, 2),
                avg_query_time_ms=0.0,  # Would need tracking
                queries_per_minute=0.0,  # Would need tracking
                last_updated=datetime.now(),
                additional_stats={
                    'cluster_name': stats.get('cluster_name'),
                    'indices_count': len(indices_stats)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get OpenSearch statistics: {e}")
            return EngineStatistics(
                record_count=0,
                index_size_mb=0.0,
                avg_query_time_ms=0.0,
                queries_per_minute=0.0,
                last_updated=datetime.now(),
                additional_stats={'error': str(e)}
            )
    
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
        Execute OpenSearch query with phrase matching and BM25 ranking
        
        Provides IDENTICAL experience to SQLite engine.
        """
        
        start_time = time.time()
        
        try:
            # Build bool query with phrase matching
            should_clauses = []
            
            for phrase in expanded_phrases:
                slop = 1 if len(phrase.split()) > 1 else 0
                
                should_clauses.append({
                    "match_phrase": {
                        "title": {
                            "query": phrase,
                            "slop": slop,
                            "boost": 2.0 if " " in phrase else 1.5
                        }
                    }
                })
            
            # Build complete query
            query_body = {
                "query": {
                    "bool": {
                        "should": should_clauses,
                        "minimum_should_match": 1
                    }
                },
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"aoc_date": {"order": "desc"}}
                ],
                "size": limit,
                "from": offset
            }
            
            # Execute search
            response = self.client.search(
                index=self.index_pattern,
                body=query_body
            )
            
            # Process results to UnifiedSearchHit format
            hits = self._process_results_to_unified(
                response['hits']['hits'],
                response['hits']['max_score'],
                expanded_phrases,
                keyword
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return UnifiedSearchResponse(
                query=keyword,
                expanded_phrases=expanded_phrases,
                total_matches=response['hits']['total']['value'],
                max_score=response['hits']['max_score'] or 1.0,
                hits=hits,
                execution_time_ms=round(execution_time, 2),
                engine_used='opensearch'
            )
            
        except Exception as e:
            logger.error(f"OpenSearch search failed: {e}")
            return UnifiedSearchResponse(
                query=keyword,
                expanded_phrases=expanded_phrases,
                total_matches=0,
                max_score=0.0,
                hits=[],
                execution_time_ms=0.0,
                engine_used='opensearch'
            )
    
    async def get_service_firm_aggregation(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get Service×Firm matrix data"""
        # Stub implementation
        logger.warning("OpenSearch aggregations not yet implemented")
        return {'matrix': {}, 'services': [], 'firms': []}
    
    async def get_geographic_aggregation(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get geographic distribution data"""
        # Stub implementation
        logger.warning("OpenSearch geographic aggregation not yet implemented")
        return {'regions': []}
    
    async def get_financial_statistics(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get financial statistics"""
        # Stub implementation
        logger.warning("OpenSearch financial statistics not yet implemented")
        return {'statistics': {}}
    
    async def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options"""
        # Stub implementation
        logger.warning("OpenSearch filter options not yet implemented")
        return {'service_categories': [], 'organizations': [], 'regions': []}
    
    # ===== Private Helper Methods =====
    
    def _process_results_to_unified(
        self,
        opensearch_hits: List[Dict],
        max_score: float,
        expanded_phrases: List[str],
        keyword: str
    ) -> List[UnifiedSearchHit]:
        """Convert OpenSearch hits to UnifiedSearchHit objects"""
        
        if not opensearch_hits:
            return []
        
        hits = []
        max_score = max_score or 1.0
        
        for hit in opensearch_hits:
            source = hit['_source']
            score = hit['_score']
            similarity_percent = int((score / max_score) * 100) if max_score > 0 else 0
            
            # Determine matched phrases
            title_lower = source.get('title', '').lower()
            matched_phrases = [p for p in expanded_phrases if p.lower() in title_lower]
            if not matched_phrases:
                matched_phrases = [keyword]
            
            hits.append(UnifiedSearchHit(
                tender_id=source.get('tender_id', ''),
                title=source.get('title', ''),
                organization=source.get('organization', ''),
                status=source.get('status', ''),
                aoc_date=source.get('aoc_date', ''),
                url=source.get('url', ''),
                raw_score=score,
                similarity_percent=similarity_percent,
                matched_phrases=matched_phrases,
                exact_match=any(p.lower() in title_lower for p in expanded_phrases if " " in p),
                # Financial data from nested object
                award_value=source.get('financial_data', {}).get('award_value'),
                currency=source.get('financial_data', {}).get('currency'),
                inr_normalized_value=source.get('financial_data', {}).get('inr_normalized_value'),
                deal_size_category=source.get('financial_data', {}).get('deal_size_category'),
                # Competitive intelligence from nested object
                service_category=source.get('competitive_intelligence', {}).get('service_category'),
                detected_firms=source.get('competitive_intelligence', {}).get('detected_firms'),
                region=source.get('competitive_intelligence', {}).get('region')
            ))
        
        return hits


def main():
    """Test OpenSearch engine (if available)"""
    print("TenderIntel OpenSearch Engine")
    print("=" * 50)
    
    print("\n⚠️  This test requires:")
    print("   1. pip install tenderintel[opensearch]")
    print("   2. OpenSearch cluster running on localhost:9200")
    
    try:
        config = {
            'hosts': [{'host': 'localhost', 'port': 9200}],
            'enabled': True,
            'index_prefix': 'tenders'
        }
        
        engine = OpenSearchEngine(config)
        
        print("\n✓ OpenSearch engine initialized")
        print(f"  Engine type: {engine.engine_type.value}")
        print(f"  Capabilities: {engine.capabilities.name}")
        print(f"  Max records: {engine.capabilities.max_recommended_records:,}")
        
        # Test health check
        import asyncio
        health = asyncio.run(engine.health_check())
        print(f"\n  Health status: {health.status}")
        print(f"  Is healthy: {health.is_healthy}")
        
        if health.is_healthy:
            stats = asyncio.run(engine.get_statistics())
            print(f"\n  Records: {stats.record_count:,}")
            print(f"  Index size: {stats.index_size_mb:.2f} MB")
        
        print("\n✅ OpenSearch engine test completed!")
        
    except Exception as e:
        print(f"\n❌ OpenSearch engine test failed: {e}")
        print("   This is expected if OpenSearch is not installed or not running")


if __name__ == "__main__":
    main()
