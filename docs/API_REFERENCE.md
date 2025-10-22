# TenderIntel API Reference

**Version:** 1.0.0  
**Base URL:** `http://localhost:8002`  
**Last Updated:** October 22, 2025

## **📋 Overview**

TenderIntel provides 18 RESTful API endpoints for intelligent government tender search, competitive intelligence, and market analysis.

**Authentication:** Currently open (add authentication for production)  
**Rate Limiting:** Not enforced (recommended: 100 requests/minute)  
**Response Format:** JSON  
**Character Encoding:** UTF-8

**Interactive Documentation:** Visit `http://localhost:8002/docs` for Swagger UI

---

## **🔍 Search Endpoints (5 endpoints)**

### **1. Basic Search**

**`GET /search`**

Execute intelligent tender search with keyword expansion and BM25 ranking.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Search keyword (1-50 characters) |
| `limit` | integer | No | Max results (1-100, default: 25) |
| `debug` | boolean | No | Include debug info (default: false) |
| `min_similarity` | integer | No | Minimum match % (0-100, default: 0) |

**Example Request:**
```bash
curl "http://localhost:8002/search?q=lan&limit=10"
```

**Example Response:**
```json
{
  "query": "lan",
  "expanded_phrases": ["local area network", "layer 2 switch", "vlan", "ethernet"],
  "domain": "networking",
  "confidence": 0.95,
  "total_matches": 4,
  "execution_time_ms": 1.4,
  "engine_used": "sqlite_fts5",
  "hits": [
    {
      "tender_id": "NIC-2025-NET-001",
      "title": "VLAN configuration and Ethernet switching equipment...",
      "organization": "National Informatics Centre",
      "status": "Published AOC",
      "aoc_date": "2025-03-15",
      "url": "https://etenders.gov.in/...",
      "similarity_percent": 100,
      "matched_phrases": ["vlan", "ethernet"],
      "exact_match": true,
      "service_category": "networking",
      "region": "delhi"
    }
  ]
}
```

---

### **2. Keyword Expansion**

**`GET /expand`**

Expand keyword into relevant technical phrases.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Keyword to expand |
| `max_expansions` | integer | No | Max phrases (1-10, default: 5) |
| `debug` | boolean | No | Include debug info |

**Example Request:**
```bash
curl "http://localhost:8002/expand?q=api"
```

**Example Response:**
```json
{
  "query": "api",
  "normalized_query": "api",
  "phrases": [
    "application programming interface",
    "rest api",
    "api gateway",
    "openapi"
  ],
  "domain": "cloud",
  "confidence": 0.95,
  "execution_time_ms": 0.8
}
```

---

### **3. Filtered Search**

**`GET /search-filtered`**

Advanced search with comprehensive categorical filtering.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Search keyword |
| `limit` | integer | No | Max results (default: 25) |
| `date_from` | string | No | From date (YYYY-MM-DD) |
| `date_to` | string | No | To date (YYYY-MM-DD) |
| `service_categories` | string | No | Comma-separated categories |
| `organizations` | string | No | Comma-separated org names |
| `value_ranges` | string | No | Comma-separated ranges |
| `regions` | string | No | Comma-separated regions |
| `status_types` | string | No | Comma-separated status |
| `department_types` | string | No | Comma-separated dept types |
| `complexity_levels` | string | No | Comma-separated complexity |
| `min_similarity` | integer | No | Min match % (0-100) |

**Example Request:**
```bash
curl "http://localhost:8002/search-filtered?q=cloud&service_categories=cloud,networking&regions=delhi&min_similarity=70"
```

---

### **4. Faceted Search**

**`GET /faceted-search`**

Search with faceted aggregations for analytics.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `q` | string | Yes | Search keyword |
| `facets` | string | Yes | Comma-separated facet fields |
| `limit` | integer | No | Max results (default: 25) |

**Supported Facets:**
- `service_category` - Service type aggregations
- `region` - Geographic distribution
- `org` - Organization breakdown
- `value_range` - Deal size distribution

**Example Request:**
```bash
curl "http://localhost:8002/faceted-search?q=security&facets=service_category,region"
```

**Example Response:**
```json
{
  "query": "security",
  "total_matches": 18,
  "hits": [...],
  "facets": {
    "service_category": [
      {"value": "security", "count": 12},
      {"value": "cloud", "count": 6}
    ],
    "region": [
      {"value": "delhi", "count": 8},
      {"value": "mumbai", "count": 5}
    ]
  }
}
```

