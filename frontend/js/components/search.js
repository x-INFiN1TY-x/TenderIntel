/**
 * TenderIntel - Advanced Search Interface Component
 * Comprehensive search with 8 filter categories, keyword expansion, and intelligent ranking
 * Version: 1.0.0
 * Last Updated: October 22, 2025
 */

function advancedSearch() {
    return {
        // ==================== CORE STATE MANAGEMENT ====================
        
        // Search state
        query: '',
        results: [],
        totalResults: 0,
        loading: false,
        error: null,
        lastSearchTime: null,
        
        // Pagination state
        currentPage: 1,
        pageSize: 25,
        
        // Sorting state
        sortColumn: 'similarity_percent',
        sortDirection: 'desc',
        
        // Filter state - All 8 categories from backend SearchFilters
        filters: {
            serviceCategories: [],      // Multi-select: cloud, networking, database, etc.
            organizations: [],          // Multi-select: NIC, CDAC, etc.
            valueRanges: [],           // Checkboxes: 0-1L, 1L-1Cr, etc.
            regions: [],               // Multi-select: north, south, east, west, central
            statusTypes: [],           // Checkboxes: published_aoc, live, closed
            departmentTypes: [],       // Radio: central, state
            complexityLevels: [],      // Checkboxes: simple, moderate, complex
            dateFrom: null,            // Date picker
            dateTo: null,              // Date picker
            minSimilarity: 0           // Slider: 0-100
        },
        
        // Filter options loaded from API
        filterOptions: {
            serviceCategories: [],
            organizations: [],
            valueRanges: [],
            regions: [],
            statusTypes: [],
            departmentTypes: [],
            complexityLevels: []
        },
        
        // UI state
        showFilters: true,
        showSavedSearches: false,
        showExpansions: false,
        selectedResults: new Set(),
        orgSearchQuery: '', // For filtering organization list
        
        // Expansion and history
        expansionPhrases: [],
        searchHistory: [],
        savedSearches: [],
        maxHistoryItems: 10,
        
        // ==================== DEMO SYSTEM STATE (NEW) ====================
        
        // Demo state
        demoMode: false,
        demoScenarios: null,
        tourInProgress: false,
        currentTourStep: 0,
        totalTourSteps: 0,
        tourPaused: false,
        showDemoExplanation: false,
        demoExplanationText: '',
        demoConfig: null,
        
        // ==================== INITIALIZATION ====================
        
        async init() {
            console.log('🔍 Advanced Search: Initializing...');
            
            try {
                // Load filter options from API
                await this.loadFilterOptions();
                
                // Restore user data from localStorage
                this.restoreSavedSearches();
                this.restoreSearchHistory();
                
                // Setup event listeners
                this.setupEventListeners();
                
                // Initialize demo system (lazy load)
                await this.initializeDemoSystem();
                
                // Check for quick search from global navigation
                const urlParams = new URLSearchParams(window.location.search);
                const quickQuery = urlParams.get('q');
                if (quickQuery) {
                    this.query = quickQuery;
                    await this.performSearch();
                }
                
                console.log('✅ Advanced Search: Initialization complete');
                
            } catch (error) {
                console.error('❌ Advanced Search: Initialization failed:', error);
                this.error = 'Failed to initialize search interface';
                this.showToast?.('error', 'Initialization Error', 
                    'Could not load search interface properly');
            }
        },
        
        // ==================== API INTEGRATION ====================
        
        async loadFilterOptions() {
            try {
                console.log('📡 Loading filter options from API...');
                const response = await window.api.getFilterOptions();
                
                if (response.filter_options) {
                    this.filterOptions = {
                        serviceCategories: response.filter_options.service_categories || this.getDefaultServiceCategories(),
                        organizations: response.filter_options.organizations || [],
                        valueRanges: response.filter_options.value_ranges || this.getDefaultValueRanges(),
                        regions: response.filter_options.regions || this.getDefaultRegions(),
                        statusTypes: response.filter_options.status_types || this.getDefaultStatusTypes(),
                        departmentTypes: response.filter_options.department_types || this.getDefaultDepartmentTypes(),
                        complexityLevels: response.filter_options.complexity_levels || this.getDefaultComplexityLevels()
                    };
                    
                    console.log('✅ Filter options loaded successfully:', {
                        serviceCategories: this.filterOptions.serviceCategories.length,
                        organizations: this.filterOptions.organizations.length,
                        regions: this.filterOptions.regions.length
                    });
                } else {
                    throw new Error('Invalid API response format');
                }
                
            } catch (error) {
                console.error('❌ Failed to load filter options:', error);
                
                // Use default filter options as fallback
                this.filterOptions = {
                    serviceCategories: this.getDefaultServiceCategories(),
                    organizations: [],
                    valueRanges: this.getDefaultValueRanges(),
                    regions: this.getDefaultRegions(),
                    statusTypes: this.getDefaultStatusTypes(),
                    departmentTypes: this.getDefaultDepartmentTypes(),
                    complexityLevels: this.getDefaultComplexityLevels()
                };
                
                this.showToast?.('warning', 'Using Default Filters', 
                    'Could not load dynamic filter options from server');
            }
        },
        
        async performSearch() {
            console.log('🔍 Starting search:', this.query, this.filters);
            
            // Input validation
            const keywordValidation = window.validators.keyword(this.query);
            if (!keywordValidation.valid) {
                this.error = keywordValidation.error;
                this.showToast?.('error', 'Invalid Keyword', keywordValidation.error);
                return;
            }
            
            const filterValidation = window.validators.searchFilters(this.filters);
            if (!filterValidation.valid) {
                this.error = filterValidation.errors.join('; ');
                this.showToast?.('error', 'Invalid Filters', this.error);
                return;
            }
            
            // Start search process
            this.loading = true;
            this.error = null;
            this.selectedResults.clear();
            
            try {
                const startTime = performance.now();
                
                // Get keyword expansions for display (if enabled)
                if (this.showExpansions) {
                    try {
                        const expansion = await window.api.expandKeyword(this.query, 5);
                        this.expansionPhrases = expansion.phrases || expansion.expansions || [];
                    } catch (expansionError) {
                        console.warn('Expansion failed, continuing without expansions:', expansionError);
                        this.expansionPhrases = [];
                    }
                }
                
                // Execute filtered search
                const response = await window.api.searchFiltered(
                    keywordValidation.value,
                    filterValidation.value,
                    {
                        limit: 100, // Get more results for client-side pagination
                        debug: false
                    }
                );
                
                // Process results
                this.results = response.hits || response.results || [];
                this.totalResults = response.total_matches || response.total_results || 0;
                this.currentPage = 1;
                this.lastSearchTime = Math.round(performance.now() - startTime);
                
                // Add to search history
                this.addToHistory();
                
                // User feedback
                const searchTime = this.lastSearchTime;
                this.showToast?.('success', 'Search Complete', 
                    `Found ${this.totalResults} result${this.totalResults !== 1 ? 's' : ''} in ${searchTime}ms`);
                
                console.log('✅ Search completed:', {
                    results: this.totalResults,
                    time: searchTime + 'ms',
                    expansions: this.expansionPhrases.length,
                    activeFilters: this.activeFilterCount
                });
                
            } catch (error) {
                console.error('❌ Search failed:', error);
                this.error = error.message || 'Search request failed';
                this.results = [];
                this.totalResults = 0;
                
                this.showToast?.('error', 'Search Error', 
                    error.message || 'Failed to execute search request');
            } finally {
                this.loading = false;
            }
        },
        
        // ==================== FILTER MANAGEMENT ====================
        
        // Toggle filter selection (handles both multi-select and single-select)
        toggleFilter(category, value) {
            const filterArray = this.filters[category];
            
            if (!Array.isArray(filterArray)) {
                // Single-value filter (radio button behavior)
                this.filters[category] = this.filters[category] === value ? null : value;
                return;
            }
            
            // Multi-select filter (checkbox behavior)
            const index = filterArray.indexOf(value);
            if (index > -1) {
                filterArray.splice(index, 1);
            } else {
                filterArray.push(value);
            }
            
            console.log(`Filter ${category} updated:`, this.filters[category]);
        },
        
        // Clear all filters
        clearFilters() {
            this.filters = {
                serviceCategories: [],
                organizations: [],
                valueRanges: [],
                regions: [],
                statusTypes: [],
                departmentTypes: [],
                complexityLevels: [],
                dateFrom: null,
                dateTo: null,
                minSimilarity: 0
            };
            
            this.showToast?.('info', 'Filters Cleared', 'All search filters have been reset');
            console.log('🗑️ All filters cleared');
        },
        
        // Clear specific filter category
        clearFilterCategory(category) {
            if (Array.isArray(this.filters[category])) {
                this.filters[category] = [];
            } else {
                this.filters[category] = category === 'minSimilarity' ? 0 : null;
            }
            
            console.log(`🗑️ Cleared filter category: ${category}`);
        },
        
        // Computed: Get active filter count for badge display
        get activeFilterCount() {
            let count = 0;
            
            Object.entries(this.filters).forEach(([key, value]) => {
                if (Array.isArray(value)) {
                    count += value.length;
                } else if (value !== null && value !== undefined && value !== '' && value !== 0) {
                    count++;
                }
            });
            
            return count;
        },
        
        // Computed: Filter organizations by search query
        get filteredOrganizations() {
            if (!this.orgSearchQuery || !this.filterOptions.organizations) {
                return this.filterOptions.organizations || [];
            }
            
            const query = this.orgSearchQuery.toLowerCase();
            return this.filterOptions.organizations.filter(org =>
                org.label.toLowerCase().includes(query) ||
                org.value.toLowerCase().includes(query)
            );
        },
        
        // ==================== RESULTS MANAGEMENT ====================
        
        // Computed: Get sorted results
        get sortedResults() {
            if (!this.sortColumn || this.results.length === 0) {
                return this.results;
            }
            
            return [...this.results].sort((a, b) => {
                const aVal = a[this.sortColumn];
                const bVal = b[this.sortColumn];
                
                // Handle numeric sorting
                if (typeof aVal === 'number' && typeof bVal === 'number') {
                    return this.sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
                }
                
                // Handle string sorting
                const aStr = aVal?.toString() || '';
                const bStr = bVal?.toString() || '';
                return this.sortDirection === 'asc' ? 
                    aStr.localeCompare(bStr) : 
                    bStr.localeCompare(aStr);
            });
        },
        
        // Computed: Get paginated results for current page
        get paginatedResults() {
            if (!this.results || !Array.isArray(this.results)) {
                return [];
            }
            const sortedData = this.sortedResults || this.results;
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return sortedData.slice(start, end);
        },
        
        // Computed: Calculate total pages
        get totalPages() {
            return Math.ceil(this.sortedResults.length / this.pageSize);
        },
        
        // Sort by column
        sortBy(column) {
            if (this.sortColumn === column) {
                this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortColumn = column;
                this.sortDirection = 'desc'; // Default to descending for most columns
            }
            this.currentPage = 1; // Reset to first page
            
            console.log(`📊 Sorted by ${column} (${this.sortDirection})`);
        },
        
        // Navigate to specific page
        goToPage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
                console.log(`📄 Navigated to page ${page}`);
            }
        },
        
        // Change page size
        changePageSize(newSize) {
            this.pageSize = parseInt(newSize);
            this.currentPage = 1; // Reset to first page
            console.log(`📏 Page size changed to ${newSize}`);
        },
        
        // ==================== BULK SELECTION ====================
        
        // Toggle select all results on current page
        toggleSelectAll() {
            if (this.selectedResults.size === this.paginatedResults.length && 
                this.paginatedResults.every(r => this.selectedResults.has(r.tender_id || r.id))) {
                // Deselect all on current page
                this.paginatedResults.forEach(result => {
                    this.selectedResults.delete(result.tender_id || result.id);
                });
            } else {
                // Select all on current page
                this.paginatedResults.forEach(result => {
                    this.selectedResults.add(result.tender_id || result.id);
                });
            }
            
            console.log(`✅ Bulk selection: ${this.selectedResults.size} items selected`);
        },
        
        // Toggle individual result selection
        toggleSelectResult(tenderId) {
            if (this.selectedResults.has(tenderId)) {
                this.selectedResults.delete(tenderId);
            } else {
                this.selectedResults.add(tenderId);
            }
        },
        
        // Get selected results data
        get selectedResultsData() {
            return this.results.filter(r => 
                this.selectedResults.has(r.tender_id || r.id)
            );
        },
        
        // ==================== EXPORT FUNCTIONALITY ====================
        
        // Export search results (selected or all)
        exportResults(format = 'csv') {
            try {
                const dataToExport = this.selectedResults.size > 0 ?
                    this.selectedResultsData :
                    this.results;
                
                if (dataToExport.length === 0) {
                    this.showToast?.('warning', 'No Data to Export', 
                        'Please perform a search or select results first');
                    return;
                }
                
                // Transform data for export
                const exportData = dataToExport.map(result => ({
                    'Tender ID': result.tender_id || result.id,
                    'Title': result.title,
                    'Organization': result.organization || result.org,
                    'Status': result.status,
                    'AOC Date': result.aoc_date,
                    'Service Category': result.service_category,
                    'Region': result.region,
                    'Similarity %': result.similarity_percent || result.score,
                    'URL': result.url
                }));
                
                if (window.exportService) {
                    const success = window.exportService.toCSV(exportData, 
                        `search_results_${Date.now()}`);
                    
                    if (success) {
                        this.showToast?.('success', 'Export Complete', 
                            `${exportData.length} results exported to CSV`);
                    } else {
                        throw new Error('Export failed');
                    }
                } else {
                    throw new Error('Export service not available');
                }
                
            } catch (error) {
                console.error('Export failed:', error);
                this.showToast?.('error', 'Export Failed', 
                    'Could not export search results');
            }
        },
        
        // ==================== SAVED SEARCHES MANAGEMENT ====================
        
        // Save current search configuration
        saveCurrentSearch(customName = null) {
            if (!this.query.trim()) {
                this.showToast?.('warning', 'Cannot Save', 'Enter a search query first');
                return;
            }
            
            const searchName = customName || 
                `"${this.query}" ${this.activeFilterCount > 0 ? `(${this.activeFilterCount} filters)` : ''}`;
            
            const savedSearch = {
                id: `search_${Date.now()}`,
                name: searchName,
                query: this.query,
                filters: JSON.parse(JSON.stringify(this.filters)), // Deep copy
                timestamp: new Date().toISOString(),
                resultCount: this.totalResults,
                searchTime: this.lastSearchTime
            };
            
            this.savedSearches.unshift(savedSearch);
            
            // Limit to 20 saved searches
            if (this.savedSearches.length > 20) {
                this.savedSearches = this.savedSearches.slice(0, 20);
            }
            
            this.persistSavedSearches();
            
            this.showToast?.('success', 'Search Saved', 
                `"${searchName}" saved successfully`);
            
            console.log('💾 Search saved:', searchName);
        },
        
        // Load saved search
        loadSavedSearch(searchId) {
            const saved = this.savedSearches.find(s => s.id === searchId);
            if (!saved) {
                this.showToast?.('error', 'Load Failed', 'Saved search not found');
                return;
            }
            
            // Restore search state
            this.query = saved.query;
            this.filters = JSON.parse(JSON.stringify(saved.filters)); // Deep copy
            
            // Execute search
            this.performSearch();
            
            console.log('📁 Loaded saved search:', saved.name);
        },
        
        // Delete saved search
        deleteSavedSearch(searchId) {
            const searchIndex = this.savedSearches.findIndex(s => s.id === searchId);
            if (searchIndex > -1) {
                const searchName = this.savedSearches[searchIndex].name;
                this.savedSearches.splice(searchIndex, 1);
                this.persistSavedSearches();
                
                this.showToast?.('info', 'Search Deleted', 
                    `"${searchName}" removed from saved searches`);
                
                console.log('🗑️ Deleted saved search:', searchName);
            }
        },
        
        // Persist saved searches to localStorage
        persistSavedSearches() {
            try {
                localStorage.setItem('tenderintel_saved_searches', 
                    JSON.stringify(this.savedSearches));
            } catch (error) {
                console.warn('Failed to persist saved searches:', error);
            }
        },
        
        // Restore saved searches from localStorage
        restoreSavedSearches() {
            try {
                const stored = localStorage.getItem('tenderintel_saved_searches');
                if (stored) {
                    this.savedSearches = JSON.parse(stored);
                    console.log(`📁 Restored ${this.savedSearches.length} saved searches`);
                }
            } catch (error) {
                console.warn('Failed to restore saved searches:', error);
                this.savedSearches = [];
            }
        },
        
        // ==================== SEARCH HISTORY MANAGEMENT ====================
        
        // Add current search to history
        addToHistory() {
            if (!this.query.trim()) return;
            
            const historyEntry = {
                id: `history_${Date.now()}`,
                query: this.query,
                timestamp: new Date().toISOString(),
                resultCount: this.totalResults,
                searchTime: this.lastSearchTime,
                activeFilters: this.activeFilterCount
            };
            
            // Remove duplicate if exists
            this.searchHistory = this.searchHistory.filter(h => h.query !== this.query);
            
            // Add to beginning
            this.searchHistory.unshift(historyEntry);
            
            // Limit history
            if (this.searchHistory.length > this.maxHistoryItems) {
                this.searchHistory = this.searchHistory.slice(0, this.maxHistoryItems);
            }
            
            this.persistSearchHistory();
        },
        
        // Persist search history to localStorage
        persistSearchHistory() {
            try {
                localStorage.setItem('tenderintel_search_history', 
                    JSON.stringify(this.searchHistory));
            } catch (error) {
                console.warn('Failed to persist search history:', error);
            }
        },
        
        // Restore search history from localStorage
        restoreSearchHistory() {
            try {
                const stored = localStorage.getItem('tenderintel_search_history');
                if (stored) {
                    this.searchHistory = JSON.parse(stored);
                    console.log(`📜 Restored ${this.searchHistory.length} search history items`);
                }
            } catch (error) {
                console.warn('Failed to restore search history:', error);
                this.searchHistory = [];
            }
        },
        
        // Load search from history
        loadFromHistory(historyId) {
            const historyEntry = this.searchHistory.find(h => h.id === historyId);
            if (historyEntry) {
                this.query = historyEntry.query;
                this.clearFilters(); // Start fresh with just the query
                this.performSearch();
            }
        },
        
        // ==================== DEFAULT FILTER OPTIONS ====================
        
        getDefaultServiceCategories() {
            return [
                { value: 'cloud', label: 'Cloud Services', count: 0 },
                { value: 'networking', label: 'Networking', count: 0 },
                { value: 'database', label: 'Database Services', count: 0 },
                { value: 'software', label: 'Software & Applications', count: 0 },
                { value: 'integration', label: 'Integration Services', count: 0 },
                { value: 'security', label: 'Security Solutions', count: 0 },
                { value: 'hardware', label: 'Hardware & Equipment', count: 0 }
            ];
        },
        
        getDefaultValueRanges() {
            return [
                { value: '0-1000000', label: 'Up to ₹10L', count: 0 },
                { value: '1000000-10000000', label: '₹10L - ₹1Cr', count: 0 },
                { value: '10000000-50000000', label: '₹1Cr - ₹5Cr', count: 0 },
                { value: '50000000-100000000', label: '₹5Cr - ₹10Cr', count: 0 },
                { value: '100000000-999999999999', label: '₹10Cr+', count: 0 }
            ];
        },
        
        getDefaultRegions() {
            return [
                { value: 'north', label: 'Northern India', count: 0 },
                { value: 'south', label: 'Southern India', count: 0 },
                { value: 'east', label: 'Eastern India', count: 0 },
                { value: 'west', label: 'Western India', count: 0 },
                { value: 'central', label: 'Central India', count: 0 }
            ];
        },
        
        getDefaultStatusTypes() {
            return [
                { value: 'published_aoc', label: 'Published AOC', count: 0 },
                { value: 'live', label: 'Live Tender', count: 0 },
                { value: 'closed', label: 'Closed', count: 0 }
            ];
        },
        
        getDefaultDepartmentTypes() {
            return [
                { value: 'central', label: 'Central Government', count: 0 },
                { value: 'state', label: 'State Government', count: 0 }
            ];
        },
        
        getDefaultComplexityLevels() {
            return [
                { value: 'simple', label: 'Simple', count: 0 },
                { value: 'moderate', label: 'Moderate', count: 0 },
                { value: 'complex', label: 'Complex', count: 0 }
            ];
        },
        
        // ==================== EVENT LISTENERS ====================
        
        setupEventListeners() {
            // Quick search from global navigation
            document.addEventListener('quickSearch', (event) => {
                this.query = event.detail.query;
                this.clearFilters(); // Fresh search
                this.performSearch();
            });
            
            // Auto-refresh support
            document.addEventListener('autoRefresh', (event) => {
                if (this.query && this.results.length > 0) {
                    console.log('🔄 Auto-refreshing search results...');
                    this.performSearch();
                }
            });
            
            // Window beforeunload - save current state
            window.addEventListener('beforeunload', () => {
                this.persistSavedSearches();
                this.persistSearchHistory();
            });
        },
        
        // ==================== UTILITY METHODS ====================
        
        // Get formatted result count text
        getResultCountText() {
            if (this.totalResults === 0) return 'No results found';
            if (this.totalResults === 1) return '1 result found';
            return `${formatters.number(this.totalResults)} results found`;
        },
        
        // Get pagination info text
        getPaginationText() {
            if (this.results.length === 0) return '';
            
            const start = (this.currentPage - 1) * this.pageSize + 1;
            const end = Math.min(this.currentPage * this.pageSize, this.results.length);
            
            return `Showing ${start} to ${end} of ${formatters.number(this.results.length)} results`;
        },
        
        // Check if tender ID is synthetic/test data
        isSyntheticTenderId(tenderId) {
            if (!tenderId) return false;
            
            const syntheticPatterns = [
                /TEST/i,           // Contains "TEST"
                /SAMPLE/i,         // Contains "SAMPLE"
                /DEMO/i,           // Contains "DEMO"
                /CPPP_TEST/i,      // CPPP test pattern
                /_\d{14}_/,        // Timestamp pattern (YYYYMMDDHHmmss)
                /^[A-Z]+_\d{8}_/   // Generic test pattern
            ];
            
            return syntheticPatterns.some(pattern => pattern.test(tenderId));
        },
        
        // Extract meaningful keywords from title (filtering generic terms)
        extractMeaningfulKeywords(title, maxWords = 5) {
            if (!title) return [];
            
            // Stop words to exclude (too generic for search)
            const stopWords = new Set([
                'supply', 'installation', 'provide', 'provision', 'services',
                'contract', 'tender', 'procurement', 'purchase', 'hiring',
                'maintenance', 'implementation', 'deployment', 'setup',
                'solution', 'solutions', 'system', 'systems',
                'for', 'and', 'the', 'of', 'to', 'in', 'at', 'on', 'with', 'from'
            ]);
            
            // Extract words, filter, and prioritize
            const words = title.toLowerCase()
                .split(/\s+/)
                .filter(w => w.length > 3)                          // Min 4 characters
                .filter(w => !stopWords.has(w))                     // Not a stop word
                .filter(w => /^[a-z]+$/.test(w));                   // Only alphabetic
            
            // Return unique words, limited to maxWords
            return [...new Set(words)].slice(0, maxWords);
        },
        
        // Build intelligent Google search URL for tender lookup (improved version)
        buildGoogleSearchUrl(result) {
            const tenderId = result.tender_id || result.id;
            const org = result.organization || result.org || '';
            const title = result.title || '';
            
            // Check if tender ID is synthetic/test data
            const isSynthetic = this.isSyntheticTenderId(tenderId);
            
            let searchTerms = [];
            
            // Add tender ID only if it's real (not synthetic)
            if (!isSynthetic && tenderId) {
                // Don't quote for more flexible matching
                searchTerms.push(tenderId);
            }
            
            // Always add organization (quoted for accuracy)
            if (org) {
                searchTerms.push(`"${org}"`);
            }
            
            // Extract meaningful keywords from title (more selective filtering)
            if (title) {
                const keywords = this.extractMeaningfulKeywords(title, 5);
                if (keywords.length > 0) {
                    searchTerms.push(keywords.join(' '));
                }
            }
            
            // Add context term to improve relevance
            searchTerms.push('government tender');
            
            // Site restrictions (broader for better results)
            const sites = 'site:etenders.gov.in OR site:eprocure.gov.in OR site:gem.gov.in OR site:cppp.gov.in';
            
            // Combine search query
            const searchQuery = `${searchTerms.join(' ')} ${sites}`;
            
            // Return encoded Google search URL
            return `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;
        },
        
        // Open tender via Google search (fixes broken direct URLs)
        openTender(result) {
            const googleSearchUrl = this.buildGoogleSearchUrl(result);
            window.open(googleSearchUrl, '_blank', 'noopener,noreferrer');
            
            // Log for analytics
            console.log(`🔍 Searching for tender: ${result.tender_id || result.id}`);
        },
        
        // Show result details (future: modal with full tender info)
        showResultDetails(result) {
            // For now, just copy key information
            const details = {
                'Tender ID': result.tender_id || result.id,
                'Title': result.title,
                'Organization': result.organization || result.org,
                'Status': result.status,
                'AOC Date': result.aoc_date,
                'Service Category': result.service_category,
                'Similarity': `${result.similarity_percent || result.score}%`
            };
            
            const detailsText = Object.entries(details)
                .map(([key, value]) => `${key}: ${value || 'N/A'}`)
                .join('\n');
            
            alert(`Tender Details:\n\n${detailsText}\n\nURL: ${result.url}`);
        },
        
        // ==================== DEMO SYSTEM (NEW - ENHANCED) ====================
        
        // Initialize demo system - load configuration
        async initializeDemoSystem() {
            try {
                const response = await fetch('assets/data/demo_scenarios.json');
                this.demoConfig = await response.json();
                this.demoScenarios = this.demoConfig.interactiveScenarios;
                console.log(`✅ Demo system initialized: ${this.demoScenarios.length} scenarios loaded`);
            } catch (error) {
                console.error('❌ Failed to load demo configuration:', error);
                this.demoScenarios = [];
            }
        },
        
        // Start guided tour
        async startGuidedTour(tourName = 'comprehensive') {
            if (!this.demoConfig) {
                await this.initializeDemoSystem();
            }
            
            const tour = this.demoConfig.guidedTours[tourName];
            if (!tour) {
                console.error(`Tour "${tourName}" not found`);
                return;
            }
            
            this.tourInProgress = true;
            this.currentTourStep = 0;
            this.totalTourSteps = tour.length;
            this.tourPaused = false;
            
            this.showDemoExplanation = true;
            this.demoExplanationText = this.demoConfig.demoMessages.welcome;
            
            console.log(`🎬 Starting ${tourName} tour: ${this.totalTourSteps} steps`);
            
            // Start first step after welcome message
            setTimeout(() => {
                this.executeNextTourStep(tour);
            }, 2000);
        },
        
        // Execute next tour step
        async executeNextTourStep(tour) {
            if (this.tourPaused || !this.tourInProgress) return;
            
            if (this.currentTourStep >= tour.length) {
                this.completeTour();
                return;
            }
            
            const step = tour[this.currentTourStep];
            console.log(`📍 Tour Step ${step.stepNumber}/${this.totalTourSteps}: ${step.title}`);
            
            // Set query and filters
            this.query = step.keyword;
            if (step.filters) {
                Object.assign(this.filters, step.filters);
            }
            this.showExpansions = true;
            
            // Show explanation
            this.showDemoExplanation = true;
            this.demoExplanationText = `Step ${step.stepNumber}/${this.totalTourSteps}: ${step.title}\n\n${step.explanation}`;
            
            // Execute search
            await this.performSearch();
            
            // Auto-advance to next step
            this.currentTourStep++;
            
            if (!step.pauseAfter && this.currentTourStep < tour.length) {
                setTimeout(() => {
                    this.executeNextTourStep(tour);
                }, this.demoConfig.configuration.auto_advance_delay_ms || 3000);
            } else if (step.pauseAfter) {
                this.tourPaused = true;
                this.showDemoExplanation = true;
                this.demoExplanationText = this.demoConfig.demoMessages.pause_message;
            }
        },
        
        // Run interactive scenario
        async runInteractiveScenario(scenarioId) {
            if (!this.demoScenarios) {
                await this.initializeDemoSystem();
            }
            
            const scenario = this.demoScenarios.find(s => s.id === scenarioId);
            if (!scenario) {
                console.error(`Scenario "${scenarioId}" not found`);
                return;
            }
            
            console.log(`🎯 Running scenario: ${scenario.name}`);
            
            // Set query and filters
            this.query = scenario.keyword;
            this.clearFilters();
            if (scenario.filters) {
                Object.assign(this.filters, scenario.filters);
            }
            this.showExpansions = true;
            
            // Show explanation
            this.showDemoExplanation = true;
            this.demoExplanationText = `${scenario.name}\n\n${scenario.explanation}`;
            
            // Execute search
            await this.performSearch();
            
            // Hide explanation after duration
            setTimeout(() => {
                this.showDemoExplanation = false;
            }, this.demoConfig?.configuration?.explanation_duration_ms || 5000);
        },
        
        // Complete tour
        completeTour() {
            this.tourInProgress = false;
            this.tourPaused = false;
            this.showDemoExplanation = true;
            this.demoExplanationText = this.demoConfig.demoMessages.tour_complete;
            
            console.log('🎉 Tour completed!');
            
            // Hide completion message after 5 seconds
            setTimeout(() => {
                this.showDemoExplanation = false;
            }, 5000);
        },
        
        // Pause/resume tour
        toggleTourPause() {
            this.tourPaused = !this.tourPaused;
            if (!this.tourPaused && this.tourInProgress) {
                const tour = this.demoConfig.guidedTours.comprehensive;
                this.executeNextTourStep(tour);
            }
        },
        
        // Stop tour
        stopTour() {
            this.tourInProgress = false;
            this.tourPaused = false;
            this.currentTourStep = 0;
            this.showDemoExplanation = false;
            console.log('⏹️ Tour stopped');
        },
        
        // ==================== ORIGINAL DEMO (Kept for compatibility) ====================
        
        // Load demo search for testing
        loadDemoSearch() {
            this.query = 'lan';
            this.filters.serviceCategories = ['networking'];
            this.filters.valueRanges = ['1000000-10000000'];
            this.showExpansions = true;
            
            this.performSearch();
            
            console.log('🧪 Demo search loaded');
        },
        
        // Clear all search data
        clearAllData() {
            this.query = '';
            this.results = [];
            this.totalResults = 0;
            this.error = null;
            this.clearFilters();
            this.selectedResults.clear();
            this.expansionPhrases = [];
            this.currentPage = 1;
            
            console.log('🧹 All search data cleared');
        }
    }
}

// ==================== GLOBAL INITIALIZATION ====================

// Initialize advanced search when function is available
window.initAdvancedSearch = function() {
    console.log('🚀 Initializing Advanced Search Interface...');
    
    // Load search content into the page
    const searchContent = document.getElementById('search-content');
    if (searchContent) {
        // Load template - will be implemented in search-content.html
        fetch('js/pages/search-content.html')
            .then(response => response.text())
            .then(html => {
                searchContent.innerHTML = html;
                console.log('✅ Search template loaded successfully');
            })
            .catch(error => {
                console.error('❌ Failed to load search template:', error);
                
                // Fallback: Basic search interface
                searchContent.innerHTML = `
                    <div x-data="advancedSearch()" x-init="init()" class="max-w-6xl mx-auto">
                        <div class="bg-white rounded-lg shadow-md p-6">
                            <h3 class="text-xl font-bold text-gray-800 mb-4">Advanced Search</h3>
                            
                            <!-- Basic Search Input -->
                            <div class="flex items-center space-x-4 mb-6">
                                <input type="text" 
                                       x-model="query"
                                       @keyup.enter="performSearch()"
                                       placeholder="Enter search keyword..."
                                       class="flex-1 px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                <button @click="performSearch()" 
                                        :disabled="loading || !query"
                                        class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50">
                                    <span x-text="loading ? 'Searching...' : 'Search'"></span>
                                </button>
                            </div>
                            
                            <!-- Loading State -->
                            <div x-show="loading" class="text-center py-8">
                                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                                <p class="text-sm text-gray-600 mt-2">Searching tenders...</p>
                            </div>
                            
                            <!-- Error State -->
                            <div x-show="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                                <p class="text-sm text-red-700" x-text="error"></p>
                            </div>
                            
                            <!-- Results Table -->
                            <div x-show="results.length > 0" class="overflow-x-auto">
                                <table class="w-full text-sm">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            <th class="px-4 py-2 text-left">Title</th>
                                            <th class="px-4 py-2 text-left">Organization</th>
                                            <th class="px-4 py-2 text-left">Status</th>
                                            <th class="px-4 py-2 text-center">Match %</th>
                                            <th class="px-4 py-2 text-center">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <template x-for="result in paginatedResults" :key="result.tender_id">
                                            <tr class="border-b hover:bg-gray-50">
                                                <td class="px-4 py-2" x-text="formatters.truncate(result.title, 50)"></td>
                                                <td class="px-4 py-2" x-text="formatters.truncate(result.organization || result.org, 30)"></td>
                                                <td class="px-4 py-2" x-text="result.status"></td>
                                                <td class="px-4 py-2 text-center" x-text="(result.similarity_percent || result.score) + '%'"></td>
                                                <td class="px-4 py-2 text-center">
                                                    <a :href="result.url" target="_blank" class="text-primary-600 hover:text-primary-700">View →</a>
                                                </td>
                                            </tr>
                                        </template>
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- Empty State -->
                            <div x-show="!loading && results.length === 0 && query" class="text-center py-8">
                                <p class="text-gray-600">No results found for "<span x-text="query"></span>"</p>
                                <p class="text-sm text-gray-500 mt-2">Try different keywords or adjust filters</p>
                            </div>
                        </div>
                    </div>
                `;
            });
    }
};

console.log('✅ TenderIntel Advanced Search Component loaded successfully');
