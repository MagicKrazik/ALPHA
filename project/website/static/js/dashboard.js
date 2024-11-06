// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // Theme Configuration
    const theme = {
        colors: {
            primary: '#2B4570',
            secondary: '#45B7D1',
            accent: '#FF8C42',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            gray: '#666666',
            light: '#f8f9fa'
        },
        fonts: {
            default: "'Inter', sans-serif"
        },
        transitions: {
            default: 'all 0.3s ease'
        }
    };

    // Chart.js Global Configuration
    Chart.defaults.font.family = theme.fonts.default;
    Chart.defaults.font.size = 13;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(43, 69, 112, 0.9)';
    Chart.defaults.plugins.legend.position = 'bottom';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.elements.point.radius = 4;
    Chart.defaults.elements.line.tension = 0.4;

    // Utility Functions
    function createGradient(ctx, colorStart, colorEnd) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, colorStart);
        gradient.addColorStop(1, colorEnd);
        return gradient;
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('es-ES', {
            month: 'short',
            year: 'numeric'
        });
    }

    function formatNumber(number) {
        return new Intl.NumberFormat('es-ES').format(number);
    }

    // Initialize ASA Distribution Chart
    function initASAChart() {
        const ctx = document.getElementById('asaChart');
        if (!ctx) return;

        const gradient = createGradient(
            ctx.getContext('2d'),
            theme.colors.primary,
            theme.colors.secondary
        );

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: asaData.map(d => 'ASA ' + d.estado_fisico_asa),
                datasets: [{
                    label: 'Pacientes',
                    data: asaData.map(d => d.count),
                    backgroundColor: gradient,
                    borderRadius: 8,
                    maxBarThickness: 50
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribución de Clasificación ASA',
                        font: {
                            size: 16,
                            weight: 600
                        }
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: context => `Pacientes: ${formatNumber(context.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            callback: value => formatNumber(value)
                        }
                    }
                }
            }
        });
    }

    // Initialize Monthly Trend Chart
    function initMonthlyTrendChart() {
        const ctx = document.getElementById('monthlyTrendChart');
        if (!ctx) return;

        const gradient = createGradient(
            ctx.getContext('2d'),
            'rgba(69, 183, 209, 0.4)',
            'rgba(69, 183, 209, 0.0)'
        );

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: monthlyData.map(d => formatDate(d.month)),
                datasets: [{
                    label: 'Cirugías',
                    data: monthlyData.map(d => d.count),
                    borderColor: theme.colors.secondary,
                    backgroundColor: gradient,
                    fill: true,
                    pointBackgroundColor: theme.colors.secondary,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: theme.colors.secondary,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Tendencia Mensual de Cirugías',
                        font: {
                            size: 16,
                            weight: 600
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: context => `Cirugías: ${formatNumber(context.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            callback: value => formatNumber(value)
                        }
                    }
                }
            }
        });
    }

    // Initialize BMI Distribution Chart
    function initBMIChart() {
        const ctx = document.getElementById('bmiChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Bajo Peso', 'Normal', 'Sobrepeso', 'Obesidad'],
                datasets: [{
                    data: Object.values(bmiDistribution),
                    backgroundColor: [
                        theme.colors.warning,
                        theme.colors.success,
                        theme.colors.accent,
                        theme.colors.danger
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribución de IMC',
                        font: {
                            size: 16,
                            weight: 600
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: context => 
                                `${context.label}: ${formatNumber(context.raw)} pacientes (${
                                    ((context.raw / Object.values(bmiDistribution).reduce((a, b) => a + b, 0)) * 100).toFixed(1)
                                }%)`
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    // Initialize Circular Progress Bars
    function initCircularProgress() {
        const progressBars = document.querySelectorAll('.circular-progress');
        progressBars.forEach(progressBar => {
            const value = parseInt(progressBar.querySelector('.progress-value').textContent);
            progressBar.style.setProperty('--progress', `${value * 3.6}deg`);
            
            // Add animation
            progressBar.style.transform = 'scale(0)';
            progressBar.style.opacity = '0';
            
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

    // Date Range Filter
    function initDateFilter() {
        const dateFilter = document.getElementById('dateFilter');
        if (!dateFilter) return;

        dateFilter.addEventListener('change', async () => {
            try {
                const response = await fetch(`/api/dashboard/stats/?date_range=${dateFilter.value}`);
                const data = await response.json();
                updateDashboardData(data);
            } catch (error) {
                console.error('Error fetching filtered data:', error);
                showNotification('Error al actualizar los datos', 'error');
            }
        });
    }

    // Notification System
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }, 100);
    }

    // Export Functionality
    function initExport() {
        const exportBtn = document.getElementById('exportDashboard');
        if (!exportBtn) return;

        exportBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/dashboard/export/');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `dashboard-${new Date().toISOString().slice(0, 10)}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
                showNotification('Datos exportados exitosamente', 'success');
            } catch (error) {
                console.error('Error exporting data:', error);
                showNotification('Error al exportar los datos', 'error');
            }
        });
    }

    // Mobile Optimization
    function initMobileOptimization() {
        if (window.innerWidth < 768) {
            const chartCards = document.querySelectorAll('.chart-card');
            chartCards.forEach(card => {
                card.style.height = '250px';
            });
        }

        window.addEventListener('resize', () => {
            const chartCards = document.querySelectorAll('.chart-card');
            chartCards.forEach(card => {
                card.style.height = window.innerWidth < 768 ? '250px' : '350px';
            });
        });
    }

    // Real-time Updates
    let updateInterval;
    function startRealTimeUpdates() {
        updateInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/dashboard/stats/');
                const data = await response.json();
                updateDashboardData(data, true);
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }, 300000); // Update every 5 minutes
    }

    function stopRealTimeUpdates() {
        clearInterval(updateInterval);
    }

    // Initialize everything
    function initDashboard() {
        initASAChart();
        initMonthlyTrendChart();
        initBMIChart();
        initCircularProgress();
        initDateFilter();
        initExport();
        initMobileOptimization();
        startRealTimeUpdates();

        // Stop updates when page is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                stopRealTimeUpdates();
            } else {
                startRealTimeUpdates();
            }
        });
    }

    // Start initialization
    initDashboard();
});