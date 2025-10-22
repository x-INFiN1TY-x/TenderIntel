/**
 * TenderIntel - API Service Layer
 * Comprehensive client for all 17 backend API endpoints
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

class TenderIntelAPI {
    constructor(baseURL = null) {
        this.baseURL = baseURL || window.constants?.API?.BASE_URL || 'http://127.0.0.1:8002';
        this.timeout = window.constants?.API?.TIMEOUT || 10000;
        this.maxRetries = window.constants?.API?.RETRY_ATTEMPTS || 3;
        this.retryDelay = window.constants?.API?.RETRY_DELAY || 1000;
    }
    
    // ==================== SEARCH APIs (5 endpoints) ====================
    
    /**
     * Basic keyword search
     * @param {string} keyword - Search keyword
     * @param {object} options - Search options
     * @returns {Promise<object>} Search results
     */
    async search(keyword, options = {}) {
        const validation = window.validators?.keyword(keyword);
        if (!validation || !validation.valid) {
            throw new Error(validation?.error || 'Invalid keyword');
        }
        
        const params = new URLSearchParams({
            q: validation.value,
            limit: options.limit || 25,
            min_similarity: options.minSimilarity || 0,
            debug: options.debug || false
        });
        
        return this._fetch(`/search?${params}`);
    }
    
    /**
     * Filtered search with multiple criteria
     * @param {string} keyword - Search keyword
     * @param {object} filters - Filter criteria
     * @param {object} options - Search options
     * @returns {Promise<object>} Filtered search results
     */
    async searchFiltered(keyword, filters = {}, options = {}) {
        const validation = window.validators?.keyword(keyword);
        if (!validation || !validation.valid) {
            throw new Error(validation?.error || 'Invalid keyword');
        }
        
        const params = new URLSearchParams({
            q: validation.value,
            limit: options.limit || 25,
            debug: options.debug || false
        });
        
        // Add filter parameters
        if (filters.dateFrom) params.append('date_from', filters.dateFrom);
        if (filters.dateTo) params.append('date_to', filters.dateTo);
        
        // Array filters - convert to comma-separated strings
        if (Array.isArray(filters.serviceCategories) && filters.serviceCategories.length > 0) {
            params.append('service_categories', filters.serviceCategories.join(','));
        }
        if (Array.isArray(filters.organizations) && filters.organizations.length > 0) {
            params.append('organizations', filters.organizations.join(','));
        }
        if (Array.isArray(filters.valueRanges) && filters.valueRanges.length > 0) {
            params.append('value_ranges', filters.valueRanges.join(','));
        }
        if (Array.isArray(filters.regions) && filters.regions.length > 0) {
            params.append('regions', filters.regions.join(','));
        }
        if (Array.isArray(filters.statusTypes) && filters.statusTypes.length > 0) {
            params.append('status_types', filters.statusTypes.join(','));
        }
        if (Array.isArray(filters.departmentTypes) && filters.departmentTypes.length > 0) {
            params.append('department_types', filters.departmentTypes.join(','));
        }
        if (Array.isArray(filters.complexityLevels) && filters.complexityLevels.length > 0) {
            params.append('complexity_levels', filters.complexityLevels.join(','));
        }
        
        if (filters.minSimilarity !== undefined) {
            params.append('min_similarity', filters.minSimilarity);
        }
        
        return this._fetch(`/search-filtered?${params}`);
    }
    
    /**
     * Faceted search with aggregations
     * @param {string} keyword - Search keyword
     * @param {Array} facets - Facets to return (e.g., ['org', 'service_category'])
     * @param {object} options - Search options
     * @returns {Promise<object>} Faceted search results
     */
    async facetedSearch(keyword, facets = [], options = {}) {
        const validation = window.validators?.keyword(keyword);
        if (!validation || !validation.valid) {
            throw new Error(validation?.error || 'Invalid keyword');
        }
        
        const params = new URLSearchParams({
            q: validation.value,
            facets: facets.join(','),
            limit: options.limit || 25
        });
        
        return this._fetch(`/faceted-search?${params}`);
    }
    
    /**
     * Expand keyword to synonym phrases
     * @param {string} keyword - Keyword to expand
     * @param {number} maxExpansions - Maximum expansions to return
     * @param {boolean} debug - Enable debug mode
     * @returns {Promise<object>} Expansion results
     */
    async expandKeyword(keyword, maxExpansions = 5, debug = false) {
        const validation = window.validators?.keyword(keyword);
        if (!validation || !validation.valid) {
            throw new Error(validation?.error || 'Invalid keyword');
        }
        
        const params = new URLSearchParams({
            q: validation.value,
            max_expansions: maxExpansions,
            debug: debug
        });
        
        return this._fetch(`/expand?${params}`);
    }
    
    /**
     * Get available filter options
     * @returns {Promise<object>} Filter options for all categories
     */
    async getFilterOptions() {
        const cacheKey = '/filter-options';
        const cached = window.cacheService?.get(cacheKey);
        
        if (cached) {
            return cached;
        }
        
        const data = await this._fetch('/filter-options');
        window.cacheService?.set(cacheKey, data, 10 * 60 * 1000); // Cache 10 minutes
        
        return data;
    }
    
    // ==================== VISUALIZATION APIs (3 endpoints) ====================
    
    /**
     * Get executive dashboard summary
     * @returns {Promise<object>} Executive summary data
     */
    async getExecutiveSummary() {
        const cacheKey = '/visualizations/executive-summary';
        const cached = window.cacheService?.get(cacheKey);
        
        if (cached) {
            return cached;
        }
        
        const data = await this._fetch('/visualizations/executive-summary');
        window.cacheService?.set(cacheKey, data, 2 * 60 * 1000); // Cache 2 minutes
        
        return data;
    }
    
    /**
     * Get heatmap data for Service×Firm matrix
     * @param {string} metric - Metric type ('market_share', 'contract_count', etc.)
     * @param {string} timeframe - Time range ('3months', '6months', '12months', '24months')
     * @returns {Promise<object>} Heatmap data
     */
    async getHeatmapData(metric = 'market_share', timeframe = '12months') {
        const params = new URLSearchParams({ metric, timeframe });
        const cacheKey = `/visualizations/heatmap-data?${params}`;
        const cached = window.cacheService?.get(cacheKey);
        
        if (cached) {
            return cached;
        }
        
        const data = await this._fetch(`/visualizations/heatmap-data?${params}`);
        window.cacheService?.set(cacheKey, data, 5 * 60 * 1000); // Cache 5 minutes
        
        return data;
    }
    
    /**
     * Get geographic procurement data
     * @returns {Promise<object>} Geographic data for choropleth map
     */
    async getGeographicData() {
        const cacheKey = '/visualizations/geographic-data';
        const cached = window.cacheService?.get(cacheKey);
        
        if (cached) {
            return cached;
        }
        
        const data = await this._fetch('/visualizations/geographic-data');
        window.cacheService?.set(cacheKey, data, 5 * 60 * 1000); // Cache 5 minutes
        
        return data;
    }
    
    // ==================== ANALYTICS APIs (4 endpoints) ====================
    
    /**
     * Get firm financial scorecard
     * @param {string} firmName - Name of the firm
     * @param {string} timeframe - Time range
     * @param {boolean} includeTrends - Include trend data
     * @param {string} currency - Currency code
     * @returns {Promise<object>} Firm scorecard data
     */
    async getFirmScorecard(firmName, timeframe = '12months', includeTrends = true, currency = 'INR') {
        const firmValidation = window.validators?.firmName(firmName);
        if (!firmValidation || !firmValidation.valid) {
            throw new Error(firmValidation?.error || 'Invalid firm name');
        }
        
        const params = new URLSearchParams({
            timeframe,
            include_trends: includeTrends,
            currency
        });
        
        return this._fetch(`/analytics/firm-scorecard/${encodeURIComponent(firmValidation.value)}?${params}`);
    }
    
    /**
     * Get market analysis for service category
     * @param {string} serviceCategory - Service category name
     * @param {string} timeframe - Time range
     * @param {boolean} includeForecasting - Include forecasting data
     * @returns {Promise<object>} Market analysis data
     */
    async getMarketAnalysis(serviceCategory, timeframe = '12months', includeForecasting = false) {
        const categoryValidation = window.validators?.serviceCategory(serviceCategory);
        if (!categoryValidation || !categoryValidation.valid) {
            throw new Error(categoryValidation?.error || 'Invalid service category');
        }
        
        const params = new URLSearchParams({
            timeframe,
            include_forecasting: includeForecasting
        });
        
        return this._fetch(`/analytics/market-analysis/${encodeURIComponent(categoryValidation.value)}?${params}`);
    }
    
    /**
     * Benchmark deal value
     * @param {number} value - Deal value to benchmark
     * @param {string} serviceCategory - Service category
     * @param {string} currency - Currency code
     * @returns {Promise<object>} Benchmarking results
     */
    async benchmarkDeal(value, serviceCategory, currency = 'INR') {
        const valueValidation = window.validators?.currencyAmount(value);
        if (!valueValidation || !valueValidation.valid) {
            throw new Error(valueValidation?.error || 'Invalid deal value');
        }
        
        const categoryValidation = window.validators?.serviceCategory(serviceCategory);
        if (!categoryValidation || !categoryValidation.valid) {
            throw new Error(categoryValidation?.error || 'Invalid service category');
        }
        
        const params = new URLSearchParams({
            value: valueValidation.value.toString(),
            service_category: categoryValidation.value,
            currency
        });
        
        return this._fetch(`/analytics/deal-benchmarking?${params}`);
    }
    
    /**
     * Normalize currency amounts
     * @param {Array} amounts - Array of {value, currency} objects
     * @returns {Promise<object>} Normalized amounts
     */
    async normalizeCurrency(amounts) {
        if (!Array.isArray(amounts) || amounts.length === 0) {
            throw new Error('Amounts must be non-empty array');
        }
        
        return this._fetch('/analytics/normalize-currency', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(amounts)
        });
    }
    
    // ==================== INTELLIGENCE APIs (1 endpoint) ====================
    
    /**
     * Get competitive intelligence summary
     * @returns {Promise<object>} Intelligence summary
     */
    async getCompetitiveIntelligenceSummary() {
        const cacheKey = '/competitive-intelligence/summary';
        const cached = window.cacheService?.get(cacheKey);
        
        if (cached) {
            return cached;
        }
        
        const data = await this._fetch('/competitive-intelligence/summary');
        window.cacheService?.set(cacheKey, data, 5 * 60 * 1000); // Cache 5 minutes
        
        return data;
    }
    
    // ==================== SYSTEM APIs (3 endpoints) ====================
    
    /**
     * Check system health
     * @returns {Promise<object>} Health status
     */
    async getHealth() {
        return this._fetch('/health');
    }
    
    /**
     * Get system statistics
     * @returns {Promise<object>} System stats
     */
    async getStats() {
        const cacheKey = '/stats';
        const cached = window.cacheService?.get(cacheKey);
        
        if (cached) {
            return cached;
        }
        
        const data = await this._fetch('/stats');
        window.cacheService?.set(cacheKey, data, 2 * 60 * 1000); // Cache 2 minutes
        
        return data;
    }
    
    /**
     * Test demo scenarios
     * @returns {Promise<object>} Demo test results
     */
    async testDemoScenarios() {
        return this._fetch('/test-demo-scenarios');
    }
    
    // ==================== SCRAPER APIs (1 endpoint) ====================
    
    /**
     * Trigger CPPP portal scraper
     * @param {object} options - Scraper options
     * @returns {Promise<object>} Scrape results
     */
    async scrapeCPPP(options = {}) {
        const params = new URLSearchParams({
            max_pages: options.maxPages || 1,
            test_mode: options.testMode !== undefined ? options.testMode : true,
            enable_captcha: options.enableCaptcha || false
        });
        
        return this._fetch(`/scraper/cppp?${params}`, { method: 'POST' });
    }
    
    // ==================== HELPER METHODS ====================
    
    /**
     * Core fetch method with error handling and retries
     * @private
     * @param {string} url - API endpoint URL
     * @param {object} options - Fetch options
     * @returns {Promise<object>} API response
     */
    async _fetch(url, options = {}) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            try {
                return await this._fetchOnce(url, options);
                
            } catch (error) {
                lastError = error;
                const classified = this._classifyError(error, url);
                
                // Don't retry client errors (4xx) or non-retryable errors
                if (!classified.retryable) {
                    throw classified;
                }
                
                // Don't retry on last attempt
                if (attempt === this.maxRetries) {
                    throw classified;
                }
                
                // Exponential backoff
                const delay = this.retryDelay * Math.pow(2, attempt - 1);
                await this._sleep(delay);
                
                console.warn(`API retry ${attempt}/${this.maxRetries} for ${url} after ${delay}ms delay`);
            }
        }
        
        throw lastError;
    }
    
    /**
     * Single fetch attempt with timeout
     * @private
     * @param {string} url - API endpoint URL
     * @param {object} options - Fetch options
     * @returns {Promise<object>} API response
     */
    async _fetchOnce(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        try {
            const fullUrl = url.startsWith('http') ? url : this.baseURL + url;
            
            const response = await fetch(fullUrl, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Validate API response
            const validation = window.validators?.apiResponse(data);
            if (validation && !validation.valid) {
                throw new Error(validation.error);
            }
            
            // Log successful API calls in development
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.log(`✅ API Success [${url}]:`, data);
            }
            
            return data;
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${this.timeout}ms: ${url}`);
            }
            
            console.error(`❌ API Error [${url}]:`, error);
            throw error;
        }
    }
    
    /**
     * Classify error for retry logic
     * @private
     * @param {Error} error - Error object
     * @param {string} url - Request URL
     * @returns {object} Classified error
     */
    _classifyError(error, url) {
        const errorPatterns = {
            network: /fetch.*failed|network.*error|ERR_NETWORK|Failed to fetch/i,
            timeout: /timeout|TIMEOUT|abort/i,
            server: /500|502|503|504/i,
            client: /400|401|403|404|422/i,
            rateLimit: /429|rate.*limit/i
        };
        
        let errorType = 'unknown';
        
        for (const [type, pattern] of Object.entries(errorPatterns)) {
            if (pattern.test(error.message) || pattern.test(error.toString())) {
                errorType = type;
                break;
            }
        }
        
        const retryable = ['network', 'timeout', 'server', 'rateLimit'].includes(errorType);
        
        return {
            type: errorType,
            originalError: error,
            message: this._getUserFriendlyMessage(errorType, url),
            retryable,
            url
        };
    }
    
    /**
     * Get user-friendly error message
     * @private
     * @param {string} errorType - Error type
     * @param {string} url - Request URL
     * @returns {string} User-friendly message
     */
    _getUserFriendlyMessage(errorType, url) {
        const messages = {
            network: window.constants?.ERRORS?.NETWORK || 'Network error - check your internet connection',
            timeout: window.constants?.ERRORS?.TIMEOUT || 'Request timed out - server may be busy',
            server: window.constants?.ERRORS?.SERVER || 'Server error - try again later',
            client: window.constants?.ERRORS?.VALIDATION || 'Invalid request - check your input',
            rateLimit: 'Too many requests - please wait before trying again',
            unknown: 'Unexpected error - please try again'
        };
        
        const endpoint = url.split('?')[0];
        return `${messages[errorType] || messages.unknown} [${endpoint}]`;
    }
    
    /**
     * Sleep utility for retry delays
     * @private
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise<void>}
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // ==================== CACHE MANAGEMENT ====================
    
    /**
     * Clear API cache
     * @param {string} pattern - Optional pattern to match
     */
    clearCache(pattern = null) {
        if (window.cacheService) {
            if (pattern) {
                window.cacheService.clearPattern(pattern);
            } else {
                window.cacheService.clearAll();
            }
        }
    }
    
    /**
     * Get cache statistics
     * @returns {object} Cache statistics
     */
    getCacheInfo() {
        if (window.cacheService) {
            return window.cacheService.getStats();
        }
        return { message: 'Cache service not available' };
    }
    
    /**
     * Warm up cache with initial data
     * @param {Array<string>} endpoints - Endpoints to pre-fetch
     * @returns {Promise<void>}
     */
    async warmUpCache(endpoints = []) {
        const defaultEndpoints = [
            '/health',
            '/filter-options',
            '/visualizations/executive-summary'
        ];
        
        const toFetch = endpoints.length > 0 ? endpoints : defaultEndpoints;
        
        for (const endpoint of toFetch) {
            try {
                await this._fetch(endpoint);
            } catch (error) {
                console.warn(`Cache warm-up failed for ${endpoint}:`, error.message);
            }
        }
    }
    
    // ==================== BATCH OPERATIONS ====================
    
    /**
     * Fetch multiple endpoints in parallel
     * @param {Array<string>} endpoints - Array of endpoint URLs
     * @returns {Promise<Array>} Array of results
     */
    async batchFetch(endpoints) {
        const promises = endpoints.map(endpoint => 
            this._fetch(endpoint).catch(error => ({ error: error.message, endpoint }))
        );
        
        return Promise.all(promises);
    }
    
    /**
     * Search multiple keywords in parallel
     * @param {Array<string>} keywords - Array of keywords
     * @param {object} options - Search options
     * @returns {Promise<Array>} Array of search results
     */
    async batchSearch(keywords, options = {}) {
        const promises = keywords.map(keyword =>
            this.search(keyword, options).catch(error => ({
                error: error.message,
                keyword,
                results: []
            }))
        );
        
        return Promise.all(promises);
    }
}

// Initialize global API instance
window.api = new TenderIntelAPI();

// Warm up cache on page load
document.addEventListener('DOMContentLoaded', () => {
    window.api.warmUpCache().catch(error => {
        console.warn('Cache warm-up failed:', error);
    });
});

console.log('✅ TenderIntel API Service loaded successfully');
