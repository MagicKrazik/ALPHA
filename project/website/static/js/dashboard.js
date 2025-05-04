// dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    // Load data from context
    const asaData = JSON.parse(document.getElementById('asa-data').textContent);
    const complicationsData = JSON.parse(document.getElementById('complications-data').textContent);
    const airwayMetrics = JSON.parse(document.getElementById('airway-metrics').textContent);
    const monthlyData = JSON.parse(document.getElementById('monthly-data').textContent);

    // Initialize charts
    initASAChart();
    initComplicationsChart();
    initAirwayChart();
    initTrendChart();

    function initASAChart() {
        const ctx = document.getElementById('asaChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: asaData.map(d => `ASA ${d.estado_fisico_asa}`),
                datasets: [{
                    label: 'Pacientes',
                    data: asaData.map(d => d.count),
                    backgroundColor: '#2B4570'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    function initComplicationsChart() {
        const ctx = document.getElementById('complicationsChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Sin Complicaciones', 'Con Complicaciones'],
                datasets: [{
                    data: [
                        complicationsData.total - complicationsData.with_complications,
                        complicationsData.with_complications
                    ],
                    backgroundColor: ['#28a745', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    function initAirwayChart() {
        const ctx = document.getElementById('airwayChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: airwayMetrics.mallampati_distribution.map(d => `Mallampati ${d.mallampati}`),
                datasets: [{
                    label: 'Pacientes',
                    data: airwayMetrics.mallampati_distribution.map(d => d.count),
                    backgroundColor: '#45B7D1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    function initTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: monthlyData.map(d => new Date(d.month).toLocaleDateString('es-ES', {
                    month: 'short',
                    year: 'numeric'
                })),
                datasets: [
                    {
                        label: 'Cirugías',
                        data: monthlyData.map(d => d.surgeries),
                        borderColor: '#2B4570',
                        fill: false
                    },
                    {
                        label: 'Complicaciones',
                        data: monthlyData.map(d => d.complications),
                        borderColor: '#dc3545',
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
});