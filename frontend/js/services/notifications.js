/**
 * TenderIntel - Notification Service
 * Manages in-app notifications, alerts, and user messaging
 * Version: 1.0.0
 * Last Updated: October 21, 2025
 */

class NotificationService {
    constructor() {
        this.subscribers = [];
        this.notificationQueue = [];
        this.maxNotifications = window.constants?.NOTIFICATION?.MAX_QUEUE_SIZE || 50;
        this.persistenceKey = window.constants?.STORAGE_KEYS?.NOTIFICATIONS || 'tenderintel_notifications';
        this.persistenceDays = window.constants?.NOTIFICATION?.PERSISTENCE_DAYS || 7;
        
        // Load persisted notifications
        this.loadPersistedNotifications();
    }
    
    /**
     * Subscribe to notification updates
     * @param {function} callback - Callback function to invoke on updates
     * @returns {function} Unsubscribe function
     */
    subscribe(callback) {
        if (typeof callback !== 'function') {
            console.warn('Notification subscriber must be a function');
            return () => {};
        }
        
        this.subscribers.push(callback);
        
        // Return unsubscribe function
        return () => {
            this.subscribers = this.subscribers.filter(cb => cb !== callback);
        };
    }
    
    /**
     * Notify all subscribers of changes
     * @private
     */
    notify() {
        this.subscribers.forEach(callback => {
            try {
                callback(this.notificationQueue);
            } catch (error) {
                console.error('Notification subscriber error:', error);
            }
        });
    }
    
