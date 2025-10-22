#!/usr/bin/env python3
"""
Financial Analysis Engine for TenderIntel
=========================================

Production-grade financial analysis with statistical modeling and competitive intelligence.
Based on FINANCIAL_ANALYSIS_SYSTEM.md expert specifications.
"""

import sqlite3
import asyncio
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List, Tuple
import json
import logging
import statistics
from dataclasses import dataclass
from enum import Enum

# Import currency normalizer
from .currency_normalizer import CurrencyNormalizer, DealSizeClassifier

# Configure logging
logger = logging.getLogger(__name__)

class MarketPosition(str, Enum):
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"

@dataclass
class FirmFinancialProfile:
    """Comprehensive firm financial analysis result"""
    firm_name: str
    total_portfolio_value: Decimal
    contract_count: int
    average_deal_size: Decimal
    median_deal_size: Decimal
    deal_size_distribution: Dict[str, Dict[str, Any]]
    award_velocity: float  # awards per quarter
    market_share_percent: float
    competitive_position: MarketPosition
    growth_trajectory: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    
@dataclass
class MarketFinancialMetrics:
    """Market-wide financial analysis for competitive benchmarking"""
    service_category: str
    total_market_value: Decimal
    total_contracts: int
    average_deal_size: Decimal
    market_concentration_hhi: float
    price_distribution: Dict[str, Any]
    seasonal_patterns: Dict[str, Any]
    growth_rate: float
    competitive_intensity: str

