"""
TenderIntel API Components
=========================

RESTful API server with comprehensive OpenAPI documentation.

Features:
- FastAPI-based production server
- 9 comprehensive endpoints for search and intelligence
- Real-time competitive analysis
- Integrated TenderX scraping capabilities
"""

from .server import app, create_app, main

__all__ = [
    "app",
    "create_app", 
    "main"
]
