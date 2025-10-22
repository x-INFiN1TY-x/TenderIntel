/**
 * TenderIntel - Main Application
 * Controls application routing, global state, and page initialization
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

function mainApp() {
    return {
        // ==================== NAVIGATION ====================
        currentPage: 'dashboard',
        showMobileMenu: false,
        previousPage: null,
        
        // ==================== USER & AUTH ====================
        user: {
            name: 'Admin User',
            initials: 'AU',
            role: 'Administrator',
            email: 'admin@tenderintel.com',
            defaultPage: 'dashboard',
            refreshInterval: '300' // seconds
        },
        showUserMenu: false,
        showPreferences: false,
        
        // ==================== NOTIFICATIONS ====================
        notifications: [],
        unreadNotifications: 0,
        showNotifications: false,
        
        // ==================== TOAST MESSAGES ====================
        toasts: [],
        toastIdCounter: 0,
        
        // ==================== GLOBAL STATE ====================
        globalLoading: false,
        quickSearch: '',
        showHelp: false,
        online: navigator.onLine,
        
        // ==================== INITIALIZATION ====================
        
        async init() {
            console.log('🚀 Initializing TenderIntel Application...');
            await this.initializeApp();
            this.initializePage();
            this.startAutoRefresh();
            this.setupEventListeners();
            this.monitorConnection();
            console.log('✅ TenderIntel Application initialized successfully');
        },
        
        async initializeApp() {
            this.globalLoading = true;
            
            try {
                // Load user preferences from localStorage
                const savedUser = localStorage.getItem(window.constants?.STORAGE_KEYS?.USER_PREFERENCES || 'tenderintel_user');
                if (savedUser) {
                    this.user = { ...this.user, ...JSON.parse(savedUser) };
                }
                
                // Load notifications
                await this.loadNotifications();
                
                // Set initial page from URL or user preference
                const urlParams = new URLSearchParams(window.location.search);
                this.currentPage = urlParams.get('page') || this.user.defaultPage || 'dashboard';
                
                // Test API connection and warm up cache
                try {
                    const health = await window.api.getHealth();
                    
                    // Check if backend is unhealthy (responding but with errors)
                    if (health.status === 'unhealthy') {
                        console.warn('Backend unhealthy:', health.error);
                        this.showToast('warning', 'Backend Issue', `Backend error: ${health.error || 'Unknown error'}`, 5000);
                        this.online = false;
                    } else if (health.status === 'degraded') {
                        console.warn('Backend degraded:', health);
                        this.showToast('warning', 'Degraded Performance', 'Backend is running slowly', 3000);
                        this.online = true;
                    } else {
                        this.showToast('success', 'Connected', 'Backend API is ready', 2000);
                        this.online = true;
                    }
                } catch (error) {
                    // Network error - actually offline or backend not responding
                    console.warn('Backend connection failed:', error);
                    const isNetworkError = error.message?.includes('fetch') || error.message?.includes('network');
                    
                    if (isNetworkError) {
                        this.showToast('warning', 'Cannot Reach Backend', 'Backend server is not responding', 5000);
                    } else {
                        this.showToast('warning', 'Connection Error', 'Using cached data - some features may be limited', 5000);
                    }
                    this.online = false;
                }
                
            } catch (error) {
                this.showToast('error', 'Initialization Error', 'Failed to initialize TenderIntel');
                console.error('App initialization failed:', error);
            } finally {
                this.globalLoading = false;
            }
        },
        
        // ==================== PAGE NAVIGATION ====================
        
        initializePage() {
            this.navigateTo(this.currentPage);
        },
        
        navigateTo(page, params = {}) {
            this.previousPage = this.currentPage;
            this.currentPage = page;
            this.showMobileMenu = false;
            
            // Update URL without page reload
            const url = new URL(window.location);
            url.searchParams.set('page', page);
            window.history.pushState({ page, params }, '', url);
            
            // Initialize page-specific components
            this.$nextTick(() => {
                switch(page) {
                    case 'dashboard':
                        this.initDashboard();
                        break;
                    case 'search':
                        this.initSearch();
                        break;
                    case 'intelligence':
                        this.initIntelligence();
                        break;
                    default:
                        console.warn(`Unknown page: ${page}`);
                        this.navigateTo('dashboard');
                }
            });
        },
        
        goBack() {
            if (this.previousPage) {
                this.navigateTo(this.previousPage);
            }
        },
        
        // Page initializers (will be implemented when page components are created)
        initDashboard() {
            console.log('Initializing Dashboard page...');
            if (typeof initExecutiveDashboard === 'function') {
                initExecutiveDashboard();
            }
        },
        
        initSearch() {
            console.log('Initializing Search page...');
            if (typeof initAdvancedSearch === 'function') {
                initAdvancedSearch();
            }
        },
        
        initIntelligence() {
            console.log('Initializing Intelligence page...');
            if (typeof initHeatmap === 'function') {
                initHeatmap();
            }
            if (typeof initCompetitiveIntelligence === 'function') {
                initCompetitiveIntelligence();
            }
        },
        

        
        // ==================== QUICK SEARCH ====================
        
        async performQuickSearch() {
            if (!this.quickSearch.trim()) return;
            
            try {
                const query = this.quickSearch.trim();
                this.navigateTo('search');
                
                // Wait for search page to initialize, then trigger search
                this.$nextTick(() => {
                    const event = new CustomEvent('quickSearch', {
                        detail: { query }
                    });
                    document.dispatchEvent(event);
                });
                
                this.quickSearch = '';
            } catch (error) {
                this.showToast('error', 'Search Error', 'Failed to perform quick search');
            }
        },
        
        // ==================== NOTIFICATION MANAGEMENT ====================
        
        async loadNotifications() {
            try {
                if (window.notificationService) {
                    this.notifications = window.notificationService.getRecent(10);
                    this.unreadNotifications = window.notificationService.getUnreadCount();
                    
                    // Subscribe to notification updates
                    window.notificationService.subscribe((notifications) => {
                        this.notifications = notifications.slice(0, 10);
                        this.unreadNotifications = window.notificationService.getUnreadCount();
                    });
                } else {
                    // Fallback: create sample notifications
                    this.notifications = [
                        {
                            id: 1,
                            type: 'success',
                            title: 'System Ready',
                            message: 'TenderIntel initialized successfully',
                            timestamp: new Date().toISOString(),
                            read: false
                        }
                    ];
                    this.unreadNotifications = 1;
                }
            } catch (error) {
                console.error('Failed to load notifications:', error);
            }
        },
        
        markNotificationRead(notificationId) {
            if (window.notificationService) {
                window.notificationService.markRead(notificationId);
            }
        },
        
        markAllNotificationsRead() {
            if (window.notificationService) {
                window.notificationService.markAllRead();
            }
        },
        
        clearNotifications() {
            if (window.notificationService) {
                window.notificationService.clearAll();
                this.showToast('success', 'Cleared', 'All notifications cleared');
            }
        },
        
        // ==================== TOAST NOTIFICATION SYSTEM ====================
        
        showToast(type, title, message, duration = 5000) {
            const toast = {
                id: ++this.toastIdCounter,
                type,
                title,
                message,
                visible: true
            };
            
            this.toasts.push(toast);
            
            // Auto-dismiss after duration
            if (duration > 0) {
                setTimeout(() => {
                    this.dismissToast(toast.id);
                }, duration);
            }
            
            return toast.id;
        },
        
        dismissToast(toastId) {
            const toastIndex = this.toasts.findIndex(t => t.id === toastId);
            if (toastIndex > -1) {
                this.toasts[toastIndex].visible = false;
                
                // Remove from array after animation
                setTimeout(() => {
                    this.toasts = this.toasts.filter(t => t.id !== toastId);
                }, 300);
            }
        },
        
        // ==================== USER PREFERENCES ====================
        
        savePreferences() {
            const storageKey = window.constants?.STORAGE_KEYS?.USER_PREFERENCES || 'tenderintel_user';
            localStorage.setItem(storageKey, JSON.stringify(this.user));
            this.showPreferences = false;
            this.showToast('success', 'Preferences Saved', 'Your preferences have been updated');
        },
        
        resetPreferences() {
            const storageKey = window.constants?.STORAGE_KEYS?.USER_PREFERENCES || 'tenderintel_user';
            localStorage.removeItem(storageKey);
            
            this.user = {
                name: 'Admin User',
                initials: 'AU',
                role: 'Administrator',
                email: 'admin@tenderintel.com',
                defaultPage: 'dashboard',
                refreshInterval: '300'
            };
            
            this.showToast('success', 'Reset Complete', 'Preferences reset to defaults');
        },
        
        // ==================== DASHBOARD EXPORT ====================
        
        async exportDashboard() {
            try {
                this.showToast('info', 'Export Started', 'Generating dashboard report...');
                
                // Get current dashboard data
                const dashboardData = await window.api.getExecutiveSummary();
                
                if (window.exportService) {
                    const success = window.exportService.exportDashboard(dashboardData, 'dashboard');
                    
                    if (success) {
                        this.showToast('success', 'Export Complete', 'Dashboard report downloaded');
                    } else {
                        throw new Error('Export failed');
                    }
                } else {
                    throw new Error('Export service not available');
                }
                
            } catch (error) {
                console.error('Dashboard export failed:', error);
                this.showToast('error', 'Export Failed', 'Failed to generate dashboard report');
            }
        },
        
        // ==================== AUTO-REFRESH FUNCTIONALITY ====================
        
        startAutoRefresh() {
            const intervalSeconds = parseInt(this.user.refreshInterval);
            
            if (isNaN(intervalSeconds) || intervalSeconds <= 0 || this.user.refreshInterval === 'manual') {
                console.log('Auto-refresh disabled (manual mode)');
                return;
            }
            
            const intervalMs = intervalSeconds * 1000;
            
            setInterval(() => {
                try {
                    // Dispatch auto-refresh event
                    const event = new CustomEvent('autoRefresh', {
                        detail: { 
                            timestamp: Date.now(),
                            source: 'timer'
                        }
                    });
                    document.dispatchEvent(event);
                    
                    console.log('Auto-refresh triggered');
                } catch (error) {
                    console.error('Auto-refresh failed:', error);
                }
            }, intervalMs);
            
            console.log(`Auto-refresh enabled: every ${intervalSeconds} seconds`);
        },
        
        // ==================== EVENT LISTENERS ====================
        
        setupEventListeners() {
            // Browser back/forward buttons
            window.addEventListener('popstate', (event) => {
                if (event.state && event.state.page) {
                    this.currentPage = event.state.page;
                    this.initializePage();
                }
            });
            
            // Online/offline detection
            window.addEventListener('online', () => {
                this.online = true;
                this.showToast('success', 'Connection Restored', 'Back online');
                this.handleReconnection();
            });
            
            window.addEventListener('offline', () => {
                this.online = false;
                this.showToast('warning', 'Connection Lost', 'Working offline');
            });
            
            // Global keyboard shortcuts
            document.addEventListener('keydown', (event) => {
                // Ctrl/Cmd + K for quick search
                if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
                    event.preventDefault();
                    document.querySelector('input[type="text"]')?.focus();
                }
                
                // Escape to close modals
                if (event.key === 'Escape') {
                    this.showPreferences = false;
                    this.showNotifications = false;
                    this.showUserMenu = false;
                }
            });
        },
        
        // ==================== CONNECTION MONITORING ====================
        
        monitorConnection() {
            // Periodic connection check
            setInterval(async () => {
                try {
                    const health = await window.api.getHealth();
                    
                    // Check health status
                    const isHealthy = health.status === 'healthy' || health.status === 'degraded';
                    
                    if (isHealthy && !this.online) {
                        this.online = true;
                        this.handleReconnection();
                    } else if (!isHealthy && this.online) {
                        this.online = false;
                        console.warn('Backend unhealthy:', health.error);
                        document.dispatchEvent(new CustomEvent('connectionLost'));
                    }
                } catch (error) {
                    if (this.online) {
                        this.online = false;
                        console.warn('Health check failed:', error);
                        document.dispatchEvent(new CustomEvent('connectionLost'));
                    }
                }
            }, 30000); // Check every 30 seconds
        },
        
        async handleReconnection() {
            try {
                // Clear stale cache
                window.api.clearCache();
                
                // Dispatch reconnection event
                document.dispatchEvent(new CustomEvent('connectionRestored'));
                
                // Reload current page data
                document.dispatchEvent(new CustomEvent('autoRefresh', {
                    detail: { source: 'reconnection' }
                }));
                
            } catch (error) {
                console.error('Reconnection handling failed:', error);
            }
        },
        
        // ==================== CACHE MANAGEMENT ====================
        
        clearCache() {
            if (window.api) {
                window.api.clearCache();
                this.showToast('success', 'Cache Cleared', 'All cached data has been removed');
            }
        },
        
        getCacheStats() {
            if (window.api) {
                const stats = window.api.getCacheInfo();
                console.log('Cache Statistics:', stats);
                return stats;
            }
            return null;
        },
        
        // ==================== HELP & SUPPORT ====================
        
        openHelp() {
            this.showHelp = true;
            // Could load help documentation or show help modal
        },
        
        closeHelp() {
            this.showHelp = false;
        },
        
        // ==================== ERROR HANDLING ====================
        
        handleError(error, context = 'Operation') {
            console.error(`${context} error:`, error);
            
            const message = error.message || error.toString();
            this.showToast('error', `${context} Failed`, message, 7000);
            
            // Log error to notification service
            if (window.notificationService) {
                window.notificationService.add(
                    'error',
                    `${context} Error`,
                    message,
                    { persistent: true }
                );
            }
        },
        
        // ==================== UTILITY METHODS ====================
        
        formatCurrency(value) {
            return window.formatters?.currency(value) || `₹${value}`;
        },
        
        formatDate(date) {
            return window.formatters?.date(date) || date;
        },
        
        formatRelativeTime(date) {
            return window.formatters?.relativeTime(date) || date;
        },
        
        // ==================== DEBUG UTILITIES ====================
        
        getDebugInfo() {
            return {
                version: '1.0.0',
                currentPage: this.currentPage,
                online: this.online,
                user: this.user,
                cacheStats: this.getCacheStats(),
                notificationCount: this.notifications.length,
                unreadCount: this.unreadNotifications,
                apiBaseURL: window.api?.baseURL,
                constants: window.constants
            };
        },
        
        logDebugInfo() {
            console.group('🔍 TenderIntel Debug Information');
            console.log(this.getDebugInfo());
            console.groupEnd();
        }
    }
}

// ==================== GLOBAL UTILITIES ====================

/**
 * Initialize TenderIntel application
 * Called automatically when Alpine.js loads
 */
