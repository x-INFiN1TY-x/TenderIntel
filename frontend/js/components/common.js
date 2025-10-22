/**
 * TenderIntel - Common Reusable Components
 * Shared UI components used across multiple pages
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

/**
 * Loading Spinner Component
 * @param {string} size - Size: 'small', 'medium', 'large'
 * @param {string} text - Optional loading text
 * @returns {object} Component definition
 */
function loadingSpinner(size = 'medium', text = '') {
    const sizes = {
        small: 'w-4 h-4',
        medium: 'w-8 h-8',
        large: 'w-12 h-12'
    };
    
    return {
        show: true,
        size: sizes[size] || sizes.medium,
        text,
        
        getHTML() {
            return `
                <div class="flex items-center justify-center py-8">
                    <div class="flex flex-col items-center space-y-3">
                        <div class="animate-spin rounded-full ${this.size} border-b-2 border-primary-600"></div>
                        ${this.text ? `<p class="text-sm text-gray-600">${this.text}</p>` : ''}
                    </div>
                </div>
            `;
        }
    };
}

/**
 * Empty State Component
 * @param {string} icon - Emoji icon
 * @param {string} title - Title text
 * @param {string} message - Message text
 * @param {string} actionText - Optional action button text
 * @param {function} actionCallback - Optional action callback
 * @returns {object} Component definition
 */
function emptyState(icon, title, message, actionText = null, actionCallback = null) {
    return {
        icon,
        title,
        message,
        actionText,
        actionCallback,
        
        getHTML() {
            const actionId = actionCallback ? `empty-state-action-${Date.now()}` : null;
            
            const html = `
                <div class="flex flex-col items-center justify-center py-12">
                    <div class="text-6xl mb-4">${this.icon}</div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">${this.title}</h3>
                    <p class="text-sm text-gray-600 mb-6 text-center max-w-md">${this.message}</p>
                    ${this.actionText ? `
                        <button id="${actionId}" 
                                class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
                            ${this.actionText}
                        </button>
                    ` : ''}
                </div>
            `;
            
            // Attach event listener if action provided
            if (actionId && actionCallback) {
                setTimeout(() => {
                    const btn = document.getElementById(actionId);
                    if (btn) btn.addEventListener('click', actionCallback);
                }, 0);
            }
            
            return html;
        }
    };
}

/**
 * Error Display Component
 * @param {string|Error} error - Error message or Error object
 * @param {function} retryCallback - Optional retry callback
 * @returns {object} Component definition
 */
function errorDisplay(error, retryCallback = null) {
    return {
        error: error instanceof Error ? error.message : error,
        errorDetails: error instanceof Error ? error : null,
        retry: retryCallback,
        
        getHTML() {
            const retryId = this.retry ? `error-retry-${Date.now()}` : null;
            
            const html = `
                <div class="bg-red-50 border border-red-200 rounded-lg p-6">
                    <div class="flex items-start space-x-3">
                        <div class="flex-shrink-0">
                            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                            </svg>
                        </div>
                        <div class="flex-1">
                            <h3 class="text-sm font-semibold text-red-800">Error</h3>
                            <p class="text-sm text-red-700 mt-1">${this.error}</p>
                            ${this.retry ? `
                                <button id="${retryId}" 
                                        class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm">
                                    Try Again
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
            
            // Attach retry listener
            if (retryId && this.retry) {
                setTimeout(() => {
                    const btn = document.getElementById(retryId);
                    if (btn) btn.addEventListener('click', this.retry);
                }, 0);
            }
            
            return html;
        }
    };
}

/**
 * Data Table Component
 * Alpine.js compatible data table with sorting and pagination
 * @returns {object} Alpine.js component
 */
