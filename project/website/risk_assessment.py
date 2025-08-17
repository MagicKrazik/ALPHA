# website/utils/risk_assessment.py
class RiskCalculator:
    @staticmethod
    def calculate_airway_risk(presurgery_form):
        """Calculate airway difficulty risk score (0-100)"""
        risk_score = 0
        risk_factors = []
        
        # Mallampati scoring
        if presurgery_form.mallampati >= 3:
            risk_score += 25
            risk_factors.append(f"Mallampati Clase {presurgery_form.mallampati}")
        
        # ASA classification
        if presurgery_form.estado_fisico_asa >= 4:
            risk_score += 30
            risk_factors.append(f"ASA {presurgery_form.estado_fisico_asa}")
        
        # BMI assessment
        if presurgery_form.imc >= 35:
            risk_score += 15
            risk_factors.append(f"IMC {presurgery_form.imc} (Obesidad)")
        
        # Previous difficulties
        if presurgery_form.antecedentes_dificultad:
            risk_score += 40
            risk_factors.append("Antecedentes de dificultad")
        
        # Patil-Aldrete
        if presurgery_form.patil_aldrete >= 3:
            risk_score += 20
            risk_factors.append(f"Patil-Aldrete {presurgery_form.patil_aldrete}")
        
        # Inter-incisal distance
        if presurgery_form.distancia_inter_incisiva < 3:
            risk_score += 10
            risk_factors.append("Distancia inter-incisiva < 3cm")
        
        return min(risk_score, 100), risk_factors
    
    @staticmethod
    def get_risk_level(score):
        """Get risk level description"""
        if score >= 70:
            return {
                'level': 'ALTO',
                'color': '#e74c3c',
                'description': 'Alto riesgo de vía aérea difícil',
                'recommendations': [
                    'Considerar intubación con paciente despierto',
                    'Tener disponible carro de vía aérea difícil',
                    'Personal experimentado requerido'
                ]
            }
        elif score >= 40:
            return {
                'level': 'MODERADO',
                'color': '#f39c12',
                'description': 'Riesgo moderado - preparación especial',
                'recommendations': [
                    'Pre-oxigenación extendida',
                    'Videolaringoscopio disponible',
                    'Plan B definido'
                ]
            }
        else:
            return {
                'level': 'BAJO',
                'color': '#27ae60',
                'description': 'Riesgo bajo - manejo estándar',
                'recommendations': [
                    'Procedimiento estándar',
                    'Monitoreo rutinario'
                ]
            }