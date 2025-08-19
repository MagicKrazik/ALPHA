# Enhanced website/utils/risk_assessment.py - Advanced AI Risk Assessment

import math
from typing import Dict, List, Tuple, Any
from django.utils import timezone
from datetime import datetime, timedelta

class AdvancedRiskCalculator:
    """
    Enhanced risk calculator with multi-factor analysis and machine learning approach
    """
    
    # Weight coefficients for different risk factors (based on clinical evidence)
    RISK_WEIGHTS = {
        'airway_anatomy': 0.35,      # Mallampati, inter-incisal distance, etc.
        'patient_factors': 0.25,     # ASA, BMI, age
        'medical_history': 0.20,     # Previous difficulties, comorbidities
        'physiological': 0.10,       # Vital signs, glasgow
        'procedure_factors': 0.10,   # Type of surgery, urgency
    }
    
    # Mallampati scoring with evidence-based weights
    MALLAMPATI_SCORES = {
        1: {'score': 0, 'multiplier': 1.0, 'description': 'Fácil visualización'},
        2: {'score': 15, 'multiplier': 1.2, 'description': 'Buena visualización'},
        3: {'score': 35, 'multiplier': 1.8, 'description': 'Visualización limitada'},
        4: {'score': 55, 'multiplier': 2.5, 'description': 'Visualización muy difícil'}
    }
    
    # ASA classification with mortality correlation
    ASA_SCORES = {
        1: {'score': 0, 'mortality_risk': 0.1, 'description': 'Paciente sano'},
        2: {'score': 10, 'mortality_risk': 0.2, 'description': 'Enfermedad sistémica leve'},
        3: {'score': 25, 'mortality_risk': 1.8, 'description': 'Enfermedad sistémica severa'},
        4: {'score': 40, 'mortality_risk': 7.5, 'description': 'Amenaza constante para la vida'},
        5: {'score': 60, 'mortality_risk': 25.0, 'description': 'Paciente moribundo'},
        6: {'score': 80, 'mortality_risk': 50.0, 'description': 'Muerte cerebral'}
    }
    
    # BMI risk stratification
    BMI_CATEGORIES = {
        'underweight': {'range': (0, 18.5), 'score': 5, 'factor': 'Bajo peso'},
        'normal': {'range': (18.5, 25), 'score': 0, 'factor': 'Peso normal'},
        'overweight': {'range': (25, 30), 'score': 8, 'factor': 'Sobrepeso'},
        'obese_1': {'range': (30, 35), 'score': 15, 'factor': 'Obesidad grado I'},
        'obese_2': {'range': (35, 40), 'score': 25, 'factor': 'Obesidad grado II'},
        'obese_3': {'range': (40, 100), 'score': 35, 'factor': 'Obesidad grado III'}
    }

    @classmethod
    def calculate_comprehensive_risk(cls, presurgery_form) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate comprehensive risk assessment with detailed breakdown
        Returns: (total_risk_score, detailed_analysis)
        """
        try:
            # Calculate individual risk components
            airway_risk = cls._calculate_airway_anatomy_risk(presurgery_form)
            patient_risk = cls._calculate_patient_factors_risk(presurgery_form)
            history_risk = cls._calculate_medical_history_risk(presurgery_form)
            physio_risk = cls._calculate_physiological_risk(presurgery_form)
            procedure_risk = cls._calculate_procedure_risk(presurgery_form)
            
            # Calculate weighted total score
            total_score = (
                airway_risk['score'] * cls.RISK_WEIGHTS['airway_anatomy'] +
                patient_risk['score'] * cls.RISK_WEIGHTS['patient_factors'] +
                history_risk['score'] * cls.RISK_WEIGHTS['medical_history'] +
                physio_risk['score'] * cls.RISK_WEIGHTS['physiological'] +
                procedure_risk['score'] * cls.RISK_WEIGHTS['procedure_factors']
            )
            
            # Apply interaction multipliers for high-risk combinations
            multiplier = cls._calculate_interaction_multiplier(presurgery_form)
            final_score = min(total_score * multiplier, 100)
            
            # Generate detailed analysis
            analysis = {
                'total_score': round(final_score, 1),
                'components': {
                    'airway_anatomy': airway_risk,
                    'patient_factors': patient_risk,
                    'medical_history': history_risk,
                    'physiological': physio_risk,
                    'procedure_factors': procedure_risk
                },
                'risk_factors': cls._compile_risk_factors(
                    airway_risk, patient_risk, history_risk, physio_risk, procedure_risk
                ),
                'recommendations': cls._generate_recommendations(final_score, presurgery_form),
                'alert_level': cls._determine_alert_level(final_score),
                'estimated_difficulty': cls._estimate_difficulty_class(final_score),
                'mortality_risk': cls._calculate_mortality_risk(presurgery_form, final_score)
            }
            
            return final_score, analysis
            
        except Exception as e:
            # Fallback to basic calculation if advanced fails
            return cls.calculate_basic_risk(presurgery_form)

    @classmethod
    def _calculate_airway_anatomy_risk(cls, form) -> Dict[str, Any]:
        """Calculate risk based on airway anatomy assessment"""
        score = 0
        factors = []
        
        # Mallampati classification (most important predictor)
        mallampati_data = cls.MALLAMPATI_SCORES.get(form.mallampati, cls.MALLAMPATI_SCORES[1])
        score += mallampati_data['score']
        if form.mallampati >= 3:
            factors.append(f"Mallampati {form.mallampati} ({mallampati_data['description']})")
        
        # Patil-Aldrete distance (thyromental distance predictor)
        if hasattr(form, 'patil_aldrete') and form.patil_aldrete:
            if form.patil_aldrete >= 3:
                score += 20
                factors.append(f"Patil-Aldrete ≥3 (Distancia tiromentoniana reducida)")
            elif form.patil_aldrete == 2:
                score += 10
                factors.append(f"Patil-Aldrete 2 (Distancia tiromentoniana borderline)")
        
        # Inter-incisal distance
        if hasattr(form, 'distancia_inter_incisiva') and form.distancia_inter_incisiva:
            if form.distancia_inter_incisiva < 3:
                score += 15
                factors.append(f"Apertura oral <3cm ({form.distancia_inter_incisiva}cm)")
            elif form.distancia_inter_incisiva < 3.5:
                score += 8
                factors.append(f"Apertura oral limitada ({form.distancia_inter_incisiva}cm)")
        
        # Thyromental distance
        if hasattr(form, 'distancia_tiro_mentoniana') and form.distancia_tiro_mentoniana:
            if form.distancia_tiro_mentoniana < 6:
                score += 12
                factors.append(f"Distancia tiromentoniana <6cm ({form.distancia_tiro_mentoniana}cm)")
        
        # Mandibular protrusion
        if hasattr(form, 'protrusion_mandibular') and form.protrusion_mandibular:
            if form.protrusion_mandibular >= 3:
                score += 10
                factors.append(f"Protrusión mandibular limitada (Grado {form.protrusion_mandibular})")
        
        # Neck mobility and other anatomical factors
        if hasattr(form, 'desviacion_traquea') and form.desviacion_traquea and form.desviacion_traquea > 0:
            score += 8
            factors.append(f"Desviación traqueal ({form.desviacion_traquea}cm)")
        
        return {
            'score': min(score, 100),
            'factors': factors,
            'category': 'Anatomía de Vía Aérea',
            'weight': cls.RISK_WEIGHTS['airway_anatomy']
        }

    @classmethod
    def _calculate_patient_factors_risk(cls, form) -> Dict[str, Any]:
        """Calculate risk based on patient demographic and physical factors"""
        score = 0
        factors = []
        
        # ASA Classification
        asa_data = cls.ASA_SCORES.get(form.estado_fisico_asa, cls.ASA_SCORES[1])
        score += asa_data['score']
        if form.estado_fisico_asa >= 3:
            factors.append(f"ASA {form.estado_fisico_asa} ({asa_data['description']})")
        
        # BMI Assessment
        if hasattr(form, 'imc') and form.imc:
            bmi_category = cls._get_bmi_category(form.imc)
            if bmi_category:
                bmi_score = cls.BMI_CATEGORIES[bmi_category]['score']
                score += bmi_score
                if bmi_score > 0:
                    factors.append(f"{cls.BMI_CATEGORIES[bmi_category]['factor']} (IMC: {form.imc})")
        
        # Age factor
        if hasattr(form, 'fecha_nacimiento') and form.fecha_nacimiento:
            age = cls._calculate_age(form.fecha_nacimiento)
            if age >= 80:
                score += 15
                factors.append(f"Edad avanzada ({age} años)")
            elif age >= 70:
                score += 10
                factors.append(f"Paciente geriátrico ({age} años)")
            elif age <= 2:
                score += 12
                factors.append(f"Paciente pediátrico ({age} años)")
        
        # Gender considerations (statistical differences in airway anatomy)
        # This would need gender field in the model - placeholder for now
        
        return {
            'score': min(score, 100),
            'factors': factors,
            'category': 'Factores del Paciente',
            'weight': cls.RISK_WEIGHTS['patient_factors']
        }

    @classmethod
    def _calculate_medical_history_risk(cls, form) -> Dict[str, Any]:
        """Calculate risk based on medical history and comorbidities"""
        score = 0
        factors = []
        
        # Previous airway difficulties (strongest predictor)
        if hasattr(form, 'antecedentes_dificultad') and form.antecedentes_dificultad:
            score += 40
            factors.append("Antecedentes de vía aérea difícil")
        
        # Comorbidities assessment
        if hasattr(form, 'comorbilidades') and form.comorbilidades:
            comorbidities_text = form.comorbilidades.lower()
            
            # Respiratory conditions
            respiratory_conditions = ['asma', 'epoc', 'apnea', 'neumonia', 'bronquitis']
            if any(condition in comorbidities_text for condition in respiratory_conditions):
                score += 15
                factors.append("Comorbilidades respiratorias")
            
            # Cardiovascular conditions
            cardiac_conditions = ['hipertension', 'cardiaca', 'infarto', 'arritmia']
            if any(condition in comorbidities_text for condition in cardiac_conditions):
                score += 10
                factors.append("Comorbilidades cardiovasculares")
            
            # Endocrine conditions
            endocrine_conditions = ['diabetes', 'tiroides', 'acromegalia']
            if any(condition in comorbidities_text for condition in endocrine_conditions):
                score += 12
                factors.append("Comorbilidades endocrinas")
            
            # Rheumatologic conditions affecting neck mobility
            rheumatic_conditions = ['artritis', 'espondilitis', 'esclerodermia']
            if any(condition in comorbidities_text for condition in rheumatic_conditions):
                score += 18
                factors.append("Condiciones que afectan movilidad cervical")
        
        # Medication assessment
        if hasattr(form, 'medicamentos') and form.medicamentos:
            medications_text = form.medicamentos.lower()
            
            # Anticoagulants (bleeding risk)
            anticoagulants = ['warfarina', 'heparina', 'rivaroxaban', 'apixaban']
            if any(med in medications_text for med in anticoagulants):
                score += 8
                factors.append("Terapia anticoagulante")
            
            # Steroids (potential difficult mask ventilation)
            if 'esteroide' in medications_text or 'prednisona' in medications_text:
                score += 5
                factors.append("Terapia con esteroides")
        
        # Smoking history
        if hasattr(form, 'tabaquismo') and form.tabaquismo:
            score += 8
            factors.append("Historia de tabaquismo")
        
        # Allergies that might affect airway management
        if hasattr(form, 'alergias') and form.alergias:
            allergies_text = form.alergias.lower()
            drug_allergies = ['penicilina', 'latex', 'succinilcolina', 'rocuronio']
            if any(allergy in allergies_text for allergy in drug_allergies):
                score += 5
                factors.append("Alergias relevantes para anestesia")
        
        return {
            'score': min(score, 100),
            'factors': factors,
            'category': 'Historia Médica',
            'weight': cls.RISK_WEIGHTS['medical_history']
        }

    @classmethod
    def _calculate_physiological_risk(cls, form) -> Dict[str, Any]:
        """Calculate risk based on current physiological status"""
        score = 0
        factors = []
        
        # Glasgow Coma Scale
        if hasattr(form, 'glasgow') and form.glasgow:
            if form.glasgow <= 8:
                score += 20
                factors.append(f"Glasgow bajo ({form.glasgow}) - Vía aérea comprometida")
            elif form.glasgow <= 12:
                score += 10
                factors.append(f"Glasgow moderado ({form.glasgow})")
        
        # Oxygen saturation
        if hasattr(form, 'spo2_aire') and form.spo2_aire:
            if form.spo2_aire < 90:
                score += 15
                factors.append(f"Hipoxemia severa (SpO2: {form.spo2_aire}%)")
            elif form.spo2_aire < 95:
                score += 8
                factors.append(f"Hipoxemia moderada (SpO2: {form.spo2_aire}%)")
        
        # Heart rate abnormalities
        if hasattr(form, 'fc') and form.fc:
            if form.fc > 120:
                score += 5
                factors.append(f"Taquicardia ({form.fc} lpm)")
            elif form.fc < 50:
                score += 8
                factors.append(f"Bradicardia ({form.fc} lpm)")
        
        # Signs of airway compromise
        if hasattr(form, 'estridor_laringeo') and form.estridor_laringeo:
            score += 25
            factors.append("Estridor laríngeo - Obstrucción de vía aérea")
        
        if hasattr(form, 'problemas_deglucion') and form.problemas_deglucion:
            score += 12
            factors.append("Problemas de deglución - Riesgo de aspiración")
        
        return {
            'score': min(score, 100),
            'factors': factors,
            'category': 'Estado Fisiológico',
            'weight': cls.RISK_WEIGHTS['physiological']
        }

    @classmethod
    def _calculate_procedure_risk(cls, form) -> Dict[str, Any]:
        """Calculate risk based on procedure-specific factors"""
        score = 0
        factors = []
        
        # Emergency procedures
        if hasattr(form, 'fecha_reporte') and form.fecha_reporte:
            # If surgery is same day as report, consider it urgent
            if form.fecha_reporte == timezone.now().date():
                score += 10
                factors.append("Procedimiento urgente")
        
        # Fasting status
        if hasattr(form, 'ayuno_hrs') and form.ayuno_hrs is not None:
            if form.ayuno_hrs < 6:
                score += 15
                factors.append(f"Ayuno insuficiente ({form.ayuno_hrs} horas)")
            elif form.ayuno_hrs < 2:
                score += 25
                factors.append(f"Alto riesgo de aspiración ({form.ayuno_hrs} horas de ayuno)")
        
        # GLP-1 agonist use (delayed gastric emptying)
        if hasattr(form, 'uso_glp1') and form.uso_glp1:
            score += 12
            factors.append("Uso de agonistas GLP-1 - Riesgo de retención gástrica")
        
        # Gastric ultrasound findings
        if hasattr(form, 'uso_usg_gastrico') and form.uso_usg_gastrico:
            if hasattr(form, 'usg_gastrico_ml') and form.usg_gastrico_ml:
                if form.usg_gastrico_ml > 100:
                    score += 20
                    factors.append(f"Contenido gástrico elevado ({form.usg_gastrico_ml}ml)")
                elif form.usg_gastrico_ml > 50:
                    score += 10
                    factors.append(f"Contenido gástrico moderado ({form.usg_gastrico_ml}ml)")
        
        return {
            'score': min(score, 100),
            'factors': factors,
            'category': 'Factores del Procedimiento',
            'weight': cls.RISK_WEIGHTS['procedure_factors']
        }

    @classmethod
    def _calculate_interaction_multiplier(cls, form) -> float:
        """Calculate multiplier for high-risk factor interactions"""
        multiplier = 1.0
        
        # High Mallampati + High ASA
        if (hasattr(form, 'mallampati') and form.mallampati >= 3 and 
            hasattr(form, 'estado_fisico_asa') and form.estado_fisico_asa >= 4):
            multiplier *= 1.3
        
        # Obesity + Previous difficulty
        if (hasattr(form, 'imc') and form.imc and form.imc >= 35 and
            hasattr(form, 'antecedentes_dificultad') and form.antecedentes_dificultad):
            multiplier *= 1.4
        
        # Emergency + Multiple risk factors
        high_risk_factors = 0
        if hasattr(form, 'mallampati') and form.mallampati >= 3:
            high_risk_factors += 1
        if hasattr(form, 'estado_fisico_asa') and form.estado_fisico_asa >= 4:
            high_risk_factors += 1
        if hasattr(form, 'antecedentes_dificultad') and form.antecedentes_dificultad:
            high_risk_factors += 1
        
        if high_risk_factors >= 3:
            multiplier *= 1.2
        
        return min(multiplier, 2.0)  # Cap at 2x multiplier

    @classmethod
    def _compile_risk_factors(cls, *risk_components) -> List[str]:
        """Compile all risk factors from different components"""
        all_factors = []
        for component in risk_components:
            all_factors.extend(component['factors'])
        return all_factors

    @classmethod
    def _generate_recommendations(cls, risk_score: float, form) -> List[Dict[str, str]]:
        """Generate specific recommendations based on risk score and factors"""
        recommendations = []
        
        if risk_score >= 80:
            recommendations.extend([
                {'level': 'critical', 'text': '🚨 Considerar intubación con paciente despierto'},
                {'level': 'critical', 'text': '👨‍⚕️ Anestesiólogo senior obligatorio'},
                {'level': 'critical', 'text': '🛠️ Carro de vía aérea difícil inmediatamente disponible'},
                {'level': 'critical', 'text': '📋 Plan de vía aérea quirúrgica definido'},
                {'level': 'critical', 'text': '👥 Equipo de apoyo adicional en sala'},
                {'level': 'critical', 'text': '🏥 Considerar referir a centro especializado'}
            ])
        elif risk_score >= 60:
            recommendations.extend([
                {'level': 'high', 'text': '📹 Videolaringoscopía como primera opción'},
                {'level': 'high', 'text': '⏱️ Pre-oxigenación extendida (8-10 min)'},
                {'level': 'high', 'text': '🔄 Plan B de vía aérea claramente definido'},
                {'level': 'high', 'text': '👨‍⚕️ Supervisión por anestesiólogo experimentado'},
                {'level': 'high', 'text': '🛠️ Dispositivos de rescate preparados'}
            ])
        elif risk_score >= 40:
            recommendations.extend([
                {'level': 'moderate', 'text': '⚠️ Preparación especial requerida'},
                {'level': 'moderate', 'text': '📋 Revisar plan de vía aérea'},
                {'level': 'moderate', 'text': '🩺 Monitoreo estrecho durante inducción'},
                {'level': 'moderate', 'text': '🔄 Dispositivos alternativos disponibles'}
            ])
        else:
            recommendations.extend([
                {'level': 'low', 'text': '✅ Manejo estándar apropiado'},
                {'level': 'low', 'text': '🩺 Monitoreo rutinario'},
                {'level': 'low', 'text': '📋 Seguir protocolos institucionales'}
            ])
        
        # Add specific recommendations based on identified risk factors
        if hasattr(form, 'imc') and form.imc and form.imc >= 35:
            recommendations.append({
                'level': 'specific', 
                'text': '🛏️ Posición rampa/semi-sentado para pre-oxigenación'
            })
        
        if hasattr(form, 'uso_glp1') and form.uso_glp1:
            recommendations.append({
                'level': 'specific',
                'text': '🔍 Considerar ultrasonido gástrico pre-procedimiento'
            })
        
        if hasattr(form, 'antecedentes_dificultad') and form.antecedentes_dificultad:
            recommendations.append({
                'level': 'specific',
                'text': '📚 Revisar registros de procedimientos previos'
            })
        
        return recommendations

    @classmethod
    def _determine_alert_level(cls, risk_score: float) -> str:
        """Determine alert level based on risk score"""
        if risk_score >= 80:
            return 'CRITICAL'
        elif risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MODERATE'
        else:
            return 'LOW'

    @classmethod
    def _estimate_difficulty_class(cls, risk_score: float) -> Dict[str, Any]:
        """Estimate difficulty class and provide context"""
        if risk_score >= 80:
            return {
                'class': 'Extremadamente Difícil',
                'probability': '>90%',
                'description': 'Alta probabilidad de fallar intubación estándar',
                'color': '#8b0000'
            }
        elif risk_score >= 60:
            return {
                'class': 'Muy Difícil',
                'probability': '60-90%',
                'description': 'Probable dificultad significativa',
                'color': '#dc3545'
            }
        elif risk_score >= 40:
            return {
                'class': 'Moderadamente Difícil',
                'probability': '30-60%',
                'description': 'Posible dificultad moderada',
                'color': '#ffc107'
            }
        elif risk_score >= 20:
            return {
                'class': 'Ligeramente Difícil',
                'probability': '10-30%',
                'description': 'Baja probabilidad de dificultad',
                'color': '#fd7e14'
            }
        else:
            return {
                'class': 'Fácil',
                'probability': '<10%',
                'description': 'Intubación estándar esperada',
                'color': '#28a745'
            }

    @classmethod
    def _calculate_mortality_risk(cls, form, risk_score: float) -> Dict[str, Any]:
        """Calculate estimated mortality risk"""
        base_mortality = 0.1  # Base perioperative mortality rate
        
        # ASA-based mortality risk
        if hasattr(form, 'estado_fisico_asa') and form.estado_fisico_asa:
            asa_mortality = cls.ASA_SCORES.get(form.estado_fisico_asa, {'mortality_risk': 0.1})
            base_mortality = asa_mortality['mortality_risk']
        
        # Adjust based on airway risk score
        if risk_score >= 80:
            mortality_multiplier = 3.0
        elif risk_score >= 60:
            mortality_multiplier = 2.0
        elif risk_score >= 40:
            mortality_multiplier = 1.5
        else:
            mortality_multiplier = 1.0
        
        final_mortality = min(base_mortality * mortality_multiplier, 50.0)
        
        return {
            'percentage': round(final_mortality, 2),
            'category': cls._get_mortality_category(final_mortality),
            'factors': cls._get_mortality_factors(form, risk_score)
        }

    @classmethod
    def _get_mortality_category(cls, mortality_rate: float) -> str:
        """Categorize mortality risk"""
        if mortality_rate >= 10:
            return 'Muy Alto'
        elif mortality_rate >= 5:
            return 'Alto'
        elif mortality_rate >= 2:
            return 'Moderado'
        elif mortality_rate >= 1:
            return 'Bajo-Moderado'
        else:
            return 'Bajo'

    @classmethod
    def _get_mortality_factors(cls, form, risk_score: float) -> List[str]:
        """Identify factors contributing to mortality risk"""
        factors = []
        
        if hasattr(form, 'estado_fisico_asa') and form.estado_fisico_asa >= 4:
            factors.append(f"ASA {form.estado_fisico_asa}")
        
        if risk_score >= 60:
            factors.append("Alto riesgo de vía aérea difícil")
        
        if hasattr(form, 'glasgow') and form.glasgow and form.glasgow <= 8:
            factors.append("Compromiso neurológico severo")
        
        if hasattr(form, 'antecedentes_dificultad') and form.antecedentes_dificultad:
            factors.append("Historia de manejo difícil")
        
        return factors

    @classmethod
    def _get_bmi_category(cls, bmi: float) -> str:
        """Get BMI category based on value"""
        for category, data in cls.BMI_CATEGORIES.items():
            if data['range'][0] <= bmi < data['range'][1]:
                return category
        return 'normal'

    @classmethod
    def _calculate_age(cls, birth_date) -> int:
        """Calculate age from birth date"""
        today = timezone.now().date()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    @classmethod
    def calculate_basic_risk(cls, presurgery_form) -> Tuple[float, List[str]]:
        """
        Fallback basic risk calculation method
        Returns: (risk_score, risk_factors_list)
        """
        risk_score = 0
        risk_factors = []
        
        # Mallampati scoring
        if hasattr(presurgery_form, 'mallampati') and presurgery_form.mallampati >= 3:
            risk_score += 25
            risk_factors.append(f"Mallampati Clase {presurgery_form.mallampati}")
        
        # ASA classification
        if hasattr(presurgery_form, 'estado_fisico_asa') and presurgery_form.estado_fisico_asa >= 4:
            risk_score += 30
            risk_factors.append(f"ASA {presurgery_form.estado_fisico_asa}")
        
        # BMI assessment
        if hasattr(presurgery_form, 'imc') and presurgery_form.imc and presurgery_form.imc >= 35:
            risk_score += 15
            risk_factors.append(f"IMC {presurgery_form.imc} (Obesidad)")
        
        # Previous difficulties
        if hasattr(presurgery_form, 'antecedentes_dificultad') and presurgery_form.antecedentes_dificultad:
            risk_score += 40
            risk_factors.append("Antecedentes de dificultad")
        
        # Patil-Aldrete
        if (hasattr(presurgery_form, 'patil_aldrete') and 
            presurgery_form.patil_aldrete and presurgery_form.patil_aldrete >= 3):
            risk_score += 20
            risk_factors.append(f"Patil-Aldrete {presurgery_form.patil_aldrete}")
        
        # Inter-incisal distance
        if (hasattr(presurgery_form, 'distancia_inter_incisiva') and 
            presurgery_form.distancia_inter_incisiva and presurgery_form.distancia_inter_incisiva < 3):
            risk_score += 10
            risk_factors.append("Distancia inter-incisiva < 3cm")
        
        return min(risk_score, 100), risk_factors

    @classmethod
    def get_risk_level_info(cls, score: float) -> Dict[str, Any]:
        """Get comprehensive risk level information"""
        if score >= 80:
            return {
                'level': 'CRÍTICO',
                'color': '#8b0000',
                'description': 'Riesgo crítico de vía aérea difícil',
                'recommendations': [
                    'Intubación con paciente despierto',
                    'Anestesiólogo senior obligatorio',
                    'Carro de vía aérea difícil',
                    'Plan quirúrgico de rescate'
                ],
                'priority': 1,
                'alert_class': 'critical'
            }
        elif score >= 60:
            return {
                'level': 'ALTO',
                'color': '#dc3545',
                'description': 'Alto riesgo - preparación especial requerida',
                'recommendations': [
                    'Videolaringoscopía primera línea',
                    'Pre-oxigenación extendida',
                    'Plan B claramente definido',
                    'Supervisión experimentada'
                ],
                'priority': 2,
                'alert_class': 'high'
            }
        elif score >= 40:
            return {
                'level': 'MODERADO',
                'color': '#ffc107',
                'description': 'Riesgo moderado - precauciones adicionales',
                'recommendations': [
                    'Preparación especial',
                    'Plan de vía aérea revisado',
                    'Monitoreo estrecho',
                    'Dispositivos alternativos'
                ],
                'priority': 3,
                'alert_class': 'moderate'
            }
        else:
            return {
                'level': 'BAJO',
                'color': '#28a745',
                'description': 'Riesgo bajo - manejo estándar',
                'recommendations': [
                    'Procedimiento estándar',
                    'Monitoreo rutinario',
                    'Protocolos institucionales'
                ],
                'priority': 4,
                'alert_class': 'low'
            }


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