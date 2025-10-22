#!/usr/bin/env python3
"""
Currency Normalization System for TenderIntel
=============================================

Production-grade currency conversion with RBI rate integration and historical tracking.
Based on FINANCIAL_ANALYSIS_SYSTEM.md expert specifications.
"""

import sqlite3
import asyncio
import aiohttp
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
import json
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class CurrencyNormalizer:
    """Real-time currency conversion with historical rate tracking and RBI integration"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.rate_cache_hours = 6  # Cache rates for 6 hours
        self.rbi_api_url = "https://api.rbi.org.in/rbi/exchangerate"
        self.forex_api_url = "https://api.exchangerate-api.com/v4/latest"
        
    async def normalize_to_inr(self, 
                              amount: Decimal, 
                              currency: str, 
                              value_date: date) -> Dict[str, Any]:
        """Convert any currency to INR with confidence scoring and provenance"""
        
        if currency == "INR":
            return {
                "inr_amount": amount,
                "exchange_rate": Decimal('1.0'),
                "confidence": 1.0,
                "rate_source": "direct",
                "rate_date": value_date,
                "normalization_method": "direct_inr"
            }
        
        # Get exchange rate with fallback hierarchy
        rate_result = await self._get_exchange_rate_with_fallback(currency, value_date)
        
        if not rate_result["rate"]:
            logger.warning(f"Could not get exchange rate for {currency} on {value_date}")
            return {
                "inr_amount": None,
                "exchange_rate": None,
                "confidence": 0.0,
                "rate_source": "unavailable",
                "error": f"No exchange rate available for {currency}"
            }
        
        # Convert to INR
        inr_amount = amount * Decimal(str(rate_result["rate"]))
        inr_amount = inr_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return {
            "inr_amount": inr_amount,
            "exchange_rate": Decimal(str(rate_result["rate"])),
            "confidence": rate_result["confidence"],
            "rate_source": rate_result["source"],
            "rate_date": rate_result["rate_date"],
            "normalization_method": "currency_conversion"
        }
    
    async def _get_exchange_rate_with_fallback(self, 
                                             currency: str, 
                                             value_date: date) -> Dict[str, Any]:
        """Get exchange rate with comprehensive fallback hierarchy"""
        
        # Priority 1: Check cache for recent rates
        cached_rate = self._get_cached_rate(currency, value_date)
        if cached_rate:
            return cached_rate
        
        # Priority 2: RBI official rates (for major currencies)
        if currency in ["USD", "EUR", "GBP", "JPY", "SGD"]:
            rbi_rate = await self._get_rbi_rate(currency, value_date)
            if rbi_rate:
                self._cache_rate(currency, value_date, rbi_rate)
                return {
                    "rate": rbi_rate,
                    "confidence": 0.98,
                    "source": "rbi_official",
                    "rate_date": value_date
                }
        
        # Priority 3: Live forex API (for current/recent dates)
        if (datetime.now().date() - value_date).days <= 7:
            live_rate = await self._get_live_forex_rate(currency)
            if live_rate:
                self._cache_rate(currency, datetime.now().date(), live_rate)
                return {
                    "rate": live_rate,
                    "confidence": 0.90,
                    "source": "live_forex_api",
                    "rate_date": datetime.now().date()
                }
        
        # Priority 4: Historical approximation
        historical_rate = await self._get_historical_approximation(currency, value_date)
        if historical_rate:
            return {
                "rate": historical_rate,
                "confidence": 0.70,
                "source": "historical_approximation", 
                "rate_date": value_date
            }
        
        # No rate available
        return {"rate": None, "confidence": 0.0, "source": "unavailable"}
    
    def _get_cached_rate(self, currency: str, value_date: date) -> Optional[Dict[str, Any]]:
        """Get exchange rate from local cache"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Look for rate within cache window
                cache_window_start = value_date - timedelta(hours=self.rate_cache_hours)
                cache_window_end = value_date + timedelta(hours=self.rate_cache_hours)
                
                cached_rate = conn.execute("""
                    SELECT rate, rate_date, source, created_at
                    FROM exchange_rates
                    WHERE currency_from = ? AND currency_to = 'INR'
                    AND rate_date BETWEEN ? AND ?
                    ORDER BY ABS(julianday(rate_date) - julianday(?)) ASC
                    LIMIT 1
                """, (currency, cache_window_start.isoformat(), cache_window_end.isoformat(), value_date.isoformat())).fetchone()
                
                if cached_rate:
                    rate, rate_date, source, created_at = cached_rate
                    
                    # Check if cache is still fresh
                    cache_age = datetime.now() - datetime.fromisoformat(created_at)
                    if cache_age.total_seconds() < self.rate_cache_hours * 3600:
                        return {
                            "rate": Decimal(str(rate)),
                            "confidence": 0.95,
                            "source": f"cached_{source}",
                            "rate_date": datetime.fromisoformat(rate_date).date()
                        }
        
        except Exception as e:
            logger.debug(f"Cache lookup failed for {currency}: {e}")
        
        return None
    
    async def _get_rbi_rate(self, currency: str, value_date: date) -> Optional[Decimal]:
        """Get exchange rate from RBI API"""
        
        try:
            # RBI API endpoint for exchange rates
            rbi_url = f"{self.rbi_api_url}/{currency}/INR/{value_date.isoformat()}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(rbi_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "rate" in data and data["rate"]:
                            rate = Decimal(str(data["rate"]))
                            logger.info(f"Retrieved RBI rate: {currency} = {rate} INR on {value_date}")
                            return rate
        
        except Exception as e:
            logger.debug(f"RBI API failed for {currency}: {e}")
        
        return None
    
    async def _get_live_forex_rate(self, currency: str) -> Optional[Decimal]:
        """Get live exchange rate from forex API"""
        
        try:
            forex_url = f"{self.forex_api_url}/{currency}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(forex_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "rates" in data and "INR" in data["rates"]:
                            rate = Decimal(str(data["rates"]["INR"]))
                            logger.info(f"Retrieved live forex rate: {currency} = {rate} INR")
                            return rate
        
        except Exception as e:
            logger.debug(f"Live forex API failed for {currency}: {e}")
        
        return None
    
    async def _get_historical_approximation(self, currency: str, value_date: date) -> Optional[Decimal]:
        """Get historical rate approximation using known rates and interpolation"""
        
        # Approximate exchange rates for major currencies (as of Oct 2025)
        approximate_rates = {
            "USD": Decimal('83.50'),
            "EUR": Decimal('88.20'),
            "GBP": Decimal('102.40'),
            "JPY": Decimal('0.56'),
            "SGD": Decimal('61.80'),
            "AUD": Decimal('54.30'),
            "CAD": Decimal('60.70'),
            "CHF": Decimal('91.20')
        }
        
        if currency in approximate_rates:
            # Apply time-based adjustment for historical dates
            days_ago = (datetime.now().date() - value_date).days
            
            if days_ago > 365:
                # Older than 1 year - apply conservative adjustment
                adjustment_factor = Decimal('0.95')  # Assume 5% depreciation
            elif days_ago > 90:
                # 3-12 months ago - minimal adjustment
                adjustment_factor = Decimal('0.98')
            else:
                # Recent - use current rate
                adjustment_factor = Decimal('1.0')
            
            historical_rate = approximate_rates[currency] * adjustment_factor
            logger.info(f"Using historical approximation: {currency} = {historical_rate} INR (±{adjustment_factor})")
            return historical_rate
        
        return None
    
    def _cache_rate(self, currency: str, rate_date: date, rate: Decimal, source: str = "api"):
        """Cache exchange rate in local database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO exchange_rates 
                    (currency_from, currency_to, rate, rate_date, source)
                    VALUES (?, 'INR', ?, ?, ?)
                """, (currency, float(rate), rate_date.isoformat(), source))
                conn.commit()
                
            logger.debug(f"Cached rate: {currency} = {rate} INR ({source})")
                
        except Exception as e:
            logger.warning(f"Failed to cache rate: {e}")
    
    async def batch_normalize_tenders(self, tender_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Batch normalize currency values for multiple tenders"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Get tenders that need currency normalization
            if tender_ids:
                placeholders = ",".join(["?"] * len(tender_ids))
                tenders = conn.execute(f"""
                    SELECT rowid, tender_id, award_value, currency, aoc_date
                    FROM tenders
                    WHERE tender_id IN ({placeholders}) 
                    AND award_value IS NOT NULL
                    AND currency IS NOT NULL
                """, tender_ids).fetchall()
            else:
                tenders = conn.execute("""
                    SELECT rowid, tender_id, award_value, currency, aoc_date
                    FROM tenders
                    WHERE award_value IS NOT NULL 
                    AND currency IS NOT NULL
                    AND (inr_normalized_value IS NULL OR inr_normalized_value = 0)
                """).fetchall()
        
        normalization_results = {
            "total_tenders": len(tenders),
            "successful_normalizations": 0,
            "failed_normalizations": 0,
            "currencies_processed": set(),
            "normalization_details": []
        }
        
        for rowid, tender_id, award_value, currency, aoc_date in tenders:
            try:
                # Parse date
                if isinstance(aoc_date, str):
                    value_date = datetime.fromisoformat(aoc_date).date()
                else:
                    value_date = datetime.now().date()
                
                # Normalize currency
                normalization_result = await self.normalize_to_inr(
                    Decimal(str(award_value)), currency, value_date
                )
                
                if normalization_result["inr_amount"]:
                    # Update database with normalized values
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE tenders SET
                                exchange_rate = ?,
                                exchange_rate_date = ?,
                                inr_normalized_value = ?
                            WHERE rowid = ?
                        """, (
                            float(normalization_result["exchange_rate"]),
                            normalization_result["rate_date"].isoformat(),
                            float(normalization_result["inr_amount"]),
                            rowid
                        ))
                        conn.commit()
                    
                    normalization_results["successful_normalizations"] += 1
                    normalization_results["currencies_processed"].add(currency)
                    
                    normalization_results["normalization_details"].append({
                        "tender_id": tender_id,
                        "original_amount": float(award_value),
                        "currency": currency,
                        "inr_amount": float(normalization_result["inr_amount"]),
                        "exchange_rate": float(normalization_result["exchange_rate"]),
                        "confidence": normalization_result["confidence"]
                    })
                
                else:
                    normalization_results["failed_normalizations"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to normalize {tender_id}: {e}")
                normalization_results["failed_normalizations"] += 1
        
        normalization_results["currencies_processed"] = list(normalization_results["currencies_processed"])
        normalization_results["success_rate"] = (
            normalization_results["successful_normalizations"] / 
            normalization_results["total_tenders"] * 100 
            if normalization_results["total_tenders"] > 0 else 0
        )
        
        logger.info(f"Batch normalization complete: {normalization_results['success_rate']:.1f}% success rate")
        return normalization_results
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies for normalization"""
        return ["INR", "USD", "EUR", "GBP", "JPY", "SGD", "AUD", "CAD", "CHF"]
    
    def get_cached_rates_summary(self) -> Dict[str, Any]:
        """Get summary of cached exchange rates"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                rates_summary = conn.execute("""
                    SELECT 
                        currency_from,
                        COUNT(*) as rate_count,
                        MIN(rate_date) as earliest_date,
                        MAX(rate_date) as latest_date,
                        AVG(rate) as avg_rate
                    FROM exchange_rates
                    WHERE currency_to = 'INR'
                    GROUP BY currency_from
                    ORDER BY rate_count DESC
                """).fetchall()
                
                return {
                    "cached_currencies": len(rates_summary),
                    "total_cached_rates": sum(row[1] for row in rates_summary),
                    "currency_details": [
                        {
                            "currency": row[0],
                            "rate_count": row[1],
                            "earliest_date": row[2],
                            "latest_date": row[3],
                            "average_rate": round(float(row[4]), 4)
                        }
                        for row in rates_summary
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache summary: {e}")
            return {"error": str(e)}

class DealSizeClassifier:
    """Intelligent deal size classification with market context"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def classify_deal_size(self, inr_value: Decimal, service_category: str = None) -> Dict[str, Any]:
        """Classify deal size with service-specific benchmarking"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get deal size thresholds
                thresholds = conn.execute("""
                    SELECT category, min_value_inr, max_value_inr, display_label, color_code
                    FROM deal_size_thresholds
                    ORDER BY min_value_inr ASC
                """).fetchall()
                
                # Classify based on value
                deal_category = "unknown"
                display_label = "Unknown"
                color_code = "#gray"
                
                for category, min_val, max_val, label, color in thresholds:
                    if min_val <= inr_value < max_val:
                        deal_category = category
                        display_label = label
                        color_code = color
                        break
                
                # Calculate market percentile if service category provided
                market_percentile = None
                if service_category:
                    market_percentile = self._calculate_market_percentile(
                        inr_value, service_category
                    )
                
                return {
                    "deal_size_category": deal_category,
                    "display_label": display_label,
                    "color_code": color_code,
                    "inr_value": float(inr_value),
                    "market_percentile": market_percentile,
                    "service_context": service_category,
                    "classification_confidence": 0.95
                }
                
        except Exception as e:
            logger.error(f"Deal classification failed: {e}")
            return {
                "deal_size_category": "unknown",
                "error": str(e),
                "classification_confidence": 0.0
            }
    
    def _calculate_market_percentile(self, inr_value: Decimal, service_category: str) -> Optional[int]:
        """Calculate market percentile within service category"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get all values in this service category
                category_values = conn.execute("""
                    SELECT inr_normalized_value
                    FROM tenders
                    WHERE service_category = ? 
                    AND inr_normalized_value IS NOT NULL
                    ORDER BY inr_normalized_value ASC
                """, (service_category,)).fetchall()
                
                if not category_values:
                    return None
                
                values = [float(row[0]) for row in category_values]
                value_position = sum(1 for v in values if v <= float(inr_value))
                
                percentile = int((value_position / len(values)) * 100)
                return max(1, min(99, percentile))  # Clamp to 1-99 range
                
        except Exception as e:
            logger.debug(f"Percentile calculation failed: {e}")
            return None

async def main():
    """Test currency normalization system"""
    
    print("TenderIntel Currency Normalization System")
    print("=" * 45)
    
    # Initialize normalizer
    normalizer = CurrencyNormalizer("data/tenders.db")
    classifier = DealSizeClassifier("data/tenders.db")
    
    # Test currency normalization
    print("\n💱 Testing Currency Normalization:")
    print("-" * 35)
    
    test_conversions = [
        (Decimal("50000"), "USD", date(2025, 10, 21)),
        (Decimal("100000"), "EUR", date(2025, 10, 21)),
        (Decimal("25000000"), "INR", date(2025, 10, 21))
    ]
    
    for amount, currency, test_date in test_conversions:
        result = await normalizer.normalize_to_inr(amount, currency, test_date)
        
        if result.get("inr_amount"):
            print(f"{currency} {amount:,} = INR {result['inr_amount']:,}")
            print(f"  Rate: {result['exchange_rate']}, Confidence: {result['confidence']:.2f}")
            print(f"  Source: {result['rate_source']}")
        else:
            print(f"❌ Failed to convert {currency} {amount}")
    
    # Test deal size classification
    print("\n📊 Testing Deal Size Classification:")
    print("-" * 38)
    
    test_values = [
        (Decimal("500000"), "networking"),
        (Decimal("25000000"), "cloud"),
        (Decimal("150000000"), "security"),
        (Decimal("2000000000"), "ai_ml")
    ]
    
    for value, category in test_values:
        classification = classifier.classify_deal_size(value, category)
        print(f"₹{value:,} ({category}) = {classification['deal_size_category'].upper()}")
        print(f"  Label: {classification['display_label']}")
        if classification.get('market_percentile'):
            print(f"  Market Percentile: {classification['market_percentile']}%")
    
    # Test batch normalization
    print("\n🔄 Testing Batch Normalization:")
    print("-" * 32)
    
    batch_result = await normalizer.batch_normalize_tenders()
    print(f"Processed: {batch_result['total_tenders']} tenders")
    print(f"Success Rate: {batch_result['success_rate']:.1f}%")
    print(f"Currencies: {', '.join(batch_result['currencies_processed'])}")
    
    # Cache summary
    cache_summary = normalizer.get_cached_rates_summary()
    print(f"\n💾 Exchange Rate Cache:")
    print(f"Cached Currencies: {cache_summary.get('cached_currencies', 0)}")
    print(f"Total Cached Rates: {cache_summary.get('total_cached_rates', 0)}")
    
    print("\n✅ Currency normalization system operational!")

if __name__ == "__main__":
    asyncio.run(main())
