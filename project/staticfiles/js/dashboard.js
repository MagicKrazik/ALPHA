// Enhanced Dashboard JavaScript with Real-time Alerts and Risk Assessment

document.addEventListener('DOMContentLoaded', function() {
    // Global configuration
    const CONFIG = {
        refreshInterval: 30000, // 30 seconds
        alertCheckInterval: 10000, // 10 seconds
        endpoints: {
            stats: '/api/dashboard/stats/',
            alerts: '/api/dashboard/alerts/',
            dismissAlert: '/api/dashboard/alerts/dismiss/',
            export: '/api/dashboard/export/'
        },
        charts: {},
        alerts: {
            active: [],
            dismissed: new Set()
        },
        timers: {
            refresh: null,
            alerts: null,
            lastUpdate: null
        }
    };

    // Theme configuration
    const THEME = {
        colors: {
            primary: '#2B4570',
            secondary: '#45B7D1',
            accent: '#FF8C42',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8',
            gray: '#6c757d',
            light: '#f8f9fa',
            // Risk colors
            riskLow: '#28a745',
            riskModerate: '#ffc107',
            riskHigh: '#fd7e14',
            riskCritical: '#dc3545'
        },
        gradients: {
            primary: ['#2B4570', '#1e3a5f'],
            secondary: ['#45B7D1', '#2980b9'],
            success: ['#28a745', '#20c997'],
            warning: ['#ffc107', '#e0a800'],
            danger: ['#dc3545', '#c82333']
        }
    };

    // Chart.js global configuration
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(43, 69, 112, 0.95)';
    Chart.defaults.plugins.legend.position = 'bottom';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.padding = 15;

    // Utility functions
    const Utils = {
        formatNumber: (number) => new Intl.NumberFormat('es-ES').format(number),
        
        formatDate: (dateString) => new Date(dateString).toLocaleDateString('es-ES', {
            month: 'short',
            year: 'numeric'
        }),
        
        formatTime: (dateString) => new Date(dateString).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        }),
        
        createGradient: (ctx, colorStart, colorEnd, direction = 'vertical') => {
            const gradient = direction === 'vertical' 
                ? ctx.createLinearGradient(0, 0, 0, 400)
                : ctx.createLinearGradient(0, 0, 400, 0);
            gradient.addColorStop(0, colorStart);
            gradient.addColorStop(1, colorEnd);
            return gradient;
        },
        
        showLoading: () => {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) overlay.classList.add('active');
        },
        
        hideLoading: () => {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) overlay.classList.remove('active');
        },
        
        showNotification: (message, type = 'info', duration = 5000) => {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                    <span>${message}</span>
                </div>
                <button class="notification-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.add('show');
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => notification.remove(), 300);
                }, duration);
            }, 100);
        },
        
        debounce: (func, wait) => {
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
    };

    // Chart initialization functions
    const Charts = {
        initASAChart: () => {
            const ctx = document.getElementById('asaChart');
            if (!ctx || !dashboardData.asaData) return;

            const gradient = Utils.createGradient(
                ctx.getContext('2d'),
                THEME.colors.primary,
                THEME.colors.secondary
            );

            CONFIG.charts.asa = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: dashboardData.asaData.map(d => `ASA ${d.estado_fisico_asa}`),
                    datasets: [{
                        label: 'Pacientes',
                        data: dashboardData.asaData.map(d => d.count),
                        backgroundColor: gradient,
                        borderRadius: 8,
                        maxBarThickness: 60
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: context => `Pacientes: ${Utils.formatNumber(context.raw)}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0,
                                callback: value => Utils.formatNumber(value)
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        },

        initMonthlyTrendChart: () => {
            const ctx = document.getElementById('monthlyTrendChart');
            if (!ctx || !dashboardData.monthlyData) return;

            const gradient = Utils.createGradient(
                ctx.getContext('2d'),
                'rgba(69, 183, 209, 0.4)',
                'rgba(69, 183, 209, 0.0)'
            );

            CONFIG.charts.monthly = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dashboardData.monthlyData.map(d => Utils.formatDate(d.month)),
                    datasets: [{
                        label: 'Cirugías',
                        data: dashboardData.monthlyData.map(d => d.count),
                        borderColor: THEME.colors.secondary,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: THEME.colors.secondary,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: context => `Cirugías: ${Utils.formatNumber(context.raw)}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0,
                                callback: value => Utils.formatNumber(value)
                            }
                        }
                    },
                    animation: {
                        duration: 1500,
                        easing: 'easeOutQuart'
                    }
                }
            });
        },

        initBMIChart: () => {
            const ctx = document.getElementById('bmiChart');
            if (!ctx || !dashboardData.bmiDistribution) return;

            CONFIG.charts.bmi = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Bajo Peso', 'Normal', 'Sobrepeso', 'Obesidad I', 'Obesidad II', 'Obesidad III'],
                    datasets: [{
                        data: Object.values(dashboardData.bmiDistribution),
                        backgroundColor: [
                            THEME.colors.info,
                            THEME.colors.success,
                            THEME.colors.warning,
                            '#fd7e14',
                            THEME.colors.danger,
                            '#6f42c1'
                        ],
                        borderWidth: 3,
                        borderColor: '#fff',
                        hoverBorderWidth: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: context => {
                                    const total = Object.values(dashboardData.bmiDistribution).reduce((a, b) => a + b, 0);
                                    const percentage = ((context.raw / total) * 100).toFixed(1);
                                    return `${context.label}: ${Utils.formatNumber(context.raw)} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: '60%',
                    animation: {
                        duration: 1200,
                        easing: 'easeOutQuart'
                    }
                }
            });
        },

        initMallampatiChart: () => {
            const ctx = document.getElementById('mallampatiChart');
            if (!ctx || !dashboardData.mallampatiData) return;

            CONFIG.charts.mallampati = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: dashboardData.mallampatiData.map(d => `Clase ${d.mallampati}`),
                    datasets: [{
                        label: 'Distribución Mallampati',
                        data: dashboardData.mallampatiData.map(d => d.count),
                        backgroundColor: 'rgba(255, 140, 66, 0.2)',
                        borderColor: THEME.colors.accent,
                        pointBackgroundColor: THEME.colors.accent,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                callback: value => Utils.formatNumber(value)
                            }
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeOutQuart'
                    }
                }
            });
        },

        initRiskDistributionChart: () => {
            const ctx = document.getElementById('riskDistributionChart');
            if (!ctx || !dashboardData.riskDistribution) return;

            const riskData = JSON.parse(dashboardData.riskDistribution);
            
            CONFIG.charts.risk = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Bajo Riesgo', 'Riesgo Moderado', 'Alto Riesgo', 'Riesgo Crítico'],
                    datasets: [{
                        data: [riskData.low, riskData.moderate, riskData.high, riskData.critical],
                        backgroundColor: [
                            THEME.colors.riskLow,
                            THEME.colors.riskModerate,
                            THEME.colors.riskHigh,
                            THEME.colors.riskCritical
                        ],
                        borderWidth: 3,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: context => {
                                    const total = Object.values(riskData).reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
                                    return `${context.label}: ${Utils.formatNumber(context.raw)} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: '50%',
                    animation: {
                        duration: 1200,
                        easing: 'easeOutQuart'
                    }
                }
            });

            // Update risk stats
            this.updateRiskStats(riskData);
        },

        updateRiskStats: (riskData) => {
            const statsContainer = document.getElementById('riskStats');
            if (!statsContainer) return;

            const total = Object.values(riskData).reduce((a, b) => a + b, 0);
            
            statsContainer.innerHTML = `
                <div class="risk-stat-item low">
                    <span>Bajo Riesgo</span>
                    <strong>${riskData.low} (${total > 0 ? ((riskData.low / total) * 100).toFixed(1) : 0}%)</strong>
                </div>
                <div class="risk-stat-item moderate">
                    <span>Riesgo Moderado</span>
                    <strong>${riskData.moderate} (${total > 0 ? ((riskData.moderate / total) * 100).toFixed(1) : 0}%)</strong>
                </div>
                <div class="risk-stat-item high">
                    <span>Alto Riesgo</span>
                    <strong>${riskData.high} (${total > 0 ? ((riskData.high / total) * 100).toFixed(1) : 0}%)</strong>
                </div>
                <div class="risk-stat-item critical">
                    <span>Riesgo Crítico</span>
                    <strong>${riskData.critical} (${total > 0 ? ((riskData.critical / total) * 100).toFixed(1) : 0}%)</strong>
                </div>
            `;
        }
    };

    // Alert system
    const AlertSystem = {
        init: () => {
            CONFIG.timers.alerts = setInterval(() => {
                AlertSystem.checkAlerts();
            }, CONFIG.alertCheckInterval);
        },

        checkAlerts: async () => {
            try {
                const response = await fetch(CONFIG.endpoints.alerts);
                const data = await response.json();
                
                if (data.alerts) {
                    CONFIG.alerts.active = data.alerts.filter(
                        alert => !CONFIG.alerts.dismissed.has(alert.id)
                    );
                    AlertSystem.updateAlertCounts(data);
                    AlertSystem.updateAlertsPanel();
                    AlertSystem.checkCriticalAlerts();
                }
            } catch (error) {
                console.error('Error checking alerts:', error);
            }
        },

        updateAlertCounts: (data) => {
            const totalBadge = document.querySelector('#alertsToggle .badge');
            const criticalCount = document.querySelector('.alert-count.critical span');
            const highCount = document.querySelector('.alert-count.high span');
            
            if (totalBadge) totalBadge.textContent = data.total_alerts || 0;
            if (criticalCount) criticalCount.textContent = data.critical_count || 0;
            if (highCount) highCount.textContent = data.high_count || 0;
            
            // Update alert count attributes for styling
            const criticalElement = document.querySelector('.alert-count.critical');
            const highElement = document.querySelector('.alert-count.high');
            
            if (criticalElement) criticalElement.setAttribute('data-count', data.critical_count || 0);
            if (highElement) highElement.setAttribute('data-count', data.high_count || 0);
        },

        updateAlertsPanel: () => {
            const alertsList = document.getElementById('alertsList');
            if (!alertsList) return;

            if (CONFIG.alerts.active.length === 0) {
                alertsList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-shield-alt"></i>
                        <p>No hay alertas activas</p>
                    </div>
                `;
                return;
            }

            alertsList.innerHTML = CONFIG.alerts.active.map(alert => `
                <div class="alert-item ${alert.severity.toLowerCase()}" data-alert-id="${alert.id}">
                    <div class="alert-header">
                        <h5 class="alert-title">${alert.patient_name}</h5>
                        <span class="alert-severity ${alert.severity.toLowerCase()}">${alert.severity}</span>
                    </div>
                    <div class="alert-patient">Folio: ${alert.folio}</div>
                    <div class="alert-message">
                        Riesgo: ${alert.risk_score}% - ${alert.risk_factors.slice(0, 2).join(', ')}
                    </div>
                    <div class="alert-actions">
                        <button class="btn btn-primary btn-sm" onclick="showRiskDetails('${alert.folio}')">
                            <i class="fas fa-eye"></i> Ver Detalles
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="dismissAlert('${alert.id}')">
                            <i class="fas fa-times"></i> Descartar
                        </button>
                    </div>
                </div>
            `).join('');
        },

        checkCriticalAlerts: () => {
            const criticalAlerts = CONFIG.alerts.active.filter(
                alert => alert.severity === 'CRITICAL'
            );
            
            if (criticalAlerts.length > 0) {
                AlertSystem.showCriticalBanner(criticalAlerts.length);
            } else {
                AlertSystem.hideCriticalBanner();
            }
        },

        showCriticalBanner: (count) => {
            let banner = document.getElementById('alertBanner');
            if (!banner) {
                banner = document.createElement('div');
                banner.id = 'alertBanner';
                banner.className = 'alert-banner critical';
                
                const container = document.querySelector('.container');
                container.insertBefore(banner, container.firstChild);
            }
            
            banner.innerHTML = `
                <div class="alert-content">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div class="alert-text">
                        <strong>${count} PACIENTE${count > 1 ? 'S' : ''} CON RIESGO CRÍTICO</strong>
                        <span>Requiere atención inmediata</span>
                    </div>
                    <button class="btn btn-light btn-sm" onclick="showAlertModal()">
                        Ver Alertas
                    </button>
                </div>
            `;
        },

        hideCriticalBanner: () => {
            const banner = document.getElementById('alertBanner');
            if (banner) {
                banner.remove();
            }
        },

        dismissAlert: async (alertId) => {
            try {
                const response = await fetch(`${CONFIG.endpoints.dismissAlert}${alertId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                });
                
                if (response.ok) {
                    CONFIG.alerts.dismissed.add(alertId);
                    CONFIG.alerts.active = CONFIG.alerts.active.filter(
                        alert => alert.id !== alertId
                    );
                    AlertSystem.updateAlertsPanel();
                    Utils.showNotification('Alerta descartada', 'success');
                }
            } catch (error) {
                console.error('Error dismissing alert:', error);
                Utils.showNotification('Error al descartar la alerta', 'error');
            }
        }
    };

    // Dashboard data refresh
    const DataRefresh = {
        init: () => {
            CONFIG.timers.refresh = setInterval(() => {
                DataRefresh.refreshData();
            }, CONFIG.refreshInterval);
            
            CONFIG.timers.lastUpdate = setInterval(() => {
                DataRefresh.updateLastUpdateTime();
            }, 60000); // Update every minute
        },

        refreshData: async () => {
            const dateFilter = document.getElementById('dateFilter');
            const dateRange = dateFilter ? dateFilter.value : '30';
            
            try {
                const response = await fetch(`${CONFIG.endpoints.stats}?date_range=${dateRange}`);
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                DataRefresh.updateStats(data);
                DataRefresh.updateCharts(data);
                DataRefresh.updateLastUpdateTime();
                
            } catch (error) {
                console.error('Error refreshing data:', error);
                Utils.showNotification('Error al actualizar los datos', 'error');
            }
        },

        updateStats: (data) => {
            // Update summary stats
            const summaryElements = {
                'total_patients': data.summary?.total_patients,
                'active_patients': data.summary?.active_patients,
                'surgeries_completed': data.summary?.surgeries_completed,
                'pending_surgeries': data.summary?.pending_surgeries
            };
            
            Object.entries(summaryElements).forEach(([key, value]) => {
                const element = document.querySelector(`[data-stat="${key}"]`);
                if (element && value !== undefined) {
                    element.textContent = Utils.formatNumber(value);
                }
            });
            
            // Update risk summary
            if (data.risk_summary) {
                Charts.updateRiskStats(data.risk_summary);
                if (CONFIG.charts.risk) {
                    CONFIG.charts.risk.data.datasets[0].data = [
                        data.risk_summary.low,
                        data.risk_summary.moderate,
                        data.risk_summary.high,
                        data.risk_summary.critical
                    ];
                    CONFIG.charts.risk.update('none');
                }
            }
        },

        updateCharts: (data) => {
            // Update ASA distribution
            if (data.asa_distribution && CONFIG.charts.asa) {
                CONFIG.charts.asa.data.labels = data.asa_distribution.map(d => `ASA ${d.estado_fisico_asa}`);
                CONFIG.charts.asa.data.datasets[0].data = data.asa_distribution.map(d => d.count);
                CONFIG.charts.asa.update('none');
            }
            
            // Update recent surgeries
            if (data.recent_surgeries && CONFIG.charts.monthly) {
                CONFIG.charts.monthly.data.labels = data.recent_surgeries.map(d => Utils.formatDate(d.week));
                CONFIG.charts.monthly.data.datasets[0].data = data.recent_surgeries.map(d => d.count);
                CONFIG.charts.monthly.update('none');
            }
        },

        updateLastUpdateTime: () => {
            const lastUpdateElement = document.getElementById('lastUpdate');
            if (lastUpdateElement) {
                const now = new Date();
                lastUpdateElement.textContent = `Actualizado a las ${Utils.formatTime(now)}`;
            }
        }
    };

    // Circular progress animation
    const CircularProgress = {
        init: () => {
            const progressBars = document.querySelectorAll('.circular-progress');
            progressBars.forEach(progressBar => {
                const percentage = parseInt(progressBar.dataset.percentage || 0);
                progressBar.style.setProperty('--progress', `${percentage * 3.6}deg`);
                
                // Animate on scroll
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            progressBar.style.transform = 'scale(1)';
                            progressBar.style.opacity = '1';
                            observer.disconnect();
                        }
                    });
                });
                
                observer.observe(progressBar);
            });
        }
    };

    // Event handlers
    const EventHandlers = {
        init: () => {
            // Date filter
            const dateFilter = document.getElementById('dateFilter');
            if (dateFilter) {
                dateFilter.addEventListener('change', Utils.debounce(() => {
                    Utils.showLoading();
                    DataRefresh.refreshData().finally(() => {
                        Utils.hideLoading();
                    });
                }, 300));
            }
            
            // Refresh button
            const refreshBtn = document.getElementById('refreshDashboard');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    Utils.showLoading();
                    DataRefresh.refreshData().finally(() => {
                        Utils.hideLoading();
                    });
                });
            }
            
            // Export button
            const exportBtn = document.getElementById('exportDashboard');
            if (exportBtn) {
                exportBtn.addEventListener('click', EventHandlers.handleExport);
            }
            
            // Alerts toggle
            const alertsToggle = document.getElementById('alertsToggle');
            if (alertsToggle) {
                alertsToggle.addEventListener('click', () => {
                    window.toggleAlertsPanel();
                });
            }
        },

        handleExport: async () => {
            try {
                Utils.showLoading();
                const response = await fetch(CONFIG.endpoints.export);
                
                if (!response.ok) {
                    throw new Error('Error en la exportación');
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `dashboard-${new Date().toISOString().slice(0, 10)}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                
                Utils.showNotification('Datos exportados exitosamente', 'success');
            } catch (error) {
                console.error('Error exporting data:', error);
                Utils.showNotification('Error al exportar los datos', 'error');
            } finally {
                Utils.hideLoading();
            }
        }
    };

    // Global functions (accessible from HTML)
    window.toggleAlertsPanel = () => {
        const panel = document.getElementById('alertsPanel');
        if (panel) {
            panel.classList.toggle('active');
        }
    };

    window.showAlertModal = () => {
        window.toggleAlertsPanel();
    };

    window.showRiskDetails = (folio) => {
        const modal = document.getElementById('riskModal');
        const title = document.getElementById('riskModalTitle');
        const content = document.getElementById('riskModalContent');
        
        if (modal && title && content) {
            const alert = CONFIG.alerts.active.find(a => a.folio === folio);
            if (alert) {
                title.textContent = `Evaluación de Riesgo - ${alert.patient_name}`;
                content.innerHTML = `
                    <div class="risk-details">
                        <div class="risk-header">
                            <h4>Paciente: ${alert.patient_name}</h4>
                            <span class="risk-score ${alert.severity.toLowerCase()}">${alert.risk_score}%</span>
                        </div>
                        <div class="risk-factors">
                            <h5>Factores de Riesgo:</h5>
                            <ul>
                                ${alert.risk_factors.map(factor => `<li>${factor}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="risk-recommendations">
                            <h5>Recomendaciones:</h5>
                            <div class="recommendations-list">
                                ${alert.risk_factors.slice(0, 3).map(rec => `
                                    <div class="recommendation-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>${rec}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `;
                modal.classList.add('active');
            }
        }
    };

    window.closeRiskModal = () => {
        const modal = document.getElementById('riskModal');
        if (modal) {
            modal.classList.remove('active');
        }
    };

    window.dismissAlert = (alertId) => {
        AlertSystem.dismissAlert(alertId);
    };

    window.showAllActivity = () => {
        Utils.showNotification('Función de actividad completa en desarrollo', 'info');
    };

    // CSRF token helper
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Initialize everything
    function initDashboard() {
        console.log('Initializing Enhanced Dashboard...');
        
        // Initialize components
        Charts.initASAChart();
        Charts.initMonthlyTrendChart();
        Charts.initBMIChart();
        Charts.initMallampatiChart();
        Charts.initRiskDistributionChart();
        
        CircularProgress.init();
        AlertSystem.init();
        DataRefresh.init();
        EventHandlers.init();
        
        // Initial data load
        AlertSystem.checkAlerts();
        
        console.log('Dashboard initialized successfully');
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Pause timers when page is hidden
                clearInterval(CONFIG.timers.refresh);
                clearInterval(CONFIG.timers.alerts);
            } else {
                // Resume timers when page is visible
                DataRefresh.init();
                AlertSystem.init();
                // Immediate refresh when returning to page
                AlertSystem.checkAlerts();
            }
        });
    }

    // Start initialization
    initDashboard();
});