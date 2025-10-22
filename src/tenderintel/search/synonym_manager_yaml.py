#!/usr/bin/env python3
"""
Enhanced Synonym Manager with YAML Configuration Support
Tier 1 & 2 Implementation: External configuration + Government procurement terms
Version: 2.0
"""

from typing import Dict, List, Optional, Set, Any
from pathlib import Path
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SynonymManagerV2:
    """Enhanced synonym manager with YAML configuration and weighted expansions"""
    
    def __init__(self, synonyms_file: Optional[str] = None):
        """
        Initialize synonym manager with YAML configuration
        
        Args:
            synonyms_file: Path to synonyms YAML file (default: config/synonyms.yaml)
        """
        self.synonyms_file = synonyms_file or "config/synonyms.yaml"
        self.last_reload_time = None
        
        # Load configuration
        self._load_from_yaml()
        
        logger.info(f"SynonymManagerV2 initialized: {self.total_keywords} keywords across {len(self.domains)} domains")
    
    def _load_from_yaml(self):
        """Load synonym dictionary from YAML configuration"""
        
        try:
            yaml_path = Path(self.synonyms_file)
            
            if not yaml_path.exists():
                logger.warning(f"Synonyms file not found: {yaml_path}, using fallback")
                self._load_fallback_synonyms()
                return
            
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Process YAML structure into internal format
            self.synonyms = {}
            self.weights = {}
            self.anti_patterns = {}
            self.domain_mapping = {}
            
            # Extract domains from YAML
            self.domains = config.get('domains', [])
            
            # Process each domain
            for domain in self.domains:
                if domain in config:
                    self.domain_mapping[domain] = set()
                    
                    for keyword, data in config[domain].items():
                        # Store expansions
                        if isinstance(data, dict):
                            expansions = data.get('expansions', [])
                            weight = data.get('weight', 1.0)
                            anti_pats = data.get('anti_patterns', [])
                        else:
                            expansions = data if isinstance(data, list) else []
                            weight = 1.0
                            anti_pats = []
                        
                        # Normalize keyword
                        norm_keyword = keyword.lower().replace('_', ' ')
                        
                        self.synonyms[norm_keyword] = expansions
                        self.weights[norm_keyword] = weight
                        if anti_pats:
                            self.anti_patterns[norm_keyword] = anti_pats
                        
                        # Add to domain mapping
                        self.domain_mapping[domain].add(norm_keyword)
            
            # Store configuration metadata
            self.config = config.get('config', {})
            self.total_keywords = len(self.synonyms)
            self.last_reload_time = datetime.now()
            
            logger.info(f"✅ Loaded {self.total_keywords} keywords from {yaml_path}")
            logger.info(f"✅ Domains: {', '.join(self.domains)}")
            
        except Exception as e:
            logger.error(f"Failed to load YAML configuration: {e}")
            self._load_fallback_synonyms()
    
    def _load_fallback_synonyms(self):
        """Load minimal fallback synonyms if YAML loading fails"""
        
        logger.warning("Using minimal fallback synonym dictionary")
        
        self.synonyms = {
            "api": ["application programming interface", "rest api", "api gateway"],
            "lan": ["local area network", "layer 2 switch", "vlan", "ethernet"],
            "cloud": ["cloud services", "cloud computing", "cloud platform"],
            "security": ["cyber security", "information security", "security solution"]
        }
        
        self.weights = {k: 1.0 for k in self.synonyms.keys()}
        self.anti_patterns = {
            "lan": ["land development", "landscape"],
            "api": ["application form"]
        }
        
        self.domain_mapping = {
            "networking": {"lan"},
            "cloud": {"api", "cloud"},
            "security": {"security"}
        }
        
        self.domains = list(self.domain_mapping.keys())
        self.total_keywords = len(self.synonyms)
        self.config = {"version": "2.0-fallback"}
        self.last_reload_time = datetime.now()
    
    def expand_keyword(self, keyword: str, max_expansions: int = 5) -> Dict[str, Any]:
        """
        Expand a keyword into relevant technical phrases with enhanced metadata
        
        Args:
            keyword: Input keyword to expand
            max_expansions: Maximum number of expansion phrases to return
            
        Returns:
            Dictionary with expansion results, confidence, weights, and metadata
        """
        normalized_keyword = keyword.lower().strip()
        
        # Get base expansions
        base_expansions = self.synonyms.get(normalized_keyword, [normalized_keyword])
        
        # Limit expansions for performance
        limited_expansions = base_expansions[:max_expansions]
        
        # Get expansion weight
        weight = self.weights.get(normalized_keyword, 0.5)
        
        # Determine domain context
        domain = self._detect_domain(normalized_keyword)
        
        # Calculate confidence based on expansion quality and weight
        confidence = self._calculate_expansion_confidence(normalized_keyword, limited_expansions, weight)
        
        return {
            "original_keyword": keyword,
            "normalized_keyword": normalized_keyword,
            "expanded_phrases": limited_expansions,
            "domain": domain,
            "confidence": confidence,
            "weight": weight,
            "anti_patterns": self.anti_patterns.get(normalized_keyword, []),
            "expansion_count": len(limited_expansions),
            "source": "yaml_config" if normalized_keyword in self.synonyms else "fallback"
        }
    
    def _detect_domain(self, keyword: str) -> Optional[str]:
        """Detect the most likely domain for a keyword"""
        
        for domain, keywords in self.domain_mapping.items():
            if keyword in keywords:
                return domain
        
        return "general"
    
    def _calculate_expansion_confidence(self, keyword: str, expansions: List[str], weight: float) -> float:
        """Calculate confidence score incorporating expansion quality and relevance weight"""
        
        base_confidence = 0.3  # Unknown keywords
        
        if keyword in self.synonyms:
            if len(expansions) >= 4:
                base_confidence = 0.95
            elif len(expansions) >= 3:
                base_confidence = 0.90
            elif len(expansions) >= 2:
                base_confidence = 0.75
            else:
                base_confidence = 0.5
        
        # Adjust confidence by relevance weight
        weighted_confidence = base_confidence * weight
        
        return round(weighted_confidence, 3)
    
    def reload_synonyms(self) -> Dict[str, Any]:
        """
        Hot-reload synonyms from YAML file without server restart
        
        Returns:
            Reload status and statistics
        """
        old_count = self.total_keywords
        old_domains = len(self.domains)
        
        try:
            self._load_from_yaml()
            
            return {
                "success": True,
                "previous_keywords": old_count,
                "current_keywords": self.total_keywords,
                "keywords_added": self.total_keywords - old_count,
                "previous_domains": old_domains,
                "current_domains": len(self.domains),
                "reload_time": self.last_reload_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Synonym reload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "keywords_count": self.total_keywords
            }
    
    def get_all_keywords(self) -> List[str]:
        """Get all available keywords sorted alphabetically"""
        return sorted(list(self.synonyms.keys()))
    
    def get_domain_keywords(self, domain: str) -> List[str]:
        """Get all keywords for a specific domain"""
        
        if domain not in self.domain_mapping:
            return []
        
        return sorted(list(self.domain_mapping[domain]))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the synonym dictionary"""
        
        total_expansions = sum(len(expansions) for expansions in self.synonyms.values())
        avg_expansions = total_expansions / self.total_keywords if self.total_keywords > 0 else 0
        
        domain_stats = {}
        for domain, keywords in self.domain_mapping.items():
            domain_stats[domain] = len(keywords)
        
        # Calculate weight distribution
        weight_values = list(self.weights.values())
        avg_weight = sum(weight_values) / len(weight_values) if weight_values else 0
        
        return {
            "total_keywords": self.total_keywords,
            "total_expansions": total_expansions,
            "average_expansions_per_keyword": round(avg_expansions, 2),
            "domain_distribution": domain_stats,
            "domains_supported": len(self.domain_mapping),
            "anti_patterns_configured": len(self.anti_patterns),
            "average_relevance_weight": round(avg_weight, 3),
            "configuration_source": self.synonyms_file,
            "last_reload": self.last_reload_time.isoformat() if self.last_reload_time else None,
            "config_version": self.config.get('version', 'unknown')
        }
    
    def search_keywords(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for keywords matching a query string
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching keywords with their expansions
        """
        query_lower = query.lower()
        matches = []
        
        for keyword, expansions in self.synonyms.items():
            if query_lower in keyword or any(query_lower in exp.lower() for exp in expansions):
                matches.append({
                    "keyword": keyword,
                    "expansions": expansions,
                    "domain": self._detect_domain(keyword),
                    "weight": self.weights.get(keyword, 1.0),
                    "has_anti_patterns": keyword in self.anti_patterns
                })
        
        return matches[:limit]
    
    def validate_synonym_quality(self) -> Dict[str, Any]:
        """
        Validate synonym dictionary quality and identify issues
        
        Returns:
            Quality assessment report
        """
        issues = []
        warnings = []
        
        # Check for keywords with no expansions
        no_expansions = [k for k, v in self.synonyms.items() if not v or len(v) == 0]
        if no_expansions:
            issues.append(f"{len(no_expansions)} keywords have no expansions")
        
        # Check for keywords with single expansion only
        single_expansion = [k for k, v in self.synonyms.items() if len(v) == 1]
        if single_expansion:
            warnings.append(f"{len(single_expansion)} keywords have only 1 expansion (recommend 2+)")
        
        # Check for duplicate expansions across keywords
        all_expansions = {}
        for keyword, expansions in self.synonyms.items():
            for exp in expansions:
                if exp in all_expansions:
                    warnings.append(f"Duplicate expansion '{exp}' in {keyword} and {all_expansions[exp]}")
                all_expansions[exp] = keyword
        
        # Check domain coverage
        uncategorized = len([k for k in self.synonyms.keys() 
                            if self._detect_domain(k) == "general"])
        if uncategorized > 0:
            warnings.append(f"{uncategorized} keywords not assigned to any domain")
        
        quality_score = 100
        quality_score -= len(issues) * 10
        quality_score -= len(warnings) * 2
        quality_score = max(0, min(100, quality_score))
        
        return {
            "quality_score": quality_score,
            "quality_rating": "excellent" if quality_score >= 90 else "good" if quality_score >= 70 else "needs_improvement",
            "issues": issues,
            "warnings": warnings,
            "total_keywords": self.total_keywords,
            "well_defined_keywords": self.total_keywords - len(no_expansions) - len(single_expansion),
            "validation_timestamp": datetime.now().isoformat()
        }


