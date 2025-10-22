/**
 * TenderIntel - Application Constants
 * Centralized configuration and constants for the entire application
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

const constants = {
    // API Configuration
    API: {
        BASE_URL: 'http://127.0.0.1:8002',
        TIMEOUT: 10000, // 10 seconds
        CACHE_TTL: 5 * 60 * 1000, // 5 minutes
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 1000 // 1 second
    },
    
    // UI Configuration
    UI: {
        PAGE_SIZE: 25,
        MAX_SEARCH_RESULTS: 100,
        TOAST_DURATION: 5000, // 5 seconds
        MOBILE_BREAKPOINT: 768, // px
        DEBOUNCE_DELAY: 300, // ms
        ANIMATION_DURATION: 300 // ms
    },
    
    // Business Rules
    BUSINESS: {
        MIN_DEAL_VALUE: 100000,      // ₹1 Lakh
        MAX_DEAL_VALUE: 10000000000, // ₹1000 Cr
        DEFAULT_CURRENCY: 'INR',
        SUPPORTED_CURRENCIES: ['INR', 'USD', 'EUR', 'GBP'],
        
        // Market concentration thresholds (HHI)
        MARKET_CONCENTRATION: {
            HIGHLY_COMPETITIVE: 0.10,
            COMPETITIVE: 0.15,
            MODERATELY_CONCENTRATED: 0.25,
            HIGHLY_CONCENTRATED: 1.00
        },
        
        // Deal size categories
        DEAL_SIZES: {
            MICRO: { min: 0, max: 1000000, label: 'Micro Deal' },      // <₹10L
            SMALL: { min: 1000000, max: 10000000, label: 'Small Deal' }, // ₹10L-₹1Cr
            MEDIUM: { min: 10000000, max: 50000000, label: 'Medium Deal' }, // ₹1Cr-₹5Cr
            LARGE: { min: 50000000, max: 100000000, label: 'Large Deal' }, // ₹5Cr-₹10Cr
            MEGA: { min: 100000000, max: Infinity, label: 'Mega Deal' }    // ≥₹10Cr
        }
    },
    
    // Service Categories
    SERVICES: {
        CLOUD: 'cloud',
        NETWORKING: 'networking',
        DATABASE: 'database',
        SOFTWARE: 'software',
        INTEGRATION: 'integration',
        SECURITY: 'security',
        HARDWARE: 'hardware'
    },
    
    // Color Schemes
    COLORS: {
        PRIMARY: '#3b82f6',
        SUCCESS: '#10b981',
        WARNING: '#f59e0b',
        DANGER: '#ef4444',
        
        SERVICE_CATEGORIES: {
            cloud: '#3b82f6',      // Blue
            networking: '#8b5cf6', // Purple
            security: '#ef4444',   // Red
            database: '#10b981',   // Green
            software: '#f59e0b',   // Orange
            integration: '#06b6d4', // Cyan
            hardware: '#6b7280'    // Gray
        },
        
        PERFORMANCE_SCALE: [
            { min: 0, max: 20, color: '#ef4444', label: 'Poor' },
            { min: 20, max: 40, color: '#f59e0b', label: 'Below Average' },
            { min: 40, max: 60, color: '#3b82f6', label: 'Average' },
            { min: 60, max: 80, color: '#8b5cf6', label: 'Good' },
            { min: 80, max: 100, color: '#10b981', label: 'Excellent' }
        ]
    },
    
    // Data Sources
    DATA_SOURCES: {
        GEM: 'GeM Portal',
        CPPP: 'CPPP Portal',
        EPROCURE: 'eProcurement Portal',
        INTERNAL: 'Internal Database'
    },
    
    // Export Formats
    EXPORT: {
        FORMATS: ['CSV', 'Excel', 'PDF'],
        MAX_RECORDS: 10000,
        FILENAME_PREFIX: 'tenderintel'
    },
    
    // Search Configuration
    SEARCH: {
        MIN_KEYWORD_LENGTH: 1,
        MAX_KEYWORD_LENGTH: 200,
        DEFAULT_SIMILARITY: 0,
        MAX_EXPANSIONS: 10,
        
        FILTER_CATEGORIES: [
            'service_categories',
            'organizations',
            'value_ranges',
            'regions',
            'status_types',
            'department_types',
            'complexity_levels',
            'date_ranges'
        ]
    },
    
    // Chart Configuration
    CHARTS: {
        DEFAULT_HEIGHT: 350,
        DEFAULT_COLORS: [
            '#3b82f6', '#8b5cf6', '#ef4444', '#10b981', 
            '#f59e0b', '#06b6d4', '#6b7280'
        ],
        ANIMATION_DURATION: 750
    },
    
    // Timeframe Options
    TIMEFRAMES: [
        { value: '3months', label: 'Last 3 Months' },
        { value: '6months', label: 'Last 6 Months' },
        { value: '12months', label: 'Last 12 Months' },
        { value: '24months', label: 'Last 24 Months' }
    ],
    
    // Error Messages
    ERRORS: {
        NETWORK: 'Network error - please check your connection',
        TIMEOUT: 'Request timeout - server may be busy',
        SERVER: 'Server error - please try again later',
        VALIDATION: 'Invalid input - please check your data',
        NOT_FOUND: 'Resource not found',
        UNAUTHORIZED: 'Access denied - please check permissions'
    },
    
    // Success Messages
    SUCCESS: {
        DATA_LOADED: 'Data loaded successfully',
        SEARCH_COMPLETE: 'Search completed',
        EXPORT_COMPLETE: 'Export completed successfully',
        PREFERENCES_SAVED: 'Preferences saved',
        CACHE_CLEARED: 'Cache cleared successfully'
    },
    
    // Local Storage Keys
    STORAGE_KEYS: {
        USER_PREFERENCES: 'tenderintel_user',
        CACHE: 'tenderintel_cache',
        NOTIFICATIONS: 'tenderintel_notifications',
        SAVED_SEARCHES: 'tenderintel_searches',
        THEME: 'tenderintel_theme'
    },
    
    // Feature Flags
    FEATURES: {
        REAL_TIME_UPDATES: true,
        ADVANCED_EXPORT: true,
        COLLABORATION: false, // Not implemented yet
        USER_MANAGEMENT: false, // Not implemented yet
        AUDIT_LOGGING: false   // Not implemented yet
    },
    
    // Pagination Configuration
    PAGINATION: {
        DEFAULT_PAGE_SIZE: 25,
        PAGE_SIZE_OPTIONS: [10, 25, 50, 100],
        MAX_VISIBLE_PAGES: 5
    },
    
    // Notification Configuration
    NOTIFICATION: {
        MAX_QUEUE_SIZE: 50,
        AUTO_DISMISS_DURATION: 5000,
        PERSISTENCE_DAYS: 7
    },
    
    // Cache Configuration
    CACHE: {
        MAX_SIZE: 100,
        DEFAULT_TTL: 5 * 60 * 1000, // 5 minutes
        LONG_TTL: 30 * 60 * 1000,   // 30 minutes
        SHORT_TTL: 1 * 60 * 1000    // 1 minute
    }
};

// Make constants globally available
window.constants = constants;

// Freeze constants to prevent accidental modification
Object.freeze(window.constants);

console.log('✅ TenderIntel Constants loaded successfully');
