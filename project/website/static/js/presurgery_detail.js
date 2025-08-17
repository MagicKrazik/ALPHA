// static/js/presurgery_detail.js
document.addEventListener('DOMContentLoaded', function() {
    // Add interactive features to presurgery detail view
    initializeRiskIndicators();
    initializeDataVisualization();
    initializePrintFunctionality();

    function initializeRiskIndicators() {
        const riskFactors = {
            'mallampati': { threshold: 3, weight: 25 },
            'patil_aldrete': { threshold: 3, weight: 20 },
            'imc': { threshold: 35, weight: 15 },
            'estado_fisico_asa': { threshold: 4, weight: 30 }
        };

        let totalRisk = 0;
        const riskIndicators = [];

        Object.keys(riskFactors).forEach(factor => {
            const element = document.querySelector(`[data-field="${factor}"]`);
            if (element) {
                const value = parseFloat(element.textContent) || 0;
                const config = riskFactors[factor];
                
                if (value >= config.threshold) {
                    totalRisk += config.weight;
                    riskIndicators.push(factor);
                    highlightRiskFactor(element);
                }
            }
        });

        displayRiskAssessment(totalRisk, riskIndicators);
    }

    function highlightRiskFactor(element) {
        element.classList.add('risk-indicator');
        element.style.backgroundColor = '#fff3cd';
        element.style.border = '1px solid #ffeaa7';
        element.style.borderRadius = '4px';
        element.style.padding = '2px 6px';
    }

    function displayRiskAssessment(riskScore, indicators) {
        const riskContainer = document.createElement('div');
        riskContainer.className = 'risk-assessment-summary';
        riskContainer.innerHTML = `
            <div class="detail-card risk-card">
                <h3>Evaluación de Riesgo</h3>
                <div class="risk-score ${getRiskClass(riskScore)}">
                    <span class="score-label">Puntuación de Riesgo:</span>
                    <span class="score-value">${riskScore}/100</span>
                </div>
                <div class="risk-level">${getRiskLevel(riskScore)}</div>
                ${indicators.length > 0 ? `
                    <div class="risk-factors">
                        <strong>Factores de Riesgo Identificados:</strong>
                        <ul>
                            ${indicators.map(factor => `<li>${getFactorDescription(factor)}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;

        const detailGrid = document.querySelector('.detail-grid');
        if (detailGrid) {
            detailGrid.appendChild(riskContainer);
        }
    }

    function getRiskClass(score) {
        if (score >= 70) return 'high-risk';
        if (score >= 40) return 'medium-risk';
        return 'low-risk';
    }

    function getRiskLevel(score) {
        if (score >= 70) return 'ALTO RIESGO - Considerar técnicas alternativas';
        if (score >= 40) return 'RIESGO MODERADO - Preparación especial recomendada';
        return 'BAJO RIESGO - Procedimiento estándar';
    }

    function getFactorDescription(factor) {
        const descriptions = {
            'mallampati': 'Mallampati Clase III/IV',
            'patil_aldrete': 'Patil-Aldrete ≥ 3',
            'imc': 'IMC ≥ 35 (Obesidad)',
            'estado_fisico_asa': 'ASA ≥ IV'
        };
        return descriptions[factor] || factor;
    }

    function initializeDataVisualization() {
        // Add visual indicators for key metrics
        const bmiValue = document.querySelector('[data-field="imc"]');
        if (bmiValue) {
            const bmi = parseFloat(bmiValue.textContent);
            if (bmi) {
                addBMIIndicator(bmiValue, bmi);
            }
        }
    }

    function addBMIIndicator(element, bmi) {
        const indicator = document.createElement('span');
        indicator.className = 'bmi-indicator';
        
        if (bmi < 18.5) {
            indicator.textContent = ' (Bajo peso)';
            indicator.style.color = '#f39c12';
        } else if (bmi < 25) {
            indicator.textContent = ' (Normal)';
            indicator.style.color = '#27ae60';
        } else if (bmi < 30) {
            indicator.textContent = ' (Sobrepeso)';
            indicator.style.color = '#f39c12';
        } else {
            indicator.textContent = ' (Obesidad)';
            indicator.style.color = '#e74c3c';
        }
        
        element.appendChild(indicator);
    }

    function initializePrintFunctionality() {
        const printBtn = document.createElement('button');
        printBtn.className = 'btn btn-secondary print-btn';
        printBtn.innerHTML = '<i class="fas fa-print"></i> Imprimir';
        printBtn.onclick = () => window.print();

        const actions = document.querySelector('.detail-actions');
        if (actions) {
            actions.appendChild(printBtn);
        }
    }
});