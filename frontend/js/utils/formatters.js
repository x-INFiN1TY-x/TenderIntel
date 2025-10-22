/**
 * TenderIntel - Data Formatters
 * Utility functions for formatting data for display
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

const formatters = {
    /**
     * Currency formatting for Indian market
     * Uses Lakh/Crore notation for large values
     * @param {number} value - Amount in INR
     * @param {number} decimals - Decimal places (default: 1)
     * @param {boolean} showSymbol - Show ₹ symbol (default: true)
     * @returns {string} Formatted currency string
     */
    currency(value, decimals = 1, showSymbol = true) {
        if (!value && value !== 0) return showSymbol ? '₹0' : '0';
        
        const absValue = Math.abs(value);
        let formatted = '';
        
        if (absValue >= 10000000) { // 1 Crore or more
            formatted = `${(absValue / 10000000).toFixed(decimals)} Cr`;
        } else if (absValue >= 100000) { // 1 Lakh or more
            formatted = `${(absValue / 100000).toFixed(decimals)} L`;
        } else if (absValue >= 1000) { // 1 Thousand or more
            formatted = `${(absValue / 1000).toFixed(decimals)} K`;
        } else {
            formatted = absValue.toLocaleString('en-IN', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });
        }
        
        const sign = value < 0 ? '-' : '';
        return showSymbol ? `${sign}₹${formatted}` : `${sign}${formatted}`;
    },
    
    /**
     * Number formatting with Indian number system
     * @param {number} value - Number to format
     * @param {number} decimals - Decimal places (default: 0)
     * @returns {string} Formatted number string
     */
    number(value, decimals = 0) {
        if (!value && value !== 0) return '0';
        return value.toLocaleString('en-IN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },
    
    /**
     * Percentage formatting
     * @param {number} value - Percentage value
     * @param {number} decimals - Decimal places (default: 1)
     * @returns {string} Formatted percentage string
     */
    percent(value, decimals = 1) {
        if (!value && value !== 0) return '0%';
        return `${value.toFixed(decimals)}%`;
    },
    
    /**
     * Date formatting with multiple format options
     * @param {string|Date} dateString - Date to format
     * @param {string} format - Format type: 'short', 'long', 'relative'
     * @returns {string} Formatted date string
     */
    date(dateString, format = 'short') {
        if (!dateString) return '-';
        const date = new Date(dateString);
        
        if (isNaN(date.getTime())) return '-';
        
        switch (format) {
            case 'short':
                return date.toLocaleDateString('en-IN', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            case 'long':
                return date.toLocaleDateString('en-IN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    weekday: 'long'
                });
            case 'relative':
                return this.relativeTime(dateString);
            case 'time':
                return date.toLocaleTimeString('en-IN', {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            case 'datetime':
                return date.toLocaleString('en-IN', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            default:
                return date.toLocaleDateString('en-IN');
        }
    },
    
    /**
     * Relative time formatting (e.g., "2 hours ago")
     * @param {string|Date} dateString - Date to format
     * @returns {string} Relative time string
     */
    relativeTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        if (isNaN(date.getTime()) || diff < 0) return this.date(dateString, 'short');
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        const months = Math.floor(days / 30);
        const years = Math.floor(days / 365);
        
        if (years > 0) return `${years} year${years > 1 ? 's' : ''} ago`;
        if (months > 0) return `${months} month${months > 1 ? 's' : ''} ago`;
        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        if (seconds > 30) return `${seconds} seconds ago`;
        return 'Just now';
    },
    
    /**
     * Text truncation with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} length - Maximum length (default: 50)
     * @param {string} suffix - Suffix to add (default: '...')
     * @returns {string} Truncated text
     */
    truncate(text, length = 50, suffix = '...') {
        if (!text) return '';
        if (text.length <= length) return text;
        return text.substring(0, length - suffix.length) + suffix;
    },
    
    /**
     * Title case formatting
     * @param {string} text - Text to format
     * @returns {string} Title cased text
     */
    titleCase(text) {
        if (!text) return '';
        return text.replace(/\w\S*/g, (txt) =>
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        );
    },
    
    /**
     * Market structure classification based on HHI
     * @param {number} hhi - Herfindahl-Hirschman Index (0-1)
     * @returns {string} Market structure description
     */
    marketStructure(hhi) {
        if (!hhi && hhi !== 0) return 'Unknown';
        
        const thresholds = window.constants?.BUSINESS?.MARKET_CONCENTRATION || {
            HIGHLY_COMPETITIVE: 0.10,
            COMPETITIVE: 0.15,
            MODERATELY_CONCENTRATED: 0.25
        };
        
        if (hhi > thresholds.MODERATELY_CONCENTRATED) return 'Highly Concentrated';
        if (hhi > thresholds.COMPETITIVE) return 'Moderately Concentrated';
        if (hhi > thresholds.HIGHLY_COMPETITIVE) return 'Competitive';
        return 'Highly Competitive';
    },
    
    /**
     * Deal size classification
     * @param {number} value - Deal value in INR
     * @returns {string} Deal size category
     */
    dealSizeCategory(value) {
        if (!value) return 'Unknown';
        
        const sizes = window.constants?.BUSINESS?.DEAL_SIZES || {
            MEGA: { min: 100000000 },
            LARGE: { min: 50000000 },
            MEDIUM: { min: 10000000 },
            SMALL: { min: 1000000 }
        };
        
        if (value >= sizes.MEGA.min) return 'Mega Deal'; // ≥₹10Cr
        if (value >= sizes.LARGE.min) return 'Large Deal';  // ≥₹5Cr
        if (value >= sizes.MEDIUM.min) return 'Medium Deal'; // ≥₹1Cr
        if (value >= sizes.SMALL.min) return 'Small Deal';   // ≥₹10L
        return 'Micro Deal';
    },
    
    /**
     * Competitive position formatting with styling
     * @param {string} position - Position code
     * @returns {object} Position metadata
     */
    competitivePosition(position) {
        const positions = {
            'market_leader': { text: 'Market Leader', color: 'text-green-600', icon: '👑', bgColor: 'bg-green-50' },
            'strong_competitor': { text: 'Strong Competitor', color: 'text-blue-600', icon: '💪', bgColor: 'bg-blue-50' },
            'niche_player': { text: 'Niche Player', color: 'text-purple-600', icon: '🎯', bgColor: 'bg-purple-50' },
            'emerging': { text: 'Emerging', color: 'text-yellow-600', icon: '⭐', bgColor: 'bg-yellow-50' },
            'declining': { text: 'Declining', color: 'text-red-600', icon: '📉', bgColor: 'bg-red-50' }
        };
        
        return positions[position] || { 
            text: position || 'Unknown', 
            color: 'text-gray-600', 
            icon: '❓', 
            bgColor: 'bg-gray-50' 
        };
    },
    
    /**
     * Format file size
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    fileSize(bytes) {
        if (!bytes && bytes !== 0) return '0 B';
        
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
    },
    
    /**
     * Format duration in milliseconds to human readable
     * @param {number} ms - Duration in milliseconds
     * @returns {string} Formatted duration
     */
    duration(ms) {
        if (!ms && ms !== 0) return '0ms';
        
        if (ms < 1000) return `${ms}ms`;
        if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
        if (ms < 3600000) return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
        
        const hours = Math.floor(ms / 3600000);
        const minutes = Math.floor((ms % 3600000) / 60000);
        return `${hours}h ${minutes}m`;
    },
    
    /**
     * Format score/similarity percentage
     * @param {number} score - Score value (0-100)
     * @returns {string} Formatted score with badge color
     */
    scoreWithBadge(score) {
        if (!score && score !== 0) return { text: '0%', class: 'bg-gray-100 text-gray-600' };
        
        const rounded = Math.round(score);
        let badgeClass;
        
        if (rounded >= 80) badgeClass = 'bg-green-100 text-green-700';
        else if (rounded >= 60) badgeClass = 'bg-blue-100 text-blue-700';
        else if (rounded >= 40) badgeClass = 'bg-yellow-100 text-yellow-700';
        else badgeClass = 'bg-red-100 text-red-700';
        
        return {
            text: `${rounded}%`,
            class: badgeClass,
            value: rounded
        };
    },
    
    /**
     * Format array to comma-separated list
     * @param {Array} arr - Array to format
     * @param {number} maxItems - Maximum items to show before truncating
     * @returns {string} Formatted list
     */
    list(arr, maxItems = 3) {
        if (!Array.isArray(arr) || arr.length === 0) return '-';
        
        if (arr.length <= maxItems) {
            return arr.join(', ');
        }
        
        const visible = arr.slice(0, maxItems).join(', ');
        const remaining = arr.length - maxItems;
        return `${visible}, +${remaining} more`;
    },
    
    /**
     * Format URL to display hostname only
     * @param {string} url - URL to format
     * @returns {string} Hostname or truncated URL
     */
    urlDisplay(url) {
        if (!url) return '-';
        
        try {
            const urlObj = new URL(url);
            return urlObj.hostname;
        } catch {
            return this.truncate(url, 30);
        }
    },
    
    /**
     * Pluralize word based on count
     * @param {number} count - Count value
     * @param {string} singular - Singular form
     * @param {string} plural - Plural form (optional, adds 's' if not provided)
     * @returns {string} Pluralized string
     */
    pluralize(count, singular, plural = null) {
        if (!plural) plural = singular + 's';
        return count === 1 ? singular : plural;
    },
    
    /**
     * Format growth rate with indicator
     * @param {number} rate - Growth rate percentage
     * @returns {object} Growth rate metadata
     */
    growthRate(rate) {
        if (!rate && rate !== 0) return { text: '0%', color: 'text-gray-600', icon: '→', trend: 'stable' };
        
        const absRate = Math.abs(rate);
        const icon = rate > 0 ? '↗' : rate < 0 ? '↘' : '→';
        const color = rate > 0 ? 'text-success-600' : rate < 0 ? 'text-danger-600' : 'text-gray-600';
        const trend = rate > 5 ? 'strong_growth' : rate > 0 ? 'growth' : rate < -5 ? 'strong_decline' : rate < 0 ? 'decline' : 'stable';
        
        return {
            text: `${rate > 0 ? '+' : ''}${rate.toFixed(1)}%`,
            color,
            icon,
            trend,
            value: rate
        };
    },
    
    /**
     * Format tender status with badge styling
     * @param {string} status - Status code
     * @returns {object} Status metadata
     */
    tenderStatus(status) {
        const statuses = {
            'published_aoc': { text: 'Published AOC', class: 'bg-green-100 text-green-700', icon: '✓' },
            'live': { text: 'Live Tender', class: 'bg-blue-100 text-blue-700', icon: '🔵' },
            'closed': { text: 'Closed', class: 'bg-gray-100 text-gray-700', icon: '🔒' },
            'cancelled': { text: 'Cancelled', class: 'bg-red-100 text-red-700', icon: '✕' },
            'draft': { text: 'Draft', class: 'bg-yellow-100 text-yellow-700', icon: '📝' }
        };
        
        const normalized = status?.toLowerCase().replace(/\s+/g, '_') || 'unknown';
        return statuses[normalized] || { 
            text: status || 'Unknown', 
            class: 'bg-gray-100 text-gray-600', 
            icon: '?' 
        };
    },
    
    /**
     * Format phone number (Indian format)
     * @param {string} phone - Phone number
     * @returns {string} Formatted phone number
     */
    phone(phone) {
        if (!phone) return '-';
        
        const cleaned = phone.replace(/\D/g, '');
        
        if (cleaned.length === 10) {
            return `${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
        } else if (cleaned.length === 11) {
            return `${cleaned.slice(0, 1)}-${cleaned.slice(1, 6)}-${cleaned.slice(6)}`;
        }
        
        return phone;
    },
    
    /**
     * Format coordinates for display
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     * @returns {string} Formatted coordinates
     */
    coordinates(lat, lng) {
        if (!lat || !lng) return '-';
        return `${lat.toFixed(4)}°, ${lng.toFixed(4)}°`;
    },
    
    /**
     * Format boolean to Yes/No
     * @param {boolean} value - Boolean value
     * @returns {string} Yes or No
     */
    yesNo(value) {
        return value ? 'Yes' : 'No';
    },
    
    /**
     * Format object to readable JSON
     * @param {object} obj - Object to format
     * @param {number} indent - Indentation spaces (default: 2)
     * @returns {string} Formatted JSON string
     */
    json(obj, indent = 2) {
        if (!obj) return '';
        try {
            return JSON.stringify(obj, null, indent);
        } catch {
            return String(obj);
        }
    }
};

// Make formatters globally available
window.formatters = formatters;

// Freeze formatters to prevent accidental modification
Object.freeze(window.formatters);

console.log('✅ TenderIntel Formatters loaded successfully');
