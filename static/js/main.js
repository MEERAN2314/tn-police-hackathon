// TOR Analysis System - Main JavaScript

class TORAnalysisApp {
    constructor() {
        this.socket = null;
        this.charts = {};
        this.isConnected = false;
        this.init();
    }

    init() {
        this.initializeSocket();
        this.initializeCharts();
        this.bindEvents();
        this.startDataRefresh();
        this.initializeAnimations();
        console.log('TOR Analysis System initialized');
    }

    initializeAnimations() {
        // Add entrance animations to elements
        this.animateOnLoad();
        
        // Setup hover effects
        this.setupHoverEffects();
    }

    animateOnLoad() {
        // Animate stat cards with staggered delay
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 150);
        });

        // Animate cards
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 200 + (index * 100));
        });

        // Animate sidebar links
        const sidebarLinks = document.querySelectorAll('.sidebar-link');
        sidebarLinks.forEach((link, index) => {
            link.style.opacity = '0';
            link.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                link.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                link.style.opacity = '1';
                link.style.transform = 'translateX(0)';
            }, 100 + (index * 50));
        });
    }

    setupHoverEffects() {
        // Enhanced button hover effects
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('mouseenter', (e) => {
                this.createRippleEffect(e);
            });
        });
    }

    createRippleEffect(e) {
        const button = e.currentTarget;
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;
        
        // Add ripple keyframes if not exists
        if (!document.querySelector('#ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'ripple-styles';
            style.textContent = `
                @keyframes ripple {
                    0% { transform: scale(0); opacity: 1; }
                    100% { transform: scale(2); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        
        button.style.position = 'relative';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    // Socket.IO Connection
    initializeSocket() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                this.isConnected = true;
                console.log('Connected to server');
                this.updateConnectionStatus(true);
                
                // Subscribe to updates
                this.socket.emit('subscribe_updates', { type: 'all' });
            });

            this.socket.on('disconnect', () => {
                this.isConnected = false;
                console.log('Disconnected from server');
                this.updateConnectionStatus(false);
            });

            this.socket.on('node_update', (data) => {
                this.handleNodeUpdate(data);
            });

            this.socket.on('correlation_update', (data) => {
                this.handleCorrelationUpdate(data);
            });

            this.socket.on('stats_update', (data) => {
                this.updateDashboardStats(data);
            });
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = connected ? 'status-connected' : 'status-disconnected';
            statusElement.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }

    // Chart Initialization
    initializeCharts() {
        // Network Topology Chart
        if (document.getElementById('network-topology-chart')) {
            this.initNetworkTopologyChart();
        }

        // Traffic Flow Chart
        if (document.getElementById('traffic-flow-chart')) {
            this.initTrafficFlowChart();
        }

        // Correlation Chart
        if (document.getElementById('correlation-chart')) {
            this.initCorrelationChart();
        }
    }

    initNetworkTopologyChart() {
        const ctx = document.getElementById('network-topology-chart');
        if (!ctx) return;

        this.charts.networkTopology = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Guard Nodes', 'Middle Nodes', 'Exit Nodes', 'Bridge Nodes'],
                datasets: [{
                    data: [450, 520, 200, 77],
                    backgroundColor: [
                        '#3b82f6',
                        '#06b6d4',
                        '#10b981',
                        '#f59e0b'
                    ],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverBorderWidth: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 14,
                                weight: '500'
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1500,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    initTrafficFlowChart() {
        const ctx = document.getElementById('traffic-flow-chart');
        if (!ctx) return;

        const labels = [];
        const data = [];
        const now = new Date();
        
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time.getHours() + ':00');
            data.push(Math.floor(Math.random() * 100) + 50);
        }

        this.charts.trafficFlow = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Traffic Volume (MB/s)',
                    data: data,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    initCorrelationChart() {
        const ctx = document.getElementById('correlation-chart');
        if (!ctx) return;

        this.charts.correlation = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['High Confidence', 'Medium Confidence', 'Low Confidence'],
                datasets: [{
                    label: 'Correlations',
                    data: [23, 35, 31],
                    backgroundColor: [
                        '#10b981',
                        '#f59e0b',
                        '#ef4444'
                    ],
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // Event Handlers
    bindEvents() {
        // Mobile menu toggle
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const sidebar = document.querySelector('.sidebar');
        
        if (mobileMenuBtn && sidebar) {
            mobileMenuBtn.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }

        // Search functionality
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        }

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', this.handleFilter.bind(this));
        });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', this.refreshData.bind(this));
        }

        // Export buttons
        document.querySelectorAll('.export-btn').forEach(btn => {
            btn.addEventListener('click', this.handleExport.bind(this));
        });

        // Analysis buttons
        document.querySelectorAll('.analysis-btn').forEach(btn => {
            btn.addEventListener('click', this.handleAnalysis.bind(this));
        });
    }

    handleSearch(event) {
        const query = event.target.value.trim();
        if (query.length >= 2) {
            this.searchNodes(query);
        }
    }

    handleFilter(event) {
        const filterType = event.target.dataset.filter;
        const filterValue = event.target.dataset.value;
        this.applyFilter(filterType, filterValue);
    }

    handleExport(event) {
        const exportType = event.target.dataset.export;
        this.exportData(exportType);
    }

    handleAnalysis(event) {
        const analysisType = event.target.dataset.analysis;
        this.runAnalysis(analysisType);
    }

    // Data Management
    async refreshData() {
        this.showLoading();
        
        try {
            const stats = await this.fetchDashboardStats();
            this.updateDashboardStats(stats);
            this.showNotification('Data refreshed successfully', 'success');
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showNotification('Failed to refresh data', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async fetchDashboardStats() {
        const response = await fetch('/api/v1/dashboard/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const result = await response.json();
        return result.data;
    }

    async runAnalysis(type) {
        this.showLoading(`Running ${type} analysis...`);
        
        try {
            const response = await fetch('/api/v1/correlations/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ analysis_type: type })
            });

            if (!response.ok) throw new Error('Analysis failed');
            
            const result = await response.json();
            this.showNotification('Analysis completed successfully', 'success');
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showNotification('Analysis failed to start', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async exportData(type) {
        try {
            const response = await fetch(`/api/v1/export/correlations?format=${type}`);
            if (!response.ok) throw new Error('Export failed');
            
            const result = await response.json();
            
            if (type === 'csv') {
                this.downloadCSV(result.data.csv, 'correlations.csv');
            } else {
                this.downloadJSON(result.data, 'correlations.json');
            }
            
            this.showNotification('Data exported successfully', 'success');
        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('Export failed', 'error');
        }
    }

    // UI Updates
    updateDashboardStats(stats) {
        if (!stats) return;

        // Update stat cards
        this.updateStatCard('total-nodes', stats.nodes?.total || 1247);
        this.updateStatCard('active-correlations', stats.correlations?.total || 89);
        this.updateStatCard('high-confidence', stats.correlations?.high_confidence || 23);
        this.updateStatCard('countries', stats.geographic?.countries || 67);

        // Update charts
        if (this.charts.networkTopology && stats.nodes) {
            this.charts.networkTopology.data.datasets[0].data = [
                stats.nodes.guard || 450,
                stats.nodes.middle || 520,
                stats.nodes.exit || 200,
                stats.nodes.bridge || 77
            ];
            this.charts.networkTopology.update('active');
        }

        if (this.charts.correlation && stats.correlations) {
            this.charts.correlation.data.datasets[0].data = [
                stats.correlations.high_confidence || 23,
                stats.correlations.medium_confidence || 35,
                (stats.correlations.total || 89) - (stats.correlations.high_confidence || 23) - (stats.correlations.medium_confidence || 35)
            ];
            this.charts.correlation.update('active');
        }
    }

    updateStatCard(id, value) {
        const element = document.getElementById(id);
        if (element) {
            const currentValue = parseInt(element.textContent) || 0;
            this.animateNumber(element, currentValue, value);
        }
    }

    animateNumber(element, start, end, duration = 1500) {
        const startTime = performance.now();
        const difference = end - start;

        const step = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(start + (difference * this.easeOutQuart(progress)));
            element.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };

        requestAnimationFrame(step);
    }

    easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    // Utility Functions
    downloadCSV(csvData, filename) {
        const blob = new Blob([csvData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    downloadJSON(jsonData, filename) {
        const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    showLoading(message = 'Loading...') {
        const loader = document.getElementById('loading-overlay');
        if (loader) {
            loader.querySelector('.loading-message').textContent = message;
            loader.classList.remove('hidden');
        }
    }

    hideLoading() {
        const loader = document.getElementById('loading-overlay');
        if (loader) {
            loader.classList.add('hidden');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification container if it doesn't exist
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(container);
        }

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        // Add icon based on type
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        notification.innerHTML = `
            <div class="notification-content">
                <div class="flex items-center">
                    <span class="mr-3 text-lg">${icons[type] || icons.info}</span>
                    <span class="notification-message">${message}</span>
                </div>
                <button class="notification-close">&times;</button>
            </div>
        `;

        container.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);

        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }

    startDataRefresh() {
        // Refresh data every 30 seconds
        setInterval(() => {
            if (this.isConnected) {
                this.refreshData();
            }
        }, 30000);
    }

    // Socket event handlers
    handleNodeUpdate(data) {
        console.log('Node update received:', data);
    }

    handleCorrelationUpdate(data) {
        console.log('Correlation update received:', data);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.torApp = new TORAnalysisApp();
});

// Additional utility functions
window.TORUtils = {
    formatFingerprint: (fingerprint) => {
        return fingerprint.match(/.{1,4}/g).join(' ');
    },

    formatUptime: (seconds) => {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) return `${days}d ${hours}h`;
        if (hours > 0) return `${hours}h ${minutes}m`;
        return `${minutes}m`;
    },

    getCountryFlag: (countryCode) => {
        return `https://flagcdn.com/16x12/${countryCode.toLowerCase()}.png`;
    }
};