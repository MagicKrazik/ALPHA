# risk_calculator.py
from typing import Dict, List, Tuple
import numpy as np
from django.db.models import Avg, StdDev

class RiskCalculator:
    """Handles risk calculations and predictions for patients"""
    
    @staticmethod
    def calculate_asa_risk(asa_score: int) -> float:
        """Calculate risk based on ASA score"""
        risk_weights = {
            1: 0.1,  # ASA I
            2: 0.3,  # ASA II
            3: 0.5,  # ASA III
            4: 0.8,  # ASA IV
            5: 0.9,  # ASA V
            6: 1.0   # ASA VI
        }
        return risk_weights.get(asa_score, 0.0)

    @staticmethod
    def calculate_airway_risk(mallampati: int, 
                            patil_aldrete: int,
                            inter_incisiva: float,
                            neck_mobility: bool = True) -> float:
        """Calculate airway difficulty risk"""
        risk_score = 0.0
        
        # Mallampati scoring
        if mallampati >= 3:
            risk_score += 0.4
        elif mallampati == 2:
            risk_score += 0.2

        # Patil-Aldrete scoring
        if patil_aldrete >= 3:
            risk_score += 0.3
        
        # Inter-incisor distance risk
        if inter_incisiva < 3:
            risk_score += 0.3
        
        # Normalize final score to 0-1 range
        return min(risk_score, 1.0)

    @staticmethod
    def calculate_comorbidity_risk(comorbidities: str) -> float:
        """Calculate risk based on comorbidities"""
        high_risk_conditions = [
            'diabetes', 'hipertension', 'obesidad', 'cardiopatia',
            'asma', 'epoc', 'cancer', 'renal', 'hepatica'
        ]
        
        risk_score = 0.0
        comorbidities_lower = comorbidities.lower()
        
        for condition in high_risk_conditions:
            if condition in comorbidities_lower:
                risk_score += 0.15
        
        return min(risk_score, 1.0)

    @staticmethod
    def calculate_procedure_risk(previous_complications: bool,
                               emergency: bool,
                               complex_surgery: bool) -> float:
        """Calculate procedure-specific risk"""
        risk_score = 0.0
        
        if previous_complications:
            risk_score += 0.4
        if emergency:
            risk_score += 0.3
        if complex_surgery:
            risk_score += 0.3
            
        return min(risk_score, 1.0)

    @staticmethod
    def get_risk_factors(patient_data: Dict) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        
        # ASA risk
        if patient_data.get('estado_fisico_asa', 1) >= 3:
            risk_factors.append('ASA ≥ III')
            
        # Airway risks
        if patient_data.get('mallampati', 1) >= 3:
            risk_factors.append('Mallampati ≥ III')
        if patient_data.get('distancia_inter_incisiva', 5) < 3:
            risk_factors.append('Apertura Bucal Reducida')
            
        # BMI risks
        if patient_data.get('imc', 25) > 30:
            risk_factors.append('Obesidad')
            
        # Additional risks
        if patient_data.get('antecedentes_dificultad'):
            risk_factors.append('Antecedentes de VAD')
        
        return risk_factors

    @staticmethod
    def calculate_total_risk(patient_data: Dict) -> Tuple[float, str, List[str]]:
        """Calculate total risk score and level"""
        # Initialize risk calculator
        rc = RiskCalculator()
        
        # Calculate component risks
        asa_risk = rc.calculate_asa_risk(patient_data.get('estado_fisico_asa', 1))
        airway_risk = rc.calculate_airway_risk(
            patient_data.get('mallampati', 1),
            patient_data.get('patil_aldrete', 1),
            patient_data.get('distancia_inter_incisiva', 5)
        )
        comorbidity_risk = rc.calculate_comorbidity_risk(
            patient_data.get('comorbilidades', '')
        )
        
        # Calculate total risk score (weighted average)
        total_risk = (
            asa_risk * 0.3 +
            airway_risk * 0.4 +
            comorbidity_risk * 0.3
        )
        
        # Get risk factors
        risk_factors = rc.get_risk_factors(patient_data)
        
        # Determine risk level
        if total_risk >= 0.7:
            risk_level = 'high'
        elif total_risk >= 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'low'
            
        return total_risk, risk_level, risk_factors

    @staticmethod
    def detect_anomalies(value: float, 
                        mean: float, 
                        std: float, 
                        threshold: float = 2.0) -> bool:
        """Detect if a value is anomalous based on z-score"""
        if std == 0:
            return False
        z_score = abs((value - mean) / std)
        return z_score > threshold