#!/usr/bin/env python3
"""
SQLite FTS5 Search Engine Implementation
Implements SearchEngineInterface with enhanced filtering and BM25 ranking
"""

import sqlite3
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
import json

# Import our interface and filters
from .search_engine_interface import SearchEngineInterface, SearchFilters
from .synonym_manager import SynonymManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteFTS5Engine:
    """SQLite FTS5 implementation of SearchEngineInterface with enhanced filtering"""
    
    def __init__(self, db_path: str = "engine/tenders.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        # Initialize synonym manager for keyword expansion
        self.synonym_manager = SynonymManager()
        
        # Validate database has FTS5 support
        self._validate_fts5_support()
        
        logger.info(f"SQLiteFTS5Engine initialized with database: {self.db_path}")
    
    def _validate_fts5_support(self):
        """Validate that SQLite has FTS5 support enabled"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Test FTS5 functionality
                result = conn.execute("""
                    SELECT COUNT(*) FROM tenders WHERE tenders MATCH 'test'
                """).fetchone()
                
                logger.info("FTS5 functionality validated successfully")
                
        except Exception as e:
            logger.error(f"FTS5 validation failed: {e}")
            raise RuntimeError("SQLite FTS5 not available or database not properly configured")
    
    def execute_search(
        self,
        keyword: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 25,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Execute enhanced search with filtering, expansion, and BM25 ranking
        
        Args:
            keyword: Original search keyword
            filters: Optional categorical filters
            limit: Maximum results to return
            debug: Include debug information
            
        Returns:
            Comprehensive search results with similarity percentages
        """
        
        start_time = time.time()
        
        try:
            # Step 1: Expand keyword using synonym manager
            expansion_result = self.synonym_manager.expand_keyword(keyword, max_expansions=6)
            expanded_phrases = expansion_result['expanded_phrases']
            
            # Step 2: Build FTS5 query with phrase prioritization
            fts5_query = self._build_enhanced_fts5_query(expanded_phrases)
            
            if not fts5_query:
                return self._empty_result(keyword, expanded_phrases, "No query could be constructed")
            
            # Step 3: Build WHERE clause for categorical filtering
            filter_clause, filter_params = self._build_filter_clause(filters)
            
            # Step 4: Execute enhanced search with filtering
            with sqlite3.connect(self.db_path) as conn:
                # Build complete SQL query
                base_query = """
                    SELECT title, org, status, aoc_date, tender_id, url,
                           service_category, value_range, region, department_type,
                           complexity, keywords, bm25(tenders) as bm25_score
                    FROM tenders 
                    WHERE tenders MATCH ?
                """
                
                if filter_clause:
                    base_query += f" AND {filter_clause}"
                
                base_query += " ORDER BY bm25_score ASC LIMIT ?"
                
                # Execute query with parameters
                query_params = [fts5_query] + filter_params + [limit]
                cursor = conn.execute(base_query, query_params)
                raw_results = cursor.fetchall()
            
            # Step 5: Process and normalize results
            processed_results = self._process_enhanced_search_results(
                raw_results, expanded_phrases, debug
            )
            
            # Step 6: Calculate execution time and build response
            execution_time = round((time.time() - start_time) * 1000, 2)
            
            response = {
                "query": keyword,
                "phrases": expanded_phrases,
                "domain": expansion_result.get('domain', 'general'),
                "confidence": expansion_result.get('confidence', 0.0),
                "total_matches": len(processed_results),
                "execution_time_ms": execution_time,
                "filters_applied": self._summarize_applied_filters(filters),
                "fts5_query": fts5_query if debug else None,
                "hits": processed_results,
                "engine_type": "sqlite_fts5"
            }
            
            logger.info(f"SQLite search completed: '{keyword}' → {len(processed_results)} results in {execution_time}ms")
            return response
            
        except Exception as e:
            logger.error(f"SQLite search execution failed: {e}")
            return self._error_result(keyword, f"Search execution error: {str(e)}")
    
    def _build_enhanced_fts5_query(self, phrases: List[str]) -> str:
        """Build optimized FTS5 MATCH query with phrase prioritization"""
        
        if not phrases:
            return ""
        
        query_parts = []
        
        # Sort phrases by specificity (word count descending)
        sorted_phrases = sorted(phrases, key=lambda p: len(p.split()), reverse=True)
        
        for phrase in sorted_phrases:
            if " " in phrase:
                # Multi-word phrase: exact phrase matching
                query_parts.append(f'"{phrase}"')
            else:
                # Single word: flexible matching
                query_parts.append(phrase)
        
        return " OR ".join(query_parts)
    
    def _build_filter_clause(self, filters: Optional[SearchFilters]) -> tuple[str, List[Any]]:
        """Build SQL WHERE clause for categorical filtering"""
        
        if not filters:
            return "", []
        
        filter_conditions = []
        filter_params = []
        
        # Date range filtering
        if filters.date_from:
            filter_conditions.append("aoc_date >= ?")
            filter_params.append(filters.date_from)
        
        if filters.date_to:
            filter_conditions.append("aoc_date <= ?")
            filter_params.append(filters.date_to)
        
        # Categorical filtering using IN clauses
        categorical_filters = [
            ("service_category", filters.service_categories),
            ("org", filters.organizations),
            ("value_range", filters.value_ranges),
            ("region", filters.regions),
            ("status", filters.status_types),
            ("department_type", filters.department_types),
            ("complexity", filters.complexity_levels)
        ]
        
        for column, values in categorical_filters:
            if values and len(values) > 0:
                placeholders = ",".join(["?"] * len(values))
                filter_conditions.append(f"{column} IN ({placeholders})")
                filter_params.extend(values)
        
        # Combine conditions with AND
        filter_clause = " AND ".join(filter_conditions) if filter_conditions else ""
        
        return filter_clause, filter_params
    
    def _process_enhanced_search_results(
        self, 
        raw_results: List[tuple], 
        expanded_phrases: List[str], 
        debug: bool
    ) -> List[Dict[str, Any]]:
        """Process raw FTS5 results with enhanced metadata"""
        
        if not raw_results:
            return []
        
        processed_results = []
        
        # Extract BM25 scores (last column) and normalize
        bm25_scores = [row[12] for row in raw_results]  # Updated index for enhanced schema
        
        if bm25_scores:
            min_score = min(bm25_scores)  # Most negative = best match
            max_score = max(bm25_scores)  # Least negative = worst match
            
            # Normalize to 0-100 scale where best match = 100%
            similarity_percentages = []
            for score in bm25_scores:
                if min_score == max_score:
                    similarity_percentages.append(100)
                else:
                    normalized = 100 * (max_score - score) / (max_score - min_score)
                    similarity_percentages.append(max(1, round(normalized)))
        else:
            similarity_percentages = []
        
        # Process each result with enhanced metadata
        for i, row in enumerate(raw_results):
            (title, org, status, aoc_date, tender_id, url,
             service_category, value_range, region, department_type,
             complexity, keywords, bm25_score) = row
            
            # Analyze phrase matches
            matched_phrases = self._analyze_phrase_matches(title, expanded_phrases)
            
            # Determine match type
            exact_match = any(phrase.lower() in title.lower() for phrase in expanded_phrases if " " in phrase)
            
            result = {
                "title": title,
                "org": org,
                "status": status,
                "aoc_date": aoc_date,
                "tender_id": tender_id,
                "url": url,
                "similarity_percent": similarity_percentages[i],
                "matched_phrases": matched_phrases,
                "exact_match": exact_match,
                # Enhanced metadata
                "service_category": service_category,
                "value_range": value_range,
                "region": region,
                "department_type": department_type,
                "complexity": complexity,
                "keywords": keywords.split(',') if keywords else []
            }
            
            # Add debug information if requested
            if debug:
                result["debug_info"] = {
                    "raw_bm25_score": bm25_score,
                    "normalized_score": similarity_percentages[i] / 100.0,
                    "rank_position": i + 1,
                    "title_length": len(title),
                    "phrase_analysis": self._debug_phrase_analysis(title, expanded_phrases)
                }
            
            processed_results.append(result)
        
        return processed_results
    
    def _analyze_phrase_matches(self, title: str, phrases: List[str]) -> List[str]:
        """Analyze which expansion phrases actually matched in the title"""
        
        title_lower = title.lower()
        matched_phrases = []
        
        for phrase in phrases:
            if phrase.lower() in title_lower:
                matched_phrases.append(phrase)
        
        return matched_phrases
    
    def _debug_phrase_analysis(self, title: str, phrases: List[str]) -> Dict[str, Any]:
        """Detailed phrase matching analysis for debugging"""
        
        title_lower = title.lower()
        analysis = {}
        
        for phrase in phrases:
            phrase_lower = phrase.lower()
            analysis[phrase] = {
                "exact_match": phrase_lower in title_lower,
                "word_matches": sum(1 for word in phrase_lower.split() if word in title_lower),
                "total_words": len(phrase_lower.split()),
                "partial_coverage": sum(1 for word in phrase_lower.split() if word in title_lower) / len(phrase_lower.split()) if phrase_lower.split() else 0
            }
        
        return analysis
    
    def _summarize_applied_filters(self, filters: Optional[SearchFilters]) -> Dict[str, Any]:
        """Summarize which filters were applied to the search"""
        
        if not filters:
            return {"filters_applied": False}
        
        applied = {}
        
        filter_mapping = [
            ("date_range", filters.date_from or filters.date_to),
            ("organizations", filters.organizations),
            ("service_categories", filters.service_categories),
            ("value_ranges", filters.value_ranges),
            ("regions", filters.regions),
            ("status_types", filters.status_types),
            ("department_types", filters.department_types),
            ("complexity_levels", filters.complexity_levels),
            ("min_similarity", filters.min_similarity and filters.min_similarity > 0)
        ]
        
        for filter_name, filter_value in filter_mapping:
            if filter_value:
                applied[filter_name] = True
        
        return {
            "filters_applied": len(applied) > 0,
            "active_filters": list(applied.keys()),
            "filter_count": len(applied)
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status for SQLite FTS5 engine"""
        
        start_time = time.time()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Basic database connectivity test
                record_count = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
                
                # FTS5 functionality test
                fts5_test = conn.execute("""
                    SELECT COUNT(*) FROM tenders WHERE tenders MATCH 'test'
                """).fetchone()[0]
                
                # Reference tables test
                categories_count = conn.execute("SELECT COUNT(*) FROM service_categories").fetchone()[0]
                regions_count = conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0]
                
                # Performance test with sample query
                perf_start = time.time()
                conn.execute("""
                    SELECT title, bm25(tenders) FROM tenders 
                    WHERE tenders MATCH 'network' 
                    LIMIT 5
                """).fetchall()
                perf_time = (time.time() - perf_start) * 1000
                
                total_time = round((time.time() - start_time) * 1000, 2)
                
                return {
                    "status": "healthy",
                    "engine_type": "sqlite_fts5",
                    "database_path": str(self.db_path),
                    "record_count": record_count,
                    "reference_tables": {
                        "service_categories": categories_count,
                        "regions": regions_count
                    },
                    "performance": {
                        "health_check_time_ms": total_time,
                        "sample_query_time_ms": round(perf_time, 2)
                    },
                    "features": {
                        "fts5_functional": True,
                        "bm25_ranking": True,
                        "phrase_matching": True,
                        "categorical_filtering": True,
                        "synonym_expansion": True
                    }
                }
                
        except Exception as e:
            logger.error(f"SQLite health check failed: {e}")
            return {
                "status": "unhealthy",
                "engine_type": "sqlite_fts5",
                "error": str(e),
                "database_path": str(self.db_path)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the SQLite database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Basic record statistics
                total_records = conn.execute("SELECT COUNT(*) FROM tenders").fetchone()[0]
                
                # Category distribution
                category_stats = conn.execute("""
                    SELECT service_category, COUNT(*) as count
                    FROM tenders
                    GROUP BY service_category
                    ORDER BY count DESC
                """).fetchall()
                
                # Organization distribution (top 20)
                org_stats = conn.execute("""
                    SELECT org, COUNT(*) as count
                    FROM tenders
                    GROUP BY org
                    ORDER BY count DESC
                    LIMIT 20
                """).fetchall()
                
                # Regional distribution
                region_stats = conn.execute("""
                    SELECT region, COUNT(*) as count
                    FROM tenders
                    GROUP BY region
                    ORDER BY count DESC
                """).fetchall()
                
                # Value range distribution
                value_stats = conn.execute("""
                    SELECT value_range, COUNT(*) as count
                    FROM tenders
                    GROUP BY value_range
                    ORDER BY count DESC
                """).fetchall()
                
                # Date range analysis
                date_range = conn.execute("""
                    SELECT MIN(aoc_date) as earliest, MAX(aoc_date) as latest,
                           COUNT(DISTINCT aoc_date) as unique_dates
                    FROM tenders
                """).fetchone()
                
                # Title analysis
                title_analysis = conn.execute("""
                    SELECT AVG(LENGTH(title)) as avg_length,
                           MIN(LENGTH(title)) as min_length,
                           MAX(LENGTH(title)) as max_length
                    FROM tenders
                """).fetchone()
                
                # Database file statistics
                db_size = self.db_path.stat().st_size
                
                return {
                    "engine_type": "sqlite_fts5",
                    "database_statistics": {
                        "total_records": total_records,
                        "database_size_bytes": db_size,
                        "database_size_mb": round(db_size / (1024 * 1024), 2)
                    },
                    "categorical_distribution": {
                        "service_categories": [
                            {"category": cat, "count": count, "percentage": round(count/total_records*100, 1)}
                            for cat, count in category_stats
                        ],
                        "regions": [
                            {"region": reg, "count": count, "percentage": round(count/total_records*100, 1)}
                            for reg, count in region_stats
                        ],
                        "value_ranges": [
                            {"range": vr, "count": count, "percentage": round(count/total_records*100, 1)}
                            for vr, count in value_stats
                        ]
                    },
                    "top_organizations": [
                        {"org": org, "count": count} for org, count in org_stats
                    ],
                    "temporal_analysis": {
                        "earliest_date": date_range[0],
                        "latest_date": date_range[1],
                        "unique_dates": date_range[2],
                        "date_span_days": self._calculate_date_span(date_range[0], date_range[1])
                    },
                    "content_analysis": {
                        "average_title_length": round(title_analysis[0], 1),
                        "min_title_length": title_analysis[1],
                        "max_title_length": title_analysis[2]
                    },
                    "synonym_statistics": self.synonym_manager.get_statistics()
                }
                
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return {"error": str(e), "engine_type": "sqlite_fts5"}
    
    def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options from the database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get unique service categories
                categories = conn.execute("""
                    SELECT DISTINCT service_category, COUNT(*) as count
                    FROM tenders
                    GROUP BY service_category
                    ORDER BY service_category
                """).fetchall()
                
                # Get unique organizations (top 50 by tender count)
                organizations = conn.execute("""
                    SELECT org, COUNT(*) as count
                    FROM tenders
                    GROUP BY org
                    ORDER BY count DESC
                    LIMIT 50
                """).fetchall()
                
                # Get unique regions
                regions = conn.execute("""
                    SELECT DISTINCT region, COUNT(*) as count
                    FROM tenders
                    GROUP BY region
                    ORDER BY region
                """).fetchall()
                
                # Get unique value ranges
                value_ranges = conn.execute("""
                    SELECT DISTINCT value_range, COUNT(*) as count
                    FROM tenders
                    GROUP BY value_range
                    ORDER BY value_range
                """).fetchall()
                
                # Get status types
                status_types = conn.execute("""
                    SELECT DISTINCT status, COUNT(*) as count
                    FROM tenders
                    GROUP BY status
                    ORDER BY status
                """).fetchall()
                
                # Get department types
                dept_types = conn.execute("""
                    SELECT DISTINCT department_type, COUNT(*) as count
                    FROM tenders
                    GROUP BY department_type
                    ORDER BY department_type
                """).fetchall()
                
                # Get complexity levels
                complexity_levels = conn.execute("""
                    SELECT DISTINCT complexity, COUNT(*) as count
                    FROM tenders
                    GROUP BY complexity
                    ORDER BY complexity
                """).fetchall()
                
                # Get date range for date picker
                date_range = conn.execute("""
                    SELECT MIN(aoc_date) as min_date, MAX(aoc_date) as max_date
                    FROM tenders
                """).fetchone()
                
                return {
                    "service_categories": [{"value": cat, "label": cat.title(), "count": count} for cat, count in categories],
                    "organizations": [{"value": org, "label": org, "count": count} for org, count in organizations],
                    "regions": [{"value": reg, "label": reg.title(), "count": count} for reg, count in regions],
                    "value_ranges": [{"value": vr, "label": vr.replace('_', ' ').title(), "count": count} for vr, count in value_ranges],
                    "status_types": [{"value": st, "label": st, "count": count} for st, count in status_types],
                    "department_types": [{"value": dt, "label": dt.title(), "count": count} for dt, count in dept_types],
                    "complexity_levels": [{"value": cl, "label": cl.title(), "count": count} for cl, count in complexity_levels],
                    "date_range": {
                        "min_date": date_range[0],
                        "max_date": date_range[1]
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get filter options: {e}")
            return {"error": str(e)}
    
    def _calculate_date_span(self, earliest: Optional[str], latest: Optional[str]) -> int:
        """Calculate span in days between earliest and latest dates"""
        
        if not earliest or not latest:
            return 0
        
        try:
            from datetime import datetime
            start_date = datetime.fromisoformat(earliest)
            end_date = datetime.fromisoformat(latest)
            return (end_date - start_date).days
        except:
            return 0
    
    def _empty_result(self, keyword: str, phrases: List[str], reason: str) -> Dict[str, Any]:
        """Return structured empty result"""
        return {
            "query": keyword,
            "phrases": phrases,
            "total_matches": 0,
            "execution_time_ms": 0,
            "hits": [],
            "message": reason,
            "engine_type": "sqlite_fts5"
        }
    
    def _error_result(self, keyword: str, error_message: str) -> Dict[str, Any]:
        """Return structured error result"""
        return {
            "query": keyword,
            "error": error_message,
            "total_matches": 0,
            "execution_time_ms": 0,
            "hits": [],
            "engine_type": "sqlite_fts5"
        }
    
    def execute_faceted_search(self, keyword: str, facet_fields: List[str], limit: int = 25) -> Dict[str, Any]:
        """Execute search with faceted aggregations"""
        
        try:
            # Get main search results
            search_result = self.execute_search(keyword, limit=limit)
            
            # Add faceted aggregations
            with sqlite3.connect(self.db_path) as conn:
                facets = {}
                
                for field in facet_fields:
                    if field in ["service_category", "region", "value_range", "complexity", "department_type"]:
                        facet_results = conn.execute(f"""
                            SELECT {field}, COUNT(*) as count
                            FROM tenders
                            WHERE tenders MATCH ?
                            GROUP BY {field}
                            ORDER BY count DESC
                            LIMIT 20
                        """, (self._build_enhanced_fts5_query(search_result["phrases"]),)).fetchall()
                        
                        facets[field] = [
                            {"value": item[0], "count": item[1]}
                            for item in facet_results
                        ]
            
            search_result["facets"] = facets
            return search_result
            
        except Exception as e:
            logger.error(f"Faceted search failed: {e}")
            return self._error_result(keyword, f"Faceted search error: {str(e)}")

def main():
    """Test SQLite FTS5 engine functionality"""
    print("Smart Tender Search PoC - SQLite FTS5 Engine")
    print("=" * 50)
    
    try:
        # Initialize SQLite engine
        engine = SQLiteFTS5Engine("engine/tenders.db")
        
        # Test health status
        print("🏥 Testing health status...")
        health = engine.get_health_status()
        print(f"   Status: {health['status']}")
        
        if health['status'] == 'healthy':
            print(f"   Records: {health['record_count']}")
            print(f"   Performance: {health['performance']['health_check_time_ms']}ms")
            
            # Test statistics
            print("\n📊 Testing statistics...")
            stats = engine.get_statistics()
            print(f"   Total records: {stats['database_statistics']['total_records']}")
            print(f"   Categories: {len(stats['categorical_distribution']['service_categories'])}")
            
            # Test filter options
            print("\n🔍 Testing filter options...")
            filters = engine.get_filter_options()
            print(f"   Service categories: {len(filters['service_categories'])}")
            print(f"   Organizations: {len(filters['organizations'])}")
            print(f"   Regions: {len(filters['regions'])}")
            
            # Test enhanced search (if data is available)
            if stats['database_statistics']['total_records'] > 0:
                print("\n🔎 Testing enhanced search...")
                
                # Create sample filters
                sample_filters = SearchFilters(
                    service_categories=["networking", "security"],
                    min_similarity=50
                )
                
                search_result = engine.execute_search("lan", filters=sample_filters, limit=5, debug=True)
                print(f"   Search results: {search_result['total_matches']} matches")
                print(f"   Execution time: {search_result['execution_time_ms']}ms")
                
                if search_result['hits']:
                    top_result = search_result['hits'][0]
                    print(f"   Top result: {top_result['title'][:50]}...")
                    print(f"   Similarity: {top_result['similarity_percent']}%")
                    print(f"   Category: {top_result['service_category']}")
        
        print("\n✅ SQLite FTS5 engine test completed successfully!")
        
    except Exception as e:
        print(f"❌ SQLite engine test failed: {e}")
        logger.error(f"SQLite engine test failed: {e}")

if __name__ == "__main__":
    main()