    /**
     * Add new notification
     * @param {string} type - Notification type: 'success', 'error', 'warning', 'info'
     * @param {string} title - Notification title
     * @param {string} message - Notification message
     * @param {object} options - Additional options
     * @returns {string} Notification ID
     */
    add(type, title, message, options = {}) {
        const notification = {
            id: `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type, // 'success', 'error', 'warning', 'info'
            title,
            message,
            timestamp: new Date().toISOString(),
            read: false,
            persistent: options.persistent || false,
            actionUrl: options.actionUrl || null,
            actionText: options.actionText || null,
            metadata: options.metadata || {},
            priority: options.priority || 'normal' // 'high', 'normal', 'low'
        };
        
        // Add to front of queue (newest first)
        this.notificationQueue.unshift(notification);
        
        // Limit queue size
        if (this.notificationQueue.length > this.maxNotifications) {
            // Remove oldest non-persistent notifications
            this.trimQueue();
        }
        
        // Persist to localStorage
        this.persist();
        
        // Notify all subscribers
        this.notify();
        
        return notification.id;
    }
    
    /**
     * Trim notification queue to max size
     * Keeps persistent and high-priority notifications
     * @private
     */
    trimQueue() {
        // Sort: persistent first, then by priority, then by timestamp
        this.notificationQueue.sort((a, b) => {
            if (a.persistent !== b.persistent) return b.persistent - a.persistent;
            
            const priorityWeight = { high: 3, normal: 2, low: 1 };
            const aPriority = priorityWeight[a.priority] || 2;
            const bPriority = priorityWeight[b.priority] || 2;
            
            if (aPriority !== bPriority) return bPriority - aPriority;
            
            return new Date(b.timestamp) - new Date(a.timestamp);
        });
        
        // Keep only maxNotifications
        this.notificationQueue = this.notificationQueue.slice(0, this.maxNotifications);
    }
    
    /**
     * Mark notification as read
     * @param {string} notificationId - Notification ID
     */
    markRead(notificationId) {
        const notification = this.notificationQueue.find(n => n.id === notificationId);
        if (notification) {
            notification.read = true;
            this.persist();
            this.notify();
        }
    }
    
    /**
     * Mark all notifications as read
     */
    markAllRead() {
        this.notificationQueue.forEach(n => n.read = true);
        this.persist();
        this.notify();
    }
    
    /**
     * Remove notification
     * @param {string} notificationId - Notification ID
     */
    remove(notificationId) {
        this.notificationQueue = this.notificationQueue.filter(n => n.id !== notificationId);
        this.persist();
        this.notify();
    }
    
    /**
     * Clear all notifications
     * Keeps persistent notifications
     */
    clearAll() {
        // Keep persistent notifications
        this.notificationQueue = this.notificationQueue.filter(n => n.persistent);
        this.persist();
        this.notify();
    }
    
    /**
     * Get unread count
     * @returns {number} Number of unread notifications
     */
    getUnreadCount() {
        return this.notificationQueue.filter(n => !n.read).length;
    }
    
    /**
     * Get all notifications
     * @returns {Array} Array of all notifications
     */
    getAll() {
        return [...this.notificationQueue];
    }
    
    /**
     * Get notifications by type
     * @param {string} type - Notification type
     * @returns {Array} Filtered notifications
     */
    getByType(type) {
        return this.notificationQueue.filter(n => n.type === type);
    }
    
    /**
     * Get recent notifications
     * @param {number} count - Number of notifications to return
     * @returns {Array} Recent notifications
     */
    getRecent(count = 10) {
        return this.notificationQueue.slice(0, count);
    }
    
    /**
     * Get unread notifications
     * @returns {Array} Unread notifications
     */
    getUnread() {
        return this.notificationQueue.filter(n => !n.read);
    }
    
    /**
     * Persist notifications to localStorage
     * @private
     */
    persist() {
        try {
            const persistData = this.notificationQueue.map(n => ({
                id: n.id,
                type: n.type,
                title: n.title,
                message: n.message,
                timestamp: n.timestamp,
                read: n.read,
                persistent: n.persistent,
                actionUrl: n.actionUrl,
                actionText: n.actionText,
                priority: n.priority,
                metadata: n.metadata
            }));
            
            localStorage.setItem(this.persistenceKey, JSON.stringify(persistData));
            
        } catch (error) {
            console.warn('Failed to persist notifications:', error);
            
            // Handle quota exceeded
            if (error.name === 'QuotaExceededError') {
                // Keep only recent important notifications
                this.notificationQueue = this.notificationQueue
                    .filter(n => n.persistent || n.priority === 'high')
                    .slice(0, 20);
                
                try {
                    localStorage.setItem(this.persistenceKey, JSON.stringify(this.notificationQueue));
                } catch {
                    console.error('Unable to persist notifications - localStorage quota exceeded');
                }
            }
        }
    }
    
    /**
     * Load notifications from localStorage
     * @private
     */
    loadPersistedNotifications() {
        try {
            const data = localStorage.getItem(this.persistenceKey);
            if (!data) return;
            
            this.notificationQueue = JSON.parse(data);
            
            // Remove expired non-persistent notifications
            const expiryTime = Date.now() - (this.persistenceDays * 24 * 60 * 60 * 1000);
            
            this.notificationQueue = this.notificationQueue.filter(n => {
                const notifTime = new Date(n.timestamp).getTime();
                return n.persistent || notifTime > expiryTime;
            });
            
            console.log(`Loaded ${this.notificationQueue.length} persisted notifications`);
            
        } catch (error) {
            console.warn('Failed to load persisted notifications:', error);
            this.notificationQueue = [];
        }
    }
    
    /**
     * Create notification from API response
     * Automatically creates appropriate notification based on response
     * @param {object} response - API response object
     */
    fromAPIResponse(response) {
        if (!response) return;
        
        if (response.error) {
            this.add('error', 'API Error', response.error.message || 'An error occurred', {
                metadata: { endpoint: response.endpoint }
            });
        } else if (response.warning) {
            this.add('warning', 'Warning', response.warning, {
                metadata: { endpoint: response.endpoint }
            });
        } else if (response.success) {
            this.add('success', 'Success', response.message || 'Operation completed successfully', {
                metadata: { endpoint: response.endpoint }
            });
        }
    }
    
    /**
     * Create notification for scraper events
     * @param {string} event - Event type
     * @param {object} data - Event data
     */
    scraperEvent(event, data = {}) {
        const eventTypes = {
            'started': {
                type: 'info',
                title: 'Scraper Started',
                message: `Data collection initiated for ${data.source || 'portal'}`
            },
            'completed': {
                type: 'success',
                title: 'Scraper Complete',
                message: `Found ${data.count || 0} tenders from ${data.source || 'portal'}`
            },
            'error': {
                type: 'error',
                title: 'Scraper Error',
                message: data.error || 'Data collection failed'
            }
        };
        
        const template = eventTypes[event];
        if (template) {
            this.add(template.type, template.title, template.message, {
                metadata: { event, data },
                persistent: event === 'error'
            });
        }
    }
    
    /**
     * Create notification for data updates
     * @param {string} dataType - Type of data updated
     * @param {number} count - Number of records
     */
    dataUpdated(dataType, count) {
        this.add('success', 'Data Updated', 
            `${count} ${dataType} record${count !== 1 ? 's' : ''} updated`,
            { metadata: { dataType, count } }
        );
    }
    
    /**
     * Create notification for export completion
     * @param {string} format - Export format
     * @param {string} filename - Filename
     */
    exportComplete(format, filename) {
        this.add('success', 'Export Complete', 
            `${format} file downloaded: ${filename}`,
            { metadata: { format, filename } }
        );
    }
    
    /**
     * Clear old notifications (cleanup utility)
     * @param {number} daysOld - Age threshold in days
     */
    clearOld(daysOld = 7) {
        const threshold = Date.now() - (daysOld * 24 * 60 * 60 * 1000);
        const originalCount = this.notificationQueue.length;
        
        this.notificationQueue = this.notificationQueue.filter(n => {
            const notifTime = new Date(n.timestamp).getTime();
            return n.persistent || notifTime > threshold;
        });
        
        const cleared = originalCount - this.notificationQueue.length;
        
        if (cleared > 0) {
            this.persist();
            this.notify();
        }
        
        return cleared;
    }
}

// Initialize global notification service
window.notificationService = new NotificationService();

// Auto-cleanup old notifications on page load
window.notificationService.clearOld();

console.log('✅ TenderIntel Notification Service loaded successfully');
