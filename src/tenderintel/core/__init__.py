"""
TenderIntel Core Components
==========================

Core functionality including database management, data models, and client interfaces.
"""

from .database_manager import DatabaseManager
from .models import TenderRecord, SearchResult, CompetitiveIntelligence, MarketAnalysis

__all__ = [
    "DatabaseManager",
    "TenderRecord", 
    "SearchResult",
    "CompetitiveIntelligence",
    "MarketAnalysis"
]
