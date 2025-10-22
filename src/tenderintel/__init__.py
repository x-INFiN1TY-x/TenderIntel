"""
TenderIntel - AI-Powered Competitive Intelligence for Government Procurement
============================================================================

A comprehensive platform that combines production-grade government portal scraping 
with intelligent search capabilities to provide actionable competitive intelligence.

Key Features:
- 215+ Technical keyword expansion with zero false positives
- BM25 relevance ranking with phrase-aware matching  
- Real-time CPPP and GeM portal integration
- Advanced competitive analysis and market intelligence
- Professional APIs and web interface

Quick Start:
    >>> from tenderintel import TenderIntelClient
    >>> client = TenderIntelClient()
    >>> results = client.search("api gateway")
    >>> print(f"Found {len(results)} relevant tenders")

For detailed documentation, visit: https://tenderintel.readthedocs.io/
"""

__version__ = "1.0.0"
__author__ = "TenderIntel Team"
__email__ = "team@tenderintel.org"
__license__ = "MIT"

# Core imports for public API
from .core.client import TenderIntelClient
from .core.models import (
    TenderRecord,
    SearchResult,
    CompetitiveIntelligence,
    MarketAnalysis
)
from .search.sqlite_fts5_engine import SQLiteFTS5Engine
from .search.synonym_manager import SynonymManager
from .scraper.tenderx_integration import TenderXIntegratedScraper, TenderXAdapter

# Version info tuple for programmatic access
VERSION_INFO = tuple(map(int, __version__.split('.')))

__all__ = [
    # Version and metadata
    "__version__",
    "VERSION_INFO",
    
    # Core client interface
    "TenderIntelClient",
    
    # Data models
    "TenderRecord",
    "SearchResult", 
    "CompetitiveIntelligence",
    "MarketAnalysis",
    
    # Engine components
    "SQLiteFTS5Engine",
    "SynonymManager",
    "TenderXIntegratedScraper",
    "TenderXAdapter"
]

def get_version() -> str:
    """Get the current version of TenderIntel."""
    return __version__

def get_build_info() -> dict:
    """Get comprehensive build and version information."""
    return {
        "version": __version__,
        "version_info": VERSION_INFO,
        "author": __author__,
        "license": __license__,
        "python_requires": ">=3.8",
        "homepage": "https://github.com/tenderintel/tenderintel"
    }