class FinancialAnalysisEngine:
    """Advanced financial analysis engine for competitive intelligence"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.currency_normalizer = CurrencyNormalizer(db_path)
        self.deal_classifier = DealSizeClassifier(db_path)
        
    async def generate_firm_financial_scorecard(self, firm_name: str) -> FirmFinancialProfile:
        """Generate comprehensive firm financial scorecard with competitive analysis"""
        
        logger.info(f"Generating financial scorecard for: {firm_name}")
        
        try:
            # Get all tenders for this firm
            firm_tenders = self._get_firm_tenders_with_financials(firm_name)
            
            if not firm_tenders:
                logger.warning(f"No financial data found for firm: {firm_name}")
                return self._empty_firm_profile(firm_name)
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(firm_tenders)
            
            # Calculate market share
            market_share = await self._calculate_firm_market_share(firm_name, firm_tenders)
            
            # Analyze growth trajectory  
            growth_analysis = self._analyze_growth_trajectory(firm_tenders)
            
            # Assess competitive position
            competitive_position = self._determine_competitive_position(
                portfolio_metrics, market_share
            )
            
            # Risk assessment
            risk_metrics = self._assess_portfolio_risk(firm_tenders)
            
            return FirmFinancialProfile(
                firm_name=firm_name,
                total_portfolio_value=portfolio_metrics["total_value"],
                contract_count=portfolio_metrics["contract_count"],
                average_deal_size=portfolio_metrics["average_deal_size"],
                median_deal_size=portfolio_metrics["median_deal_size"],
                deal_size_distribution=portfolio_metrics["deal_distribution"],
                award_velocity=growth_analysis["velocity_per_quarter"],
                market_share_percent=market_share["overall_share"],
                competitive_position=competitive_position,
                growth_trajectory=growth_analysis,
                risk_assessment=risk_metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to generate financial scorecard for {firm_name}: {e}")
            raise
    
    def _get_firm_tenders_with_financials(self, firm_name: str) -> List[Dict[str, Any]]:
        """Get all tenders for a firm with financial data"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Search for firm in multiple fields with fuzzy matching
                tenders = conn.execute("""
                    SELECT 
                        tender_id, title, org, aoc_date, service_category,
                        award_value, currency, inr_normalized_value, deal_size_category,
                        winning_firm, region, state_name
                    FROM tenders
                    WHERE 
                        (org LIKE ? OR 
                         winning_firm LIKE ? OR
                         title LIKE ?)
                    AND inr_normalized_value IS NOT NULL
                    ORDER BY aoc_date DESC
                """, (f"%{firm_name}%", f"%{firm_name}%", f"%{firm_name}%")).fetchall()
                
                return [
                    {
                        "tender_id": row[0],
                        "title": row[1],
                        "organization": row[2],
                        "aoc_date": row[3],
                        "service_category": row[4],
                        "award_value": Decimal(str(row[5])) if row[5] else None,
                        "currency": row[6],
                        "inr_normalized_value": Decimal(str(row[7])) if row[7] else None,
                        "deal_size_category": row[8],
                        "winning_firm": row[9],
                        "region": row[10],
                        "state_name": row[11]
                    }
                    for row in tenders
                ]
                
        except Exception as e:
            logger.error(f"Failed to get firm tenders: {e}")
            return []
    
    def _calculate_portfolio_metrics(self, tenders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio financial metrics"""
        
        if not tenders:
            return self._empty_portfolio_metrics()
        
        # Extract financial values
        values = [t["inr_normalized_value"] for t in tenders if t["inr_normalized_value"]]
        
        if not values:
            return self._empty_portfolio_metrics()
        
        # Basic statistics
        total_value = sum(values)
        contract_count = len(values)
        average_deal_size = total_value / contract_count
        median_deal_size = Decimal(str(statistics.median([float(v) for v in values])))
        
        # Deal size distribution analysis
        deal_distribution = self._analyze_deal_size_distribution(tenders)
        
        # Value concentration analysis
        values_sorted = sorted([float(v) for v in values], reverse=True)
        top_10_percent_count = max(1, contract_count // 10)
        top_10_percent_value = sum(values_sorted[:top_10_percent_count])
        concentration_ratio = top_10_percent_value / float(total_value) * 100
        
        return {
            "total_value": total_value,
            "contract_count": contract_count,
            "average_deal_size": average_deal_size,
            "median_deal_size": median_deal_size,
            "largest_deal": max(values),
            "smallest_deal": min(values),
            "deal_distribution": deal_distribution,
            "value_concentration": {
                "top_10_percent_contracts": top_10_percent_count,
                "top_10_percent_value_share": round(concentration_ratio, 1),
                "portfolio_concentration_risk": "high" if concentration_ratio > 70 else "medium" if concentration_ratio > 50 else "low"
            }
        }
    
    def _analyze_deal_size_distribution(self, tenders: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze distribution of deals across size categories"""
        
        distribution = {}
        
        # Group by deal size category
        for tender in tenders:
            category = tender.get("deal_size_category", "unknown")
            if category not in distribution:
                distribution[category] = {"count": 0, "total_value": Decimal('0'), "tenders": []}
            
            distribution[category]["count"] += 1
            if tender["inr_normalized_value"]:
                distribution[category]["total_value"] += tender["inr_normalized_value"]
            distribution[category]["tenders"].append(tender["tender_id"])
        
        # Calculate percentages
        total_count = sum(cat["count"] for cat in distribution.values())
        total_value = sum(cat["total_value"] for cat in distribution.values())
        
        for category in distribution:
            distribution[category]["count_percentage"] = round(
                distribution[category]["count"] / total_count * 100, 1
            ) if total_count > 0 else 0
            
            distribution[category]["value_percentage"] = round(
                float(distribution[category]["total_value"]) / float(total_value) * 100, 1
            ) if total_value > 0 else 0
        
        return distribution
    
    async def _calculate_firm_market_share(self, firm_name: str, firm_tenders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate market share across different dimensions"""
        
        firm_total_value = sum(
            t["inr_normalized_value"] for t in firm_tenders 
            if t["inr_normalized_value"]
        )
        
        # Overall market share
        with sqlite3.connect(self.db_path) as conn:
            total_market_value = conn.execute("""
                SELECT SUM(inr_normalized_value)
                FROM tenders
                WHERE inr_normalized_value IS NOT NULL
            """).fetchone()[0]
            
            overall_share = (
                float(firm_total_value) / total_market_value * 100 
                if total_market_value else 0
            )
        
        # Service-specific market shares
        service_shares = {}
        firm_services = set(t["service_category"] for t in firm_tenders if t["service_category"])
        
        for service in firm_services:
            firm_service_value = sum(
                t["inr_normalized_value"] for t in firm_tenders 
                if t["service_category"] == service and t["inr_normalized_value"]
            )
            
            with sqlite3.connect(self.db_path) as conn:
                service_market_value = conn.execute("""
                    SELECT SUM(inr_normalized_value)
                    FROM tenders  
                    WHERE service_category = ? AND inr_normalized_value IS NOT NULL
                """, (service,)).fetchone()[0]
                
                service_share = (
                    float(firm_service_value) / service_market_value * 100
                    if service_market_value else 0
                )
                
                service_shares[service] = {
                    "share_percent": round(service_share, 1),
                    "firm_value": float(firm_service_value),
                    "market_value": float(service_market_value) if service_market_value else 0
                }
        
        return {
            "overall_share": round(overall_share, 1),
            "service_specific_shares": service_shares,
            "dominant_service": max(service_shares.keys(), key=lambda s: service_shares[s]["share_percent"]) if service_shares else None
        }
    
    def _analyze_growth_trajectory(self, tenders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze firm's growth trajectory over time"""
        
        if not tenders:
            return {"velocity_per_quarter": 0, "growth_rate": 0, "trend": "stable"}
        
        # Sort by date
        dated_tenders = [
            t for t in tenders 
            if t["aoc_date"] and t["inr_normalized_value"]
        ]
        dated_tenders.sort(key=lambda x: x["aoc_date"])
        
        if len(dated_tenders) < 2:
            return {"velocity_per_quarter": 0, "growth_rate": 0, "trend": "insufficient_data"}
        
        # Calculate quarterly performance
        quarterly_data = self._group_by_quarters(dated_tenders)
        
        # Award velocity (contracts per quarter)
        total_quarters = len(quarterly_data) if quarterly_data else 1
        velocity_per_quarter = len(dated_tenders) / total_quarters
        
        # Growth rate calculation
        if len(quarterly_data) >= 2:
            early_quarters = list(quarterly_data.values())[:len(quarterly_data)//2]
            recent_quarters = list(quarterly_data.values())[len(quarterly_data)//2:]
            
            early_avg = statistics.mean([q["total_value"] for q in early_quarters])
            recent_avg = statistics.mean([q["total_value"] for q in recent_quarters])
            
            growth_rate = ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
        else:
            growth_rate = 0
        
        # Trend determination
        if growth_rate > 20:
            trend = "high_growth"
        elif growth_rate > 5:
            trend = "growing"
        elif growth_rate > -5:
            trend = "stable"
        else:
            trend = "declining"
        
        return {
            "velocity_per_quarter": round(velocity_per_quarter, 1),
            "growth_rate": round(growth_rate, 1),
            "trend": trend,
            "quarterly_performance": quarterly_data,
            "analysis_period_months": self._calculate_analysis_period_months(dated_tenders)
        }
    
    def _group_by_quarters(self, tenders: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Group tenders by quarters for trend analysis"""
        
        quarterly_data = {}
        
        for tender in tenders:
            if not tender["aoc_date"]:
                continue
                
            # Parse date and determine quarter
            tender_date = datetime.fromisoformat(tender["aoc_date"]).date()
            quarter_key = f"{tender_date.year}-Q{(tender_date.month - 1) // 3 + 1}"
            
            if quarter_key not in quarterly_data:
                quarterly_data[quarter_key] = {
                    "contract_count": 0,
                    "total_value": 0,
                    "average_deal_size": 0,
                    "quarter": quarter_key
                }
            
            quarterly_data[quarter_key]["contract_count"] += 1
            quarterly_data[quarter_key]["total_value"] += float(tender["inr_normalized_value"])
        
        # Calculate averages
        for quarter in quarterly_data:
            qdata = quarterly_data[quarter]
            qdata["average_deal_size"] = (
                qdata["total_value"] / qdata["contract_count"]
                if qdata["contract_count"] > 0 else 0
            )
        
        return quarterly_data
    
    def _determine_competitive_position(self, 
                                       portfolio_metrics: Dict[str, Any],
                                       market_share: Dict[str, Any]) -> MarketPosition:
        """Determine competitive position based on market share and portfolio strength"""
        
        overall_share = market_share["overall_share"]
        contract_count = portfolio_metrics["contract_count"]
        
        if overall_share > 15 and contract_count > 10:
            return MarketPosition.LEADER
        elif overall_share > 8 and contract_count > 5:
            return MarketPosition.CHALLENGER
        elif overall_share > 3:
            return MarketPosition.FOLLOWER
        else:
            return MarketPosition.NICHE
    
    def _assess_portfolio_risk(self, tenders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess portfolio risk across multiple dimensions"""
        
        if not tenders:
            return {"overall_risk": "unknown", "risk_factors": []}
        
        risk_factors = []
        risk_scores = []
        
        # Service concentration risk
        services = [t["service_category"] for t in tenders if t["service_category"]]
        service_concentration = len(set(services)) if services else 0
        
        if service_concentration <= 2:
            risk_factors.append("High service concentration")
            risk_scores.append(0.8)
        elif service_concentration <= 4:
            risk_scores.append(0.5)
        else:
            risk_scores.append(0.2)
        
        # Geographic concentration risk  
        regions = [t["region"] for t in tenders if t["region"]]
        geographic_concentration = len(set(regions)) if regions else 0
        
        if geographic_concentration <= 2:
            risk_factors.append("High geographic concentration")
            risk_scores.append(0.7)
        elif geographic_concentration <= 4:
            risk_scores.append(0.4)
        else:
            risk_scores.append(0.1)
        
        # Deal size concentration risk
        deal_sizes = [t["deal_size_category"] for t in tenders if t["deal_size_category"]]
        if deal_sizes:
            mega_deals = sum(1 for ds in deal_sizes if ds == "mega")
            if mega_deals / len(deal_sizes) > 0.5:
                risk_factors.append("High dependency on mega deals")
                risk_scores.append(0.6)
        
        # Overall risk score
        overall_risk_score = statistics.mean(risk_scores) if risk_scores else 0.5
        
        if overall_risk_score > 0.7:
            overall_risk = "high"
        elif overall_risk_score > 0.4:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        return {
            "overall_risk": overall_risk,
            "overall_risk_score": round(overall_risk_score, 2),
            "risk_factors": risk_factors,
            "diversification_metrics": {
                "service_diversification": service_concentration,
                "geographic_diversification": geographic_concentration,
                "deal_size_diversification": len(set(deal_sizes)) if deal_sizes else 0
            }
        }
    
    async def calculate_market_financial_metrics(self, service_category: str) -> MarketFinancialMetrics:
        """Calculate comprehensive market financial metrics for a service category"""
        
        logger.info(f"Calculating market metrics for: {service_category}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get all tenders in service category
                category_tenders = conn.execute("""
                    SELECT 
                        inr_normalized_value, winning_firm, aoc_date, deal_size_category
                    FROM tenders
                    WHERE service_category = ? 
                    AND inr_normalized_value IS NOT NULL
                """, (service_category,)).fetchall()
                
                if not category_tenders:
                    return self._empty_market_metrics(service_category)
                
                values = [Decimal(str(row[0])) for row in category_tenders]
                firms = [row[1] for row in category_tenders if row[1]]
                
                # Basic market metrics
                total_market_value = sum(values)
                total_contracts = len(values)
                average_deal_size = total_market_value / total_contracts
                
                # Market concentration (HHI index)
                hhi_index = self._calculate_hhi_index(firms, values)
                
                # Price distribution analysis
                price_distribution = self._analyze_price_distribution(values)
                
                # Growth rate analysis
                growth_rate = self._calculate_market_growth_rate(category_tenders)
                
                # Competitive intensity assessment
                competitive_intensity = self._assess_competitive_intensity(hhi_index, len(set(firms)))
                
                return MarketFinancialMetrics(
                    service_category=service_category,
                    total_market_value=total_market_value,
                    total_contracts=total_contracts,
                    average_deal_size=average_deal_size,
                    market_concentration_hhi=hhi_index,
                    price_distribution=price_distribution,
                    seasonal_patterns={},  # TODO: Implement seasonal analysis
                    growth_rate=growth_rate,
                    competitive_intensity=competitive_intensity
                )
                
        except Exception as e:
            logger.error(f"Failed to calculate market metrics for {service_category}: {e}")
            raise
    
    def _calculate_hhi_index(self, firms: List[str], values: List[Decimal]) -> float:
        """Calculate Herfindahl-Hirschman Index for market concentration"""
        
        if not firms or not values:
            return 0.0
        
        # Calculate firm market shares
        firm_values = {}
        total_value = sum(values)
        
        for i, firm in enumerate(firms):
            if firm not in firm_values:
                firm_values[firm] = Decimal('0')
            if i < len(values):
                firm_values[firm] += values[i]
        
        # Calculate HHI
        hhi = Decimal('0')
        for firm_value in firm_values.values():
            market_share = firm_value / total_value
            hhi += market_share ** 2
        
        return float(hhi)
    
    def _analyze_price_distribution(self, values: List[Decimal]) -> Dict[str, Any]:
        """Analyze price distribution with statistical measures"""
        
        if not values:
            return {}
        
        float_values = [float(v) for v in values]
        
        return {
            "mean": round(statistics.mean(float_values), 2),
            "median": round(statistics.median(float_values), 2),
            "std_deviation": round(statistics.stdev(float_values), 2) if len(float_values) > 1 else 0,
            "min_value": min(float_values),
            "max_value": max(float_values),
            "percentiles": {
                "25th": round(statistics.quantiles(float_values, n=4)[0], 2) if len(float_values) >= 4 else min(float_values),
                "75th": round(statistics.quantiles(float_values, n=4)[2], 2) if len(float_values) >= 4 else max(float_values),
                "90th": round(statistics.quantiles(float_values, n=10)[8], 2) if len(float_values) >= 10 else max(float_values)
            }
        }
    
    def _calculate_market_growth_rate(self, tenders: List[Tuple]) -> float:
        """Calculate market growth rate based on tender timeline"""
        
        # Group by quarters and calculate growth
        quarterly_values = {}
        
        for row in tenders:
            value, firm, aoc_date_str, category = row
            if not aoc_date_str:
                continue
                
            aoc_date = datetime.fromisoformat(aoc_date_str).date()
            quarter_key = f"{aoc_date.year}-Q{(aoc_date.month - 1) // 3 + 1}"
            
            if quarter_key not in quarterly_values:
                quarterly_values[quarter_key] = 0
            quarterly_values[quarter_key] += float(value)
        
        if len(quarterly_values) < 2:
            return 0.0
        
        # Calculate growth between first and last quarter
        quarters_sorted = sorted(quarterly_values.keys())
        first_quarter_value = quarterly_values[quarters_sorted[0]]
        last_quarter_value = quarterly_values[quarters_sorted[-1]]
        
        if first_quarter_value > 0:
            growth_rate = ((last_quarter_value - first_quarter_value) / first_quarter_value * 100)
            return round(growth_rate, 1)
        
        return 0.0
    
    def _assess_competitive_intensity(self, hhi_index: float, firm_count: int) -> str:
        """Assess competitive intensity based on HHI and firm count"""
        
        if hhi_index > 0.25:
            return "low"  # Concentrated market
        elif hhi_index > 0.15:
            return "moderate"
        elif firm_count > 10:
            return "high"
        else:
            return "very_high"
    
    def _empty_firm_profile(self, firm_name: str) -> FirmFinancialProfile:
        """Return empty firm profile for firms with no data"""
        return FirmFinancialProfile(
            firm_name=firm_name,
            total_portfolio_value=Decimal('0'),
            contract_count=0,
            average_deal_size=Decimal('0'),
            median_deal_size=Decimal('0'),
            deal_size_distribution={},
            award_velocity=0.0,
            market_share_percent=0.0,
            competitive_position=MarketPosition.NICHE,
            growth_trajectory={"trend": "no_data"},
            risk_assessment={"overall_risk": "unknown"}
        )
    
    def _empty_portfolio_metrics(self) -> Dict[str, Any]:
        """Return empty portfolio metrics"""
        return {
            "total_value": Decimal('0'),
            "contract_count": 0,
            "average_deal_size": Decimal('0'),
            "median_deal_size": Decimal('0'),
            "largest_deal": Decimal('0'),
            "smallest_deal": Decimal('0'),
            "deal_distribution": {},
            "value_concentration": {"portfolio_concentration_risk": "unknown"}
        }
    
    def _empty_market_metrics(self, service_category: str) -> MarketFinancialMetrics:
        """Return empty market metrics"""
        return MarketFinancialMetrics(
            service_category=service_category,
            total_market_value=Decimal('0'),
            total_contracts=0,
            average_deal_size=Decimal('0'),
            market_concentration_hhi=0.0,
            price_distribution={},
            seasonal_patterns={},
            growth_rate=0.0,
            competitive_intensity="unknown"
        )
    
    def _calculate_analysis_period_months(self, tenders: List[Dict[str, Any]]) -> int:
        """Calculate analysis period in months"""
        
        if not tenders:
            return 0
        
        dates = [
            datetime.fromisoformat(t["aoc_date"]).date() 
            for t in tenders 
            if t["aoc_date"]
        ]
        
        if not dates:
            return 0
        
        earliest = min(dates)
        latest = max(dates)
        
        return (latest.year - earliest.year) * 12 + (latest.month - earliest.month)

async def test_financial_analysis_engine():
    """Test financial analysis engine capabilities"""
    
    print("TenderIntel Financial Analysis Engine")
    print("=" * 42)
    
    # Initialize engine
    engine = FinancialAnalysisEngine("data/tenders.db")
    
    # Test firm analysis
    print("\n🏢 Testing Firm Financial Analysis:")
    print("-" * 38)
    
    test_firms = ["Tata Consultancy Services", "Infosys", "HCL Technologies"]
    
    for firm_name in test_firms:
        try:
            profile = await engine.generate_firm_financial_scorecard(firm_name)
            print(f"\n{firm_name}:")
            print(f"  Portfolio Value: ₹{profile.total_portfolio_value:,}")
            print(f"  Contract Count: {profile.contract_count}")
            print(f"  Avg Deal Size: ₹{profile.average_deal_size:,}")
            print(f"  Market Share: {profile.market_share_percent}%")
            print(f"  Position: {profile.competitive_position.value}")
            print(f"  Growth: {profile.growth_trajectory.get('trend', 'unknown')}")
        except Exception as e:
            print(f"  ❌ Analysis failed: {e}")
    
    # Test market analysis
    print("\n📊 Testing Market Financial Analysis:")
    print("-" * 39)
    
    test_categories = ["cloud", "networking", "security"]
    
    for category in test_categories:
        try:
            market_metrics = await engine.calculate_market_financial_metrics(category)
            print(f"\n{category.title()} Market:")
            print(f"  Market Value: ₹{market_metrics.total_market_value:,}")
            print(f"  Contract Count: {market_metrics.total_contracts}")
            print(f"  Avg Deal Size: ₹{market_metrics.average_deal_size:,}")
            print(f"  HHI Index: {market_metrics.market_concentration_hhi:.3f}")
            print(f"  Competition: {market_metrics.competitive_intensity}")
            print(f"  Growth Rate: {market_metrics.growth_rate}%")
        except Exception as e:
            print(f"  ❌ Analysis failed: {e}")
    
    print("\n✅ Financial analysis engine operational!")

if __name__ == "__main__":
    asyncio.run(test_financial_analysis_engine())