---

### **5. Filter Options**

**`GET /filter-options`**

Get available filter options for UI dropdowns.

**No Parameters Required**

**Example Request:**
```bash
curl "http://localhost:8002/filter-options"
```

**Example Response:**
```json
{
  "filter_options": {
    "service_categories": [
      {"value": "cloud", "label": "Cloud Services", "count": 18},
      {"value": "networking", "label": "Networking", "count": 15}
    ],
    "organizations": [
      {"value": "NIC", "label": "National Informatics Centre", "count": 12}
    ],
    "regions": [
      {"value": "north", "label": "Northern India", "count": 25}
    ],
    "value_ranges": [
      {"value": "0-1000000", "label": "Up to ₹10L", "count": 8}
    ]
  },
  "total_categories": 46
}
```

---

## **📊 Intelligence Endpoints (1 endpoint)**

### **6. Competitive Intelligence Summary**

**`GET /competitive-intelligence/summary`**

Get comprehensive market intelligence and competitor analysis.

**No Parameters Required**

**Example Request:**
```bash
curl "http://localhost:8002/competitive-intelligence/summary"
```

**Example Response:**
```json
{
  "competitive_intelligence": {
    "market_overview": {
      "total_analyzed_tenders": 59,
      "service_categories": 7,
      "active_regions": 5
    },
    "service_category_analysis": [
      {"category": "cloud", "tender_count": 18},
      {"category": "networking", "tender_count": 15}
    ],
    "organization_performance": [
      {
        "organization": "NIC",
        "service_category": "cloud",
        "participation_count": 12
      }
    ],
    "regional_distribution": [
      {"region": "delhi", "tender_count": 25, "unique_organizations": 15}
    ]
  }
}
```

---

## **📈 Analytics Endpoints (4 endpoints)**

### **7. Firm Financial Scorecard**

**`GET /analytics/firm-scorecard/{firm_name}`**

Generate comprehensive financial scorecard for a specific firm.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `firm_name` | string | Name of the firm (URL encoded) |

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `timeframe` | string | 12months | Analysis period |
| `include_trends` | boolean | true | Include trend data |
| `currency` | string | INR | Display currency |

**Example Request:**
```bash
curl "http://localhost:8002/analytics/firm-scorecard/Infosys?timeframe=12months"
```

**Example Response:**
```json
{
  "firm_profile": {
    "firm_name": "Infosys",
    "market_position": "challenger"
  },
  "portfolio_metrics": {
    "total_portfolio_value_inr": 380000000,
    "contract_count": 6,
    "average_deal_size_inr": 63333333
  },
  "performance_metrics": {
    "award_velocity_per_quarter": 1.5,
    "market_share_percent": 12.8,
    "competitive_position": "challenger"
  },
  "risk_assessment": {
    "overall_risk": "medium",
    "risk_factors": ["service_concentration"]
  }
}
```

---

### **8. Market Analysis**

**`GET /analytics/market-analysis/{service_category}`**

Get comprehensive market analysis for a service category.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `service_category` | string | Service category name |

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `timeframe` | string | 12months | Analysis period |
| `include_forecasting` | boolean | false | Include forecasts |

**Example Request:**
```bash
curl "http://localhost:8002/analytics/market-analysis/cloud"
```

**Example Response:**
```json
{
  "market_overview": {
    "total_market_value_inr": 1274000000,
    "total_contracts": 18,
    "average_deal_size_inr": 70777777
  },
  "market_structure": {
    "hhi_index": 0.067,
    "competitive_intensity": "high",
    "market_structure_type": "Competitive"
  },
  "financial_analysis": {
    "price_distribution": {
      "mean": 70777777,
      "median": 65000000,
      "percentiles": {
        "25th": 65000000,
        "75th": 71500000,
        "90th": 91000000
      }
    },
    "growth_rate_percent": 18.2
  }
}
```

---

### **9. Deal Benchmarking**

**`GET /analytics/deal-benchmarking`**

Benchmark deal value against market standards.

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `value` | float | Yes | Deal value to benchmark |
| `service_category` | string | Yes | Service category |
| `currency` | string | No | Currency code (default: INR) |

