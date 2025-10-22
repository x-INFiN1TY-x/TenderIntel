/**
 * TenderIntel - Client-Side Cache Service
 * Manages temporary storage of API responses with TTL and LRU eviction
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

class CacheService {
    constructor(maxSize = 100, defaultTTL = 5 * 60 * 1000) {
        this.cache = new Map();
        this.maxSize = maxSize;
        this.defaultTTL = defaultTTL;
        this.accessLog = new Map(); // For LRU tracking
        this.hitCount = 0;
        this.missCount = 0;
    }
    
    /**
     * Set cache entry with optional TTL
     * @param {string} key - Cache key
     * @param {any} value - Value to cache
     * @param {number} ttl - Time to live in milliseconds
     */
    set(key, value, ttl = this.defaultTTL) {
        // Enforce size limit with LRU eviction
        if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
            this.evictLRU();
        }
        
        this.cache.set(key, {
            value,
            timestamp: Date.now(),
            ttl,
            hits: 0
        });
        
        this.accessLog.set(key, Date.now());
    }
    
    /**
     * Get cache entry if valid
     * @param {string} key - Cache key
     * @returns {any|null} Cached value or null if expired/missing
     */
    get(key) {
        const entry = this.cache.get(key);
        
        if (!entry) {
            this.missCount++;
            return null;
        }
        
        // Check if expired
        if (Date.now() - entry.timestamp > entry.ttl) {
            this.cache.delete(key);
            this.accessLog.delete(key);
            this.missCount++;
            return null;
        }
        
        // Update access tracking
        entry.hits++;
        this.accessLog.set(key, Date.now());
        this.hitCount++;
        
        return entry.value;
    }
    
    /**
     * Check if key exists and is valid
     * @param {string} key - Cache key
     * @returns {boolean} True if key exists and not expired
     */
    has(key) {
        return this.get(key) !== null;
    }
    
    /**
     * Remove specific cache entry
     * @param {string} key - Cache key to remove
     */
    delete(key) {
        this.cache.delete(key);
        this.accessLog.delete(key);
    }
    
    /**
     * Clear cache entries matching pattern
     * @param {string|RegExp} pattern - Pattern to match
     */
    clearPattern(pattern) {
        const regex = pattern instanceof RegExp ? pattern : new RegExp(pattern);
        
        for (const key of this.cache.keys()) {
            if (regex.test(key)) {
                this.delete(key);
            }
        }
    }
    
    /**
     * Clear all cache entries
     */
    clearAll() {
        this.cache.clear();
        this.accessLog.clear();
        this.hitCount = 0;
        this.missCount = 0;
    }
    
    /**
     * Evict least recently used entry
     * @private
     */
    evictLRU() {
        let oldestKey = null;
        let oldestTime = Date.now();
        
        for (const [key, time] of this.accessLog.entries()) {
            if (time < oldestTime) {
                oldestTime = time;
                oldestKey = key;
            }
        }
        
        if (oldestKey) {
            this.delete(oldestKey);
        }
    }
    
    /**
     * Get cache statistics
     * @returns {object} Cache statistics
     */
    getStats() {
        let totalHits = 0;
        let validEntries = 0;
        let expiredEntries = 0;
        
        for (const [key, entry] of this.cache.entries()) {
            if (Date.now() - entry.timestamp <= entry.ttl) {
                validEntries++;
                totalHits += entry.hits;
            } else {
                expiredEntries++;
            }
        }
        
        const totalRequests = this.hitCount + this.missCount;
        const hitRate = totalRequests > 0 ? (this.hitCount / totalRequests) * 100 : 0;
        
        return {
            totalEntries: this.cache.size,
            validEntries,
            expiredEntries,
            totalHits,
            hitCount: this.hitCount,
            missCount: this.missCount,
            hitRate: hitRate.toFixed(1),
            maxSize: this.maxSize,
            utilizationPercent: ((this.cache.size / this.maxSize) * 100).toFixed(1)
        };
    }
    
    /**
     * Serialize cache to localStorage for persistence
     * @param {string} key - localStorage key
     */
    persist(key = 'tenderintel_cache') {
        try {
            const serializable = {};
            
            for (const [k, v] of this.cache.entries()) {
                // Only persist non-expired entries
                if (Date.now() - v.timestamp <= v.ttl) {
                    serializable[k] = {
                        value: v.value,
                        timestamp: v.timestamp,
                        ttl: v.ttl,
                        hits: v.hits
                    };
                }
            }
            
            localStorage.setItem(key, JSON.stringify(serializable));
            
        } catch (error) {
            console.warn('Cache persistence failed:', error);
            
            // Try to handle quota exceeded error
            if (error.name === 'QuotaExceededError') {
                // Clear old entries and retry
                this.clearExpired();
                try {
                    localStorage.setItem(key, JSON.stringify({}));
                } catch {
                    console.error('Unable to persist cache - localStorage quota exceeded');
                }
            }
        }
    }
    
    /**
     * Restore cache from localStorage
     * @param {string} key - localStorage key
     */
    restore(key = 'tenderintel_cache') {
        try {
            const data = localStorage.getItem(key);
            if (!data) return;
            
            const deserialized = JSON.parse(data);
            
            for (const [k, v] of Object.entries(deserialized)) {
                // Only restore non-expired entries
                if (Date.now() - v.timestamp <= v.ttl) {
                    this.cache.set(k, v);
                    this.accessLog.set(k, v.timestamp);
                }
            }
            
            console.log(`Restored ${this.cache.size} cache entries from localStorage`);
            
        } catch (error) {
            console.warn('Cache restoration failed:', error);
        }
    }
    
    /**
     * Clear expired entries
     */
    clearExpired() {
        const now = Date.now();
        const keysToDelete = [];
        
        for (const [key, entry] of this.cache.entries()) {
            if (now - entry.timestamp > entry.ttl) {
                keysToDelete.push(key);
            }
        }
        
        keysToDelete.forEach(key => this.delete(key));
        
        return keysToDelete.length;
    }
    
    /**
     * Get all cache keys
     * @returns {Array<string>} Array of cache keys
     */
    keys() {
        return Array.from(this.cache.keys());
    }
    
    /**
     * Get cache size in bytes (approximation)
     * @returns {number} Approximate size in bytes
     */
    getSize() {
        try {
            const serialized = JSON.stringify(Array.from(this.cache.entries()));
            return new Blob([serialized]).size;
        } catch {
            return 0;
        }
    }
    
    /**
     * Warm cache with initial data
     * @param {object} data - Initial data to cache {key: value}
     * @param {number} ttl - TTL for all entries
     */
    warmUp(data, ttl = this.defaultTTL) {
        for (const [key, value] of Object.entries(data)) {
            this.set(key, value, ttl);
        }
    }
}

// Initialize global cache instance with settings from constants
const cacheConfig = window.constants?.CACHE || {
    MAX_SIZE: 100,
    DEFAULT_TTL: 5 * 60 * 1000
};

window.cacheService = new CacheService(
    cacheConfig.MAX_SIZE,
    cacheConfig.DEFAULT_TTL
);

// Attempt to restore cache from previous session
window.cacheService.restore();

// Persist cache before page unload
window.addEventListener('beforeunload', () => {
    window.cacheService.persist();
});

// Periodic cleanup of expired entries
setInterval(() => {
    const cleared = window.cacheService.clearExpired();
    if (cleared > 0) {
        console.log(`Cleared ${cleared} expired cache entries`);
    }
}, 60000); // Every minute

console.log('✅ TenderIntel Cache Service loaded successfully');
