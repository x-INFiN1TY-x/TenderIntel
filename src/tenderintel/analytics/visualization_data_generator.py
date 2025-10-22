#!/usr/bin/env python3
"""
Visualization Data Generator for TenderIntel
===========================================

Generates data optimized for D3.js heatmaps, Leaflet geographic maps, and Material-UI dashboards.
Based on EXECUTIVE_DASHBOARD_UI_COMPONENTS.md expert specifications.
"""

import sqlite3
import json
from typing import Dict, Any, List, Tuple, Optional
from decimal import Decimal
from datetime import datetime, date
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ServiceFirmHeatmapGenerator:
    """Generate Service×Firm performance matrix data for D3.js heatmaps"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def generate_heatmap_data(self, 
                            timeframe: str = "12months",
                            metric: str = "market_share") -> Dict[str, Any]:
        """Generate Service×Firm heatmap matrix data for D3.js visualization"""
        
        logger.info(f"Generating Service×Firm heatmap data (timeframe: {timeframe}, metric: {metric})")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get Service×Firm performance matrix
                matrix_data = conn.execute("""
                    SELECT 
                        service_category,
                        COALESCE(winning_firm, org) as firm,
                        COUNT(*) as contract_count,
                        SUM(COALESCE(inr_normalized_value, award_value, 25000000)) as total_value,
                        AVG(COALESCE(inr_normalized_value, award_value, 25000000)) as avg_deal_size
                    FROM tenders
                    WHERE service_category IS NOT NULL 
                    AND service_category != ''
                    AND (winning_firm IS NOT NULL OR org IS NOT NULL)
                    GROUP BY service_category, COALESCE(winning_firm, org)
                    HAVING contract_count > 0
                    ORDER BY total_value DESC
                """).fetchall()
                
                if not matrix_data:
                    return self._empty_heatmap_data()
                
                # Process data into heatmap format
                services = sorted(list(set(row[0] for row in matrix_data)))
                firms = sorted(list(set(row[1] for row in matrix_data)))
                
                # Create cell data for D3.js
                cell_data = []
                max_value = 0
                
                for service_category, firm, count, total_value, avg_deal in matrix_data:
                    # Calculate metric value based on selection
                    if metric == "market_share":
                        # Calculate market share within service category
                        service_total = sum(
                            row[3] for row in matrix_data 
                            if row[0] == service_category
                        )
                        metric_value = (total_value / service_total * 100) if service_total > 0 else 0
                    elif metric == "contract_count":
                        metric_value = count
                    elif metric == "total_value":
                        metric_value = float(total_value)
                    else:
                        metric_value = float(avg_deal)
                    
                    max_value = max(max_value, metric_value)
                    
                    cell_data.append({
                        "service": service_category,
                        "firm": firm,
                        "value": round(metric_value, 2),
                        "contract_count": count,
                        "total_value": float(total_value),
                        "avg_deal_size": float(avg_deal),
                        "display_value": self._format_display_value(metric_value, metric)
                    })
                
                # Calculate color scale domain
                color_scale_domain = [0, max_value * 0.33, max_value * 0.66, max_value]
                
                # Generate performance summary
                performance_summary = self._calculate_performance_summary(matrix_data, metric)
                
                return {
                    "heatmap_data": {
                        "services": services,
                        "firms": firms,
                        "cell_data": cell_data,
                        "max_value": max_value,
                        "metric_type": metric,
                        "color_scale_domain": color_scale_domain
                    },
                    "performance_summary": performance_summary,
                    "metadata": {
                        "timeframe": timeframe,
                        "total_cells": len(cell_data),
                        "unique_services": len(services),
                        "unique_firms": len(firms),
                        "generated_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Heatmap data generation failed: {e}")
            return {"error": str(e)}
    
    def _format_display_value(self, value: float, metric: str) -> str:
        """Format value for display in heatmap tooltips"""
        
        if metric == "market_share":
            return f"{value:.1f}%"
        elif metric == "contract_count":
            return f"{int(value)} contracts"
        elif metric == "total_value":
            return f"₹{value/10000000:.1f}Cr"
        else:
            return f"₹{value/10000000:.1f}Cr avg"
    
    def _calculate_performance_summary(self, matrix_data: List[Tuple], metric: str) -> Dict[str, Any]:
        """Calculate performance summary for heatmap insights"""
        
        # Top performing service categories
        service_performance = {}
        for row in matrix_data:
            service = row[0]
            total_value = float(row[3])
            
            if service not in service_performance:
                service_performance[service] = {"total_value": 0, "contract_count": 0}
            
            service_performance[service]["total_value"] += total_value
            service_performance[service]["contract_count"] += row[2]
        
        top_services = sorted(
            service_performance.items(),
            key=lambda x: x[1]["total_value"],
            reverse=True
        )[:5]
        
        # Top performing firms
        firm_performance = {}
        for row in matrix_data:
            firm = row[1]
            total_value = float(row[3])
            
            if firm not in firm_performance:
                firm_performance[firm] = {"total_value": 0, "contract_count": 0}
                
            firm_performance[firm]["total_value"] += total_value
            firm_performance[firm]["contract_count"] += row[2]
        
        top_firms = sorted(
            firm_performance.items(),
            key=lambda x: x[1]["total_value"],
            reverse=True
        )[:5]
        
        return {
            "top_services": [
                {
                    "service": service,
                    "total_value": perf["total_value"],
                    "contract_count": perf["contract_count"]
                }
                for service, perf in top_services
            ],
            "top_firms": [
                {
                    "firm": firm,
                    "total_value": perf["total_value"],
                    "contract_count": perf["contract_count"]
                }
                for firm, perf in top_firms
            ]
        }
    
    def _empty_heatmap_data(self) -> Dict[str, Any]:
        """Return empty heatmap data structure"""
        return {
            "heatmap_data": {
                "services": [],
                "firms": [],
                "cell_data": [],
                "max_value": 0,
                "metric_type": "market_share",
                "color_scale_domain": [0, 1]
            },
            "performance_summary": {"top_services": [], "top_firms": []},
            "metadata": {"message": "No data available for heatmap generation"}
        }

class GeographicIntelligenceGenerator:
    """Generate geographic intelligence data for Leaflet choropleth maps"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        # Indian states mapping for choropleth visualization
        self.indian_states = {
            "DL": {"name": "Delhi", "coordinates": [28.6139, 77.2090]},
            "MH": {"name": "Maharashtra", "coordinates": [19.7515, 75.7139]},
            "KA": {"name": "Karnataka", "coordinates": [15.3173, 75.7139]},
            "TN": {"name": "Tamil Nadu", "coordinates": [11.1271, 78.6569]},
            "WB": {"name": "West Bengal", "coordinates": [22.9868, 87.8550]},
            "TG": {"name": "Telangana", "coordinates": [18.1124, 79.0193]},
            "UP": {"name": "Uttar Pradesh", "coordinates": [26.8467, 80.9462]},
            "GJ": {"name": "Gujarat", "coordinates": [23.0225, 72.5714]},
            "RJ": {"name": "Rajasthan", "coordinates": [27.0238, 74.2179]},
            "HR": {"name": "Haryana", "coordinates": [29.0588, 76.0856]}
        }
    
    def generate_geographic_data(self) -> Dict[str, Any]:
        """Generate geographic intelligence data for Indian states choropleth"""
        
        logger.info("Generating geographic intelligence data for Indian states")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get state-wise procurement data
                state_data = conn.execute("""
                    SELECT 
                        COALESCE(state_code, 'UN') as state_code,
                        COALESCE(state_name, region, 'Unknown') as state_name,
                        COUNT(*) as tender_count,
                        SUM(COALESCE(inr_normalized_value, award_value, 25000000)) as total_value,
                        AVG(COALESCE(inr_normalized_value, award_value, 25000000)) as avg_value,
                        COUNT(DISTINCT service_category) as service_diversity,
                        COUNT(DISTINCT COALESCE(winning_firm, org)) as firm_diversity
                    FROM tenders
                    GROUP BY COALESCE(state_code, 'UN'), COALESCE(state_name, region, 'Unknown')
                    HAVING tender_count > 0
                    ORDER BY total_value DESC
                """).fetchall()
                
                if not state_data:
                    return self._empty_geographic_data()
                
                # Calculate procurement density (normalized 0-1)
                max_total_value = max(float(row[3]) for row in state_data)
                max_tender_count = max(row[2] for row in state_data)
                
                state_metrics = {}
                choropleth_data = []
                
                for row in state_data:
                    state_code, state_name, tender_count, total_value, avg_value, service_div, firm_div = row
                    
                    # Calculate normalized metrics
                    value_density = float(total_value) / max_total_value if max_total_value > 0 else 0
                    volume_density = tender_count / max_tender_count if max_tender_count > 0 else 0
                    procurement_density = (value_density + volume_density) / 2
                    
                    # Get additional state information
                    state_info = self.indian_states.get(state_code, {
                        "name": state_name,
                        "coordinates": [20.5937, 78.9629]  # Center of India default
                    })
                    
                    state_analysis = {
                        "state_code": state_code,
                        "state_name": state_name,
                        "coordinates": state_info["coordinates"],
                        "procurement_metrics": {
                            "total_tenders": tender_count,
                            "total_value_inr": float(total_value),
                            "average_deal_size_inr": float(avg_value),
                            "procurement_density": round(procurement_density, 3)
                        },
                        "diversity_metrics": {
                            "service_categories": service_div,
                            "active_firms": firm_div,
                            "diversification_score": round((service_div + firm_div) / 2, 1)
                        },
                        "competitive_intelligence": self._get_state_competitive_intelligence(state_code)
                    }
                    
                    state_metrics[state_code] = state_analysis
                    
                    # Choropleth data for map visualization  
                    choropleth_data.append({
                        "state_code": state_code,
                        "state_name": state_name,
                        "value": procurement_density,
                        "display_value": f"₹{total_value/10000000:.1f}Cr",
                        "tender_count": tender_count
                    })
                
                # Generate insights
                insights = self._generate_geographic_insights(state_metrics)
                
                return {
                    "geographic_intelligence": {
                        "state_metrics": state_metrics,
                        "choropleth_data": choropleth_data,
                        "procurement_hotspots": self._identify_procurement_hotspots(state_metrics),
                        "regional_analysis": self._analyze_regional_patterns(state_metrics)
                    },
                    "insights": insights,
                    "metadata": {
                        "total_states": len(state_metrics),
                        "total_procurement_value": sum(s["procurement_metrics"]["total_value_inr"] for s in state_metrics.values()),
                        "generated_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Geographic data generation failed: {e}")
            return {"error": str(e)}
    
    def _get_state_competitive_intelligence(self, state_code: str) -> Dict[str, Any]:
        """Get competitive intelligence for a specific state"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Top firms in this state
                top_firms = conn.execute("""
                    SELECT 
                        COALESCE(winning_firm, org) as firm,
                        COUNT(*) as contracts,
                        SUM(COALESCE(inr_normalized_value, award_value, 25000000)) as total_value
                    FROM tenders
                    WHERE COALESCE(state_code, 'UN') = ?
                    GROUP BY COALESCE(winning_firm, org)
                    ORDER BY total_value DESC
                    LIMIT 5
                """, (state_code,)).fetchall()
                
                # Top service categories
                top_services = conn.execute("""
                    SELECT 
                        service_category,
                        COUNT(*) as contracts,
                        SUM(COALESCE(inr_normalized_value, award_value, 25000000)) as total_value
                    FROM tenders
                    WHERE COALESCE(state_code, 'UN') = ?
                    AND service_category IS NOT NULL
                    GROUP BY service_category
                    ORDER BY total_value DESC
                    LIMIT 3
                """, (state_code,)).fetchall()
                
                return {
                    "leading_firms": [
                        {
                            "firm": row[0],
                            "contracts": row[1],
                            "total_value_inr": float(row[2])
                        }
                        for row in top_firms
                    ],
                    "dominant_services": [
                        {
                            "service": row[0],
                            "contracts": row[1], 
                            "total_value_inr": float(row[2])
                        }
                        for row in top_services
                    ]
                }
                
        except Exception as e:
            logger.debug(f"State competitive intelligence failed for {state_code}: {e}")
            return {"leading_firms": [], "dominant_services": []}
    
    def _identify_procurement_hotspots(self, state_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify top procurement hotspots for geographic visualization"""
        
        hotspots = []
        
        for state_code, metrics in state_metrics.items():
            procurement_score = (
                metrics["procurement_metrics"]["procurement_density"] * 0.5 +
                metrics["diversity_metrics"]["diversification_score"] / 10 * 0.3 +
                min(metrics["procurement_metrics"]["total_tenders"] / 20, 1.0) * 0.2
            )
            
            if procurement_score > 0.3:  # Significant procurement activity
                hotspots.append({
                    "state_code": state_code,
                    "state_name": metrics["state_name"],
                    "coordinates": metrics["coordinates"],
                    "procurement_score": round(procurement_score, 3),
                    "total_value": metrics["procurement_metrics"]["total_value_inr"],
                    "tender_count": metrics["procurement_metrics"]["total_tenders"]
                })
        
        return sorted(hotspots, key=lambda x: x["procurement_score"], reverse=True)
    
    def _analyze_regional_patterns(self, state_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze regional procurement patterns for insights"""
        
        # Group states by regions
        regional_groups = {
            "North": ["DL", "HR", "UP", "PB"],
            "West": ["MH", "GJ", "RJ", "MP"],
            "South": ["KA", "TN", "TG", "AP", "KL"],
            "East": ["WB", "JH", "OR", "BR"],
            "Northeast": ["AS", "MZ", "MN", "TR"]
        }
        
        regional_analysis = {}
        
        for region, state_codes in regional_groups.items():
            region_states = [
                metrics for code, metrics in state_metrics.items() 
                if code in state_codes
            ]
            
            if region_states:
                total_value = sum(s["procurement_metrics"]["total_value_inr"] for s in region_states)
                total_tenders = sum(s["procurement_metrics"]["total_tenders"] for s in region_states)
                
                regional_analysis[region] = {
                    "states_active": len(region_states),
                    "total_procurement_value": total_value,
                    "total_tenders": total_tenders,
                    "average_deal_size": total_value / total_tenders if total_tenders > 0 else 0,
                    "procurement_intensity": total_value / len(region_states) if region_states else 0
                }
        
        return regional_analysis
    
    def _generate_geographic_insights(self, state_metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from geographic analysis"""
        
        insights = []
        
        # Find highest value state
        highest_value_state = max(
            state_metrics.items(),
            key=lambda x: x[1]["procurement_metrics"]["total_value_inr"]
        )
        insights.append(
            f"{highest_value_state[1]['state_name']} leads with ₹{highest_value_state[1]['procurement_metrics']['total_value_inr']/10000000:.1f}Cr in procurement value"
        )
        
        # Find most diverse state
        most_diverse_state = max(
            state_metrics.items(),
            key=lambda x: x[1]["diversity_metrics"]["diversification_score"]
        )
        insights.append(
            f"{most_diverse_state[1]['state_name']} shows highest market diversity with {most_diverse_state[1]['diversity_metrics']['service_categories']} service categories"
        )
        
        # Calculate concentration
        total_market_value = sum(s["procurement_metrics"]["total_value_inr"] for s in state_metrics.values())
        top_3_states = sorted(
            state_metrics.items(),
            key=lambda x: x[1]["procurement_metrics"]["total_value_inr"],
            reverse=True
        )[:3]
        
        top_3_share = sum(s[1]["procurement_metrics"]["total_value_inr"] for s in top_3_states) / total_market_value * 100
        insights.append(f"Top 3 states account for {top_3_share:.1f}% of total procurement value")
        
        return insights
    
    def _empty_geographic_data(self) -> Dict[str, Any]:
        """Return empty geographic data structure"""
        return {
            "geographic_intelligence": {
                "state_metrics": {},
                "choropleth_data": [],
                "procurement_hotspots": [],
                "regional_analysis": {}
            },
            "insights": ["No geographic data available"],
            "metadata": {"message": "No data available for geographic analysis"}
        }

class DashboardDataProvider:
    """Central data provider for executive dashboard components"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.heatmap_generator = ServiceFirmHeatmapGenerator(db_path)
        self.geographic_generator = GeographicIntelligenceGenerator(db_path)
    
    def generate_executive_summary_data(self) -> Dict[str, Any]:
        """Generate executive summary data for dashboard cards"""
        
        logger.info("Generating executive summary dashboard data")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Overall market metrics
                market_overview = conn.execute("""
                    SELECT 
                        COUNT(*) as total_tenders,
                        SUM(COALESCE(inr_normalized_value, award_value, 25000000)) as total_market_value,
                        AVG(COALESCE(inr_normalized_value, award_value, 25000000)) as avg_deal_size,
                        COUNT(DISTINCT service_category) as service_categories,
                        COUNT(DISTINCT COALESCE(winning_firm, org)) as active_competitors
                    FROM tenders
                """).fetchone()
                
                if not market_overview or not market_overview[0]:
                    return self._empty_executive_summary()
                
                total_tenders, total_value, avg_deal, service_cats, competitors = market_overview
                
                # Calculate market concentration (simplified)
                firm_distribution = conn.execute("""
                    SELECT 
                        COALESCE(winning_firm, org) as firm,
                        SUM(COALESCE(inr_normalized_value, award_value, 25000000)) as value
                    FROM tenders
                    GROUP BY COALESCE(winning_firm, org)
                    ORDER BY value DESC
                """).fetchall()
                
                # Calculate HHI for market concentration
                firm_shares = []
                for firm, value in firm_distribution:
                    share = float(value) / float(total_value) if total_value > 0 else 0
                    firm_shares.append(share)
                
                hhi_index = sum(share ** 2 for share in firm_shares)
                
                # Growth analysis (simplified - need historical data for real growth)
                recent_tenders = conn.execute("""
                    SELECT COUNT(*) 
                    FROM tenders 
                    WHERE aoc_date >= date('now', '-3 months')
                """).fetchone()[0] or 0
                
                growth_estimate = (recent_tenders / total_tenders * 4 - 1) * 100 if total_tenders > 0 else 0
                
                return {
                    "executive_summary": {
                        "total_market_value": float(total_value),
                        "active_competitors": competitors,
                        "avg_deal_size": float(avg_deal),
                        "market_growth": max(0, min(50, growth_estimate)),  # Clamp to reasonable range
                        "hhi": round(hhi_index, 3),
                        "concentration_trend": "moderate",
                        "deal_size_trend": 15.0,  # Placeholder for trend analysis
                        "new_entrants": max(0, competitors // 10)  # Estimate
                    },
                    "key_metrics": {
                        "total_tenders": total_tenders,
                        "service_categories": service_cats,
                        "geographic_coverage": len([s for s in firm_distribution if s]),
                        "market_maturity": "developing" if competitors < 20 else "mature"
                    },
                    "generated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return {"error": str(e)}
    
    def _empty_executive_summary(self) -> Dict[str, Any]:
        """Return empty executive summary"""
        return {
            "executive_summary": {
                "total_market_value": 0,
                "active_competitors": 0,
                "avg_deal_size": 0,
                "market_growth": 0,
                "hhi": 0,
                "concentration_trend": "unknown",
                "deal_size_trend": 0,
                "new_entrants": 0
            },
            "key_metrics": {
                "total_tenders": 0,
                "service_categories": 0,
                "geographic_coverage": 0,
                "market_maturity": "unknown"
            },
            "message": "No data available for executive summary"
        }

async def test_visualization_data_generation():
    """Test visualization data generation capabilities"""
    
    print("TenderIntel Visualization Data Generator")
    print("=" * 42)
    
    # Initialize generators
    heatmap_gen = ServiceFirmHeatmapGenerator("data/tenders.db")
    geo_gen = GeographicIntelligenceGenerator("data/tenders.db")
    dashboard_provider = DashboardDataProvider("data/tenders.db")
    
    # Test Service×Firm heatmap data
    print("\n🔥 Testing Service×Firm Heatmap Data:")
    print("-" * 40)
    
    heatmap_data = heatmap_gen.generate_heatmap_data(metric="market_share")
    if "error" not in heatmap_data:
        print(f"  Services: {len(heatmap_data['heatmap_data']['services'])}")
        print(f"  Firms: {len(heatmap_data['heatmap_data']['firms'])}")
        print(f"  Matrix Cells: {len(heatmap_data['heatmap_data']['cell_data'])}")
        print(f"  Max Value: {heatmap_data['heatmap_data']['max_value']:.2f}%")
    else:
        print(f"  ❌ Error: {heatmap_data['error']}")
    
    # Test geographic intelligence
    print("\n🗺️  Testing Geographic Intelligence:")
    print("-" * 38)
    
    geo_data = geo_gen.generate_geographic_data()
    if "error" not in geo_data:
        print(f"  Active States: {geo_data['metadata']['total_states']}")
        print(f"  Total Market: ₹{geo_data['metadata']['total_procurement_value']/10000000:.1f}Cr")
        print(f"  Hotspots: {len(geo_data['geographic_intelligence']['procurement_hotspots'])}")
        
        if geo_data['insights']:
            print("  Key Insights:")
            for insight in geo_data['insights'][:2]:
                print(f"    • {insight}")
    else:
        print(f"  ❌ Error: {geo_data['error']}")
    
    # Test executive dashboard data
    print("\n📊 Testing Executive Dashboard Data:")
    print("-" * 38)
    
    exec_data = dashboard_provider.generate_executive_summary_data()
    if "error" not in exec_data:
        summary = exec_data["executive_summary"]
        print(f"  Market Value: ₹{summary['total_market_value']/10000000:.1f}Cr")
        print(f"  Competitors: {summary['active_competitors']}")
        print(f"  Avg Deal: ₹{summary['avg_deal_size']/10000000:.1f}Cr")
        print(f"  Market Growth: {summary['market_growth']:.1f}%")
        print(f"  HHI Index: {summary['hhi']:.3f}")
    else:
        print(f"  ❌ Error: {exec_data['error']}")
    
    print("\n✅ Visualization data generation operational!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_visualization_data_generation())
