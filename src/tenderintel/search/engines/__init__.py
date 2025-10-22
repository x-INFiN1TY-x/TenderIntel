#!/usr/bin/env python3
"""
Search Engine Implementations for TenderIntel
Conditional import pattern for optional OpenSearch support
"""

import logging

logger = logging.getLogger(__name__)

# SQLite FTS5 Engine - ALWAYS available (no external dependencies)
from .sqlite_engine import SQLiteFTS5Engine

# OpenSearch Engine - OPTIONAL (requires opensearch-py)
try:
    from .opensearch_engine import OpenSearchEngine
    OPENSEARCH_AVAILABLE = True
    logger.debug("OpenSearch engine available")
except ImportError:
    OPENSEARCH_AVAILABLE = False
    logger.debug("OpenSearch engine not available (opensearch-py not installed)")
    
    # Create dummy class that provides helpful error message
    class OpenSearchEngine:
        """Placeholder when OpenSearch is not installed"""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "OpenSearch engine not available.\n"
                "Install with: pip install tenderintel[opensearch]\n"
                "Or switch to SQLite engine in config.yaml"
            )


__all__ = [
    'SQLiteFTS5Engine',
    'OpenSearchEngine',
    'OPENSEARCH_AVAILABLE'
]


def get_available_engines() -> list:
    """
    Get list of available search engines
    
    Returns:
        List of engine names that can be used
    """
    engines = ['sqlite']  # SQLite always available
    
    if OPENSEARCH_AVAILABLE:
        engines.append('opensearch')
    
    return engines


def is_engine_available(engine_name: str) -> bool:
    """
    Check if specific engine is available
    
    Args:
        engine_name: Name of engine to check ('sqlite' or 'opensearch')
    
    Returns:
        True if engine is available, False otherwise
    """
    engine_name = engine_name.lower()
    
    if engine_name == 'sqlite':
        return True  # Always available
    elif engine_name == 'opensearch':
        return OPENSEARCH_AVAILABLE
    else:
        return False


def get_engine_installation_command(engine_name: str) -> str:
    """
    Get installation command for an engine
    
    Args:
        engine_name: Name of engine
    
    Returns:
        Installation command string
    """
    engine_name = engine_name.lower()
    
    if engine_name == 'sqlite':
        return "SQLite FTS5 is included by default - no installation needed"
    elif engine_name == 'opensearch':
        return "pip install tenderintel[opensearch]"
    else:
        return f"Unknown engine: {engine_name}"


def main():
    """Test engine availability"""
    print("TenderIntel Search Engines")
    print("=" * 50)
    
    print(f"\n📦 Available Engines: {', '.join(get_available_engines())}")
    
    print("\n🔍 Engine Availability:")
    print(f"   SQLite FTS5: {'✅ Available' if is_engine_available('sqlite') else '❌ Not Available'}")
    print(f"   OpenSearch: {'✅ Available' if is_engine_available('opensearch') else '❌ Not Available'}")
    
    if not OPENSEARCH_AVAILABLE:
        print(f"\n💡 To enable OpenSearch:")
        print(f"   {get_engine_installation_command('opensearch')}")
    
    print("\n✅ Engine availability check completed!")


if __name__ == "__main__":
    main()