**Example Request:**
```bash
curl "http://localhost:8002/analytics/deal-benchmarking?value=50000000&service_category=cloud"
```

**Example Response:**
```json
{
  "deal_analysis": {
    "original_value": 50000000,
    "deal_classification": "medium"
  },
  "market_benchmarking": {
    "percentile_position": 65.4,
    "market_position": "above_average",
    "comparison_stats": {
      "percentile_25": 28000000,
      "percentile_50": 45000000,
      "percentile_75": 89000000
    }
  }
}
```

---

### **10. Currency Normalization**

**`POST /analytics/normalize-currency`**

Batch currency normalization to INR.

**Request Body:**
```json
[
  {"amount": 50000, "currency": "USD", "date": "2025-10-21"},
  {"amount": 25000000, "currency": "INR", "date": "2025-10-21"}
]
```

**Example Request:**
```bash
curl -X POST "http://localhost:8002/analytics/normalize-currency" \
  -H "Content-Type: application/json" \
  -d '[{"amount": 50000, "currency": "USD", "date": "2025-10-21"}]'
```

**Example Response:**
```json
[
  {
    "original_amount": 50000,
    "original_currency": "USD",
    "inr_equivalent": 4187500,
    "exchange_rate": 83.75,
    "confidence": 0.98,
    "rate_source": "rbi_official"
  }
]
```

---

## **🎨 Visualization Endpoints (3 endpoints)**

### **11. Executive Summary**

**`GET /visualizations/executive-summary`**

Get executive dashboard KPI data.

**Example Response:**
```json
{
  "total_market_value_inr": 32480000000,
  "market_growth_percent": 12.5,
  "total_firms": 37,
  "total_services": 7,
  "market_concentration_hhi": 0.048,
  "avg_deal_size_inr": 88000000,
  "service_breakdown": [
    {"name": "cloud", "tender_count": 18, "market_share_percent": 30.5}
  ]
}
```

---

### **12. Heatmap Data**

**`GET /visualizations/heatmap-data`**

Generate Service×Firm performance matrix.

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `metric` | string | market_share | Metric type |
| `timeframe` | string | 12months | Time period |

**Supported Metrics:**
- `market_share` - Market share percentage
- `contract_count` - Number of contracts
- `total_value` - Total contract value

**Example Request:**
```bash
curl "http://localhost:8002/visualizations/heatmap-data?metric=market_share"
```

**Example Response:**
```json
{
  "heatmap_data": {
    "services": ["cloud", "networking", "security", "database"],
    "firms": ["TCS", "Infosys", "HCL", "Wipro"],
    "cell_data": [
      {
        "service": "cloud",
        "firm": "TCS",
        "value": 25.6,
        "contract_count": 8,
        "display_value": "25.6%"
      }
    ],
    "max_value": 100
  }
}
```

---

### **13. Geographic Data**

**`GET /visualizations/geographic-data`**

Get Indian states procurement data for choropleth maps.

**Example Response:**
```json
{
  "geographic_intelligence": {
    "state_metrics": {
      "DL": {
        "state_name": "Delhi",
        "coordinates": [28.6139, 77.2090],
        "procurement_metrics": {
          "total_tenders": 25,
          "total_value_inr": 890000000,
          "procurement_density": 0.89
        }
      }
    },
    "procurement_hotspots": [
      {
        "state_code": "DL",
        "state_name": "Delhi",
        "procurement_score": 0.89
      }
    ]
  }
}
```

---

## **🏭 Scraping Endpoints (1 endpoint)**

### **14. CPPP Portal Scraper**

**`POST /scraper/cppp`**

Trigger CPPP portal scraping with TenderX integration.

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `max_pages` | integer | 1 | Max pages to scrape (1-10) |
| `test_mode` | boolean | true | Use sample data |
| `enable_captcha` | boolean | false | Enable CAPTCHA solving |

**Example Request:**
```bash
curl -X POST "http://localhost:8002/scraper/cppp?max_pages=5&test_mode=false"
```

**Example Response:**
```json
{
  "scraping_status": "success",
  "source": "CPPP",
  "execution_results": {
    "total_tenders_processed": 25,
    "successfully_saved": 23,
    "execution_time_ms": 45000
  },
  "competitive_intelligence": {
    "service_categories_found": 7,
    "firms_detected": 15
  }
}
```

---

## **🏥 System Endpoints (3 endpoints)**

