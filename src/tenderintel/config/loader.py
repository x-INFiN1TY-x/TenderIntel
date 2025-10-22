#!/usr/bin/env python3
"""
Configuration Loader for TenderIntel
Loads configuration from multiple sources with intelligent fallback
"""

import yaml
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .defaults import get_default_config, get_minimal_config

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Load configuration from multiple sources with priority ordering
    
    Priority (highest to lowest):
    1. Command-line arguments (handled by CLI)
    2. Environment variables
    3. config.yaml in current directory
    4. config.yaml in user home directory (~/.tenderintel/)
    5. Hardcoded defaults (SQLite-only, always works)
    """
    
    DEFAULT_CONFIG_PATHS = [
        "config.yaml",
        "config/config.yaml",
        Path.home() / ".tenderintel" / "config.yaml",
        Path("/etc/tenderintel/config.yaml")
    ]
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration with intelligent fallback
        
        Args:
            config_path: Optional explicit path to config file
        
        Returns:
            Complete configuration dictionary
        """
        
        # Start with default config (SQLite-only, always works)
        config = get_default_config()
        
        # Try to load from file
        loaded_config = None
        source = "defaults"
        
        if config_path:
            # Explicit config path provided
            loaded_config = cls._load_from_file(config_path)
            if loaded_config:
                source = config_path
        else:
            # Try default locations
            for path in cls.DEFAULT_CONFIG_PATHS:
                config_file = Path(path)
                if config_file.exists():
                    loaded_config = cls._load_from_file(str(config_file))
                    if loaded_config:
                        source = str(config_file)
                        break
        
        # Merge loaded config with defaults
        if loaded_config:
            config = cls._merge_configs(config, loaded_config)
        
        # Override with environment variables
        config = cls._apply_environment_overrides(config)
        
        logger.info(f"Configuration loaded from: {source}")
        logger.info(f"Search engine: {config.get('search', {}).get('engine', 'sqlite')}")
        
        return config
    
    @staticmethod
    def _load_from_file(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration from YAML file
        
        Args:
            file_path: Path to configuration file
        
        Returns:
            Configuration dictionary or None if loading fails
        """
        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.debug(f"Loaded configuration from: {file_path}")
                return config if config else {}
        except FileNotFoundError:
            logger.debug(f"Config file not found: {file_path}")
            return None
        except yaml.YAMLError as e:
            logger.warning(f"Invalid YAML in {file_path}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Failed to load config from {file_path}: {e}")
            return None
    
    @staticmethod
    def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two configuration dictionaries
        
        Args:
            base: Base configuration (defaults)
            override: Override configuration (from file)
        
        Returns:
            Merged configuration dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursive merge for nested dicts
                result[key] = ConfigLoader._merge_configs(result[key], value)
            else:
                # Direct override
                result[key] = value
        
        return result
    
    @staticmethod
    def _apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration
        
        Supports environment variables like:
        - TENDERINTEL_SEARCH_ENGINE=opensearch
        - TENDERINTEL_OPENSEARCH_HOST=opensearch.example.com
        - TENDERINTEL_OPENSEARCH_PORT=9200
        
        Args:
            config: Base configuration
        
        Returns:
            Configuration with environment overrides applied
        """
        
        # Search engine override
        engine = os.getenv('TENDERINTEL_SEARCH_ENGINE')
        if engine:
            config['search']['engine'] = engine.lower()
            logger.info(f"Search engine overridden by environment: {engine}")
        
        # SQLite path override
        sqlite_path = os.getenv('TENDERINTEL_SQLITE_PATH')
        if sqlite_path:
            config['search']['sqlite']['database_path'] = sqlite_path
            logger.info(f"SQLite path overridden by environment: {sqlite_path}")
        
        # OpenSearch host override
        opensearch_host = os.getenv('TENDERINTEL_OPENSEARCH_HOST')
        opensearch_port = os.getenv('TENDERINTEL_OPENSEARCH_PORT', '9200')
        if opensearch_host:
            config['search']['opensearch']['hosts'] = [
                {'host': opensearch_host, 'port': int(opensearch_port)}
            ]
            logger.info(f"OpenSearch host overridden by environment: {opensearch_host}:{opensearch_port}")
        
        # OpenSearch enabled override
        opensearch_enabled = os.getenv('TENDERINTEL_OPENSEARCH_ENABLED')
        if opensearch_enabled:
            config['search']['opensearch']['enabled'] = opensearch_enabled.lower() in ('true', '1', 'yes')
        
        # API port override
        api_port = os.getenv('TENDERINTEL_API_PORT')
        if api_port:
            config['api']['port'] = int(api_port)
        
        # Log level override
        log_level = os.getenv('TENDERINTEL_LOG_LEVEL')
        if log_level:
            config['logging']['level'] = log_level.upper()
        
        return config
    
    @classmethod
    def save(cls, config: Dict[str, Any], file_path: str = "config.yaml") -> bool:
        """
        Save configuration to file
        
        Args:
            config: Configuration dictionary to save
            file_path: Path where to save configuration
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            config_file = Path(file_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as YAML
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Configuration saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {e}")
            return False
    
    @classmethod
    def create_default_config_file(cls, file_path: str = "config.yaml") -> bool:
        """
        Create default configuration file if it doesn't exist
        
        Args:
            file_path: Path where to create config file
        
        Returns:
            True if created, False if already exists or error
        """
        config_file = Path(file_path)
        
        if config_file.exists():
            logger.info(f"Configuration file already exists: {file_path}")
            return False
        
        # Create default config
        default_config = get_default_config()
        
        # Save to file
        return cls.save(default_config, file_path)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load configuration
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        Complete configuration dictionary
    """
    return ConfigLoader.load(config_path)


def get_search_engine_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extract search engine configuration from complete config
    
    Args:
        config: Complete configuration dictionary (or None for defaults)
    
    Returns:
        Search engine configuration
    """
    if config is None:
        config = get_default_config()
    
    return config.get('search', {})


def get_active_engine_type(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get the active search engine type from configuration
    
    Args:
        config: Complete configuration dictionary (or None for defaults)
    
    Returns:
        Engine type: 'sqlite' or 'opensearch'
    """
    search_config = get_search_engine_config(config)
    return search_config.get('engine', 'sqlite')


def is_opensearch_enabled(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if OpenSearch is enabled in configuration
    
    Args:
        config: Complete configuration dictionary (or None for defaults)
    
    Returns:
        True if OpenSearch is enabled, False otherwise
    """
    search_config = get_search_engine_config(config)
    
    # Check both engine type and explicit enabled flag
    engine_is_opensearch = search_config.get('engine') == 'opensearch'
    opensearch_enabled = search_config.get('opensearch', {}).get('enabled', False)
    
    return engine_is_opensearch and opensearch_enabled


def main():
    """Test configuration loading"""
    print("TenderIntel Configuration Loader Test")
    print("=" * 50)
    
    # Test default config loading
    print("\n1. Testing default configuration...")
    default_config = ConfigLoader.load()
    print(f"   Engine: {default_config['search']['engine']}")
    print(f"   SQLite DB: {default_config['search']['sqlite']['database_path']}")
    print(f"   OpenSearch enabled: {default_config['search']['opensearch']['enabled']}")
    
    # Test config file creation
    print("\n2. Testing config file creation...")
    test_path = "test_config.yaml"
    if ConfigLoader.create_default_config_file(test_path):
        print(f"   ✓ Created: {test_path}")
        
        # Test loading from file
        file_config = ConfigLoader.load(test_path)
        print(f"   ✓ Loaded from file")
        print(f"   Engine: {file_config['search']['engine']}")
        
        # Cleanup
        Path(test_path).unlink()
        print(f"   ✓ Cleaned up test file")
    
    # Test environment overrides
    print("\n3. Testing environment variable overrides...")
    os.environ['TENDERINTEL_SEARCH_ENGINE'] = 'opensearch'
    env_config = ConfigLoader.load()
    print(f"   Engine with env override: {env_config['search']['engine']}")
    del os.environ['TENDERINTEL_SEARCH_ENGINE']
    
    # Test helper functions
    print("\n4. Testing helper functions...")
    print(f"   Active engine type: {get_active_engine_type()}")
    print(f"   Is OpenSearch enabled: {is_opensearch_enabled()}")
    
    print("\n✅ Configuration loader test completed successfully!")


if __name__ == "__main__":
    main()
