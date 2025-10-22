/**
 * TenderIntel - Input Validation Utilities
 * Validates user inputs and API responses for security and data integrity
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

const validators = {
    /**
     * Validate keyword search input
     * @param {string} value - Keyword to validate
     * @returns {object} Validation result {valid, error?, value?}
     */
    keyword(value) {
        if (!value || typeof value !== 'string') {
            return { valid: false, error: 'Keyword is required' };
        }
        
        const trimmed = value.trim();
        
        if (trimmed.length < 1) {
            return { valid: false, error: 'Keyword must be at least 1 character' };
        }
        
        if (trimmed.length > 200) {
            return { valid: false, error: 'Keyword must be less than 200 characters' };
        }
        
        // Check for SQL injection patterns (basic security)
        const sqlPattern = /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|SCRIPT)\b)/i;
        if (sqlPattern.test(trimmed)) {
            return { valid: false, error: 'Invalid characters detected in keyword' };
        }
        
        // Check for XSS patterns
        const xssPattern = /<script|javascript:|onerror=|onclick=/i;
        if (xssPattern.test(trimmed)) {
            return { valid: false, error: 'Invalid characters detected in keyword' };
        }
        
        return { valid: true, value: trimmed };
    },
    
    /**
     * Validate date range
     * @param {string} startDate - Start date (ISO format)
     * @param {string} endDate - End date (ISO format)
     * @returns {object} Validation result
     */
    dateRange(startDate, endDate) {
        if (!startDate || !endDate) {
            return { valid: true }; // Optional dates - no validation needed
        }
        
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (isNaN(start.getTime())) {
            return { valid: false, error: 'Invalid start date format' };
        }
        
        if (isNaN(end.getTime())) {
            return { valid: false, error: 'Invalid end date format' };
        }
        
        if (start > end) {
            return { valid: false, error: 'Start date must be before end date' };
        }
        
        // Check if range is reasonable (not more than 10 years)
        const maxRange = 10 * 365 * 24 * 60 * 60 * 1000;
        if (end - start > maxRange) {
            return { valid: false, error: 'Date range cannot exceed 10 years' };
        }
        
        // Check if dates are not in the far future
        const oneYearFromNow = new Date();
        oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);
        
        if (end > oneYearFromNow) {
            return { valid: false, error: 'End date cannot be more than 1 year in the future' };
        }
        
        return { 
            valid: true, 
            startDate: start.toISOString().split('T')[0], 
            endDate: end.toISOString().split('T')[0]
        };
    },
    
    /**
     * Validate currency amount
     * @param {number} value - Amount to validate
     * @param {number} min - Minimum allowed value
     * @param {number} max - Maximum allowed value
     * @returns {object} Validation result
     */
    currencyAmount(value, min = 0, max = 1000000000000) {
        if (value === null || value === undefined || value === '') {
            return { valid: false, error: 'Amount is required' };
        }
        
        const numValue = parseFloat(value);
        
        if (isNaN(numValue)) {
            return { valid: false, error: 'Amount must be a valid number' };
        }
        
        if (numValue < min) {
            return { 
                valid: false, 
                error: `Amount must be at least ${window.formatters?.currency(min) || min}` 
            };
        }
        
        if (numValue > max) {
            return { 
                valid: false, 
                error: `Amount cannot exceed ${window.formatters?.currency(max) || max}` 
            };
        }
        
        return { valid: true, value: numValue };
    },
    
    /**
     * Validate percentage value
     * @param {number} value - Percentage to validate
     * @param {number} min - Minimum allowed percentage
     * @param {number} max - Maximum allowed percentage
     * @returns {object} Validation result
     */
    percentage(value, min = 0, max = 100) {
        if (value === null || value === undefined || value === '') {
            return { valid: false, error: 'Percentage is required' };
        }
        
        const numValue = parseFloat(value);
        
        if (isNaN(numValue)) {
            return { valid: false, error: 'Percentage must be a valid number' };
        }
        
        if (numValue < min) {
            return { valid: false, error: `Percentage must be at least ${min}%` };
        }
        
        if (numValue > max) {
            return { valid: false, error: `Percentage cannot exceed ${max}%` };
        }
        
        return { valid: true, value: numValue };
    },
    
    /**
     * Validate firm name
     * @param {string} value - Firm name to validate
     * @returns {object} Validation result
     */
    firmName(value) {
        if (!value || typeof value !== 'string') {
            return { valid: false, error: 'Firm name is required' };
        }
        
        const trimmed = value.trim();
        
        if (trimmed.length < 2) {
            return { valid: false, error: 'Firm name must be at least 2 characters' };
        }
        
        if (trimmed.length > 100) {
            return { valid: false, error: 'Firm name must be less than 100 characters' };
        }
        
        // Check for suspicious patterns
        const suspiciousPattern = /<script|javascript:|onerror=/i;
        if (suspiciousPattern.test(trimmed)) {
            return { valid: false, error: 'Invalid characters in firm name' };
        }
        
        return { valid: true, value: trimmed };
    },
    
    /**
     * Validate service category
     * @param {string} value - Service category to validate
     * @returns {object} Validation result
     */
    serviceCategory(value) {
        const validCategories = [
            'cloud', 'networking', 'database', 'software', 
            'integration', 'security', 'hardware'
        ];
        
        if (!value) {
            return { valid: false, error: 'Service category is required' };
        }
        
        const normalized = value.toLowerCase().trim();
        
        if (!validCategories.includes(normalized)) {
            return { 
                valid: false, 
                error: `Invalid service category. Must be one of: ${validCategories.join(', ')}` 
            };
        }
        
        return { valid: true, value: normalized };
    },
    
    /**
     * Validate API response structure
     * @param {object} response - API response to validate
     * @returns {object} Validation result
     */
    apiResponse(response) {
        if (!response) {
            return { valid: false, error: 'Empty API response received' };
        }
        
        if (typeof response !== 'object') {
            return { valid: false, error: 'API response must be an object' };
        }
        
        if (response.error) {
            return { valid: false, error: response.error };
        }
        
        return { valid: true, value: response };
    },
    
    /**
     * Validate array input
     * @param {Array} value - Array to validate
     * @param {number} minLength - Minimum array length
     * @param {number} maxLength - Maximum array length
     * @returns {object} Validation result
     */
    arrayInput(value, minLength = 0, maxLength = 100) {
        if (!Array.isArray(value)) {
            return { valid: false, error: 'Value must be an array' };
        }
        
        if (value.length < minLength) {
            return { valid: false, error: `Array must have at least ${minLength} item${minLength !== 1 ? 's' : ''}` };
        }
        
        if (value.length > maxLength) {
            return { valid: false, error: `Array cannot have more than ${maxLength} items` };
        }
        
        return { valid: true, value };
    },
    
    /**
     * Validate search filters object
     * @param {object} filters - Filters object to validate
     * @returns {object} Validation result with validated filters
     */
    searchFilters(filters) {
        const validatedFilters = {};
        const errors = [];
        
        // Validate date range if provided
        if (filters.dateFrom || filters.dateTo) {
            const dateValidation = this.dateRange(filters.dateFrom, filters.dateTo);
            if (!dateValidation.valid) {
                errors.push(dateValidation.error);
            } else if (dateValidation.startDate && dateValidation.endDate) {
                validatedFilters.dateFrom = dateValidation.startDate;
                validatedFilters.dateTo = dateValidation.endDate;
            }
        }
        
        // Validate service categories array
        if (filters.serviceCategories) {
            const arrayValidation = this.arrayInput(filters.serviceCategories, 0, 10);
            if (!arrayValidation.valid) {
                errors.push(arrayValidation.error);
            } else {
                // Validate each category
                const validCategories = [];
                filters.serviceCategories.forEach(cat => {
                    const catValidation = this.serviceCategory(cat);
                    if (catValidation.valid) {
                        validCategories.push(catValidation.value);
                    }
                });
                if (validCategories.length > 0) {
                    validatedFilters.serviceCategories = validCategories;
                }
            }
        }
        
        // Validate organizations array
        if (filters.organizations) {
            const arrayValidation = this.arrayInput(filters.organizations, 0, 20);
            if (!arrayValidation.valid) {
                errors.push(arrayValidation.error);
            } else {
                validatedFilters.organizations = arrayValidation.value;
            }
        }
        
        // Validate value ranges array
        if (filters.valueRanges) {
            const arrayValidation = this.arrayInput(filters.valueRanges, 0, 10);
            if (!arrayValidation.valid) {
                errors.push(arrayValidation.error);
            } else {
                validatedFilters.valueRanges = arrayValidation.value;
            }
        }
        
        // Validate regions array
        if (filters.regions) {
            const arrayValidation = this.arrayInput(filters.regions, 0, 10);
            if (!arrayValidation.valid) {
                errors.push(arrayValidation.error);
            } else {
                validatedFilters.regions = arrayValidation.value;
            }
        }
        
        // Validate minimum similarity percentage
        if (filters.minSimilarity !== undefined && filters.minSimilarity !== null) {
            const percentValidation = this.percentage(filters.minSimilarity, 0, 100);
            if (!percentValidation.valid) {
                errors.push(percentValidation.error);
            } else {
                validatedFilters.minSimilarity = percentValidation.value;
            }
        }
        
        return {
            valid: errors.length === 0,
            errors: errors,
            value: validatedFilters
        };
    },
    
    /**
     * Validate email address
     * @param {string} email - Email to validate
     * @returns {object} Validation result
     */
    email(email) {
        if (!email || typeof email !== 'string') {
            return { valid: false, error: 'Email is required' };
        }
        
        const trimmed = email.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailPattern.test(trimmed)) {
            return { valid: false, error: 'Invalid email format' };
        }
        
        if (trimmed.length > 254) {
            return { valid: false, error: 'Email is too long' };
        }
        
        return { valid: true, value: trimmed.toLowerCase() };
    },
    
    /**
     * Validate URL
     * @param {string} url - URL to validate
     * @returns {object} Validation result
     */
    url(url) {
        if (!url || typeof url !== 'string') {
            return { valid: false, error: 'URL is required' };
        }
        
        try {
            const urlObj = new URL(url);
            
            // Only allow http and https protocols
            if (!['http:', 'https:'].includes(urlObj.protocol)) {
                return { valid: false, error: 'URL must use HTTP or HTTPS protocol' };
            }
            
            return { valid: true, value: url.trim() };
            
        } catch {
            return { valid: false, error: 'Invalid URL format' };
        }
    },
    
    /**
     * Validate number within range
     * @param {number} value - Number to validate
     * @param {number} min - Minimum allowed value
     * @param {number} max - Maximum allowed value
     * @param {string} fieldName - Field name for error messages
     * @returns {object} Validation result
     */
    numberRange(value, min, max, fieldName = 'Value') {
        if (value === null || value === undefined || value === '') {
            return { valid: false, error: `${fieldName} is required` };
        }
        
        const numValue = parseFloat(value);
        
        if (isNaN(numValue)) {
            return { valid: false, error: `${fieldName} must be a valid number` };
        }
        
        if (numValue < min) {
            return { valid: false, error: `${fieldName} must be at least ${min}` };
        }
        
        if (numValue > max) {
            return { valid: false, error: `${fieldName} cannot exceed ${max}` };
        }
        
        return { valid: true, value: numValue };
    },
    
    /**
     * Validate required field
     * @param {any} value - Value to validate
     * @param {string} fieldName - Field name for error messages
     * @returns {object} Validation result
     */
    required(value, fieldName = 'Field') {
        if (value === null || value === undefined || value === '') {
            return { valid: false, error: `${fieldName} is required` };
        }
        
        if (typeof value === 'string' && value.trim().length === 0) {
            return { valid: false, error: `${fieldName} cannot be empty` };
        }
        
        return { valid: true, value };
    },
    
    /**
     * Validate pagination parameters
     * @param {number} page - Page number
     * @param {number} pageSize - Page size
     * @returns {object} Validation result
     */
    pagination(page, pageSize) {
        const errors = [];
        
        // Validate page number
        if (page !== null && page !== undefined) {
            const pageNum = parseInt(page);
            if (isNaN(pageNum) || pageNum < 1) {
                errors.push('Page number must be at least 1');
            }
        }
        
        // Validate page size
        if (pageSize !== null && pageSize !== undefined) {
            const size = parseInt(pageSize);
            const maxSize = window.constants?.UI?.MAX_SEARCH_RESULTS || 100;
            
            if (isNaN(size) || size < 1) {
                errors.push('Page size must be at least 1');
            } else if (size > maxSize) {
                errors.push(`Page size cannot exceed ${maxSize}`);
            }
        }
        
        return {
            valid: errors.length === 0,
            errors: errors,
            value: {
                page: parseInt(page) || 1,
                pageSize: parseInt(pageSize) || 25
            }
        };
    },
    
    /**
     * Validate timeframe option
     * @param {string} timeframe - Timeframe value
     * @returns {object} Validation result
     */
    timeframe(timeframe) {
        const validTimeframes = ['3months', '6months', '12months', '24months'];
        
        if (!timeframe) {
            return { valid: false, error: 'Timeframe is required' };
        }
        
        if (!validTimeframes.includes(timeframe)) {
            return { 
                valid: false, 
                error: `Invalid timeframe. Must be one of: ${validTimeframes.join(', ')}` 
            };
        }
        
        return { valid: true, value: timeframe };
    },
    
    /**
     * Validate currency code
     * @param {string} currency - Currency code (ISO 4217)
     * @returns {object} Validation result
     */
    currencyCode(currency) {
        const supported = window.constants?.BUSINESS?.SUPPORTED_CURRENCIES || ['INR', 'USD', 'EUR', 'GBP'];
        
        if (!currency) {
            return { valid: false, error: 'Currency code is required' };
        }
        
        const upper = currency.toUpperCase();
        
        if (!supported.includes(upper)) {
            return { 
                valid: false, 
                error: `Unsupported currency. Must be one of: ${supported.join(', ')}` 
            };
        }
        
        return { valid: true, value: upper };
    },
    
    /**
     * Batch validate multiple fields
     * @param {object} values - Object with field names as keys
     * @param {object} rules - Validation rules {fieldName: validatorFunction}
     * @returns {object} Validation result with all errors
     */
    batch(values, rules) {
        const errors = {};
        const validatedValues = {};
        let isValid = true;
        
        for (const [field, validator] of Object.entries(rules)) {
            const result = validator(values[field]);
            
            if (!result.valid) {
                errors[field] = result.error;
                isValid = false;
            } else if (result.value !== undefined) {
                validatedValues[field] = result.value;
            }
        }
        
        return {
            valid: isValid,
            errors: errors,
            value: validatedValues
        };
    },
    
    /**
     * Sanitize HTML to prevent XSS
     * @param {string} html - HTML string to sanitize
     * @returns {string} Sanitized HTML
     */
    sanitizeHtml(html) {
        if (!html) return '';
        
        const tempDiv = document.createElement('div');
        tempDiv.textContent = html;
        return tempDiv.innerHTML;
    },
    
    /**
     * Validate and sanitize user input for display
     * @param {string} input - User input
     * @returns {string} Sanitized input
     */
    sanitizeInput(input) {
        if (!input || typeof input !== 'string') return '';
        
        return input
            .trim()
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;');
    }
};

// Make validators globally available
window.validators = validators;

// Freeze to prevent accidental modification
Object.freeze(window.validators);

console.log('✅ TenderIntel Validators loaded successfully');