### **15. Health Check**

**`GET /health`**

Comprehensive system health check.

**Example Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "record_count": 59,
      "fts5_functional": true
    },
    "synonym_manager": {
      "status": "healthy",
      "total_keywords": 266
    },
    "search_engine": {
      "status": "healthy",
      "engine_type": "sqlite_fts5"
    }
  },
  "system_info": {
    "api_version": "1.0.0",
    "total_endpoints": 18
  }
}
```

---

### **16. System Statistics**

**`GET /stats`**

Get comprehensive system statistics.

**Example Response:**
```json
{
  "database_statistics": {
    "total_records": 59,
    "date_range": {
      "earliest": "2025-01-10",
      "latest": "2025-07-10"
    },
    "top_organizations": [
      {"organization": "NIC", "tender_count": 12}
    ]
  },
  "synonym_statistics": {
    "total_keywords": 266,
    "domains_supported": 29
  }
}
```

---

### **17. Demo Scenarios**

**`GET /test-demo-scenarios`**

Validate system with demo test scenarios.

**Example Response:**
```json
{
  "demo_validation": {
    "total_scenarios": 3,
    "successful_scenarios": 3,
    "success_rate": 100.0,
    "overall_status": "ready"
  },
  "scenario_results": [
    {
      "scenario": "Networking Equipment Search",
      "keyword": "lan",
      "expansion_test": {
        "success": true,
        "actual_expansions": ["local area network", "vlan", "ethernet"]
      }
    }
  ]
}
```

---

## **🔐 Error Responses**

### **Standard Error Format:**

```json
{
  "detail": "Error message here",
  "status_code": 400,
  "error_type": "validation_error"
}
```

### **HTTP Status Codes:**

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Endpoint doesn't exist |
| 422 | Validation Error | Parameter validation failed |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Backend temporarily unavailable |

### **Common Errors:**

**Empty Keyword:**
```json
{
  "detail": "Search keyword cannot be empty",
  "status_code": 400
}
```

**Invalid Limit:**
```json
{
  "detail": "limit: ensure this value is less than or equal to 100",
  "status_code": 422
}
```

**Database Error:**
```json
{
  "detail": "Database connection failed",
  "status_code": 500
}
```

---

## **⚡ Performance Optimization**

### **Caching:**
- Filter options cached for 10 minutes
- Executive summary cached for 2 minutes
- Visualization data cached for 5 minutes

### **Best Practices:**
- Use appropriate `limit` values (25-50 recommended)
- Enable `debug=false` for production
- Implement client-side caching
- Batch requests when possible

### **Rate Limiting (Recommended):**
```
100 requests per minute per IP
1000 requests per hour per API key
```

---

## **🔧 Integration Examples**

### **Python Client:**

```python
import requests

base_url = "http://localhost:8002"

# Search
response = requests.get(f"{base_url}/search", params={"q": "cloud", "limit": 10})
data = response.json()

print(f"Found {data['total_matches']} results")
for hit in data['hits']:
    print(f"- {hit['title']} ({hit['similarity_percent']}%)")
```

### **JavaScript/Node.js:**

```javascript
const axios = require('axios');

const baseURL = 'http://localhost:8002';

async function search(keyword) {
  const response = await axios.get(`${baseURL}/search`, {
    params: { q: keyword, limit: 10 }
  });
  
  console.log(`Found ${response.data.total_matches} results`);
  return response.data.hits;
}

search('api').then(results => console.log(results));
```

### **cURL Examples:**

```bash
# Basic search
curl "http://localhost:8002/search?q=security&limit=5"

# Filtered search
curl "http://localhost:8002/search-filtered?q=cloud&service_categories=cloud&regions=delhi"

# Get health status
curl "http://localhost:8002/health"

# Expand keyword
curl "http://localhost:8002/expand?q=lan&max_expansions=5"
```

---

## **📝 Changelog**

### **Version 1.0.0 (2025-10-22)**
- Initial API release
- 18 comprehensive endpoints
- Intelligent search with 266+ keywords
- Competitive intelligence analytics
- Visualization data generation
- TenderX integration

---

## **🆘 Support**

**Issues:** GitHub Issues  
**Questions:** GitHub Discussions  
**Email:** team@tenderintel.org  
**Documentation:** Full docs at `docs/`

**API Status:** Check `http://localhost:8002/health`