window.initTenderIntel = function() {
    console.log('TenderIntel initialization requested');
    
    // Verify all dependencies are loaded
    const dependencies = [
        'constants',
        'formatters',
        'colorUtils',
        'validators',
        'cacheService',
        'notificationService',
        'exportService',
        'api',
        'components'
    ];
    
    const missing = dependencies.filter(dep => !window[dep]);
    
    if (missing.length > 0) {
        console.error('❌ Missing dependencies:', missing);
        alert(`Failed to load TenderIntel: Missing dependencies (${missing.join(', ')})`);
        return;
    }
    
    console.log('✅ All dependencies loaded successfully');
};

// ==================== BROWSER COMPATIBILITY ====================

// Polyfill for older browsers
if (!String.prototype.replaceAll) {
    String.prototype.replaceAll = function(search, replace) {
        return this.split(search).join(replace);
    };
}

// ==================== GLOBAL ERROR HANDLER ====================

window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    
    // Don't show toast for script load errors (handled elsewhere)
    if (event.filename && event.filename.includes('.js')) {
        return;
    }
    
    // Show user-friendly error for runtime errors
    if (window.mainApp) {
        // Toast will be shown by mainApp instance
    }
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Suppress default browser console error
    event.preventDefault();
});

console.log('✅ TenderIntel Main Application loaded successfully');
