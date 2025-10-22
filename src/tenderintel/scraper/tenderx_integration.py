"""
TenderX Integration Adapter
==========================

Bridges TenderX scraping capabilities with Smart Tender Search intelligence.
Transforms TenderX raw data into our enhanced schema with competitive intelligence.

Integration Architecture:
- TenderX: Raw CPPP scraping + document downloads + S3 storage
- Our PoC: 215+ keyword intelligence + BM25 search + competitive analysis
- This Adapter: Data transformation + categorization + firm detection
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add TenderX backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../tenderX/backend"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../tenderX/backend/scraper"))

# Import our enhanced search capabilities
from ..search.synonym_manager import SynonymManager

class TenderXAdapter:
    """
    Adapts TenderX scraped data to our enhanced schema with competitive intelligence
    """
    
    def __init__(self, db_path: str = "data/tenders.db"):
        self.db_path = db_path
        self.synonym_manager = SynonymManager()
        
        # Enhanced competitive firm database based on our service umbrellas
        self.competitor_firms = {
            "cloud_ai_ml": [
                "Cyfuture Cloud", "Softlabs Group", "fxis.ai", "DataToBiz", 
                "Talentica Software", "Quytech", "Rapyder", "Amazon AWS", 
                "Microsoft Azure", "AWS", "Azure"
            ],
            "compute_hardware": [
                "Intel India", "Acer", "Dell", "Arrow Electronics", "Tonbo Imaging"
            ],
            "application_integration": [
                "Cognizant", "Infosys", "Wipro", "HCL Technologies", 
                "Tata Consultancy Services", "TCS", "Capgemini", "NTT DATA", "Deloitte"
            ],
            "security_compliance": [
                "Tech Mahindra", "Secure Network Solutions", "ControlCase", 
                "TUV India", "Sattrix", "IBM Security"
            ],
            "cloud_management": [
                "AWS", "Azure", "Tata Communications", "Datacipher", 
                "Aspire Systems", "Microland"
            ],
            "networking_connectivity": [
                "Cisco", "Tata Communications", "Reliance Jio", "Vodafone Idea", 
                "BSNL", "TCS", "Wipro", "IBM", "HCL", "L&T"
            ],
            "data_analytics": [
                "Wipro", "HCL Technologies", "Mu Sigma", "SG Analytics", 
                "Accenture", "TCS", "Infosys", "Fractal Analytics"
            ]
        }
        
        # Service categorization keywords
        self.service_categories = {
            "Cloud AI/ML": ["machine learning", "artificial intelligence", "ml platform", "ai platform", "deep learning", "neural network"],
            "Compute & Hardware": ["server", "hardware", "compute", "processor", "workstation", "blade server"],
            "Application & Integration": ["application development", "system integration", "software development", "api integration"],
            "Storage & Backup": ["storage", "backup", "data protection", "archive", "disaster recovery"],
            "Security & Compliance": ["security", "firewall", "cybersecurity", "compliance", "audit", "vulnerability"],
            "Cloud Management": ["cloud management", "devops", "orchestration", "automation", "monitoring"],
            "Networking & Connectivity": ["network", "connectivity", "router", "switch", "wifi", "broadband"],
            "Data & Analytics": ["data analytics", "business intelligence", "data warehouse", "big data", "analytics"],
            "Database Services": ["database", "mysql", "postgresql", "nosql", "database management"],
            "Identity & Access Management": ["identity", "access management", "authentication", "authorization", "iam"],
            "Business Systems & Software": ["erp", "crm", "business software", "enterprise software"],
            "Communication & Messaging": ["communication", "messaging", "email", "collaboration"],
            "Data Center & Infrastructure": ["data center", "infrastructure", "colocation", "hosting"],
            "IT Service Management": ["itsm", "service management", "helpdesk", "it support"],
            "IoT & Automation": ["iot", "automation", "smart devices", "sensors", "industrial automation"]
        }
        
    def extract_tender_metadata(self, browser, tender_url: str) -> Optional[Dict[str, Any]]:
        """
        Enhanced metadata extraction from TenderX scraped tender pages
        Combines TenderX's scraping with our intelligent categorization
        """
        try:
            # Basic TenderX extraction (simplified for now)
            # This would normally use the TenderX scraper methods
            tender_data = {
                "tender_url": tender_url,
                "scraped_at": datetime.now().isoformat(),
                "source": "CPPP"
            }
            
            # Our enhanced processing
            if "tender_id" in tender_data:
                tender_data = self.enhance_tender_data(tender_data)
                
            return tender_data
            
        except Exception as e:
            print(f"Error extracting metadata from {tender_url}: {e}")
            return None
    
    def enhance_tender_data(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply our intelligent enhancements to TenderX raw data
        """
        enhanced = tender_data.copy()
        
        title = tender_data.get("title", "")
        organization = tender_data.get("organization", "")
        
        # Apply our service categorization
        enhanced["service_category"] = self.categorize_service(title)
        enhanced["sub_category"] = self.get_subcategory(title)
        
        # Extract our 215+ keywords
        enhanced["extracted_keywords"] = self.extract_relevant_keywords(title)
        
        # Detect competitor firms
        enhanced["detected_firms"] = self.detect_competitor_firms(title, organization)
        
        # Assess complexity
        enhanced["complexity_level"] = self.assess_complexity(title)
        
        # Geographic classification
        enhanced["region"] = self.extract_region(organization)
        
        # Technology stack detection
        enhanced["technology_stack"] = self.detect_technology_stack(title)
        
        return enhanced
    
    def categorize_service(self, title: str) -> str:
        """
        Intelligent service categorization using our keyword intelligence
        """
        title_lower = title.lower()
        
        for category, keywords in self.service_categories.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category
                    
        return "Other"
    
    def get_subcategory(self, title: str) -> str:
        """
        Extract detailed subcategory based on our 215+ keyword expansion
        """
        title_lower = title.lower()
        
        # Map to subcategories using keyword detection
        if any(kw in title_lower for kw in ["local area network", "lan", "ethernet", "switch"]):
            return "Networking Infrastructure"
        elif any(kw in title_lower for kw in ["api", "application programming interface", "rest"]):
            return "API & Integration"
        elif any(kw in title_lower for kw in ["security", "firewall", "cybersecurity"]):
            return "Security Solutions"
        elif any(kw in title_lower for kw in ["cloud", "aws", "azure"]):
            return "Cloud Services"
        
        return "General"
    
    def extract_relevant_keywords(self, title: str) -> List[str]:
        """
        Extract relevant keywords using our 215+ expansion dictionary
        """
        expanded_keywords = []
        
        # Use our synonym manager to find all relevant expansions
        words = title.lower().split()
        for word in words:
            expansion_result = self.synonym_manager.expand_keyword(word)
            expanded_keywords.extend(expansion_result.get('expanded_phrases', []))
        
        return list(set(expanded_keywords))
    
    def detect_competitor_firms(self, title: str, organization: str = "") -> List[str]:
        """
        Detect competitor firms mentioned in title or organization
        """
        detected_firms = []
        text_to_search = f"{title} {organization}".lower()
        
        for category, firms in self.competitor_firms.items():
            for firm in firms:
                if firm.lower() in text_to_search:
                    detected_firms.append(firm)
        
        return detected_firms
    
    def assess_complexity(self, title: str) -> str:
        """
        Assess tender complexity based on technical indicators
        """
        complexity_indicators = {
            "high": ["enterprise", "nationwide", "pan india", "multi-state", "complex", "advanced"],
            "medium": ["state-wide", "regional", "integration", "deployment", "implementation"],
            "low": ["maintenance", "support", "basic", "simple", "routine"]
        }
        
        title_lower = title.lower()
        
        for level, indicators in complexity_indicators.items():
            for indicator in indicators:
                if indicator in title_lower:
                    return level.capitalize()
                    
        return "Medium"  # Default
    
    def extract_region(self, organization: str) -> str:
        """
        Extract region/state information from organization name
        """
        # Basic region mapping
        region_keywords = {
            "Delhi": ["delhi", "new delhi", "nd"],
            "Maharashtra": ["maharashtra", "mumbai", "pune"],
            "Karnataka": ["karnataka", "bangalore", "bengaluru"],
            "Tamil Nadu": ["tamil nadu", "chennai"],
            "Uttar Pradesh": ["uttar pradesh", "lucknow", "noida"],
            "Gujarat": ["gujarat", "ahmedabad"],
            "West Bengal": ["west bengal", "kolkata"],
            "Rajasthan": ["rajasthan", "jaipur"],
            "National": ["india", "national", "central", "ministry"]
        }
        
        org_lower = organization.lower()
        
        for region, keywords in region_keywords.items():
            for keyword in keywords:
                if keyword in org_lower:
                    return region
                    
        return "Unknown"
    
    def detect_technology_stack(self, title: str) -> List[str]:
        """
        Detect technology stack mentioned in tender
        """
        tech_keywords = {
            "Cloud": ["aws", "azure", "google cloud", "cloud platform"],
            "Database": ["mysql", "postgresql", "oracle", "sql server", "mongodb"],
            "Programming": ["java", "python", ".net", "nodejs", "php"],
            "Infrastructure": ["kubernetes", "docker", "linux", "windows server"],
            "Security": ["ssl", "encryption", "firewall", "antivirus"],
            "Networking": ["cisco", "juniper", "router", "switch", "wifi"]
        }
        
        detected_tech = []
        title_lower = title.lower()
        
        for tech, keywords in tech_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    detected_tech.append(tech)
                    break
        
        return detected_tech
    
    def save_enhanced_tender(self, enhanced_data: Dict[str, Any]) -> bool:
        """
        Save enhanced tender data to our SQLite FTS5 database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # FTS5 insert query matching actual schema
            insert_query = """
            INSERT INTO tenders (
                tender_id, title, org, status, aoc_date, url,
                service_category, value_range, region, 
                department_type, complexity, keywords
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Prepare values matching FTS5 schema
            values = (
                enhanced_data.get("tender_id", f"CPPP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                enhanced_data.get("title", "Unknown Title"),
                enhanced_data.get("organization", "Unknown Organization"),  # maps to 'org'
                enhanced_data.get("status", "Published AOC"),
                enhanced_data.get("published_date", datetime.now().date().isoformat()),  # maps to 'aoc_date'
                enhanced_data.get("tender_url", ""),  # maps to 'url'
                enhanced_data.get("service_category", "Other"),
                "5_to_25_lakh",  # Default value range
                enhanced_data.get("region", "delhi").lower(),
                "central",  # Default department type
                enhanced_data.get("complexity_level", "medium").lower(),  # maps to 'complexity'
                ",".join(enhanced_data.get("extracted_keywords", []))  # keywords
            )
            
            cursor.execute(insert_query, values)
            conn.commit()
            conn.close()
            
            print(f"✅ Saved tender {enhanced_data.get('tender_id')} to FTS5 database")
            return True
            
        except Exception as e:
            print(f"❌ Error saving enhanced tender: {e}")
            return False

class TenderXIntegratedScraper:
    """
    Integrated scraper combining TenderX capabilities with our intelligence
    """
    
    def __init__(self):
        self.adapter = TenderXAdapter()
        
    def scrape_and_enhance_tenders(self, max_pages: int = 1) -> List[Dict[str, Any]]:
        """
        Main integration method: scrape via TenderX + enhance with our intelligence
        """
        # Import TenderX components
        try:
            from .tender_scraper import initialize_browser, open_website, search_open_tenders
            from .downloader import process_tenders
        except ImportError as e:
            print(f"Error importing TenderX modules: {e}")
            return []
        
        enhanced_tenders = []
        
        try:
            # Initialize TenderX browser
            browser = initialize_browser()
            
            # Navigate to CPPP
            open_website(browser)
            
            # Perform search (with CAPTCHA handling)
            search_open_tenders(browser)
            
            # Extract tender links (simplified for integration testing)
            tender_links = self._extract_sample_tender_links()
            
            print(f"Found {len(tender_links)} tender links for processing")
            
            # Process each tender with our enhancements
            for i, link in enumerate(tender_links):
                print(f"Processing tender {i+1}/{len(tender_links)}: {link}")
                
                # Extract metadata (this would use TenderX's existing logic)
                tender_data = self._extract_tender_metadata_from_link(browser, link)
                
                if tender_data:
                    # Apply our intelligent enhancements
                    enhanced_tender = self.adapter.enhance_tender_data(tender_data)
                    
                    # Save to our database
                    if self.adapter.save_enhanced_tender(enhanced_tender):
                        enhanced_tenders.append(enhanced_tender)
                        print(f"✅ Enhanced and saved tender: {enhanced_tender.get('tender_id')}")
                    else:
                        print(f"❌ Failed to save tender: {enhanced_tender.get('tender_id')}")
            
            browser.quit()
            
        except Exception as e:
            print(f"Error in integrated scraping: {e}")
        
        return enhanced_tenders
    
    def _extract_sample_tender_links(self) -> List[str]:
        """
        Extract sample tender links for testing
        Based on TenderX's extract_all_tender_links logic
        """
        # For now, return sample links for testing
        # In production, this would use TenderX's pagination logic
        return [
            "https://etenders.gov.in/eprocure/app?component=%24DirectLink_0&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=SJF6CyWn8RggyMYtNn0%2BHhw%3D%3D",
            "https://etenders.gov.in/eprocure/app?component=%24DirectLink_0&page=FrontEndAdvancedSearchResult&service=direct&session=T&sp=SBxt1NZPECd9xxZB8ZLBoZw%3D%3D"
        ]
    
    def _extract_tender_metadata_from_link(self, browser, tender_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract tender metadata from individual tender page
        This integrates with TenderX's existing extraction logic
        """
        try:
            # Navigate to tender page in new tab
            browser.execute_script("window.open(arguments[0]);", tender_url)
            browser.switch_to.window(browser.window_handles[-1])
            
            # Extract basic metadata (simplified for integration)
            tender_data = {
                "tender_id": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "title": "Sample Network Infrastructure Tender",  # Would extract from page
                "organization": "Sample Government Department",     # Would extract from page
                "department": "IT Department",                      # Would extract from page
                "published_date": datetime.now().date().isoformat(),
                "closing_date": "2025-11-30",
                "status": "Open",
                "tender_url": tender_url,
                "source": "CPPP"
            }
            
            # Close tab and return to main window
            browser.close()
            if len(browser.window_handles) > 0:
                browser.switch_to.window(browser.window_handles[0])
            
            return tender_data
            
        except Exception as e:
            print(f"Error extracting metadata from {tender_url}: {e}")
            # Close tab on error
            try:
                browser.close()
                if len(browser.window_handles) > 0:
                    browser.switch_to.window(browser.window_handles[0])
            except:
                pass
            return None

    def _create_sample_real_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Create realistic sample data that looks like real CPPP tenders
        Used for testing the integration pipeline without actual scraping
        """
        sample_tenders = [
            {
                "tender_id": f"CPPP_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i:03d}",
                "title": title,
                "organization": org,
                "department": dept,
                "tender_value": value,
                "published_date": "2025-10-20",
                "closing_date": "2025-11-30",
                "status": "Open",
                "source": "CPPP",
                "tender_url": f"https://etenders.gov.in/sample/test_{i}",
                "scraped_at": datetime.now().isoformat()
            }
            for i, (title, org, dept, value) in enumerate([
                (
                    "Supply and Installation of Local Area Network Infrastructure with Ethernet Switches",
                    "Ministry of Electronics and Information Technology",
                    "IT Infrastructure Division",
                    7500000.00
                ),
                (
                    "Development of REST API Gateway for Government Services Integration",
                    "National Informatics Centre",
                    "Software Development Division", 
                    3200000.00
                ),
                (
                    "Implementation of Web Application Firewall and Security Solutions",
                    "Department of Telecommunications",
                    "Cybersecurity Division",
                    4800000.00
                ),
                (
                    "Procurement of Identity and Access Management System",
                    "Controller of Certifying Authorities",
                    "Security Division",
                    6100000.00
                ),
                (
                    "Setup of Security Information and Event Management Platform",
                    "Indian Computer Emergency Response Team",
                    "Incident Response Division",
                    8900000.00
                )
            ], 1)
        ]
        
        # Apply our intelligent enhancements to each sample
        enhanced_samples = []
        for tender in sample_tenders[:count]:
            enhanced = self.adapter.enhance_tender_data(tender)
            enhanced_samples.append(enhanced)
            
        return enhanced_samples

def test_integration():
    """
    Test the TenderX integration with our intelligent search
    """
    print("🚀 Testing TenderX Integration with Smart Tender Search")
    print("=" * 60)
    
    # Initialize integrated scraper
    scraper = TenderXIntegratedScraper()
    
    # Test scraping and enhancement
    enhanced_tenders = scraper.scrape_and_enhance_tenders(max_pages=1)
    
    print(f"\n📊 Integration Results:")
    print(f"   Enhanced tenders: {len(enhanced_tenders)}")
    
    for tender in enhanced_tenders:
        print(f"\n🎯 Tender: {tender.get('tender_id')}")
        print(f"   Service Category: {tender.get('service_category')}")
        print(f"   Keywords: {tender.get('extracted_keywords', [])}")
        print(f"   Detected Firms: {tender.get('detected_firms', [])}")
        print(f"   Complexity: {tender.get('complexity_level')}")

if __name__ == "__main__":
    test_integration()