function dataTable() {
    return {
        data: [],
        columns: [],
        sortColumn: null,
        sortDirection: 'asc',
        currentPage: 1,
        pageSize: 10,
        searchQuery: '',
        
        init(data, columns) {
            this.data = data || [];
            this.columns = columns || [];
        },
        
        get filteredData() {
            if (!this.searchQuery) return this.data;
            
            const query = this.searchQuery.toLowerCase();
            return this.data.filter(row => {
                return this.columns.some(col => {
                    const value = row[col.key]?.toString().toLowerCase() || '';
                    return value.includes(query);
                });
            });
        },
        
        get sortedData() {
            if (!this.sortColumn) return this.filteredData;
            
            return [...this.filteredData].sort((a, b) => {
                const aVal = a[this.sortColumn];
                const bVal = b[this.sortColumn];
                
                if (typeof aVal === 'number' && typeof bVal === 'number') {
                    return this.sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
                }
                
                const aStr = aVal?.toString() || '';
                const bStr = bVal?.toString() || '';
                return this.sortDirection === 'asc' ? 
                    aStr.localeCompare(bStr) : 
                    bStr.localeCompare(aStr);
            });
        },
        
        get paginatedData() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.sortedData.slice(start, end);
        },
        
        get totalPages() {
            return Math.ceil(this.sortedData.length / this.pageSize);
        },
        
        sortBy(column) {
            if (this.sortColumn === column) {
                this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortColumn = column;
                this.sortDirection = 'asc';
            }
            this.currentPage = 1;
        },
        
        goToPage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
            }
        },
        
        exportTable() {
            const exportData = this.sortedData.map(row => {
                const formatted = {};
                this.columns.forEach(col => {
                    formatted[col.label] = row[col.key];
                });
                return formatted;
            });
            
            if (window.exportService) {
                window.exportService.toCSV(exportData, 'table_export');
            }
        }
    };
}

/**
 * Modal Dialog Component
 * @returns {object} Alpine.js component
 */
