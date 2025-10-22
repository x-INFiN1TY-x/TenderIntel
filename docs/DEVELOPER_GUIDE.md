# TenderIntel Developer Guide

**Version:** 1.0.0  
**Last Updated:** October 22, 2025  
**For:** Contributors, Maintainers, System Integrators

## **📖 Table of Contents**

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Development Workflow](#development-workflow)
5. [Testing Strategy](#testing-strategy)
6. [Extending TenderIntel](#extending-tenderintel)
7. [Performance Optimization](#performance-optimization)

---

## **🏗️ Architecture Overview**

### **System Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                   TENDERINTEL SYSTEM                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐      ┌──────────────────────────┐  │
│  │   Web UI        │      │    REST API (FastAPI)    │  │
│  │  Alpine.js      │─────▶│  18 Endpoints           │  │
│  │  Tailwind CSS   │      │  OpenAPI Docs           │  │
│  └─────────────────┘      └──────────────────────────┘  │
│                                      │                    │
│                                      ▼                    │
│                     ┌────────────────────────────┐       │
│                     │  UnifiedSearchManager      │       │
│                     │  (Engine Abstraction)      │       │
│                     └────────────────────────────┘       │
│                           │              │                │
│                           ▼              ▼                │
│                  ┌──────────────┐  ┌──────────────┐     │
│                  │ SQLite FTS5  │  │  OpenSearch  │     │
│                  │  (Default)   │  │  (Optional)  │     │
│                  └──────────────┘  └──────────────┘     │
│                           │                               │
│                           ▼                               │
│              ┌─────────────────────────┐                 │
│              │   SQLite Database       │                 │
│              │   59 Records            │                 │
│              │   33 Fields (FTS5)      │                 │
│              │   Porter Stemming       │                 │
│              └─────────────────────────┘                 │
│                                                           │
└─────────────────────────────────────────────────────────┘

      ┌──────────────────────────────────────────┐
      │         Supporting Systems                │
      ├──────────────────────────────────────────┤
      │  • SynonymManager (266+ keywords)        │
      │  • FinancialAnalysisEngine               │
      │  • CurrencyNormalizer                    │
      │  • VisualizationDataGenerator            │
      │  • TenderXIntegratedScraper              │
      └──────────────────────────────────────────┘
```

### **Technology Stack**

**Backend:**
- **Web Framework:** FastAPI 0.104+ with Uvicorn ASGI server
- **Database:** SQLite with FTS5 full-text search extension
- **Search:** BM25 ranking algorithm with Porter stemming
- **Data Models:** Pydantic 2.4+ for validation and serialization
- **Configuration:** PyYAML for flexible configuration management

**Frontend:**
- **Framework:** Alpine.js 3.x (reactive components)
- **Styling:** Tailwind CSS 3.x (utility-first)
- **Charts:** Chart.js 4.x (visualizations)
- **Maps:** Leaflet 1.9.x (geographic intelligence)
- **HTTP:** Native Fetch API with retry logic

**Data Collection:**
- **Scraping:** Selenium WebDriver for browser automation
- **CAPTCHA:** Tesseract OCR for image recognition
- **Storage:** AWS S3 via boto3 for document management

---

## **📁 Project Structure**

```
TenderIntel/
├── src/tenderintel/              # Main package source
│   ├── __init__.py              # Public API exports
│   ├── core/                    # Core functionality
│   │   ├── client.py           # TenderIntelClient interface
│   │   ├── database_manager.py # Database operations
│   │   └── models.py           # Pydantic data models
│   ├── search/                  # Search engine
│   │   ├── manager.py          # UnifiedSearchManager
│   │   ├── sqlite_fts5_engine.py # SQLite implementation
│   │   ├── synonym_manager.py   # Keyword expansion (original)
│   │   ├── synonym_manager_yaml.py # YAML-based (v2.0)
│   │   └── engines/            # Engine implementations
│   ├── analytics/               # Analytics engines
│   │   ├── financial_analysis_engine.py
│   │   ├── currency_normalizer.py
│   │   └── visualization_data_generator.py
│   ├── scraper/                 # Data collection
│   │   ├── tenderx_integration.py
│   │   ├── captcha_solver.py
│   │   └── downloader.py
│   ├── api/                     # API server
│   │   └── server.py           # FastAPI application
│   └── config/                  # Configuration
│       ├── defaults.py
│       ├── loader.py
│       └── validator.py
├── frontend/                     # Web interface
│   ├── index.html              # Main application shell
│   ├── js/
│   │   ├── app.js              # Application state
│   │   ├── components/         # Page components
│   │   ├── services/           # API services
│   │   └── utils/              # Utility functions
│   └── css/                    # Custom styles
├── tests/                        # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # API integration tests
│   └── financial/              # Financial tests
├── config/                       # Configuration files
│   ├── synonyms.yaml           # Keyword dictionary
│   ├── config.yaml             # Main config
│   └── dev/                    # Development configs
├── scripts/                      # Utility scripts
│   ├── setup/                  # Initialization
│   └── data/                   # Data management
├── docs/                         # Documentation
│   ├── INSTALLATION.md
│   ├── USER_MANUAL.md
│   ├── API_REFERENCE.md
│   └── DEVELOPER_GUIDE.md (this file)
├── docker/                       # Docker configs
├── examples/                     # Usage examples
├── README.md                     # Project overview
├── CONTRIBUTING.md              # Contribution guide
├── CODE_OF_CONDUCT.md          # Community standards
├── SECURITY.md                  # Security policy
├── CHANGELOG.md                 # Version history
└── pyproject.toml              # Package configuration
```

---

## **🧩 Core Components**

### **1. Search Engine Architecture**

**UnifiedSearchManager** (`src/tenderintel/search/manager.py`)

Central search interface that abstracts engine selection:

```python
class UnifiedSearchManager:
    """Single interface for search operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.synonym_manager = SynonymManager()
        self.current_engine = self._initialize_engine()
    
    async def search(self, keyword: str, filters: Dict, limit: int):
        # 1. Expand keyword
        expansion = self.synonym_manager.expand_keyword(keyword)
        
        # 2. Execute on active engine
        result = await self.current_engine.execute_search(
            keyword, expansion['expanded_phrases'], filters, limit
        )
        
        # 3. Return unified response
        return result
```

**Key Design Patterns:**
- **Strategy Pattern:** Switchable search engines (SQLite/OpenSearch)
- **Adapter Pattern:** Unified interface for different backends
- **Factory Pattern:** Engine creation based on configuration

---

### **2. Synonym Expansion System**

**SynonymManagerV2** (`src/tenderintel/search/synonym_manager_yaml.py`)

YAML-based keyword expansion with domain classification:

```python
class SynonymManagerV2:
    """Enhanced synonym manager with external configuration"""
    
    def __init__(self, synonyms_file: str = "config/synonyms.yaml"):
        self._load_from_yaml()  # Load 266+ keywords
        
    def expand_keyword(self, keyword: str, max_expansions: int = 5):
        # Returns: expanded_phrases, domain, confidence, weight
        pass
    
    def reload_synonyms(self):
        # Hot-reload without server restart
        pass
```

**YAML Structure:**
```yaml
networking:
  lan:
    expansions:
      - local area network
      - layer 2 switch
      - vlan
      - ethernet
    weight: 1.0
    anti_patterns:
      - land development
```

**Adding New Keywords:**
1. Edit `config/synonyms.yaml`
2. Add keyword under appropriate domain
3. Specify expansions and optional weight
4. Test: `python src/tenderintel/search/synonym_manager_yaml.py`
5. Hot-reload: Call `reload_synonyms()` API (future feature)

---

### **3. Database Schema**

**FTS5 Virtual Table** (33 fields)

```sql
CREATE VIRTUAL TABLE tenders USING fts5(
    -- Core Fields (6)
    title, org, status, aoc_date, tender_id, url,
    
    -- Classification (5)
    service_category, value_range, region, 
    department_type, complexity,
    
    -- Intelligence (12)  
    keywords, award_value, currency, exchange_rate,
    inr_normalized_value, deal_size_category,
    winning_firm, runner_up_firms, total_bidders,
    ...
    
    -- Search Configuration
    tokenize=porter,      -- Porter stemming algorithm
    prefix='2,3'         -- Enable 2-3 char prefix matching
);
```

**Indexing Strategy:**
- **Primary:** Title field (FTS5 indexed)
- **Auxiliary:** All other fields (filterable, not full-text)
- **Stemming:** Porter algorithm for English
- **Prefix:** Enabled for short technical terms (api, lan, iam)

---

### **4. API Server**

**FastAPI Application** (`src/tenderintel/api/server.py`)

```python
app = FastAPI(
    title="TenderIntel API",
    version="1.0.0",
    description="AI-Powered Competitive Intelligence"
)

# Initialize services
search_manager = UnifiedSearchManager(load_config())
database_manager = DatabaseManager(db_path)
synonym_manager = SynonymManager()

@app.get("/search")
async def search_tenders(q: str, limit: int = 25):
    # 1. Validate input
    # 2. Call search_manager
    # 3. Return results
    pass
```

**Endpoint Categories:**
- **Search (5):** search, expand, search-filtered, faceted-search, filter-options
- **Intelligence (1):** competitive-intelligence/summary
- **Analytics (4):** firm-scorecard, market-analysis, deal-benchmarking, normalize-currency
- **Visualization (3):** heatmap-data, geographic-data, executive-summary
- **Scraping (1):** scraper/cppp
- **System (3):** health, stats, test-demo-scenarios
- **Landing (1):** root landing page

---

### **5. Financial Analysis**

**FinancialAnalysisEngine** (`src/tenderintel/analytics/financial_analysis_engine.py`)

```python
class FinancialAnalysisEngine:
    """Advanced financial analysis with statistical modeling"""
    
    async def generate_firm_financial_scorecard(self, firm_name: str):
        # 1. Get firm tenders from database
        # 2. Calculate portfolio metrics
        # 3. Calculate market share
        # 4. Analyze growth trajectory
        # 5. Assess competitive position
        # 6. Calculate risk metrics
        return FirmFinancialProfile(...)
    
    async def calculate_market_financial_metrics(self, service_category: str):
        # 1. Get all tenders in category
        # 2. Calculate HHI index
        # 3. Analyze price distribution
        # 4. Calculate growth rate
        # 5. Assess competitive intensity
        return MarketFinancialMetrics(...)
```

**Key Metrics:**
- **HHI Index:** Market concentration (0-1 scale)
- **Deal Size Classification:** Micro/Small/Medium/Large/Mega
- **Portfolio Value:** Sum of all contract values
- **Market Share:** Firm value / Total market value × 100
- **Growth Rate:** (Recent - Early) / Early × 100

---

## **💻 Development Workflow**

### **Setting Up Development Environment**

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/tenderintel.git
cd TenderIntel

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install with dev dependencies
pip install -e ".[dev,tenderx]"

# 4. Install pre-commit hooks
pre-commit install

# 5. Initialize database
make setup

# 6. Verify installation
pytest

# 7. Start development server
make run
```

### **Development Commands**

```bash
# Code formatting
make format              # black + isort

# Code quality
make lint                # flake8 + mypy + bandit

# Testing
make test                # All tests with coverage
make test-unit           # Unit tests only
make test-integration    # Integration tests only

# Development server
make run                 # Start with auto-reload

# Database operations
make reset-db            # Reset database
make status              # Project status

# Quick start
make quickstart          # Setup + Run
```

### **Git Workflow**

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Run quality checks
make format
make lint
make test

# 4. Push and create PR
git push origin feature/your-feature-name
# Create PR on GitHub
```

**Commit Message Convention:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code formatting
- `refactor:` Code restructuring
- `test:` Test additions/modifications
- `chore:` Build/tooling changes

---

## **🧪 Testing Strategy**

### **Test Organization**

```
tests/
├── unit/                 # Component-level tests
│   ├── test_synonym_manager.py
│   ├── test_search_engine.py
│   └── test_financial_analysis.py
├── integration/          # API integration tests  
│   ├── test_api_comprehensive.py
│   └── test_search_accuracy.py
├── financial/            # Financial system tests
│   └── test_financial_analysis_system.py
└── e2e/                  # End-to-end workflows
    └── test_user_workflows.py
```

### **Writing Tests**

**Unit Test Example:**
```python
import pytest
from tenderintel.search.synonym_manager_yaml import SynonymManagerV2

def test_keyword_expansion():
    sm = SynonymManagerV2()
    result = sm.expand_keyword("lan")
    
    assert "local area network" in result['expanded_phrases']
    assert result['domain'] == "networking"
    assert result['confidence'] >= 0.9

def test_anti_patterns():
    sm = SynonymManagerV2()
    result = sm.expand_keyword("lan")
    
    assert "land development" in result['anti_patterns']
    assert "landscape" in result['anti_patterns']
```

**Integration Test Example:**
```python
import pytest
import requests

BASE_URL = "http://localhost:8002"

def test_search_endpoint():
    response = requests.get(f"{BASE_URL}/search", params={"q": "lan"})
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['total_matches'] > 0
    assert 'lan' in data['query'].lower()
    assert data['execution_time_ms'] < 100  # Performance check
```

### **Running Tests**

```bash
# All tests with coverage
pytest --cov=src/tenderintel --cov-report=html

# Specific test file
pytest tests/unit/test_synonym_manager.py -v

# Specific test function  
pytest -k "test_keyword_expansion" -v

# With debug output
pytest -s -v

# Coverage threshold
pytest --cov=src/tenderintel --cov-fail-under=80
```

---

## **🔧 Extending TenderIntel**

### **Adding New Keywords**

**Method 1: Edit YAML (Recommended)**
```yaml
# config/synonyms.yaml
your_domain:
  your_keyword:
    expansions:
      - expansion phrase 1
      - expansion phrase 2
    weight: 1.0
    anti_patterns:
      - avoid this phrase
```

**Method 2: Programmatic Addition**
```python
from tenderintel.search.synonym_manager_yaml import SynonymManagerV2

sm = SynonymManagerV2()
sm.synonyms['newkeyword'] = ['expansion1', 'expansion2']
sm.domain_mapping['your_domain'].add('newkeyword')
```

### **Adding New API Endpoint**

```python
# In src/tenderintel/api/server.py

@app.get("/your-endpoint", tags=["Your Category"])
async def your_endpoint_function(
    param1: str = Query(..., description="Parameter description"),
    param2: int = Query(25, ge=1, le=100)
) -> Dict[str, Any]:
    """
    Your endpoint documentation
    
    Detailed description of what this endpoint does.
    """
    try:
        # Your logic here
        result = process_data(param1, param2)
        return {"success": True, "data": result}
        
    except Exception as e:
        logger.error(f"Endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### **Adding New Search Engine**

**1. Implement SearchEngine Interface:**
```python
# src/tenderintel/search/engines/your_engine.py

from ..base import SearchEngine, UnifiedSearchResponse

class YourSearchEngine(SearchEngine):
    engine_type = SearchEngineType.YOUR_ENGINE
    
    async def execute_search(self, keyword, expanded_phrases, filters, limit):
        # Your implementation
        pass
    
    async def health_check(self):
        # Health check logic
        pass
```

**2. Register in UnifiedSearchManager:**
```python
# src/tenderintel/search/manager.py

def _initialize_engine(self):
    if requested_engine == 'your_engine':
        return YourSearchEngine(config)
```

### **Adding New Visualization**

```python
# src/tenderintel/analytics/visualization_data_generator.py

class YourVisualizationGenerator:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def generate_your_visualization_data(self) -> Dict[str, Any]:
        # Query database
        # Process data for visualization
        # Return formatted data
        return {
            "visualization_data": {...},
            "metadata": {...}
        }
```

**Add API Endpoint:**
```python
@app.get("/visualizations/your-viz")
async def get_your_visualization():
    generator = YourVisualizationGenerator(db_path)
    return generator.generate_your_visualization_data()
```

---

## **⚡ Performance Optimization**

### **Database Optimization**

**FTS5 Performance:**
```sql
-- Optimize FTS5 index
PRAGMA optimize;

-- Analyze query patterns
EXPLAIN QUERY PLAN 
SELECT * FROM tenders WHERE tenders MATCH 'keyword';

-- Rebuild index if needed
INSERT INTO tenders(tenders) VALUES('rebuild');
```

**Connection Pool:**
```python
# Use connection pooling for concurrent requests
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()
```

### **API Performance**

**Caching Strategy:**
```python
# Frontend (JavaScript)
class CacheService:
    def set(key, value, ttl=300000):  # 5 minutes default
        cache[key] = {value, timestamp: Date.now(), ttl}
    
    def get(key):
        if cached and not_expired:
            return cached.value
        return null
```

**Backend Optimization:**
```python
# Use async/await for I/O operations
async def fetch_data():
    results = await asyncio.gather(
        get_search_results(),
        get_intelligence_data(),
        get_analytics()
    )
    return combine_results(results)
```

### **Frontend Optimization**

**Lazy Loading:**
```javascript
// Load heavy components only when needed
const Heatmap = lazy(() => import('./components/heatmap.js'));
```

**Debouncing:**
```javascript
// Debounce search input
const debouncedSearch = debounce(performSearch, 300);
```

---

## **🔍 Debugging**

### **Enable Debug Mode**

**API Server:**
```bash
# Start with debug logging
uvicorn tenderintel.api.server:app --log-level=debug --reload
```

**Search Debug:**
```bash
# Add debug=true to see FTS5 queries
curl "http://localhost:8002/search?q=lan&debug=true"
```

**Frontend Debug:**
```javascript
// Enable debug console
window.app.logDebugInfo();  // Shows app state

// Check API cache
window.api.getCacheInfo();   // Shows cached responses
```

### **Common Debugging Scenarios**

**Search Returns Wrong Results:**
```python
# Check synonym expansion
result = synonym_manager.expand_keyword("your_keyword")
print(f"Expansions: {result['expanded_phrases']}")
print(f"Domain: {result['domain']}")

# Check FTS5 query
# Set debug=true in search endpoint to see actual FTS5 MATCH query
```

**Performance Issues:**
```bash
# Profile Python code
python -m cProfile -o profile.stats src/tenderintel/api/server.py

# Analyze with snakeviz
snakeviz profile.stats
```

**Database Issues:**
```bash
# Check database integrity
sqlite3 data/tenders.db "PRAGMA integrity_check;"

# Check FTS5 index
sqlite3 data/tenders.db "INSERT INTO tenders(tenders) VALUES('integrity-check');"
```

---

## **📦 Releasing New Versions**

### **Release Checklist**

1. **Update Version:**
```python
# src/tenderintel/__init__.py
__version__ = "1.1.0"

# pyproject.toml
version = "1.1.0"
```

2. **Update Changelog:**
```markdown
## [1.1.0] - 2025-01-15

### Added
- Feature descriptions
### Fixed
- Bug fix descriptions
```

3. **Run Full Test Suite:**
```bash
make full-test  # format + lint + test
```

4. **Build Distribution:**
```bash
make build-dist  # Creates wheel and tarball
```

5. **Tag Release:**
```bash
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

6. **Publish to PyPI:**
```bash
make upload-prod  # Uploads to PyPI
```

---

## **🏛️ Architecture Decisions**

### **Why SQLite FTS5 as Default?**

**Pros:**
- Zero configuration required
- Excellent performance (<2ms) for <100K records
- Built-in with Python
- ACID compliance
- No external dependencies

**When to Use OpenSearch:**
- Dataset >100K records
- Distributed search needed
- Multiple concurrent write operations
- Advanced analytics requirements

### **Why Alpine.js for Frontend?**

**Pros:**
- Lightweight (15KB vs React 140KB)
- Zero build step (edit and refresh)
- Vue-like reactivity
- Easy to learn
- Fast development

**When to Consider React:**
- Complex state management needed
- Large development team
- Extensive component library required
- TypeScript type safety critical

### **Why Hybrid Architecture?**

**Design Philosophy:**
- Start simple (SQLite)
- Scale when needed (OpenSearch)
- No forced complexity
- User choice flexibility

---

## **🎯 Best Practices**

### **Code Style**

**Python:**
```python
# Use type hints
def expand_keyword(keyword: str, max_expansions: int = 5) -> Dict[str, Any]:
    pass

# Use docstrings (Google style)
def function_name(param: str) -> str:
    """
    Brief description.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
    pass

# Use Pydantic for validation
class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=50)
```

**JavaScript:**
```javascript
// Use const/let (never var)
const result = await api.search(keyword);

// Use arrow functions
const formatCurrency = (value) => `₹${value/10000000}Cr`;

// Comment complex logic
// Calculate BM25 normalization: (max - score) / (max - min)
const similarity = normalize(score, min, max);
```

### **Security Guidelines**

```python
# ✅ DO: Parameterized queries
cursor.execute("SELECT * FROM tenders WHERE id = ?", (tender_id,))

# ❌ DON'T: String interpolation
cursor.execute(f"SELECT * FROM tenders WHERE id = {tender_id}")

# ✅ DO: Input validation
class SearchRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=50)

# ❌ DON'T: Trust user input
keyword = request.get('q')  # No validation
```

---

## **📚 Additional Resources**

**Code References:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite FTS5](https://sqlite.org/fts5.html)
- [Pydantic](https://docs.pydantic.dev/)
- [Alpine.js](https://alpinejs.dev/)

**Learning Resources:**
- BM25 Algorithm: [Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
- FTS5 Internals: [SQLite Docs](https://www.sqlite.org/fts5.html)
- Porter Stemming: [Tartarus](https://tartarus.org/martin/PorterStemmer/)

---

## **🤝 Getting Help**

**For Development Questions:**
- GitHub Discussions (preferred)
- Email: dev@tenderintel.org
- Code reviews in PRs

**For Architecture Decisions:**
- Create GitHub Issue with `architecture` label
- Propose in GitHub Discussions
- Email maintainers for major changes

---

**Happy coding! 🚀**
