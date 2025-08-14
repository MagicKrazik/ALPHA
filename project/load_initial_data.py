# load_initial_data.py - Run this in Django shell
from website.models import RiskFactor, AlertRule

def load_initial_risk_factors():
    """Load initial risk factors"""
    
    risk_factors_data = [
        # Airway Risk Factors
        {
            'name': 'Mallampati Alto (III-IV)',
            'category': 'airway',
            'description': 'Clasificación Mallampati III o IV indica mayor dificultad para la intubación',
            'severity_level': 'high'
        },
        {
            'name': 'Obesidad Mórbida',
            'category': 'airway',
            'description': 'IMC ≥ 35 kg/m² aumenta significativamente el riesgo de vía aérea difícil',
            'severity_level': 'high'
        },
        {
            'name': 'Antecedentes de Vía Aérea Difícil',
            'category': 'airway',
            'description': 'Historia previa de dificultad en el manejo de la vía aérea',
            'severity_level': 'critical'
        },
        {
            'name': 'Apertura Bucal Limitada',
            'category': 'airway',
            'description': 'Distancia inter-incisiva < 3 cm',
            'severity_level': 'medium'
        },
        {
            'name': 'Cuello Corto o Grueso',
            'category': 'airway',
            'description': 'Distancia tiro-mentoniana < 6 cm',
            'severity_level': 'medium'
        },
        
        # Cardiovascular Risk Factors
        {
            'name': 'ASA Alto Riesgo (IV-VI)',
            'category': 'cardiac',
            'description': 'Clasificación ASA IV, V o VI indica enfermedad sistémica severa',
            'severity_level': 'critical'
        },
        {
            'name': 'Hipertensión No Controlada',
            'category': 'cardiac',
            'description': 'Presión arterial > 180/110 mmHg',
            'severity_level': 'high'
        },
        {
            'name': 'Cardiopatía Isquémica',
            'category': 'cardiac',
            'description': 'Antecedente de infarto al miocardio o angina',
            'severity_level': 'high'
        },
        {
            'name': 'Edad Avanzada',
            'category': 'cardiac',
            'description': 'Paciente ≥ 70 años',
            'severity_level': 'medium'
        },
        
        # Respiratory Risk Factors
        {
            'name': 'Tabaquismo Activo',
            'category': 'respiratory',
            'description': 'Fumador activo aumenta riesgo de complicaciones respiratorias',
            'severity_level': 'medium'
        },
        {
            'name': 'Apnea del Sueño',
            'category': 'respiratory',
            'description': 'STOP-BANG ≥ 3 sugiere apnea obstructiva del sueño',
            'severity_level': 'high'
        },
        {
            'name': 'Hipoxemia',
            'category': 'respiratory',
            'description': 'SpO2 < 95% en aire ambiente',
            'severity_level': 'high'
        },
        
        # Metabolic Risk Factors
        {
            'name': 'Diabetes Mellitus',
            'category': 'metabolic',
            'description': 'Diabetes con o sin complicaciones',
            'severity_level': 'medium'
        },
        {
            'name': 'Uso de GLP-1',
            'category': 'metabolic',
            'description': 'Uso de agonistas GLP-1 puede retrasar vaciamiento gástrico',
            'severity_level': 'low'
        },
        
        # General Risk Factors
        {
            'name': 'Cirugía de Emergencia',
            'category': 'general',
            'description': 'Ayuno < 6 horas o cirugía urgente',
            'severity_level': 'medium'
        },
        {
            'name': 'Estado Neurológico Alterado',
            'category': 'general',
            'description': 'Glasgow < 15 puntos',
            'severity_level': 'high'
        }
    ]
    
    for factor_data in risk_factors_data:
        factor, created = RiskFactor.objects.get_or_create(
            name=factor_data['name'],
            defaults=factor_data
        )
        if created:
            print(f"Created risk factor: {factor.name}")
        else:
            print(f"Risk factor already exists: {factor.name}")


def load_initial_alert_rules():
    """Load initial alert rules"""
    
    alert_rules_data = [
        {
            'name': 'Vía Aérea Difícil - Alto Riesgo',
            'description': 'Alerta cuando el riesgo de vía aérea difícil es alto',
            'rule_type': 'threshold',
            'rule_config': {
                'field': 'airway_risk_score',
                'operator': '>=',
                'threshold': 70
            },
            'priority': 1
        },
        {
            'name': 'Riesgo General Crítico',
            'description': 'Alerta cuando el riesgo general del paciente es crítico',
            'rule_type': 'threshold',
            'rule_config': {
                'field': 'overall_risk_score',
                'operator': '>=',
                'threshold': 80
            },
            'priority': 1
        },
        {
            'name': 'Combinación Vía Aérea + Cardiovascular',
            'description': 'Alerta cuando hay riesgo alto tanto de vía aérea como cardiovascular',
            'rule_type': 'combination',
            'rule_config': {
                'conditions': [
                    {'field': 'airway_risk_score', 'operator': '>=', 'value': 60},
                    {'field': 'cardiovascular_risk_score', 'operator': '>=', 'value': 60}
                ],
                'logic': 'AND'
            },
            'priority': 2
        },
        {
            'name': 'Alta Probabilidad de Complicaciones',
            'description': 'Alerta cuando la probabilidad de complicaciones es alta',
            'rule_type': 'threshold',
            'rule_config': {
                'field': 'complication_probability',
                'operator': '>=',
                'threshold': 70
            },
            'priority': 2
        },
        {
            'name': 'Intubación Difícil Probable',
            'description': 'Alerta cuando la probabilidad de intubación difícil es alta',
            'rule_type': 'threshold',
            'rule_config': {
                'field': 'difficult_airway_probability',
                'operator': '>=',
                'threshold': 60
            },
            'priority': 2
        },
        {
            'name': 'Paciente ASA IV o Superior',
            'description': 'Alerta para pacientes con clasificación ASA muy alta',
            'rule_type': 'combination',
            'rule_config': {
                'conditions': [
                    {'field': 'cardiovascular_risk_score', 'operator': '>=', 'value': 60}
                ],
                'logic': 'AND'
            },
            'priority': 3
        }
    ]
    
    for rule_data in alert_rules_data:
        rule, created = AlertRule.objects.get_or_create(
            name=rule_data['name'],
            defaults=rule_data
        )
        if created:
            print(f"Created alert rule: {rule.name}")
        else:
            print(f"Alert rule already exists: {rule.name}")


def setup_initial_data():
    """Setup all initial data"""
    print("Loading initial risk factors...")
    load_initial_risk_factors()
    
    print("\nLoading initial alert rules...")
    load_initial_alert_rules()
    
    print("\nInitial data setup completed!")


# Run this function
if __name__ == "__main__":
    setup_initial_data()