function modalDialog() {
    return {
        show: false,
        title: '',
        content: '',
        confirmText: 'Confirm',
        cancelText: 'Cancel',
        onConfirm: null,
        onCancel: null,
        loading: false,
        
        open(title, content, options = {}) {
            this.title = title;
            this.content = content;
            this.confirmText = options.confirmText || 'Confirm';
            this.cancelText = options.cancelText || 'Cancel';
            this.onConfirm = options.onConfirm || null;
            this.onCancel = options.onCancel || null;
            this.show = true;
            this.loading = false;
        },
        
        close() {
            this.show = false;
            this.loading = false;
        },
        
        async confirm() {
            if (this.onConfirm) {
                this.loading = true;
                try {
                    await this.onConfirm();
                } catch (error) {
                    console.error('Modal confirm error:', error);
                } finally {
                    this.loading = false;
                }
            }
            this.close();
        },
        
        cancel() {
            if (this.onCancel) {
                this.onCancel();
            }
            this.close();
        },
        
        getHTML() {
            return `
                <div x-show="show" 
                     class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                     @click.self="cancel()">
                    <div class="bg-white rounded-lg max-w-2xl w-full mx-4 shadow-xl">
                        <div class="p-6 border-b">
                            <h3 class="text-lg font-semibold text-gray-800" x-text="title"></h3>
                        </div>
                        <div class="p-6" x-html="content"></div>
                        <div class="p-6 border-t flex justify-end space-x-3">
                            <button @click="cancel()" 
                                    :disabled="loading"
                                    class="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 transition-colors">
                                <span x-text="cancelText"></span>
                            </button>
                            <button @click="confirm()" 
                                    :disabled="loading"
                                    class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors">
                                <span x-show="!loading" x-text="confirmText"></span>
                                <span x-show="loading">Processing...</span>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
    };
}

/**
 * Tooltip Component
 * @returns {object} Alpine.js component
 */
function tooltip() {
    return {
        visible: false,
        x: 0,
        y: 0,
        content: '',
        
        show(event, content) {
            const rect = event.target.getBoundingClientRect();
            this.x = rect.left + rect.width / 2;
            this.y = rect.top + window.scrollY;
            this.content = content;
            this.visible = true;
        },
        
        hide() {
            this.visible = false;
        },
        
        getHTML() {
            return `
                <div x-show="visible" 
                     x-transition:enter="transition ease-out duration-200"
                     x-transition:enter-start="opacity-0"
                     x-transition:enter-end="opacity-100"
                     class="absolute bg-gray-800 text-white text-xs rounded-lg px-3 py-2 shadow-lg pointer-events-none z-50"
                     :style="\`left: \${x}px; top: \${y}px; transform: translate(-50%, -100%); margin-top: -8px;\`"
                     x-html="content">
                </div>
            `;
        }
    };
}

/**
 * Badge Component Generator
 * @param {string} text - Badge text
 * @param {string} variant - Badge style: 'success', 'error', 'warning', 'info', 'default'
 * @returns {string} HTML string
 */
function badge(text, variant = 'default') {
    const variants = {
        success: 'bg-green-100 text-green-700',
        error: 'bg-red-100 text-red-700',
        warning: 'bg-yellow-100 text-yellow-700',
        info: 'bg-blue-100 text-blue-700',
        default: 'bg-gray-100 text-gray-700'
    };
    
    const classes = variants[variant] || variants.default;
    
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${classes}">${text}</span>`;
}

/**
 * Progress Bar Component
 * @param {number} value - Progress value (0-100)
 * @param {string} variant - Color variant
 * @returns {string} HTML string
 */
function progressBar(value, variant = 'primary') {
    const colors = {
        primary: 'bg-primary-600',
        success: 'bg-green-600',
        warning: 'bg-yellow-600',
        danger: 'bg-red-600'
    };
    
    const color = colors[variant] || colors.primary;
    const percentage = Math.max(0, Math.min(100, value));
    
    return `
        <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div class="${color} h-2.5 rounded-full transition-all duration-300" 
                 style="width: ${percentage}%"></div>
        </div>
    `;
}

/**
 * Card Component Generator
 * @param {string} title - Card title
 * @param {string} content - Card content (HTML)
 * @param {object} options - Additional options
 * @returns {string} HTML string
 */
function card(title, content, options = {}) {
    const { 
        icon = null, 
        actions = null, 
        className = '',
        borderColor = null
    } = options;
    
    return `
        <div class="bg-white rounded-lg shadow-md hover:shadow-lg p-6 transition-shadow ${className} ${borderColor ? `border-l-4 ${borderColor}` : ''}">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-2">
                    ${icon ? `<span class="text-2xl">${icon}</span>` : ''}
                    <h3 class="text-lg font-bold text-gray-800">${title}</h3>
                </div>
                ${actions ? `<div class="flex items-center space-x-2">${actions}</div>` : ''}
            </div>
            <div>${content}</div>
        </div>
    `;
}

/**
 * Alert Component
 * @param {string} type - Alert type: 'success', 'error', 'warning', 'info'
 * @param {string} message - Alert message
 * @param {boolean} dismissible - Show dismiss button
 * @returns {object} Component definition
 */
function alert(type, message, dismissible = true) {
    const styles = {
        success: {
            bg: 'bg-green-50',
            border: 'border-green-200',
            text: 'text-green-800',
            icon: '✓'
        },
        error: {
            bg: 'bg-red-50',
            border: 'border-red-200',
            text: 'text-red-800',
            icon: '✕'
        },
        warning: {
            bg: 'bg-yellow-50',
            border: 'border-yellow-200',
            text: 'text-yellow-800',
            icon: '⚠'
        },
        info: {
            bg: 'bg-blue-50',
            border: 'border-blue-200',
            text: 'text-blue-800',
            icon: 'ℹ'
        }
    };
    
    const style = styles[type] || styles.info;
    const dismissId = dismissible ? `alert-dismiss-${Date.now()}` : null;
    
    return {
        visible: true,
        
        dismiss() {
            this.visible = false;
        },
        
        getHTML() {
            const html = `
                <div x-show="visible" 
                     class="${style.bg} ${style.border} ${style.text} border rounded-lg p-4 mb-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <span class="text-xl">${style.icon}</span>
                            <p class="text-sm font-medium">${message}</p>
                        </div>
                        ${dismissible ? `
                            <button id="${dismissId}" 
                                    class="text-current opacity-70 hover:opacity-100 transition-opacity">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
            
            if (dismissId) {
                setTimeout(() => {
                    const btn = document.getElementById(dismissId);
                    if (btn) btn.addEventListener('click', () => this.dismiss());
                }, 0);
            }
            
            return html;
        }
    };
}

/**
 * Stat Card Component
 * @param {string} label - Stat label
 * @param {string|number} value - Stat value
 * @param {object} options - Additional options
 * @returns {string} HTML string
 */
function statCard(label, value, options = {}) {
    const {
        icon = null,
        trend = null,
        trendValue = null,
        subtitle = null,
        color = 'primary'
    } = options;
    
    const colors = {
        primary: 'border-primary-500 bg-primary-50',
        success: 'border-green-500 bg-green-50',
        warning: 'border-yellow-500 bg-yellow-50',
        danger: 'border-red-500 bg-red-50',
        purple: 'border-purple-500 bg-purple-50'
    };
    
    const cardColor = colors[color] || colors.primary;
    
    return `
        <div class="bg-white rounded-lg shadow-md hover:shadow-lg p-6 border-l-4 ${cardColor} transition-shadow">
            <div class="flex items-center justify-between">
                <div class="flex-1">
                    <p class="text-sm font-medium text-gray-500 uppercase tracking-wide">${label}</p>
                    <p class="text-3xl font-bold text-gray-900 mt-2">${value}</p>
                    ${trend && trendValue ? `
                        <div class="flex items-center mt-2">
                            <span class="${trend === 'up' ? 'text-success-500' : 'text-danger-500'} text-sm font-semibold">
                                ${trend === 'up' ? '↗' : '↘'} ${trendValue}
                            </span>
                            ${subtitle ? `<span class="text-sm text-gray-500 ml-2">${subtitle}</span>` : ''}
                        </div>
                    ` : ''}
                </div>
                ${icon ? `
                    <div class="bg-${color}-50 rounded-full p-3">
                        <span class="text-2xl">${icon}</span>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

/**
 * Skeleton Loader Component
 * @param {string} type - Skeleton type: 'card', 'table', 'chart'
 * @returns {string} HTML string
 */
function skeletonLoader(type = 'card') {
    const templates = {
        card: `
            <div class="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div class="flex items-center justify-between">
                    <div class="flex-1">
                        <div class="h-4 bg-gray-200 rounded mb-2 w-1/3"></div>
                        <div class="h-8 bg-gray-200 rounded mb-2 w-2/3"></div>
                        <div class="h-3 bg-gray-200 rounded w-1/2"></div>
                    </div>
                    <div class="w-12 h-12 bg-gray-200 rounded-full"></div>
                </div>
            </div>
        `,
        table: `
            <div class="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div class="h-4 bg-gray-200 rounded mb-4 w-1/4"></div>
                <div class="space-y-3">
                    ${Array(5).fill(0).map(() => '<div class="h-12 bg-gray-200 rounded"></div>').join('')}
                </div>
            </div>
        `,
        chart: `
            <div class="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div class="h-4 bg-gray-200 rounded mb-4 w-1/3"></div>
                <div class="h-64 bg-gray-200 rounded"></div>
            </div>
        `
    };
    
    return templates[type] || templates.card;
}

// Register common components globally
window.components = {
    loadingSpinner,
    emptyState,
    errorDisplay,
    dataTable,
    modalDialog,
    tooltip,
    badge,
    progressBar,
    card,
    statCard,
    alert,
    skeletonLoader
};

console.log('✅ TenderIntel Common Components loaded successfully');
