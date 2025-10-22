#!/usr/bin/env python3
"""
Comprehensive Synonym Manager for Smart Tender Search PoC
Contains all 179+ technical keywords with expansion mappings
Based on extensive keyword research from government procurement analysis
"""

from typing import Dict, List, Optional, Set, Any
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SynonymManager:
    """Manages comprehensive synonym dictionary with domain-aware expansions"""
    
    def __init__(self):
        self.synonyms = self._initialize_comprehensive_synonyms()
        self.domain_mapping = self._create_domain_mapping()
        self.anti_patterns = self._initialize_anti_patterns()
    
    def _initialize_comprehensive_synonyms(self) -> Dict[str, List[str]]:
        """Initialize complete synonym dictionary with all 179+ keywords from our research"""
        
        return {
            # Cloud AI/ML Platform Services
            "ai": ["artificial intelligence", "machine learning platform", "ai platform"],
            "ml": ["machine learning", "model training platform", "mlops platform"],
            "nlp": ["natural language processing", "text analytics", "language processing"],
            "cv": ["computer vision", "image recognition", "visual analytics"],
            "genai": ["generative ai model hosting", "llm hosting", "ai model hosting"],
            
            # API & Integration Services
            "api": ["application programming interface", "rest api", "api gateway", "openapi"],
            "rest": ["representational state transfer", "rest api", "restful services"],
            "soap": ["simple object access protocol", "web services", "soap api"],
            "graphql": ["graph query language", "api query language"],
            "webhook": ["web hooks", "callback api", "event notifications"],
            
            # Compute & Hardware
            "cpu": ["central processing unit", "processor", "compute instance"],
            "gpu": ["graphics processing unit", "accelerated computing", "parallel processing"],
            "hdd": ["hard disk drive", "spinning disk", "magnetic storage"],
            "ssd": ["solid state drive", "flash storage", "nvme storage"],
            "ram": ["random access memory", "system memory", "main memory"],
            "hpc": ["high performance computing", "supercomputing", "parallel computing"],
            "vm": ["virtual machine", "compute instance", "virtual server"],
            "bare": ["bare metal server", "dedicated server", "physical server"],
            
            # Storage & Backup Solutions
            "storage": ["data storage", "storage solution", "storage array"],
            "backup": ["backup solution", "data backup", "backup and recovery"],
            "archive": ["data archival", "long term storage", "cold storage"],
            "san": ["storage area network", "block storage", "shared storage"],
            "nas": ["network attached storage", "file storage", "network storage"],
            "s3": ["object storage", "blob storage", "cloud storage"],
            "snapshot": ["data snapshot", "backup snapshot", "point in time backup"],
            
            # Networking & Connectivity Infrastructure
            "lan": ["local area network", "layer 2 switch", "layer 3 switch", "vlan", "ethernet"],
            "wan": ["wide area network", "wan connectivity", "internet connectivity"],
            "vpn": ["virtual private network", "site to site vpn", "vpn gateway", "ipsec"],
            "dns": ["domain name system", "name resolution", "dns server"],
            "dhcp": ["dynamic host configuration protocol", "ip assignment", "network configuration"],
            "vlan": ["virtual local area network", "network segmentation", "lan virtualization"],
            "mpls": ["multiprotocol label switching", "mpls network", "carrier ethernet"],
            "sdwan": ["software defined wan", "sd wan solution", "network virtualization"],
            "sdn": ["software defined networking", "network virtualization", "programmable network"],
            "noc": ["network operations center", "network management", "network monitoring"],
            "nms": ["network management system", "network monitoring", "snmp management"],
            
            # Load Balancing & Traffic Management
            "load": ["load balancer", "application load balancer", "traffic distribution"],
            "cdn": ["content delivery network", "edge caching", "content distribution"],
            "proxy": ["reverse proxy", "forward proxy", "proxy server"],
            "cache": ["caching solution", "data cache", "application cache"],
            "traffic": ["traffic routing", "traffic management", "load distribution"],
            
            # Security & Compliance Solutions
            "iam": ["identity and access management", "user management", "access control"],
            "pam": ["privileged access management", "privileged identity management"],
            "mfa": ["multi factor authentication", "two factor authentication", "strong authentication"],
            "sso": ["single sign on", "federated authentication", "identity federation"],
            "saml": ["security assertion markup language", "xml based sso", "federated identity"],
            "oauth": ["open authorization", "api authorization", "token based auth"],
            "ldap": ["lightweight directory access protocol", "directory service", "user directory"],
            "ad": ["active directory", "microsoft directory", "windows authentication"],
            
            # Security Monitoring & Analytics
            "siem": ["security information event management", "security analytics", "log correlation"],
            "soar": ["security orchestration automation response", "security automation"],
            "soc": ["security operations center", "security operations", "cyber defense"],
            "ueba": ["user entity behavior analytics", "behavioral analytics", "anomaly detection"],
            "dlp": ["data loss prevention", "data leakage prevention", "information protection"],
            "casb": ["cloud access security broker", "cloud security", "saas security"],
            
            # Network Security
            "firewall": ["network firewall", "packet filtering", "network security"],
            "ngfw": ["next generation firewall", "application firewall", "deep packet inspection"],
            "waf": ["web application firewall", "application layer firewall", "web protection"],
            "ips": ["intrusion prevention system", "network intrusion prevention"],
            "ids": ["intrusion detection system", "network intrusion detection"],
            "utm": ["unified threat management", "integrated security", "security appliance"],
            
            # Endpoint Security
            "antivirus": ["endpoint protection", "malware protection", "virus protection"],
            "edr": ["endpoint detection and response", "endpoint security", "host protection"],
            "xdr": ["extended detection and response", "extended endpoint security"],
            "endpoint": ["endpoint protection platform", "endpoint security", "host security"],
            
            # Database Services
            "db": ["database", "database management", "data storage"],
            "sql": ["structured query language", "relational database", "sql database"],
            "nosql": ["nosql database", "document database", "non relational database"],
            "mysql": ["mysql database", "open source database", "relational database"],
            "postgresql": ["postgresql database", "postgres database", "object relational database"],
            "oracle": ["oracle database", "enterprise database", "commercial database"],
            "mongodb": ["mongodb", "document database", "json database"],
            "redis": ["redis database", "in memory database", "cache database"],
            "cassandra": ["apache cassandra", "wide column database", "distributed database"],
            
            # Data Analytics & Business Intelligence
            "etl": ["extract transform load", "data pipeline", "data integration"],
            "bi": ["business intelligence", "analytics platform", "reporting system"],
            "dwh": ["data warehouse", "analytical database", "data mart"],
            "olap": ["online analytical processing", "multidimensional analysis", "cube analysis"],
            "oltp": ["online transaction processing", "transactional database"],
            "big": ["big data", "large scale data", "data analytics"],
            "spark": ["apache spark", "distributed computing", "big data processing"],
            "hadoop": ["apache hadoop", "distributed storage", "big data framework"],
            
            # IT Service Management
            "itsm": ["it service management", "service management platform"],
            "itil": ["information technology infrastructure library", "service management framework"],
            "cmdb": ["configuration management database", "it asset management"],
            "ticketing": ["helpdesk system", "ticket management", "service desk"],
            "monitoring": ["infrastructure monitoring", "system monitoring", "application monitoring"],
            "logging": ["log management", "centralized logging", "log analytics"],
            "apm": ["application performance monitoring", "application monitoring"],
            
            # Disaster Recovery & Business Continuity
            "dr": ["disaster recovery", "business continuity", "backup recovery"],
            "backup": ["data backup", "backup solution", "data protection"],
            "replication": ["data replication", "database replication", "storage replication"],
            "ha": ["high availability", "fault tolerance", "redundancy"],
            "clustering": ["server clustering", "database clustering", "application clustering"],
            
            # Communication & Collaboration
            "voip": ["voice over internet protocol", "ip telephony", "voice communications"],
            "pbx": ["private branch exchange", "telephone system", "call management"],
            "sip": ["session initiation protocol", "sip trunking", "voip protocol"],
            "pri": ["primary rate interface", "isdn service", "digital telephony"],
            "sms": ["short message service", "text messaging", "mobile messaging"],
            "email": ["electronic mail", "email system", "messaging platform"],
            "collaboration": ["team collaboration", "unified communications", "workspace platform"],
            "video": ["video conferencing", "video communication", "remote meeting"],
            "webex": ["cisco webex", "web conferencing", "online meetings"],
            "teams": ["microsoft teams", "collaboration platform", "workspace"],
            "zoom": ["video conferencing", "online meetings", "web conferencing"],
            
            # Enterprise Applications
            "erp": ["enterprise resource planning", "business management system", "integrated business"],
            "crm": ["customer relationship management", "sales management", "customer management"],
            "hrms": ["human resource management system", "hr software", "personnel management"],
            "scm": ["supply chain management", "procurement system", "vendor management"],
            "cms": ["content management system", "web content management", "digital content"],
            "dms": ["document management system", "document storage", "file management"],
            "ecm": ["enterprise content management", "content repository", "document workflow"],
            "bpm": ["business process management", "workflow management", "process automation"],
            "workflow": ["business workflow", "process automation", "task management"],
            
            # Development & DevOps
            "devops": ["development operations", "continuous integration", "software delivery"],
            "cicd": ["continuous integration continuous delivery", "automated deployment"],
            "git": ["version control", "source control", "code repository"],
            "jenkins": ["build automation", "ci cd pipeline", "deployment automation"],
            "docker": ["containerization", "application containers", "container platform"],
            "kubernetes": ["container orchestration", "k8s platform", "container management"],
            "ansible": ["configuration management", "automation platform", "infrastructure as code"],
            "terraform": ["infrastructure as code", "cloud provisioning", "resource management"],
            
            # Mobile & Telecom Services
            "4g": ["fourth generation", "lte network", "mobile broadband"],
            "5g": ["fifth generation", "next generation mobile", "ultra fast mobile"],
            "lte": ["long term evolution", "4g technology", "mobile broadband"],
            "gsm": ["global system for mobile", "cellular network", "mobile communication"],
            "cdma": ["code division multiple access", "cellular technology", "wireless communication"],
            "sim": ["subscriber identity module", "sim card", "mobile identity"],
            "esim": ["embedded sim", "virtual sim", "programmable sim"],
            "m2m": ["machine to machine", "iot connectivity", "device communication"],
            "iot": ["internet of things", "connected devices", "smart devices"],
            "broadband": ["high speed internet", "internet connectivity", "wide bandwidth"],
            "wifi": ["wireless fidelity", "wireless network", "wifi connectivity"],
            "bluetooth": ["short range wireless", "device pairing", "wireless communication"],
            
            # Data Center & Infrastructure
            "dc": ["data center", "data centre", "server facility"],
            "colocation": ["data center colocation", "hosted infrastructure", "colo services"],
            "hosting": ["web hosting", "server hosting", "cloud hosting"],
            "virtualization": ["server virtualization", "infrastructure virtualization"],
            "hypervisor": ["virtual machine monitor", "virtualization platform"],
            "ups": ["uninterruptible power supply", "backup power", "power protection"],
            "hvac": ["heating ventilation air conditioning", "cooling system", "climate control"],
            "rack": ["server rack", "equipment rack", "data center rack"],
            "blade": ["blade server", "modular server", "high density server"],
            
            # Specialized Technologies
            "blockchain": ["distributed ledger", "cryptocurrency platform", "decentralized database"],
            "ar": ["augmented reality", "mixed reality", "immersive technology"],
            "vr": ["virtual reality", "immersive simulation", "3d environment"],
            "gis": ["geographic information system", "spatial analysis", "mapping system"],
            "cad": ["computer aided design", "design software", "engineering software"],
            "plm": ["product lifecycle management", "design management", "engineering data"],
            
            # Compliance & Governance
            "gdpr": ["general data protection regulation", "data privacy", "privacy compliance"],
            "hipaa": ["health insurance portability", "healthcare privacy", "medical data protection"],
            "sox": ["sarbanes oxley", "financial compliance", "audit compliance"],
            "pci": ["payment card industry", "payment security", "card data protection"],
            "iso": ["international organization standardization", "quality management", "compliance framework"],
            
            # Testing & Quality Assurance
            "qa": ["quality assurance", "software testing", "quality control"],
            "testing": ["software testing", "test automation", "quality validation"],
            "selenium": ["web testing", "browser automation", "ui testing"],
            "junit": ["unit testing", "java testing", "automated testing"],
            "performance": ["performance testing", "load testing", "stress testing"],
            "security": ["security testing", "penetration testing", "vulnerability assessment"],
            
            # Additional Technical Acronyms (completing the 179+ from our discussions)
            "sdk": ["software development kit", "development framework", "programming interface"],
            "api": ["application programming interface", "programming interface", "software interface"],
            "ui": ["user interface", "graphical interface", "user experience"],
            "ux": ["user experience", "interface design", "usability"],
            "cdn": ["content delivery network", "edge delivery", "content distribution"],
            "ssl": ["secure sockets layer", "transport security", "encryption protocol"],
            "tls": ["transport layer security", "secure communication", "encryption protocol"],
            "tcp": ["transmission control protocol", "reliable transport", "network protocol"],
            "udp": ["user datagram protocol", "connectionless protocol", "fast transport"],
            "http": ["hypertext transfer protocol", "web protocol", "internet protocol"],
            "https": ["secure hypertext transfer protocol", "secure web protocol"],
            "ftp": ["file transfer protocol", "file sharing", "data transfer"],
            "sftp": ["secure file transfer protocol", "encrypted file transfer"],
            "smtp": ["simple mail transfer protocol", "email protocol", "mail server"],
            "pop3": ["post office protocol", "email retrieval", "mail download"],
            "imap": ["internet message access protocol", "email synchronization"],
            
            # Additional Security Acronyms
            "aes": ["advanced encryption standard", "symmetric encryption", "data encryption"],
            "rsa": ["rivest shamir adleman", "asymmetric encryption", "public key crypto"],
            "pki": ["public key infrastructure", "certificate management", "crypto infrastructure"],
            "ca": ["certificate authority", "digital certificates", "trust authority"],
            "hsm": ["hardware security module", "cryptographic hardware", "secure crypto"],
            "kms": ["key management service", "encryption key management", "crypto key storage"],
            
            # Network Protocols & Services
            "bgp": ["border gateway protocol", "routing protocol", "internet routing"],
            "ospf": ["open shortest path first", "interior routing", "link state routing"],
            "rip": ["routing information protocol", "distance vector routing"],
            "snmp": ["simple network management protocol", "network monitoring", "device management"],
            "ntp": ["network time protocol", "time synchronization", "clock sync"],
            "dhcp": ["dynamic host configuration protocol", "automatic ip assignment"],
            "nat": ["network address translation", "ip address mapping", "address translation"],
            "vrf": ["virtual routing forwarding", "route isolation", "network virtualization"],
            
            # Additional Database & Analytics
            "acid": ["atomicity consistency isolation durability", "database properties"],
            "crud": ["create read update delete", "data operations", "database operations"],
            "orm": ["object relational mapping", "database abstraction", "data modeling"],
            "sql": ["structured query language", "database query", "relational database"],
            "ddl": ["data definition language", "schema definition", "database structure"],
            "dml": ["data manipulation language", "data modification", "database operations"],
            
            # Mobile & IoT Specific
            "ble": ["bluetooth low energy", "low power bluetooth", "energy efficient wireless"],
            "nfc": ["near field communication", "short range communication", "contactless communication"],
            "rfid": ["radio frequency identification", "wireless identification", "automatic identification"],
            "gps": ["global positioning system", "satellite navigation", "location services"],
            "lbs": ["location based services", "geo location", "position services"],
            
            # Additional Development Tools
            "ide": ["integrated development environment", "code editor", "development tools"],
            "sdk": ["software development kit", "development framework", "api library"],
            "framework": ["software framework", "development platform", "application framework"],
            "library": ["code library", "software component", "reusable code"],
            "package": ["software package", "code module", "software component"],
            "repository": ["code repository", "version control", "source control"],
            
            # Advanced Analytics & AI
            "etl": ["extract transform load", "data pipeline", "data processing"],
            "elt": ["extract load transform", "modern data pipeline", "cloud data processing"],
            "olap": ["online analytical processing", "multidimensional analysis", "business intelligence"],
            "oltp": ["online transaction processing", "transactional system", "real time processing"],
            "dwh": ["data warehouse", "analytical database", "business intelligence database"],
            "mart": ["data mart", "departmental database", "focused analytics"],
            "lake": ["data lake", "raw data storage", "unstructured data repository"],
            "mesh": ["data mesh", "decentralized data", "domain oriented data"],
            
            # Enterprise Integration
            "esb": ["enterprise service bus", "integration platform", "message routing"],
            "api": ["application programming interface", "service interface", "integration point"],
            "soa": ["service oriented architecture", "modular architecture", "service design"],
            "microservices": ["microservice architecture", "service decomposition", "distributed services"],
            "middleware": ["integration middleware", "message oriented middleware", "system integration"],
            
            # Quality & Testing
            "sla": ["service level agreement", "performance guarantee", "quality commitment"],
            "kpi": ["key performance indicator", "performance metric", "success measure"],
            "rpo": ["recovery point objective", "data loss tolerance", "backup frequency"],
            "rto": ["recovery time objective", "downtime tolerance", "restoration time"],
            "mttr": ["mean time to repair", "recovery time", "incident resolution"],
            "mtbf": ["mean time between failures", "reliability measure", "system uptime"]
        }
    
    def _create_domain_mapping(self) -> Dict[str, Set[str]]:
        """Create domain classification for keywords to improve expansion context"""
        
        return {
            "networking": {
                "lan", "wan", "vpn", "dns", "dhcp", "vlan", "mpls", "sdwan", "sdn", 
                "noc", "nms", "bgp", "ospf", "snmp", "nat", "vrf", "switch", "router"
            },
            "security": {
                "iam", "pam", "mfa", "sso", "saml", "oauth", "siem", "soar", "soc", 
                "ueba", "dlp", "casb", "firewall", "ngfw", "waf", "ips", "ids", "utm",
                "antivirus", "edr", "xdr", "endpoint", "pki", "ca", "hsm", "kms"
            },
            "cloud": {
                "api", "saas", "paas", "iaas", "vm", "container", "kubernetes", "docker",
                "serverless", "microservices", "cdn", "load", "auto", "scale"
            },
            "database": {
                "db", "sql", "nosql", "mysql", "postgresql", "oracle", "mongodb", 
                "redis", "cassandra", "etl", "bi", "dwh", "olap", "oltp", "lake"
            },
            "ai_ml": {
                "ai", "ml", "nlp", "cv", "genai", "neural", "deep", "learning",
                "model", "training", "inference", "algorithm"
            },
            "mobile_iot": {
                "4g", "5g", "lte", "gsm", "cdma", "sim", "esim", "m2m", "iot",
                "ble", "nfc", "rfid", "gps", "mobile", "wireless"
            },
            "enterprise": {
                "erp", "crm", "hrms", "scm", "cms", "dms", "ecm", "bpm", "workflow",
                "itsm", "itil", "cmdb", "ticketing"
            }
        }
    
    def _initialize_anti_patterns(self) -> Dict[str, List[str]]:
        """Initialize anti-patterns to avoid false positive expansions"""
        
        return {
            # Prevent "lan" from matching land-related terms
            "lan": ["land development", "land acquisition", "landscape", "landmark"],
            
            # Prevent "api" from matching non-technical applications
            "api": ["application form", "job application", "permit application"],
            
            # Prevent "soc" from matching social terms
            "soc": ["social welfare", "social security", "social media", "soccer"],
            
            # Prevent "ram" from matching non-technical terms
            "ram": ["random", "male sheep", "battering ram"],
            
            # Prevent "mobile" from matching non-technical mobility
            "mobile": ["mobile home", "mobile unit", "physical mobility"]
        }
    
    def expand_keyword(self, keyword: str, max_expansions: int = 5) -> Dict[str, Any]:
        """
        Expand a keyword into relevant technical phrases
        
        Args:
            keyword: Input keyword to expand
            max_expansions: Maximum number of expansion phrases to return
            
        Returns:
            Dictionary with expansion results and metadata
        """
        normalized_keyword = keyword.lower().strip()
        
        # Get base expansions
        base_expansions = self.synonyms.get(normalized_keyword, [normalized_keyword])
        
        # Limit expansions for performance
        limited_expansions = base_expansions[:max_expansions]
        
        # Determine domain context
        domain = self._detect_domain(normalized_keyword)
        
        # Calculate confidence based on expansion quality
        confidence = self._calculate_expansion_confidence(normalized_keyword, limited_expansions)
        
        return {
            "original_keyword": keyword,
            "normalized_keyword": normalized_keyword,
            "expanded_phrases": limited_expansions,
            "domain": domain,
            "confidence": confidence,
            "anti_patterns": self.anti_patterns.get(normalized_keyword, []),
            "expansion_count": len(limited_expansions)
        }
    
    def _detect_domain(self, keyword: str) -> Optional[str]:
        """Detect the most likely domain for a keyword"""
        
        for domain, keywords in self.domain_mapping.items():
            if keyword in keywords:
                return domain
        
        return "general"
    
    def _calculate_expansion_confidence(self, keyword: str, expansions: List[str]) -> float:
        """Calculate confidence score for expansion quality"""
        
        if keyword not in self.synonyms:
            return 0.3  # Low confidence for unknown keywords
        
        if len(expansions) >= 3:
            return 0.95  # High confidence for well-defined expansions
        elif len(expansions) >= 2:
            return 0.75  # Medium confidence
        else:
            return 0.5   # Low confidence for single expansion
    
    def get_all_keywords(self) -> List[str]:
        """Get all available keywords in the synonym dictionary"""
        return sorted(list(self.synonyms.keys()))
    
    def get_domain_keywords(self, domain: str) -> List[str]:
        """Get all keywords for a specific domain"""
        
        if domain not in self.domain_mapping:
            return []
        
        return sorted(list(self.domain_mapping[domain]))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the synonym dictionary"""
        
        total_keywords = len(self.synonyms)
        total_expansions = sum(len(expansions) for expansions in self.synonyms.values())
        avg_expansions = total_expansions / total_keywords if total_keywords > 0 else 0
        
        domain_stats = {}
        for domain, keywords in self.domain_mapping.items():
            domain_stats[domain] = len(keywords)
        
        return {
            "total_keywords": total_keywords,
            "total_expansions": total_expansions,
            "average_expansions_per_keyword": round(avg_expansions, 2),
            "domain_distribution": domain_stats,
            "domains_supported": len(self.domain_mapping),
            "anti_patterns_configured": len(self.anti_patterns)
        }

def main():
    """Test the synonym manager functionality"""
    print("Smart Tender Search PoC - Synonym Manager Test")
    print("=" * 55)
    
    # Initialize synonym manager
    synonym_manager = SynonymManager()
    
    # Get statistics
    stats = synonym_manager.get_statistics()
    print("\nSynonym Dictionary Statistics:")
    print("-" * 35)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Test expansions for key demo scenarios
    test_keywords = ["lan", "api", "waf", "iam", "siem"]
    
    print("\nTest Keyword Expansions:")
    print("-" * 28)
    
    for keyword in test_keywords:
        result = synonym_manager.expand_keyword(keyword)
        print(f"\n'{keyword}' → {result['expanded_phrases']}")
        print(f"   Domain: {result['domain']}")
        print(f"   Confidence: {result['confidence']}")
        if result['anti_patterns']:
            print(f"   Anti-patterns: {result['anti_patterns']}")
    
    print("\n✅ Synonym manager test completed successfully!")
    print(f"📊 Total keywords supported: {stats['total_keywords']}")
    print(f"🎯 Average expansions per keyword: {stats['average_expansions_per_keyword']}")

if __name__ == "__main__":
    main()
