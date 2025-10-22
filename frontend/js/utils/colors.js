/**
 * TenderIntel - Color Utilities
 * Color scale generators and utilities for visualizations
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

const colorUtils = {
    /**
     * Color scale for heatmap visualizations
     * Uses red-yellow-green gradient for performance metrics
     * @param {number} value - Value to color
     * @param {number} min - Minimum value in dataset
     * @param {number} max - Maximum value in dataset
     * @param {number} opacity - Color opacity (0-1)
     * @returns {string} RGBA color string
     */
    getHeatmapColor(value, min = 0, max = 100, opacity = 0.8) {
        if (!value && value !== 0) return `rgba(156, 163, 175, 0.1)`; // Gray for no data
        
        // Normalize value to 0-1 range
        const normalized = Math.max(0, Math.min(1, (value - min) / (max - min)));
        
        // Use a red-yellow-green color scale
        const colors = [
            { r: 239, g: 68, b: 68 },   // Red (low performance)
            { r: 251, g: 191, b: 36 },  // Yellow (medium)
            { r: 34, g: 197, b: 94 }    // Green (high performance)
        ];
        
        let color;
        if (normalized <= 0.5) {
            // Interpolate between red and yellow
            const t = normalized * 2;
            color = {
                r: Math.round(colors[0].r + (colors[1].r - colors[0].r) * t),
                g: Math.round(colors[0].g + (colors[1].g - colors[0].g) * t),
                b: Math.round(colors[0].b + (colors[1].b - colors[0].b) * t)
            };
        } else {
            // Interpolate between yellow and green
            const t = (normalized - 0.5) * 2;
            color = {
                r: Math.round(colors[1].r + (colors[2].r - colors[1].r) * t),
                g: Math.round(colors[1].g + (colors[2].g - colors[1].g) * t),
                b: Math.round(colors[1].b + (colors[2].b - colors[1].b) * t)
            };
        }
        
        return `rgba(${color.r}, ${color.g}, ${color.b}, ${opacity})`;
    },
    
    /**
     * Color for geographic choropleth maps
     * Uses yellow-orange-red scale for procurement density
     * @param {number} density - Procurement density value (0-100)
     * @param {number} opacity - Color opacity (0-1)
     * @returns {string} RGBA color string
     */
    getGeographicColor(density, opacity = 0.7) {
        if (!density && density !== 0) return `rgba(156, 163, 175, 0.1)`; // Gray for no data
        
        // Use a scale from light yellow to dark red for procurement density
        if (density > 80) return `rgba(128, 0, 38, ${opacity})`;    // Dark red - Very high
        if (density > 60) return `rgba(189, 0, 38, ${opacity})`;    // Red - High
        if (density > 40) return `rgba(227, 26, 28, ${opacity})`;   // Light red - Medium-high
        if (density > 20) return `rgba(252, 78, 42, ${opacity})`;   // Orange - Medium
        if (density > 10) return `rgba(253, 141, 60, ${opacity})`;  // Light orange - Medium-low
        if (density > 5) return `rgba(254, 178, 76, ${opacity})`;   // Yellow-orange - Low
        if (density > 0) return `rgba(254, 217, 118, ${opacity})`;  // Yellow - Very low
        return `rgba(255, 255, 204, ${opacity})`;                   // Very light yellow - Minimal
    },
    
    /**
     * Service category color mapping
     * Returns consistent colors for service categories
     * @param {string} category - Service category name
     * @returns {string} Hex color code
     */
    getServiceCategoryColor(category) {
        const colors = {
            'cloud': '#3b82f6',      // Blue
            'networking': '#8b5cf6', // Purple
            'security': '#ef4444',   // Red
            'database': '#10b981',   // Green
            'software': '#f59e0b',   // Orange
            'integration': '#06b6d4', // Cyan
            'hardware': '#6b7280'    // Gray
        };
        
        return colors[category?.toLowerCase()] || '#6b7280';
    },
    
    /**
     * Performance-based color scale
     * @param {number} percentage - Performance percentage (0-100)
     * @param {number} opacity - Color opacity (0-1)
     * @returns {string} RGBA color string
     */
    getPerformanceColor(percentage, opacity = 1) {
        if (percentage >= 80) return `rgba(34, 197, 94, ${opacity})`;   // Green - Excellent
        if (percentage >= 60) return `rgba(168, 85, 247, ${opacity})`;  // Purple - Good
        if (percentage >= 40) return `rgba(59, 130, 246, ${opacity})`;  // Blue - Average
        if (percentage >= 20) return `rgba(251, 191, 36, ${opacity})`;  // Yellow - Below average
        return `rgba(239, 68, 68, ${opacity})`;                        // Red - Poor
    },
    
    /**
     * Generate color palette for charts
     * @param {number} count - Number of colors needed
     * @returns {Array<string>} Array of hex color codes
     */
    generateChartPalette(count) {
        const baseColors = [
            '#3b82f6', '#8b5cf6', '#ef4444', '#10b981', 
            '#f59e0b', '#06b6d4', '#6b7280', '#ec4899',
            '#14b8a6', '#f43f5e', '#8b5cf6', '#6366f1'
        ];
        
        if (count <= baseColors.length) {
            return baseColors.slice(0, count);
        }
        
        // Generate additional colors by lightening/darkening base colors
        const extended = [...baseColors];
        while (extended.length < count) {
            const baseIndex = extended.length % baseColors.length;
            const lighten = Math.floor(extended.length / baseColors.length) % 2 === 0;
            extended.push(this.adjustColorBrightness(baseColors[baseIndex], lighten ? 20 : -20));
        }
        
        return extended.slice(0, count);
    },
    
    /**
     * Adjust color brightness
     * @param {string} hexColor - Hex color code
     * @param {number} percent - Adjustment percentage (-100 to 100)
     * @returns {string} Adjusted hex color code
     */
    adjustColorBrightness(hexColor, percent) {
        const num = parseInt(hexColor.replace('#', ''), 16);
        const amt = Math.round(2.55 * percent);
        const R = Math.min(255, Math.max(0, (num >> 16) + amt));
        const G = Math.min(255, Math.max(0, (num >> 8 & 0x00FF) + amt));
        const B = Math.min(255, Math.max(0, (num & 0x0000FF) + amt));
        
        return '#' + (0x1000000 + (R << 16) + (G << 8) + B).toString(16).slice(1);
    },
    
    /**
     * Convert hex color to RGB
     * @param {string} hex - Hex color code
     * @returns {object} RGB object {r, g, b}
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    },
    
    /**
     * Convert RGB to hex color
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {string} Hex color code
     */
    rgbToHex(r, g, b) {
        return '#' + [r, g, b].map(x => {
            const hex = Math.round(x).toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');
    },
    
    /**
     * Get contrasting text color for background
     * @param {string} bgColor - Background color (hex)
     * @returns {string} Black or white hex color
     */
    getContrastingTextColor(bgColor) {
        const rgb = this.hexToRgb(bgColor);
        if (!rgb) return '#000000';
        
        // Calculate luminance
        const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
        
        // Return black for light backgrounds, white for dark backgrounds
        return luminance > 0.5 ? '#000000' : '#FFFFFF';
    },
    
    /**
     * Generate gradient stops for linear gradients
     * @param {string} startColor - Start color (hex)
     * @param {string} endColor - End color (hex)
     * @param {number} steps - Number of gradient steps
     * @returns {Array<string>} Array of hex color codes
     */
    generateGradient(startColor, endColor, steps) {
        const start = this.hexToRgb(startColor);
        const end = this.hexToRgb(endColor);
        
        if (!start || !end) return [startColor, endColor];
        
        const gradient = [];
        
        for (let i = 0; i < steps; i++) {
            const ratio = i / (steps - 1);
            const r = start.r + (end.r - start.r) * ratio;
            const g = start.g + (end.g - start.g) * ratio;
            const b = start.b + (end.b - start.b) * ratio;
            
            gradient.push(this.rgbToHex(r, g, b));
        }
        
        return gradient;
    },
    
    /**
     * Get color from performance scale
     * @param {number} value - Performance value (0-100)
     * @returns {string} Hex color code
     */
    getPerformanceScaleColor(value) {
        const scale = window.constants?.COLORS?.PERFORMANCE_SCALE || [
            { min: 0, max: 20, color: '#ef4444' },
            { min: 20, max: 40, color: '#f59e0b' },
            { min: 40, max: 60, color: '#3b82f6' },
            { min: 60, max: 80, color: '#8b5cf6' },
            { min: 80, max: 100, color: '#10b981' }
        ];
        
        for (const range of scale) {
            if (value >= range.min && value < range.max) {
                return range.color;
            }
        }
        
        // Return last color for values >= 100
        return scale[scale.length - 1].color;
    },
    
    /**
     * Apply alpha to hex color
     * @param {string} hexColor - Hex color code
     * @param {number} alpha - Alpha value (0-1)
     * @returns {string} RGBA color string
     */
    applyAlpha(hexColor, alpha) {
        const rgb = this.hexToRgb(hexColor);
        if (!rgb) return hexColor;
        
        return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
    },
    
    /**
     * Get trend color based on direction and magnitude
     * @param {number} value - Trend value (can be negative)
     * @param {number} threshold - Significance threshold (default: 5)
     * @returns {string} Hex color code
     */
    getTrendColor(value, threshold = 5) {
        if (!value && value !== 0) return '#6b7280'; // Gray - no data
        
        if (value > threshold) return '#10b981';      // Green - strong positive
        if (value > 0) return '#3b82f6';              // Blue - slight positive
        if (value > -threshold) return '#f59e0b';     // Yellow - slight negative
        return '#ef4444';                             // Red - strong negative
    }
};

// Make color utilities globally available
window.colorUtils = colorUtils;

// Freeze to prevent accidental modification
Object.freeze(window.colorUtils);

console.log('✅ TenderIntel Color Utilities loaded successfully');
