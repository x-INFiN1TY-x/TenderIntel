/**
 * TenderIntel - Service×Firm Heatmap Component
 * Interactive 7×37 matrix visualization with color coding
 * Version: 1.0.0
 * Last Updated: October 22, 2025
 */

function serviceFirmHeatmap() {
    return {
        loading: true,
        error: null,
        data: {},
        
        // Configuration
        selectedMetric: 'market_share_percent',
        selectedTimeframe: '12months',
        
        // Data arrays
        services: [],
        firms: [],
        matrix: {},
        
        // Tooltip state
        tooltip: {
            visible: false,
            x: 0,
            y: 0,
            content: ''
        },
        
        async init() {
            await this.loadTemplate();
            await this.loadHeatmapData();
            this.setupEventListeners();
            this.loading = false;
        },
        
        async loadTemplate() {
            try {
                const response = await fetch('js/pages/heatmap-content.html');
                const html = await response.text();
                
                const container = this.$el;
                if (container) {
                    container.innerHTML = html;
                }
            } catch (error) {
                console.warn('Heatmap template not found:', error);
            }
        },
        
        async loadHeatmapData() {
            try {
                const heatmapData = await window.api.getHeatmapData(
                    this.selectedMetric, 
                    this.selectedTimeframe
                );
                
                this.services = heatmapData.services || this.getDefaultServices();
                this.firms = heatmapData.firms || this.getDefaultFirms();
                this.matrix = heatmapData.matrix || this.generateDemoMatrix();
                
            } catch (error) {
                console.error('Failed to load heatmap data:', error);
                this.error = error.message;
                
                // Use demo data
                this.services = this.getDefaultServices();
                this.firms = this.getDefaultFirms();
                this.matrix = this.generateDemoMatrix();
            }
        },
        
        getDefaultServices() {
            return ['cloud', 'networking', 'database', 'software', 'integration', 'security', 'hardware'];
        },
        
        getDefaultFirms() {
            return [
                'Tata Consultancy Services', 'Infosys', 'HCL Technologies', 'Wipro', 
                'Tech Mahindra', 'Cognizant', 'Capgemini', 'NTT DATA', 'Deloitte',
                'Amazon AWS', 'Microsoft Azure', 'Google Cloud', 'IBM',
                'Accenture', 'L&T', 'Cisco', 'Dell', 'Intel India'
            ];
        },
        
        generateDemoMatrix() {
            const matrix = {};
            
            this.firms.forEach(firm => {
                matrix[firm] = {};
                this.services.forEach(service => {
                    // Generate realistic demo values
                    let value = 0;
                    
                    // Different firms have different strengths
                    if (firm.includes('TCS') && ['cloud', 'database', 'integration'].includes(service)) {
                        value = Math.random() * 40 + 60; // 60-100%
                    } else if (firm.includes('Infosys') && ['software', 'cloud'].includes(service)) {
                        value = Math.random() * 30 + 50; // 50-80%
                    } else if (firm.includes('AWS') && service === 'cloud') {
                        value = Math.random() * 20 + 80; // 80-100%
                    } else if (firm.includes('Azure') && service === 'cloud') {
                        value = Math.random() * 20 + 70; // 70-90%
                    } else if (firm.includes('Cisco') && service === 'networking') {
                        value = Math.random() * 30 + 60; // 60-90%
                    } else {
                        value = Math.random() * 30 + 10; // 10-40%
                    }
                    
                    matrix[firm][service] = Math.round(value * 100) / 100;
                });
            });
            
            return matrix;
        },
        
        setupEventListeners() {
            document.addEventListener('autoRefresh', () => {
                if (this.currentPage === 'heatmap' || this.currentPage === 'intelligence') {
                    this.refreshHeatmap(false);
                }
            });
        },
        
        // Heatmap data access methods
        getCellValue(firm, service) {
            return this.matrix[firm]?.[service] || 0;
        },
        
        getCellColor(firm, service) {
            const value = this.getCellValue(firm, service);
            const max = this.getMaxValue();
            return window.colorUtils?.getHeatmapColor(value, 0, max, 0.8) || `rgba(156, 163, 175, 0.1)`;
        },
        
        getCellTextColor(firm, service) {
            const value = this.getCellValue(firm, service);
            const max = this.getMaxValue();
            const normalized = value / (max || 1);
            
            return normalized > 0.6 ? 'text-white' : 'text-gray-800';
        },
        
        formatCellValue(value) {
            if (!value && value !== 0) return '-';
            
            switch (this.selectedMetric) {
                case 'market_share_percent':
                    return `${value.toFixed(1)}%`;
                case 'contract_count':
                    return Math.round(value).toString();
                case 'total_value_inr':
                    return window.formatters?.currency(value, 0, false) || value.toString();
                case 'avg_deal_size':
                    return window.formatters?.currency(value, 1, false) || value.toString();
                case 'growth_rate':
                    return `${value.toFixed(1)}%`;
                default:
                    return value.toString();
            }
        },
        
        getMaxValue() {
            let max = 0;
            this.firms.forEach(firm => {
                this.services.forEach(service => {
                    const value = this.getCellValue(firm, service);
                    if (value > max) max = value;
                });
            });
            return max || 100;
        },
        
        getFirmTotal(firm) {
            let total = 0;
            this.services.forEach(service => {
                total += this.getCellValue(firm, service);
            });
            return total;
        },
        
        getServiceTotal(service) {
            let total = 0;
            this.firms.forEach(firm => {
                total += this.getCellValue(firm, service);
            });
            return total;
        },
        
        getGrandTotal() {
            let total = 0;
            this.firms.forEach(firm => {
                total += this.getFirmTotal(firm);
            });
            return total;
        },
        
        // User interactions
        async updateHeatmap() {
            this.loading = true;
            await this.loadHeatmapData();
            this.loading = false;
        },
        
        async refreshHeatmap(showToast = true) {
            this.loading = true;
            
            try {
                window.api.clearCache('/visualizations/heatmap-data');
                await this.loadHeatmapData();
                
                if (showToast) {
                    this.showToast?.('success', 'Heatmap Updated', 'Latest data loaded');
                }
            } catch (error) {
                console.error('Heatmap refresh failed:', error);
                if (showToast) {
                    this.showToast?.('error', 'Refresh Failed', 'Could not load latest data');
                }
            } finally {
                this.loading = false;
            }
        },
        
        showCellDetails(firm, service) {
            const value = this.getCellValue(firm, service);
            const message = `${firm} × ${window.formatters?.titleCase(service)}\n\n` +
                          `${this.getMetricLabel()}: ${this.formatCellValue(value)}`;
            
            alert(message);
        },
        
        showFirmDetails(firm) {
            const total = this.getFirmTotal(firm);
            const message = `Firm: ${firm}\n\n` +
                          `Total ${this.getMetricLabel()}: ${this.formatCellValue(total)}`;
            
            alert(message);
        },
        
        showTooltip(event, firm, service) {
            const value = this.getCellValue(firm, service);
            const rect = event.target.getBoundingClientRect();
            
            this.tooltip = {
                visible: true,
                x: rect.left + rect.width / 2,
                y: rect.top + window.scrollY - 10,
                content: `
                    <div class="text-left">
                        <strong class="block">${firm}</strong>
                        <strong class="block">${window.formatters?.titleCase(service)}</strong>
                        <span class="block mt-1">${this.getMetricLabel()}: <strong>${this.formatCellValue(value)}</strong></span>
                    </div>
                `
            };
        },
        
        hideTooltip() {
            this.tooltip.visible = false;
        },
        
        getMetricLabel() {
            const labels = {
                'market_share_percent': 'Market Share',
                'contract_count': 'Contracts',
                'total_value_inr': 'Total Value',
                'avg_deal_size': 'Avg Deal Size',
                'growth_rate': 'Growth Rate'
            };
            return labels[this.selectedMetric] || 'Value';
        },
        
        sortByFirm() {
            this.firms.sort((a, b) => {
                const totalA = this.getFirmTotal(a);
                const totalB = this.getFirmTotal(b);
                return totalB - totalA;
            });
        },
        
        sortByService(service) {
            this.firms.sort((a, b) => {
                const valueA = this.getCellValue(a, service);
                const valueB = this.getCellValue(b, service);
                return valueB - valueA;
            });
        },
        
        async exportHeatmap() {
            try {
                const success = window.exportService?.exportHeatmap(
                    this.matrix,
                    this.firms,
                    this.services,
                    this.selectedMetric,
                    'service_firm_heatmap'
                );
                
                if (success) {
                    this.showToast?.('success', 'Export Complete', 'Heatmap data downloaded as CSV');
                } else {
                    throw new Error('Export failed');
                }
            } catch (error) {
                console.error('Heatmap export failed:', error);
                this.showToast?.('error', 'Export Failed', 'Could not export heatmap data');
            }
        },
        
        // Computed filters for responsive display
        get displayFirms() {
            // For mobile, could show top 10 firms
            if (window.innerWidth < 768) {
                return this.firms.slice(0, 10);
            }
            return this.firms;
        }
    }
}

window.initHeatmap = async function() {
    console.log('✅ Service×Firm Heatmap component initialized');
};

console.log('✅ TenderIntel Heatmap Component loaded');
