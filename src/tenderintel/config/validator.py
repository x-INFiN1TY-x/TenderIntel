#!/usr/bin/env python3
"""
Configuration Validator for TenderIntel
Validates configuration and provides helpful error messages
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    valid: bool
    engine: Optional[str] = None
    error: Optional[str] = None
    suggestion: Optional[str] = None
    fallback_action: Optional[str] = None
    warnings: Optional[list] = None


class ConfigValidator:
    """
    Validates TenderIntel configuration with helpful feedback
    
    Provides clear error messages and suggestions when:
    - OpenSearch is requested but not installed
    - OpenSearch is requested but cluster is unavailable
    - Configuration is invalid or incomplete
    """
    
    def __init__(self):
        self.warnings = []
    
    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete configuration
        
        Args:
            config: Configuration dictionary to validate
        
        Returns:
            ValidationResult with status and helpful messages
        """
        self.warnings = []
        
        # Validate search configuration exists
        if 'search' not in config:
            return ValidationResult(
                valid=False,
                error="Missing 'search' section in configuration",
                suggestion="Add 'search' section with 'engine' key",
                fallback_action="Will use SQLite with default settings"
            )
        
        search_config = config['search']
        
        # Validate engine type
        engine = search_config.get('engine', 'sqlite').lower()
        if engine not in ['sqlite', 'opensearch']:
            return ValidationResult(
                valid=False,
                error=f"Invalid engine type: {engine}",
                suggestion="Engine must be 'sqlite' or 'opensearch'",
                fallback_action="Will use SQLite instead"
            )
        
        # Validate SQLite configuration
        sqlite_result = self._validate_sqlite_config(search_config.get('sqlite', {}))
        if not sqlite_result.valid:
            return sqlite_result
        
        # Validate OpenSearch configuration if selected
        if engine == 'opensearch':
            opensearch_result = self._validate_opensearch_config(
                search_config.get('opensearch', {})
            )
            if not opensearch_result.valid:
                return opensearch_result
        
        # Configuration is valid
        return ValidationResult(
            valid=True,
            engine=engine,
            warnings=self.warnings if self.warnings else None
        )
    
    def _validate_sqlite_config(self, sqlite_config: Dict[str, Any]) -> ValidationResult:
        """Validate SQLite-specific configuration"""
        
        if not sqlite_config:
            self.warnings.append("No SQLite configuration provided, using defaults")
            return ValidationResult(valid=True)
        
        # Validate database path
        db_path = sqlite_config.get('database_path')
        if not db_path:
            return ValidationResult(
                valid=False,
                error="SQLite database_path not specified",
                suggestion="Add search.sqlite.database_path to configuration",
                fallback_action="Will use default: data/tenders.db"
            )
        
        # Validate numeric parameters
        cache_size = sqlite_config.get('cache_size_kb', 64000)
        if cache_size < 1000:
            self.warnings.append(
                f"SQLite cache_size_kb ({cache_size}) is very small, recommend at least 10000"
            )
        
        return ValidationResult(valid=True)
    
    def _validate_opensearch_config(self, opensearch_config: Dict[str, Any]) -> ValidationResult:
        """Validate OpenSearch-specific configuration"""
        
        # Check if OpenSearch library is available
        try:
            import opensearchpy
            opensearch_available = True
        except ImportError:
            opensearch_available = False
        
        if not opensearch_available:
            return ValidationResult(
                valid=False,
                error="OpenSearch selected but opensearch-py not installed",
                suggestion="Install with: pip install tenderintel[opensearch]",
                fallback_action="Will use SQLite FTS5 instead"
            )
        
        # Check if OpenSearch is explicitly enabled
        if not opensearch_config.get('enabled', False):
            return ValidationResult(
                valid=False,
                error="OpenSearch selected but not enabled in configuration",
                suggestion="Set search.opensearch.enabled = true in config.yaml",
                fallback_action="Will use SQLite FTS5 instead"
            )
        
        # Validate hosts configuration
        hosts = opensearch_config.get('hosts', [])
        if not hosts:
            return ValidationResult(
                valid=False,
                error="OpenSearch enabled but no hosts configured",
                suggestion="Add search.opensearch.hosts to configuration",
                fallback_action="Will use SQLite FTS5 instead"
            )
        
        # Validate host format
        for i, host in enumerate(hosts):
            if not isinstance(host, dict):
                return ValidationResult(
                    valid=False,
                    error=f"Invalid host format at index {i}",
                    suggestion="Hosts must be dict with 'host' and 'port' keys",
                    fallback_action="Will use SQLite FTS5 instead"
                )
            
            if 'host' not in host:
                return ValidationResult(
                    valid=False,
                    error=f"Missing 'host' key in hosts[{i}]",
                    suggestion="Each host must have 'host' and 'port' keys",
                    fallback_action="Will use SQLite FTS5 instead"
                )
        
        # Try to connect to OpenSearch cluster
        connection_result = self._test_opensearch_connection(opensearch_config)
        if not connection_result.valid:
            return connection_result
        
        return ValidationResult(valid=True)
    
    def _test_opensearch_connection(self, opensearch_config: Dict[str, Any]) -> ValidationResult:
        """
        Test connection to OpenSearch cluster
        
        Args:
            opensearch_config: OpenSearch configuration
        
        Returns:
            ValidationResult indicating connection status
        """
        try:
            from opensearchpy import OpenSearch
            
            # Create client
            client = OpenSearch(
                hosts=opensearch_config.get('hosts', []),
                use_ssl=opensearch_config.get('use_ssl', False),
                verify_certs=opensearch_config.get('verify_certs', False),
                timeout=5  # Short timeout for validation
            )
            
            # Test connection with cluster health
            health = client.cluster.health()
            
            status = health.get('status', 'unknown')
            
            if status == 'red':
                self.warnings.append(
                    f"OpenSearch cluster status is RED. Some functionality may be impaired."
                )
            elif status == 'yellow':
                self.warnings.append(
                    f"OpenSearch cluster status is YELLOW. This is acceptable for development."
                )
            
            logger.info(f"OpenSearch connection successful. Cluster status: {status}")
            return ValidationResult(valid=True)
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Cannot connect to OpenSearch cluster: {str(e)}",
                suggestion="Check if OpenSearch is running and accessible at configured hosts",
                fallback_action="Will use SQLite FTS5 instead"
            )
    
    def validate_and_suggest(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration and provide suggestions for improvement
        
        Args:
            config: Configuration to validate
        
        Returns:
            Dictionary with validation results and suggestions
        """
        result = self.validate(config)
        
        suggestions = []
        
        if result.valid:
            # Provide optimization suggestions
            search_config = config.get('search', {})
            engine = search_config.get('engine', 'sqlite')
            
            if engine == 'sqlite':
                # SQLite-specific suggestions
                sqlite_config = search_config.get('sqlite', {})
                cache_size = sqlite_config.get('cache_size_kb', 64000)
                
                if cache_size < 32000:
                    suggestions.append({
                        'type': 'performance',
                        'message': 'Consider increasing cache_size_kb to at least 32000 for better performance'
                    })
                
                if not sqlite_config.get('enable_wal', True):
                    suggestions.append({
                        'type': 'concurrency',
                        'message': 'Enable WAL mode (enable_wal: true) for better concurrent access'
                    })
            
            elif engine == 'opensearch':
                # OpenSearch-specific suggestions
                opensearch_config = search_config.get('opensearch', {})
                replicas = opensearch_config.get('replicas', 1)
                
                if replicas < 1:
                    suggestions.append({
                        'type': 'reliability',
                        'message': 'Consider setting replicas >= 1 for high availability'
                    })
        
        return {
            'valid': result.valid,
            'engine': result.engine,
            'error': result.error,
            'suggestion': result.suggestion,
            'fallback_action': result.fallback_action,
            'warnings': result.warnings,
            'suggestions': suggestions if suggestions else None
        }


def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate configuration
    
    Args:
        config: Configuration dictionary
    
    Returns:
        ValidationResult
    """
    validator = ConfigValidator()
    return validator.validate(config)


def main():
    """Test configuration validator"""
    print("TenderIntel Configuration Validator Test")
    print("=" * 50)
    
    from .defaults import get_default_config
    
    validator = ConfigValidator()
    
    # Test 1: Valid SQLite configuration
    print("\n1. Testing valid SQLite configuration...")
    sqlite_config = get_default_config()
    result = validator.validate(sqlite_config)
    print(f"   Valid: {result.valid}")
    print(f"   Engine: {result.engine}")
    
    # Test 2: Invalid engine type
    print("\n2. Testing invalid engine type...")
    invalid_config = get_default_config()
    invalid_config['search']['engine'] = 'invalid_engine'
    result = validator.validate(invalid_config)
    print(f"   Valid: {result.valid}")
    print(f"   Error: {result.error}")
    print(f"   Suggestion: {result.suggestion}")
    
    # Test 3: OpenSearch without installation
    print("\n3. Testing OpenSearch without installation...")
    opensearch_config = get_default_config()
    opensearch_config['search']['engine'] = 'opensearch'
    opensearch_config['search']['opensearch']['enabled'] = True
    result = validator.validate(opensearch_config)
    print(f"   Valid: {result.valid}")
    if not result.valid:
        print(f"   Error: {result.error}")
        print(f"   Fallback: {result.fallback_action}")
    
    # Test 4: Validation with suggestions
    print("\n4. Testing validation with suggestions...")
    validation_report = validator.validate_and_suggest(get_default_config())
    print(f"   Valid: {validation_report['valid']}")
    if validation_report.get('suggestions'):
        print(f"   Suggestions: {len(validation_report['suggestions'])}")
    
    print("\n✅ Configuration validator test completed!")


if __name__ == "__main__":
    main()
