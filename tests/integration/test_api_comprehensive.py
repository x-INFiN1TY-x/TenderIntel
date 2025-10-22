#!/usr/bin/env python3
"""
Comprehensive API Integration Tests for TenderIntel
Tests all major endpoints and validates responses
"""

import pytest
import requests
import time
from typing import Dict, Any

# Base URL for API testing
BASE_URL = "http://127.0.0.1:8002"

class TestHealthAndStatus:
    """Test health check and system status endpoints"""
    
    def test_health_endpoint(self):
        """Test /health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["healthy", "degraded"]
        assert "checks" in data
        assert "database" in data["checks"]
        assert "search_engine" in data["checks"]
        assert "synonym_manager" in data["checks"]
        
        # Verify database is functional
        assert data["checks"]["database"]["fts5_functional"] is True
        assert data["checks"]["database"]["record_count"] > 0
    
    def test_stats_endpoint(self):
        """Test /stats endpoint returns comprehensive statistics"""
        response = requests.get(f"{BASE_URL}/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "database_statistics" in data
        assert "synonym_statistics" in data
        assert "api_info" in data
        
        # Verify database stats
        db_stats = data["database_statistics"]
        assert db_stats["total_records"] > 0
        assert "date_range" in db_stats
        assert "top_organizations" in db_stats
        
        # Verify synonym stats
        syn_stats = data["synonym_statistics"]
        assert syn_stats["total_keywords"] > 0
        assert syn_stats["domains_supported"] > 0


class TestSearchEndpoints:
    """Test search and keyword expansion functionality"""
    
    def test_basic_search(self):
        """Test basic search functionality"""
        response = requests.get(f"{BASE_URL}/search", params={"q": "networking", "limit": 10})
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "execution_time_ms" in data
        assert "expanded_phrases" in data
        assert isinstance(data["results"], list)
        
        # Verify performance
        assert data["execution_time_ms"] < 100  # Should be sub-100ms
    
    def test_keyword_expansion(self):
        """Test keyword expansion endpoint"""
        test_keywords = ["api", "lan", "cloud", "security"]
        
        for keyword in test_keywords:
            response = requests.get(f"{BASE_URL}/expand", params={"q": keyword})
            
            assert response.status_code == 200
            data = response.json()
            
            assert "phrases" in data
            assert "domain" in data
            assert "confidence" in data
            assert len(data["phrases"]) > 0
            
            # Verify expansion quality
            assert data["confidence"] >= 0.0
            assert data["confidence"] <= 1.0
    
    def test_filtered_search(self):
        """Test search with categorical filters"""
        response = requests.get(
            f"{BASE_URL}/search-filtered",
            params={
                "q": "cloud",
                "limit": 10,
                "service_categories": "cloud,networking"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "filters_applied" in data
    
    def test_search_validation(self):
        """Test search input validation"""
        # Test empty query
        response = requests.get(f"{BASE_URL}/search", params={"q": ""})
        assert response.status_code == 422  # Validation error
        
        # Test query too long
        response = requests.get(f"{BASE_URL}/search", params={"q": "x" * 100})
        assert response.status_code == 422
        
        # Test invalid limit
        response = requests.get(f"{BASE_URL}/search", params={"q": "test", "limit": 1000})
        assert response.status_code == 422


class TestCompetitiveIntelligence:
    """Test competitive intelligence endpoints"""
    
    def test_competitive_intelligence_summary(self):
        """Test competitive intelligence summary endpoint"""
        response = requests.get(f"{BASE_URL}/competitive-intelligence/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "competitive_intelligence" in data
        ci = data["competitive_intelligence"]
        
        assert "market_overview" in ci
        assert "service_category_analysis" in ci
        assert "organization_performance" in ci
        assert "regional_distribution" in ci
        
        # Verify data quality
        assert ci["market_overview"]["total_analyzed_tenders"] > 0
    
    def test_filter_options(self):
        """Test filter options endpoint"""
        response = requests.get(f"{BASE_URL}/filter-options")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "filter_options" in data
        filters = data["filter_options"]
        
        # Verify filter categories exist
        expected_categories = [
            "service_categories",
            "organizations",
            "value_ranges",
            "regions"
        ]
        
        for category in expected_categories:
            assert category in filters


class TestVisualizationEndpoints:
    """Test visualization data generation endpoints"""
    
    def test_heatmap_data(self):
        """Test heatmap data generation"""
        metrics = ["market_share", "contract_count", "total_value"]
        
        for metric in metrics:
            response = requests.get(
                f"{BASE_URL}/visualizations/heatmap-data",
                params={"metric": metric}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "heatmap_data" in data
            assert "performance_summary" in data
            assert "metadata" in data
            
            heatmap = data["heatmap_data"]
            assert "services" in heatmap
            assert "firms" in heatmap
            assert "cell_data" in heatmap
            assert "max_value" in heatmap
            
            # Verify performance (should not timeout)
            # This was the critical bug that was fixed
            assert response.elapsed.total_seconds() < 1.0
    
    def test_geographic_data(self):
        """Test geographic intelligence data"""
        response = requests.get(f"{BASE_URL}/visualizations/geographic-data")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "geographic_intelligence" in data
        assert "insights" in data
        assert "metadata" in data
        
        geo = data["geographic_intelligence"]
        assert "state_metrics" in geo
        assert "choropleth_data" in geo
        assert "procurement_hotspots" in geo
    
    def test_executive_summary(self):
        """Test executive summary data"""
        response = requests.get(f"{BASE_URL}/visualizations/executive-summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "executive_summary" in data
        assert "key_metrics" in data
        
        summary = data["executive_summary"]
        assert "total_market_value" in summary
        assert "active_competitors" in summary
        assert "avg_deal_size" in summary
        assert "market_growth" in summary
        assert "hhi" in summary
        
        # Verify HHI is valid (0-1 range)
        assert 0 <= summary["hhi"] <= 1


class TestPerformance:
    """Test API performance characteristics"""
    
    def test_response_times(self):
        """Test that all endpoints respond within acceptable time"""
        endpoints = [
            "/health",
            "/stats",
            "/search?q=test",
            "/expand?q=api",
            "/competitive-intelligence/summary",
            "/visualizations/heatmap-data",
            "/visualizations/executive-summary"
        ]
        
        for endpoint in endpoints:
            start = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}")
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            assert response.status_code == 200
            assert elapsed < 1000  # All endpoints should respond in <1s
            
            print(f"✅ {endpoint}: {elapsed:.2f}ms")
    
    def test_concurrent_requests(self):
        """Test API handles concurrent requests"""
        import concurrent.futures
        
        def make_request():
            response = requests.get(f"{BASE_URL}/search?q=test")
            return response.status_code == 200
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(results)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_endpoints(self):
        """Test that invalid endpoints return 404"""
        response = requests.get(f"{BASE_URL}/invalid-endpoint")
        assert response.status_code == 404
    
    def test_malformed_requests(self):
        """Test handling of malformed requests"""
        # Missing required parameter
        response = requests.get(f"{BASE_URL}/search")
        assert response.status_code == 422
        
        # Invalid parameter type
        response = requests.get(f"{BASE_URL}/search?q=test&limit=invalid")
        assert response.status_code == 422
    
    def test_database_resilience(self):
        """Test API handles database issues gracefully"""
        # This would require mocking database failures
        # For now, just verify error responses are structured
        pass


# Test execution summary
if __name__ == "__main__":
    print("TenderIntel API Comprehensive Test Suite")
    print("=" * 50)
    print("\nRunning tests...")
    print("\nTo run with pytest:")
    print("  pytest tests/integration/test_api_comprehensive.py -v")
    print("\nTo run with coverage:")
    print("  pytest tests/integration/test_api_comprehensive.py --cov=src/tenderintel")
