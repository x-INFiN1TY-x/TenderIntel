#!/usr/bin/env python3
"""
Default Configuration for TenderIntel
Provides sensible defaults that work out-of-the-box with SQLite FTS5
"""

from typing import Dict, Any


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration - optimized for SQLite FTS5
    
    This configuration works immediately after installation with zero setup.
    Users never need to modify this unless they want to use OpenSearch.
    
    Returns:
        Complete default configuration dictionary
    """
    return {
        'search': {
            # Search engine: 'sqlite' or 'opensearch'
            # Default: sqlite (no external dependencies required)
            'engine': 'sqlite',
            
            # Synonym expansion settings
            'synonyms': {
                'file': 'config/synonyms.yaml',
                'enable_auto_expansion': True,
                'max_expansions': 6
            },
            
            # SQLite FTS5 configuration (always active)
            'sqlite': get_sqlite_config(),
            
            # OpenSearch configuration (optional, ignored if engine != opensearch)
            'opensearch': {
                'enabled': False,  # Explicitly disabled by default
                'hosts': [{'host': 'localhost', 'port': 9200}],
                'use_ssl': False,
                'verify_certs': False,
                'timeout': 30,
                'max_retries': 3,
                'index_prefix': 'tenders',
                'shards': 2,
                'replicas': 1
            }
        },
        
        'performance': {
            'query_timeout': 30,
            'max_search_results': 100,
            'default_search_results': 25,
            'enable_response_cache': True,
            'cache_ttl_seconds': 300
        },
        
        'api': {
            'host': '0.0.0.0',
            'port': 8000,
            'cors_enabled': True,
            'cors_origins': ['*'],
            'rate_limit_enabled': False
        },
        
        'logging': {
            'level': 'INFO',
            'log_queries': True,
            'log_performance': True,
            'log_file': 'logs/tenderintel.log'
        },
        
        'analytics': {
            'enable_currency_normalization': True,
            'default_currency': 'INR',
            'enable_financial_analysis': True,
            'enable_competitive_intelligence': True
        }
    }


def get_sqlite_config() -> Dict[str, Any]:
    """
    Get SQLite FTS5 specific configuration
    
    Optimized for production-grade performance with up to 100K records.
    
    Returns:
        SQLite configuration dictionary
    """
    return {
        'database_path': 'data/tenders.db',
        'fts5_tokenizer': 'porter unicode61',
        'enable_wal': True,  # Write-Ahead Logging for better concurrency
        'cache_size_kb': 64000,  # 64MB cache for better performance
        'mmap_size_mb': 256,  # 256MB memory-mapped I/O
        'page_size': 4096,  # Standard page size
        'temp_store': 'memory',  # Temporary tables in memory
        'synchronous': 'normal',  # Balance between safety and speed
        'optimize_on_startup': True,  # Run ANALYZE on startup
        'connection_pool_size': 5  # Number of reusable connections
    }


def get_opensearch_config() -> Dict[str, Any]:
    """
    Get OpenSearch specific configuration example
    
    This is provided as a reference for users who want to enable OpenSearch.
    By default, OpenSearch is disabled.
    
    Returns:
        OpenSearch configuration dictionary
    """
    return {
        'enabled': False,  # Must be explicitly enabled
        'hosts': [
            {'host': 'localhost', 'port': 9200}
        ],
        'use_ssl': False,
        'verify_certs': False,
        'ca_certs': None,
        'client_cert': None,
        'client_key': None,
        'timeout': 30,
        'max_retries': 3,
        'retry_on_timeout': True,
        'http_compress': True,
        
        # Index configuration
        'index_prefix': 'tenders',
        'index_pattern': 'tenders-*',
        'shards': 2,
        'replicas': 1,
        'refresh_interval': '5s',
        'max_result_window': 50000,
        
        # Performance tuning
        'bulk_chunk_size': 1000,
        'bulk_queue_size': 4,
        'request_timeout': 60,
        
        # Analyzer settings
        'analyzer': {
            'name': 'competitive_intelligence_analyzer',
            'tokenizer': 'standard',
            'filters': ['lowercase', 'asciifolding', 'porter_stem']
        },
        
        # Synonym settings
        'synonyms': {
            'enable_synonym_graph': True,
            'synonyms_file': 'config/opensearch_synonyms.txt'
        }
    }


def get_minimal_config() -> Dict[str, Any]:
    """
    Get minimal configuration for quick start
    
    Absolute minimum required to run TenderIntel with SQLite.
    
    Returns:
        Minimal configuration dictionary
    """
    return {
        'search': {
            'engine': 'sqlite',
            'sqlite': {
                'database_path': 'data/tenders.db'
            }
        }
    }


# Configuration recommendations based on deployment scale
DEPLOYMENT_RECOMMENDATIONS = {
    'small': {
        'description': 'Small deployment: <10K records, <10 users',
        'recommended_engine': 'sqlite',
        'config': {
            'search': {
                'engine': 'sqlite',
                'sqlite': {
                    'cache_size_kb': 32000,  # 32MB cache
                    'mmap_size_mb': 128
                }
            }
        }
    },
    'medium': {
        'description': 'Medium deployment: 10K-100K records, 10-20 users',
        'recommended_engine': 'sqlite',
        'config': {
            'search': {
                'engine': 'sqlite',
                'sqlite': {
                    'cache_size_kb': 64000,  # 64MB cache
                    'mmap_size_mb': 256,
                    'enable_wal': True
                }
            },
            'performance': {
                'enable_response_cache': True,
                'cache_ttl_seconds': 600
            }
        }
    },
    'large': {
        'description': 'Large deployment: 100K+ records, 20+ users',
        'recommended_engine': 'opensearch',
        'recommendation_message': (
            'For large deployments, consider OpenSearch for better performance. '
            'However, SQLite FTS5 can still work with proper optimization. '
            'Install OpenSearch with: pip install tenderintel[opensearch]'
        ),
        'config': {
            'search': {
                'engine': 'opensearch',  # Recommended but not required
                'opensearch': {
                    'enabled': True,
                    'shards': 3,
                    'replicas': 2
                }
            }
        }
    }
}


def get_recommended_config(deployment_scale: str) -> Dict[str, Any]:
    """
    Get recommended configuration for deployment scale
    
    Args:
        deployment_scale: 'small', 'medium', or 'large'
    
    Returns:
        Recommended configuration for the specified scale
    """
    if deployment_scale not in DEPLOYMENT_RECOMMENDATIONS:
        raise ValueError(f"Unknown deployment scale: {deployment_scale}")
    
    recommendation = DEPLOYMENT_RECOMMENDATIONS[deployment_scale]
    
    # Start with default config
    config = get_default_config()
    
    # Merge recommended settings
    for key, value in recommendation['config'].items():
        if key in config:
            config[key].update(value)
        else:
            config[key] = value
    
    return config
