# tasks.py
"""
Background tasks for risk calculation and alert generation
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import (
    TreatmentCase, PreSurgeryForm, PostDuringSurgeryForm,
    PatientRiskProfile, RiskAlert, AlertRule, RiskFactor,
    AlertNotification
)
import logging
import json

logger = logging.getLogger(__name__)


@shared_task
def calculate_patient_risk_profile(treatment_case_id):
    """
    Calculate comprehensive risk profile for a patient/treatment case
    """
    try:
        treatment_case = TreatmentCase.objects.get(id=treatment_case_id)
        
        # Get or create risk profile
        risk_profile, created = PatientRiskProfile.objects.get_or_create(
            treatment_case=treatment_case
        )
        
        # Get pre-surgery form if exists
        try:
            pre_surgery = treatment_case.pre_surgery_form
        except PreSurgeryForm.DoesNotExist:
            logger.warning(f"No pre-surgery form found for case {treatment_case_id}")
            return
        
        # Calculate airway risk score
        airway_risk = calculate_airway_risk(pre_surgery)
        risk_profile.airway_risk_score = airway_risk
        
        # Calculate cardiovascular risk
        cardiovascular_risk = calculate_cardiovascular_risk(pre_surgery)
        risk_profile.cardiovascular_risk_score = cardiovascular_risk
        
        # Calculate respiratory risk
        respiratory_risk = calculate_respiratory_risk(pre_surgery)
        risk_profile.respiratory_risk_score = respiratory_risk
        
        # Calculate overall risk score (weighted average)
        risk_profile.overall_risk_score = (
            airway_risk * 0.4 +
            cardiovascular_risk * 0.3 +
            respiratory_risk * 0.3
        )
        
        # Calculate specific probabilities
        risk_profile.difficult_airway_probability = calculate_difficult_airway_probability(pre_surgery)
        risk_profile.complication_probability = calculate_complication_probability(pre_surgery)
        
        # Identify risk factors
        risk_factors = identify_risk_factors(pre_surgery)
        risk_profile.identified_risk_factors.set(risk_factors)
        
        risk_profile.save()
        
        # Generate alerts based on risk profile
        generate_risk_alerts.delay(treatment_case_id)
        
        logger.info(f"Risk profile calculated for case {treatment_case_id}")
        
    except Exception as e:
        logger.error(f"Error calculating risk profile for case {treatment_case_id}: {str(e)}")


def calculate_airway_risk(pre_surgery):
    """
    Calculate airway management risk score (0-100)
    """
    risk_score = 0
    
    # Mallampati score (higher = more risk)
    mallampati_scores = {1: 0, 2: 20, 3: 50, 4: 80}
    risk_score += mallampati_scores.get(pre_surgery.mallampati, 0)
    
    # BMI factor
    if pre_surgery.imc:
        if pre_surgery.imc >= 35:
            risk_score += 30
        elif pre_surgery.imc >= 30:
            risk_score += 20
        elif pre_surgery.imc >= 25:
            risk_score += 10
    
    # Patil-Aldrete score
    patil_scores = {1: 40, 2: 20, 3: 10, 4: 0}
    risk_score += patil_scores.get(pre_surgery.patil_aldrete, 0)
    
    # Distance measurements
    if pre_surgery.distancia_inter_incisiva < 3:
        risk_score += 25
    elif pre_surgery.distancia_inter_incisiva < 4:
        risk_score += 15
    
    if pre_surgery.distancia_tiro_mentoniana < 6:
        risk_score += 20
    elif pre_surgery.distancia_tiro_mentoniana < 7:
        risk_score += 10
    
    # History of difficult airway
    if pre_surgery.antecedentes_dificultad:
        risk_score += 40
    
    # Additional factors
    if pre_surgery.problemas_deglucion:
        risk_score += 15
    
    if pre_surgery.estridor_laringeo:
        risk_score += 25
    
    # STOP-BANG score (sleep apnea risk)
    if pre_surgery.stop_bang >= 5:
        risk_score += 20
    elif pre_surgery.stop_bang >= 3:
        risk_score += 10
    
    # Neck deviation
    if pre_surgery.desviacion_traquea > 2:
        risk_score += 15
    
    return min(risk_score, 100)  # Cap at 100


def calculate_cardiovascular_risk(pre_surgery):
    """
    Calculate cardiovascular risk score (0-100)
    """
    risk_score = 0
    
    # ASA score
    asa_scores = {1: 0, 2: 10, 3: 30, 4: 60, 5: 80, 6: 90}
    risk_score += asa_scores.get(pre_surgery.estado_fisico_asa, 0)
    
    # Age factor (from patient)
    age = pre_surgery.patient.edad
    if age >= 80:
        risk_score += 30
    elif age >= 70:
        risk_score += 20
    elif age >= 60:
        risk_score += 10
    
    # Vital signs
    if pre_surgery.fc > 100 or pre_surgery.fc < 50:
        risk_score += 15
    
    # Parse blood pressure
    try:
        if '/' in pre_surgery.ta:
            systolic, diastolic = map(int, pre_surgery.ta.split('/'))
            if systolic > 180 or diastolic > 110:
                risk_score += 25
            elif systolic > 160 or diastolic > 100:
                risk_score += 15
    except:
        pass
    
    # Comorbidities analysis
    if pre_surgery.comorbilidades:
        comorbidities = pre_surgery.comorbilidades.lower()
        cardiovascular_terms = [
            'hipertension', 'diabetes', 'infarto', 'cardiaco', 'coronario',
            'arritmia', 'insuficiencia', 'angina', 'marcapasos'
        ]
        for term in cardiovascular_terms:
            if term in comorbidities:
                risk_score += 15
                break
    
    return min(risk_score, 100)


def calculate_respiratory_risk(pre_surgery):
    """
    Calculate respiratory risk score (0-100)
    """
    risk_score = 0
    
    # SpO2 levels
    if pre_surgery.spo2_aire < 90:
        risk_score += 40
    elif pre_surgery.spo2_aire < 95:
        risk_score += 20
    
    # Smoking history
    if pre_surgery.tabaquismo:
        risk_score += 20
    
    # BMI factor (obesity affects respiratory function)
    if pre_surgery.imc and pre_surgery.imc >= 35:
        risk_score += 15
    
    # STOP-BANG (sleep apnea)
    if pre_surgery.stop_bang >= 5:
        risk_score += 25
    elif pre_surgery.stop_bang >= 3:
        risk_score += 15
    
    # Comorbidities analysis
    if pre_surgery.comorbilidades:
        comorbidities = pre_surgery.comorbilidades.lower()
        respiratory_terms = [
            'asma', 'epoc', 'apnea', 'respiratorio', 'pulmonar',
            'bronquitis', 'enfisema', 'fibrosis'
        ]
        for term in respiratory_terms:
            if term in comorbidities:
                risk_score += 20
                break
    
    # Glasgow score (neurological impact on respiratory)
    if pre_surgery.glasgow < 13:
        risk_score += 20
    elif pre_surgery.glasgow < 15:
        risk_score += 10
    
    return min(risk_score, 100)


def calculate_difficult_airway_probability(pre_surgery):
    """
    Calculate probability of difficult airway (0-100%)
    """
    # Base probability from multiple predictors
    probability = 0
    
    # Mallampati (strong predictor)
    mallampati_prob = {1: 5, 2: 15, 3: 35, 4: 65}
    probability += mallampati_prob.get(pre_surgery.mallampati, 0)
    
    # Anatomical measurements
    if pre_surgery.distancia_inter_incisiva < 3:
        probability += 30
    
    if pre_surgery.distancia_tiro_mentoniana < 6:
        probability += 25
    
    # Previous difficulty
    if pre_surgery.antecedentes_dificultad:
        probability += 50
    
    # BMI
    if pre_surgery.imc and pre_surgery.imc >= 35:
        probability += 20
    
    # MACOCHA score (if high)
    if pre_surgery.macocha >= 3:
        probability += 25
    
    return min(probability, 100)


def calculate_complication_probability(pre_surgery):
    """
    Calculate probability of complications (0-100%)
    """
    probability = 0
    
    # ASA score is strong predictor
    asa_prob = {1: 5, 2: 15, 3: 35, 4: 60, 5: 85, 6: 95}
    probability += asa_prob.get(pre_surgery.estado_fisico_asa, 0)
    
    # Age factor
    age = pre_surgery.patient.edad
    if age >= 80:
        probability += 25
    elif age >= 70:
        probability += 15
    elif age >= 60:
        probability += 10
    
    # Emergency surgery (short fasting time)
    if pre_surgery.ayuno_hrs < 6:
        probability += 15
    
    # Multiple comorbidities
    if pre_surgery.comorbilidades and len(pre_surgery.comorbilidades.split(',')) > 2:
        probability += 20
    
    # Poor functional status indicators
    if pre_surgery.glasgow < 15:
        probability += 15
    
    # Respiratory compromise
    if pre_surgery.spo2_aire < 95:
        probability += 20
    
    return min(probability, 100)


def identify_risk_factors(pre_surgery):
    """
    Identify specific risk factors present in the patient
    """
    risk_factors = []
    
    # Get all active risk factors
    all_factors = RiskFactor.objects.filter(is_active=True)
    
    for factor in all_factors:
        if should_apply_risk_factor(factor, pre_surgery):
            risk_factors.append(factor)
    
    return risk_factors


def should_apply_risk_factor(risk_factor, pre_surgery):
    """
    Determine if a specific risk factor applies to the patient
    """
    factor_name = risk_factor.name.lower()
    
    # Airway-related factors
    if 'mallampati' in factor_name and 'alto' in factor_name:
        return pre_surgery.mallampati >= 3
    
    if 'obesidad' in factor_name:
        return pre_surgery.imc and pre_surgery.imc >= 30
    
    if 'via aerea dificil' in factor_name:
        return pre_surgery.antecedentes_dificultad
    
    if 'apertura bucal' in factor_name:
        return pre_surgery.distancia_inter_incisiva < 3
    
    # Cardiovascular factors
    if 'asa alto' in factor_name:
        return pre_surgery.estado_fisico_asa >= 4
    
    if 'hipertension' in factor_name and pre_surgery.comorbilidades:
        return 'hipertension' in pre_surgery.comorbilidades.lower()
    
    # Respiratory factors
    if 'tabaquismo' in factor_name:
        return pre_surgery.tabaquismo
    
    if 'apnea' in factor_name:
        return pre_surgery.stop_bang >= 3
    
    if 'hipoxemia' in factor_name:
        return pre_surgery.spo2_aire < 95
    
    # Metabolic factors
    if 'diabetes' in factor_name and pre_surgery.comorbilidades:
        return 'diabetes' in pre_surgery.comorbilidades.lower()
    
    if 'glp1' in factor_name:
        return pre_surgery.uso_glp1
    
    # Age-related factors
    if 'edad avanzada' in factor_name:
        return pre_surgery.patient.edad >= 70
    
    return False


@shared_task
def generate_risk_alerts(treatment_case_id):
    """
    Generate alerts based on patient risk profile and active rules
    """
    try:
        treatment_case = TreatmentCase.objects.get(id=treatment_case_id)
        risk_profile = treatment_case.risk_profile
        
        # Get all active alert rules
        active_rules = AlertRule.objects.filter(is_active=True)
        
        for rule in active_rules:
            if should_trigger_alert(rule, risk_profile):
                create_alert(rule, treatment_case, risk_profile)
        
        logger.info(f"Alerts generated for case {treatment_case_id}")
        
    except Exception as e:
        logger.error(f"Error generating alerts for case {treatment_case_id}: {str(e)}")


def should_trigger_alert(rule, risk_profile):
    """
    Determine if an alert rule should trigger based on the risk profile
    """
    try:
        config = rule.rule_config
        rule_type = rule.rule_type
        
        if rule_type == 'threshold':
            return check_threshold_rule(config, risk_profile)
        elif rule_type == 'combination':
            return check_combination_rule(config, risk_profile)
        elif rule_type == 'trend':
            return check_trend_rule(config, risk_profile)
        elif rule_type == 'ml_prediction':
            return check_ml_prediction_rule(config, risk_profile)
        
        return False
        
    except Exception as e:
        logger.error(f"Error evaluating rule {rule.id}: {str(e)}")
        return False


def check_threshold_rule(config, risk_profile):
    """
    Check if threshold-based rule should trigger
    Example config: {
        "field": "overall_risk_score",
        "operator": ">=",
        "threshold": 70
    }
    """
    field = config.get('field')
    operator = config.get('operator')
    threshold = config.get('threshold')
    
    if not all([field, operator, threshold]):
        return False
    
    value = getattr(risk_profile, field, None)
    if value is None:
        return False
    
    if operator == '>=':
        return value >= threshold
    elif operator == '>':
        return value > threshold
    elif operator == '<=':
        return value <= threshold
    elif operator == '<':
        return value < threshold
    elif operator == '==':
        return value == threshold
    
    return False


def check_combination_rule(config, risk_profile):
    """
    Check if combination rule should trigger
    Example config: {
        "conditions": [
            {"field": "airway_risk_score", "operator": ">=", "value": 60},
            {"field": "difficult_airway_probability", "operator": ">=", "value": 50}
        ],
        "logic": "AND"  # or "OR"
    }
    """
    conditions = config.get('conditions', [])
    logic = config.get('logic', 'AND')
    
    results = []
    for condition in conditions:
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if not all([field, operator, value is not None]):
            results.append(False)
            continue
        
        field_value = getattr(risk_profile, field, None)
        if field_value is None:
            results.append(False)
            continue
        
        if operator == '>=':
            results.append(field_value >= value)
        elif operator == '>':
            results.append(field_value > value)
        elif operator == '<=':
            results.append(field_value <= value)
        elif operator == '<':
            results.append(field_value < value)
        elif operator == '==':
            results.append(field_value == value)
        else:
            results.append(False)
    
    if logic == 'AND':
        return all(results)
    elif logic == 'OR':
        return any(results)
    
    return False


def check_trend_rule(config, risk_profile):
    """
    Check trend-based rules (for future implementation)
    """
    # This would require historical data analysis
    # For now, return False
    return False


def check_ml_prediction_rule(config, risk_profile):
    """
    Check ML prediction-based rules (for future implementation)
    """
    # This would use trained ML models
    # For now, return False
    return False


def create_alert(rule, treatment_case, risk_profile):
    """
    Create a new risk alert
    """
    # Check if similar alert already exists and is active
    existing_alert = RiskAlert.objects.filter(
        treatment_case=treatment_case,
        alert_rule=rule,
        status='active'
    ).first()
    
    if existing_alert:
        return  # Don't create duplicate alerts
    
    # Determine alert type based on risk level
    overall_risk = risk_profile.overall_risk_score or 0
    if overall_risk >= 80:
        alert_type = 'critical'
    elif overall_risk >= 60:
        alert_type = 'warning'
    elif overall_risk >= 40:
        alert_type = 'preventive'
    else:
        alert_type = 'informational'
    
    # Generate alert message
    title, message = generate_alert_message(rule, risk_profile)
    
    # Generate recommendations
    recommendations = generate_recommendations(rule, risk_profile)
    
    # Create the alert
    alert = RiskAlert.objects.create(
        treatment_case=treatment_case,
        alert_rule=rule,
        alert_type=alert_type,
        title=title,
        message=message,
        risk_score=overall_risk,
        confidence_level=calculate_confidence_level(rule, risk_profile),
        recommendations=recommendations
    )
    
    # Send notifications
    send_alert_notifications.delay(alert.id)
    
    return alert


def generate_alert_message(rule, risk_profile):
    """
    Generate appropriate alert title and message
    """
    rule_name = rule.name
    overall_risk = risk_profile.overall_risk_score or 0
    
    if 'vía aérea' in rule_name.lower():
        title = "Alerta de Vía Aérea Difícil"
        message = f"El paciente presenta un riesgo elevado ({overall_risk:.0f}%) de vía aérea difícil. "
        message += f"Probabilidad de dificultad: {risk_profile.difficult_airway_probability:.0f}%"
    
    elif 'cardiovascular' in rule_name.lower():
        title = "Alerta de Riesgo Cardiovascular"
        message = f"El paciente presenta riesgo cardiovascular elevado ({risk_profile.cardiovascular_risk_score:.0f}%). "
        message += "Se recomienda evaluación cardiológica y monitoreo continuo."
    
    elif 'complicación' in rule_name.lower():
        title = "Alerta de Riesgo de Complicaciones"
        message = f"Probabilidad elevada de complicaciones ({risk_profile.complication_probability:.0f}%). "
        message += "Se sugiere preparación para manejo de complicaciones."
    
    else:
        title = f"Alerta: {rule_name}"
        message = f"Se ha detectado un factor de riesgo que requiere atención. Riesgo general: {overall_risk:.0f}%"
    
    return title, message


def generate_recommendations(rule, risk_profile):
    """
    Generate specific recommendations based on the alert
    """
    recommendations = []
    rule_name = rule.name.lower()
    
    if 'vía aérea' in rule_name:
        recommendations.extend([
            "Preparar carro de vía aérea difícil",
            "Considerar videolaringoscopía",
            "Tener disponible máscara laríngea",
            "Preparar material para vía aérea quirúrgica",
            "Considerar intubación con paciente despierto si es necesario"
        ])
    
    if 'cardiovascular' in rule_name:
        recommendations.extend([
            "Monitoreo cardiovascular continuo",
            "Optimizar estado hemodinámico preoperatorio",
            "Considerar consulta cardiológica",
            "Preparar medicamentos vasoactivos",
            "Monitoreo invasivo si está indicado"
        ])
    
    if risk_profile.overall_risk_score and risk_profile.overall_risk_score >= 70:
        recommendations.extend([
            "Informar al paciente sobre riesgos elevados",
            "Documentar consentimiento informado detallado",
            "Considerar diferir cirugía si es posible",
            "Preparar equipo de reanimación",
            "Notificar a equipo quirúrgico sobre riesgos"
        ])
    
    return recommendations


def calculate_confidence_level(rule, risk_profile):
    """
    Calculate confidence level for the alert (0-100%)
    """
    # Base confidence on number of contributing factors
    contributing_factors = 0
    total_factors = 0
    
    # Check each risk score component
    if risk_profile.airway_risk_score:
        total_factors += 1
        if risk_profile.airway_risk_score > 50:
            contributing_factors += 1
    
    if risk_profile.cardiovascular_risk_score:
        total_factors += 1
        if risk_profile.cardiovascular_risk_score > 50:
            contributing_factors += 1
    
    if risk_profile.respiratory_risk_score:
        total_factors += 1
        if risk_profile.respiratory_risk_score > 50:
            contributing_factors += 1
    
    # Number of identified risk factors
    risk_factor_count = risk_profile.identified_risk_factors.count()
    if risk_factor_count > 0:
        total_factors += 1
        if risk_factor_count >= 3:
            contributing_factors += 1
    
    if total_factors == 0:
        return 50  # Default confidence
    
    confidence = (contributing_factors / total_factors) * 100
    return min(max(confidence, 30), 95)  # Keep between 30-95%


@shared_task
def send_alert_notifications(alert_id):
    """
    Send notifications for a new alert
    """
    try:
        alert = RiskAlert.objects.get(id=alert_id)
        treatment_case = alert.treatment_case
        
        # Get users to notify
        users_to_notify = []
        users_to_notify.append(treatment_case.medico_responsable)
        users_to_notify.extend(treatment_case.medicos_secundarios.all())
        
        for user in users_to_notify:
            # Create in-app notification
            AlertNotification.objects.create(
                alert=alert,
                recipient=user,
                notification_type='in_app',
                status='sent',
                sent_at=timezone.now()
            )
            
            # Send email notification for critical alerts
            if alert.alert_type == 'critical':
                send_email_notification.delay(alert_id, user.id)
        
        logger.info(f"Notifications sent for alert {alert_id}")
        
    except Exception as e:
        logger.error(f"Error sending notifications for alert {alert_id}: {str(e)}")


@shared_task
def send_email_notification(alert_id, user_id):
    """
    Send email notification for critical alerts
    """
    try:
        alert = RiskAlert.objects.get(id=alert_id)
        user = alert.treatment_case.medico_responsable.__class__.objects.get(id=user_id)
        
        subject = f"ALPHA - Alerta Crítica: {alert.title}"
        message = f"""
        Estimado Dr. {user.get_full_name()},
        
        Se ha generado una alerta crítica para el paciente:
        
        Paciente: {alert.treatment_case.patient.nombre_completo}
        Folio: {alert.treatment_case.folio_hospitalizacion}
        Alerta: {alert.title}
        
        Mensaje: {alert.message}
        
        Nivel de Riesgo: {alert.risk_score:.0f}%
        Confianza: {alert.confidence_level:.0f}%
        
        Por favor, revise inmediatamente el caso en el sistema ALPHA.
        
        Saludos,
        Sistema ALPHA
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
        
        # Update notification status
        notification = AlertNotification.objects.filter(
            alert=alert,
            recipient=user,
            notification_type='email'
        ).first()
        
        if notification:
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()
        
        logger.info(f"Email notification sent for alert {alert_id} to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")


@shared_task
def cleanup_old_alerts():
    """
    Clean up old resolved alerts (run daily)
    """
    try:
        # Delete resolved alerts older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        old_alerts = RiskAlert.objects.filter(
            status='resolved',
            resolved_at__lt=cutoff_date
        )
        
        count = old_alerts.count()
        old_alerts.delete()
        
        logger.info(f"Cleaned up {count} old alerts")
        
    except Exception as e:
        logger.error(f"Error cleaning up old alerts: {str(e)}")


@shared_task
def update_risk_profiles():
    """
    Update all risk profiles (run weekly)
    """
    try:
        # Get all active treatment cases with pre-surgery forms
        active_cases = TreatmentCase.objects.filter(
            activo=True,
            pre_surgery_form__isnull=False
        )
        
        for case in active_cases:
            calculate_patient_risk_profile.delay(case.id)
        
        logger.info(f"Queued risk profile updates for {active_cases.count()} cases")
        
    except Exception as e:
        logger.error(f"Error updating risk profiles: {str(e)}")