def main():
    """Test the enhanced YAML-based synonym manager"""
    print("TenderIntel Enhanced Synonym Manager V2.0")
    print("=" * 55)
    
    # Initialize YAML-based synonym manager
    try:
        synonym_manager = SynonymManagerV2()
        
        # Get statistics
        print("\n📊 Synonym Dictionary Statistics:")
        print("-" * 40)
        stats = synonym_manager.get_statistics()
        for key, value in stats.items():
            if key not in ['domain_distribution']:
                print(f"  {key}: {value}")
        
        print("\n🌍 Domain Distribution:")
        for domain, count in stats['domain_distribution'].items():
            print(f"  {domain}: {count} keywords")
        
        # Test expansions for key demo scenarios
        print("\n🔬 Testing Keyword Expansions:")
        print("-" * 40)
        test_keywords = ["lan", "api", "rfp", "gem", "genai", "aoc"]
        
        for keyword in test_keywords:
            result = synonym_manager.expand_keyword(keyword)
            print(f"\n'{keyword}' →")
            print(f"  Expansions: {result['expanded_phrases']}")
            print(f"  Domain: {result['domain']}")
            print(f"  Confidence: {result['confidence']} (weight: {result['weight']})")
            print(f"  Source: {result['source']}")
            if result['anti_patterns']:
                print(f"  Anti-patterns: {result['anti_patterns']}")
        
        # Test search functionality
        print("\n🔍 Testing Keyword Search:")
        print("-" * 40)
        search_results = synonym_manager.search_keywords("government", limit=5)
        print(f"Found {len(search_results)} keywords matching 'government':")
        for match in search_results:
            print(f"  - {match['keyword']} ({match['domain']}): {len(match['expansions'])} expansions")
        
        # Validate quality
        print("\n✅ Validating Synonym Quality:")
        print("-" * 40)
        quality = synonym_manager.validate_synonym_quality()
        print(f"  Quality Score: {quality['quality_score']}/100 ({quality['quality_rating']})")
        print(f"  Well-defined Keywords: {quality['well_defined_keywords']}/{quality['total_keywords']}")
        
        if quality['issues']:
            print(f"  ⚠️  Issues: {len(quality['issues'])}")
            for issue in quality['issues']:
                print(f"     - {issue}")
        
        if quality['warnings']:
            print(f"  ⚠️  Warnings: {len(quality['warnings'])}")
            for warning in quality['warnings'][:3]:  # Show first 3
                print(f"     - {warning}")
        
        # Test hot-reload
        print("\n🔄 Testing Hot-Reload Capability:")
        print("-" * 40)
        reload_result = synonym_manager.reload_synonyms()
        print(f"  Reload Success: {reload_result['success']}")
        print(f"  Current Keywords: {reload_result['current_keywords']}")
        
        print("\n✅ Enhanced Synonym Manager V2.0 test completed successfully!")
        print(f"📈 Improvement: {stats['total_keywords']} keywords (was 215)")
        print(f"🌍 Domains: {len(stats['domain_distribution'])} (was 7)")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Synonym manager test failed: {e}")
        raise


if __name__ == "__main__":
    main()
