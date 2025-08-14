from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid
from django.urls import reverse
import re
from datetime import datetime, timezone
from django.utils import timezone as django_timezone


class Patient(models.Model):
    """
    Core patient model - represents a unique individual patient
    """
    # Identification and linking fields
    id_paciente = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID Paciente")
    )
    
    # Personal information
    nombres = models.CharField(
        max_length=100,
        verbose_name=_("Nombres")
    )
    apellidos = models.CharField(
        max_length=100,
        verbose_name=_("Apellidos")
    )
    fecha_nacimiento = models.DateField(
        verbose_name=_("Fecha de Nacimiento")
    )
    email = models.EmailField(
        verbose_name=_("Correo electrónico"),
        blank=True,
        null=True
    )
    telefono = models.CharField(
        max_length=15,
        verbose_name=_("Teléfono"),
        blank=True,
        null=True
    )
    
    # Metadata
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de Registro")
    )
    ultima_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Última Actualización")
    )
    activo = models.BooleanField(
        default=True,
        verbose_name=_("Activo")
    )
    aceptacion_privacidad = models.BooleanField(
        default=False,
        verbose_name=_("Aceptación de Política de Privacidad")
    )

    class Meta:
        verbose_name = _("Paciente")
        verbose_name_plural = _("Pacientes")
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['nombres', 'apellidos']),
            models.Index(fields=['fecha_nacimiento']),
            models.Index(fields=['fecha_registro'])
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def get_absolute_url(self):
        return reverse('patient-detail', args=[str(self.id_paciente)])

    @property
    def edad(self):
        """Calculate patient age"""
        today = datetime.now().date()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class TreatmentCase(models.Model):
    """
    Represents a single treatment case/hospitalization
    Links patient to specific medical treatment with unique folio
    """
    id_case = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID Caso")
    )
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='treatment_cases',
        verbose_name=_("Paciente")
    )
    
    folio_hospitalizacion = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Folio de Hospitalización")
    )
    
    medico_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='treatment_cases_responsable',
        verbose_name=_("Médico Responsable")
    )
    
    # Additional doctors who can access this case
    medicos_secundarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='treatment_cases_secundarios',
        blank=True,
        verbose_name=_("Médicos Secundarios")
    )
    
    diagnostico_inicial = models.TextField(
        verbose_name=_("Diagnóstico Inicial"),
        blank=True
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name=_("Caso Activo")
    )
    
    fecha_ingreso = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de Ingreso")
    )
    
    fecha_alta = models.DateTimeField(
        verbose_name=_("Fecha de Alta"),
        null=True,
        blank=True
    )
    
    # Barcode field moved here since it's case-specific
    codigo_barras = models.ImageField(
        upload_to='codigos_barra/%Y/%m/',
        verbose_name=_("Código de Barras"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Caso de Tratamiento")
        verbose_name_plural = _("Casos de Tratamiento")
        ordering = ['-fecha_ingreso']
        indexes = [
            models.Index(fields=['folio_hospitalizacion']),
            models.Index(fields=['patient', 'activo']),
            models.Index(fields=['medico_responsable', 'fecha_ingreso'])
        ]

    def __str__(self):
        return f"{self.folio_hospitalizacion} - {self.patient.nombre_completo}"

    def user_has_access(self, user):
        """Check if user has access to this treatment case"""
        return (
            self.medico_responsable == user or
            self.medicos_secundarios.filter(id=user.id).exists() or
            user.is_staff
        )


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'Consulta General'),
        ('technical', 'Soporte Técnico'),
        ('collaboration', 'Propuesta de Colaboración'),
        ('other', 'Otro')
    ]

    name = models.CharField(_('nombre'), max_length=100)
    email = models.EmailField(_('correo electrónico'))
    phone = models.CharField(_('teléfono'), max_length=20, blank=True)
    subject = models.CharField(_('asunto'), max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField(_('mensaje'))
    created_at = models.DateTimeField(_('fecha de envío'), auto_now_add=True)
    is_read = models.BooleanField(_('leído'), default=False)

    class Meta:
        verbose_name = _('Mensaje de Contacto')
        verbose_name_plural = _('Mensajes de Contacto')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name} ({self.created_at.strftime('%d/%m/%Y')})"


# Rule to avoid accents in patient registration fields
def validate_no_accents_or_special_chars(value):
    """Validates that the name does not contain accents or special characters."""
    if not re.match(r'^[a-zA-Z\s]+$', value):
        raise ValidationError(
            _('El nombre sólo puede contener letras y espacios (sin acentos ni caracteres especiales).'),
            code='invalid_nombre'
        )
    

def validate_integer_only(value):
    """Validates that the input is an integer."""
    if not isinstance(value, int):
        try:
            int(value)
        except ValueError:
            raise ValidationError(
                _('Solo se permiten números')
            )     


class MedicoUser(AbstractUser):
    """
    Custom user model for medical professionals participating in the ALPHA Project.
    """
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('usuario'),
        max_length=150,
        unique=True,
        help_text=_('Requerido. 150 caracteres o menos. Letras, números, puntos y guiones bajos solamente.'),
        validators=[username_validator],
        error_messages={
            'unique': _("Ya existe un usuario con este nombre."),
        },
    )

    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("Ya existe un usuario con este correo electrónico."),
        }
    )
    
    nombre = models.CharField(
        _('nombre'),
        max_length=100,
        help_text=_('Nombres del médico')
    )
    
    apellidos = models.CharField(
        _('apellidos'),
        max_length=100,
        help_text=_('Apellidos del médico')
    )
    
    telefono = models.CharField(
        _('teléfono'),
        max_length=17,
        help_text=_('Número de contacto del médico')
    )
    
    class Especialidad(models.TextChoices):
        ANESTESIOLOGIA = 'ANE', _('Anestesiología')
        ANESTESIOLOGIA_PEDIATRICA = 'ANP', _('Anestesiología Pediátrica')
        MEDICINA_CRITICA = 'MEC', _('Medicina Crítica')
        MEDICINA_DOLOR = 'MED', _('Medicina del Dolor')
        OTRA = 'OTR', _('Otra Especialidad')
    
    especialidad = models.CharField(
        _('especialidad'),
        max_length=3,
        choices=Especialidad.choices,
        default=Especialidad.ANESTESIOLOGIA,
    )

    class Meta:
        verbose_name = _('médico')
        verbose_name_plural = _('médicos')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellidos}"


class PreSurgeryForm(models.Model):
    """
    Model for pre-surgery evaluation form containing patient information and initial assessments.
    """
    # Primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Link to TreatmentCase (one-to-one relationship)
    treatment_case = models.OneToOneField(
        TreatmentCase,
        on_delete=models.CASCADE,
        verbose_name=_("Caso de Tratamiento"),
        related_name='pre_surgery_form'
    )

    ASA_CHOICES = [
        (1, 'I'),
        (2, 'II'),
        (3, 'III'),
        (4, 'IV'),
        (5, 'V'),
        (6, 'VI'),
    ]

    MALLAMPATI_CHOICES = [(i, str(i)) for i in range(1, 5)]
    PATIL_ALDRETE_CHOICES = [(i, str(i)) for i in range(1, 5)]
    PROTRUSION_CHOICES = [(i, str(i)) for i in range(1, 5)]
    
    # Medical Information
    fecha_reporte = models.DateField(
        verbose_name="Fecha de Reporte",
        default=django_timezone.now
    )
    medico_tratante = models.CharField(
        max_length=100,
        verbose_name="Médico Tratante"
    )
    diagnostico_preoperatorio = models.TextField(
        verbose_name="Diagnóstico Preoperatorio"
    )
    
    # Physical Measurements
    peso = models.FloatField(verbose_name="Peso (kg)")
    talla = models.FloatField(verbose_name="Talla (cm)")
    imc = models.FloatField(verbose_name="IMC", null=True, blank=True)
    
    # Medical Assessment
    estado_fisico_asa = models.IntegerField(
        choices=ASA_CHOICES,
        verbose_name="Estado Físico ASA"
    )
    comorbilidades = models.TextField(
        blank=True,
        verbose_name="Comorbilidades"
    )
    medicamentos = models.TextField(
        blank=True,
        verbose_name="Medicamentos"
    )
    
    # Pre-surgery Details
    ayuno_hrs = models.FloatField(verbose_name="Ayuno (hrs)")
    uso_glp1 = models.BooleanField(
        default=False,
        verbose_name="Uso de GLP1"
    )
    dosis_glp1 = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Dosis GLP1"
    )
    alergias = models.TextField(
        blank=True,
        verbose_name="Alergias"
    )
    tabaquismo = models.BooleanField(
        default=False,
        verbose_name="Tabaquismo"
    )
    
    # Difficulty Management History
    antecedentes_dificultad = models.BooleanField(
        default=False,
        verbose_name="Antecedentes de Dificultad de Manejo"
    )
    descripcion_dificultad = models.TextField(
        blank=True,
        verbose_name="Descripción de Dificultad"
    )
    
    # Evaluation
    evaluacion_preoperatoria = models.TextField(
        verbose_name="Evaluación Preoperatoria"
    )
    estudios_radiologicos_va = models.ImageField(
        upload_to='estudios_radiologicos/',
        blank=True,
        verbose_name="Estudios Radiológicos VA"
    )
    
    # USG Assessment
    uso_usg_gastrico = models.BooleanField(
        default=False,
        verbose_name="Uso de USG Gástrico"
    )
    usg_gastrico_ml = models.FloatField(
        null=True,
        blank=True,
        verbose_name="USG Gástrico (ml)"
    )
    imagen_usg_gastrico = models.ImageField(
        upload_to='usg_gastrico/',
        blank=True,
        verbose_name="Imagen USG Gástrico"
    )
    
    # Vital Signs
    fc = models.IntegerField(verbose_name="FC")
    ta = models.CharField(max_length=20, verbose_name="TA")
    spo2_aire = models.IntegerField(verbose_name="SpO2 Aire Ambiente")
    spo2_oxigeno = models.IntegerField(verbose_name="SpO2 con Oxígeno")
    glasgow = models.IntegerField(
        verbose_name="Glasgow",
        validators=[MinValueValidator(3), MaxValueValidator(15)]
    )
    
    # Airway Assessment
    mallampati = models.IntegerField(
        choices=MALLAMPATI_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name="Mallampati"
    )
    patil_aldrete = models.IntegerField(
        choices=PATIL_ALDRETE_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name="Patil-Aldrete"
    )
    distancia_inter_incisiva = models.FloatField(
        verbose_name="Distancia Inter-incisiva (cm)"
    )
    distancia_tiro_mentoniana = models.FloatField(
        verbose_name="Distancia Tiro-mentoniana (cm)"
    )
    protrusion_mandibular = models.IntegerField(
        choices=PROTRUSION_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name="Protrusión Mandibular"
    )
    
    # Additional Assessments
    macocha = models.IntegerField(verbose_name="Macocha")
    stop_bang = models.IntegerField(
        verbose_name="Stop Bang",
        validators=[MinValueValidator(0), MaxValueValidator(8)]
    )
    desviacion_traquea = models.FloatField(
        verbose_name="Desviación de la Tráquea (cm)"
    )
    problemas_deglucion = models.BooleanField(
        default=False,
        verbose_name="Problemas de Deglución"
    )
    estridor_laringeo = models.BooleanField(
        default=False,
        verbose_name="Estridor Laríngeo"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pre-Surgery: {self.treatment_case}"

    @property
    def patient(self):
        return self.treatment_case.patient

    @property
    def folio_hospitalizacion(self):
        return self.treatment_case.folio_hospitalizacion

    def save(self, *args, **kwargs):
        # Auto-calculate BMI if not provided
        if self.peso and self.talla and not self.imc:
            height_m = self.talla / 100
            self.imc = round(self.peso / (height_m ** 2), 2)
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        # Validate Glasgow score
        if self.glasgow and (self.glasgow < 3 or self.glasgow > 15):
            raise ValidationError({
                'glasgow': _('El valor de Glasgow debe estar entre 3 y 15')
            })

        # Validate SpO2 values
        for field in ['spo2_aire', 'spo2_oxigeno']:
            value = getattr(self, field, None)
            if value is not None and (value < 0 or value > 100):
                raise ValidationError({
                    field: _('El valor de SpO2 debe estar entre 0 y 100')
                })

    class Meta:
        verbose_name = _("Formulario Pre-Quirúrgico")
        verbose_name_plural = _("Formularios Pre-Quirúrgicos")
        ordering = ['-fecha_reporte']


class PostDuringSurgeryForm(models.Model):
    """
    Model for recording information during and after surgery.
    """
    # Primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Link to the treatment case and pre-surgery form
    treatment_case = models.OneToOneField(
        TreatmentCase,
        on_delete=models.CASCADE,
        verbose_name=_("Caso de Tratamiento"),
        related_name='post_surgery_form'
    )
    
    pre_surgery_form = models.OneToOneField(
        PreSurgeryForm,
        on_delete=models.CASCADE,
        verbose_name=_("Formulario Pre-Quirúrgico"),
        related_name='post_surgery_form'
    )
    
    HAN_CHOICES = [(i, str(i)) for i in range(5)]  # 0-4
    CORMACK_CHOICES = [(i, str(i)) for i in range(1, 5)]  # 1-4
    
    # Location and Personnel
    lugar_problema = models.CharField(
        max_length=200,
        verbose_name="Lugar o Área del Problema"
    )
    presencia_anestesiologo = models.BooleanField(
        verbose_name="Presencia de Anestesiólogo"
    )
    
    # Equipment and Techniques
    tecnica_utilizada = models.CharField(
        max_length=200,
        verbose_name="Técnica Utilizada"
    )
    carro_via_aerea = models.BooleanField(
        verbose_name="Carro de Vía Aérea Difícil Disponible"
    )
    tipo_video_laringoscopia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo de Video-laringoscopía"
    )
    video_laringoscopia = models.FileField(
        upload_to='video_laringoscopia/',
        blank=True,
        verbose_name="Video de Laringoscopía"
    )
    
    # Classifications and Measurements
    clasificacion_han = models.IntegerField(
        choices=HAN_CHOICES,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        verbose_name="Clasificación HAN"
    )
    aditamento_via_aerea = models.CharField(
        max_length=200,
        verbose_name="Aditamento de Vía Aérea"
    )
    tiempo_preoxigenacion = models.IntegerField(
        verbose_name="Tiempo de Pre-oxigenación (minutos)"
    )
    
    # Supraglottic Device
    uso_supraglotico = models.BooleanField(
        verbose_name="Uso de Supraglótico"
    )
    tipo_supraglotico = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tipo de Supraglótico"
    )
    problemas_supragloticos = models.TextField(
        blank=True,
        verbose_name="Problemas con Supraglóticos"
    )
    
    # Intubation Details
    tipo_intubacion = models.CharField(
        max_length=100,
        verbose_name="Tipo de Intubación"
    )
    numero_intentos = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Número de Intentos"
    )
    laringoscopia_directa = models.TextField(
        verbose_name="Laringoscopía Directa"
    )
    cormack = models.IntegerField(
        choices=CORMACK_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name="Cormack"
    )
    pogo = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="POGO (%)"
    )
    
    # Additional Procedures
    intubacion_tecnica_mixta = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Intubación Técnica Mixta"
    )
    intubacion_despierto = models.BooleanField(
        verbose_name="Intubación Despierto"
    )
    descripcion_intubacion_despierto = models.TextField(
        blank=True,
        verbose_name="Descripción Intubación Despierto"
    )
    
    # Anesthesia Details
    tipo_anestesia = models.CharField(
        max_length=200,
        verbose_name="Tipo de Anestesia"
    )
    sedacion = models.CharField(
        max_length=200,
        verbose_name="Sedación"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    cooperacion_paciente = models.CharField(
        max_length=200,
        verbose_name="Cooperación del Paciente"
    )
    
    # Emergency Procedures
    algoritmo_no_intubacion = models.BooleanField(
        default=False,
        verbose_name="Algoritmo No Intubación"
    )
    crico_tiroidotomia = models.BooleanField(
        default=False,
        verbose_name="Crico-tiroidotomía"
    )
    traqueostomia_percutanea = models.BooleanField(
        default=False,
        verbose_name="Traqueostomía Percutánea"
    )
    
    # Outcomes
    complicaciones = models.TextField(
        blank=True,
        verbose_name="Complicaciones"
    )
    resultado_final = models.TextField(
        verbose_name="Resultado Final"
    )
    
    # Media
    fotos_videos = models.FileField(
        upload_to='fotos_videos_cirugia/',
        blank=True,
        verbose_name="Fotos o Videos Relacionados"
    )
    
    # Morbidity and Mortality
    morbilidad = models.BooleanField(default=False)
    descripcion_morbilidad = models.TextField(
        blank=True,
        verbose_name="Descripción Morbilidad"
    )
    mortalidad = models.BooleanField(default=False)
    descripcion_mortalidad = models.TextField(
        blank=True,
        verbose_name="Descripción Mortalidad"
    )
    
    # Medical Personnel
    nombre_anestesiologo = models.CharField(
        max_length=200,
        verbose_name="Nombre del Anestesiólogo"
    )
    cedula_profesional = models.CharField(
        max_length=50,
        verbose_name="Cédula Profesional"
    )
    especialidad = models.CharField(
        max_length=100,
        verbose_name="Especialidad"
    )
    nombre_residente = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre del Residente"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post-Surgery: {self.treatment_case}"

    @property
    def patient(self):
        return self.treatment_case.patient

    @property
    def folio_hospitalizacion(self):
        return self.treatment_case.folio_hospitalizacion

    def clean(self):
        super().clean()
        # Validate POGO score
        if self.pogo is not None and (self.pogo < 0 or self.pogo > 100):
            raise ValidationError({'pogo': _('El valor POGO debe estar entre 0 y 100')})
        
        # Validate number of attempts
        if self.numero_intentos is not None and self.numero_intentos < 1:
            raise ValidationError({'numero_intentos': _('Debe haber al menos un intento')})

    class Meta:
        verbose_name = _("Formulario Post-Quirúrgico")
        verbose_name_plural = _("Formularios Post-Quirúrgicos")
        ordering = ['-created_at']


# ===== ALERT SYSTEM MODELS =====

class RiskFactor(models.Model):
    """
    Defines different risk factors that can be calculated from patient data
    """
    CATEGORY_CHOICES = [
        ('airway', 'Vía Aérea'),
        ('cardiac', 'Cardiovascular'),
        ('respiratory', 'Respiratorio'),
        ('metabolic', 'Metabólico'),
        ('general', 'General'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Bajo'),
        ('medium', 'Moderado'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre del Factor")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(verbose_name="Descripción")
    severity_level = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Factor de Riesgo"
        verbose_name_plural = "Factores de Riesgo"

    def __str__(self):
        return f"{self.name} ({self.get_severity_level_display()})"


class AlertRule(models.Model):
    """
    Defines rules for generating alerts based on patient data
    """
    RULE_TYPE_CHOICES = [
        ('threshold', 'Umbral'),
        ('combination', 'Combinación'),
        ('trend', 'Tendencia'),
        ('ml_prediction', 'Predicción ML'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nombre de la Regla")
    description = models.TextField(verbose_name="Descripción")
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    
    # JSON field to store rule configuration
    rule_config = models.JSONField(
        verbose_name="Configuración de la Regla",
        help_text="JSON con la configuración específica de la regla"
    )
    
    risk_factors = models.ManyToManyField(
        RiskFactor,
        related_name='alert_rules',
        blank=True
    )
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1, help_text="1=Máxima, 5=Mínima")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Regla de Alerta"
        verbose_name_plural = "Reglas de Alerta"
        ordering = ['priority', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class PatientRiskProfile(models.Model):
    """
    Stores calculated risk profile for each patient/treatment case
    """
    treatment_case = models.OneToOneField(
        TreatmentCase,
        on_delete=models.CASCADE,
        related_name='risk_profile'
    )
    
    # Overall risk scores
    airway_risk_score = models.FloatField(null=True, blank=True)
    cardiovascular_risk_score = models.FloatField(null=True, blank=True)
    respiratory_risk_score = models.FloatField(null=True, blank=True)
    overall_risk_score = models.FloatField(null=True, blank=True)
    
    # Risk categories
    difficult_airway_probability = models.FloatField(null=True, blank=True)
    complication_probability = models.FloatField(null=True, blank=True)
    
    # Associated risk factors
    identified_risk_factors = models.ManyToManyField(
        RiskFactor,
        related_name='patient_profiles',
        blank=True
    )
    
    # Calculation metadata
    last_calculated = models.DateTimeField(auto_now=True)
    calculation_version = models.CharField(max_length=20, default="1.0")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Perfil de Riesgo del Paciente"
        verbose_name_plural = "Perfiles de Riesgo de Pacientes"

    def __str__(self):
        return f"Risk Profile: {self.treatment_case}"

    @property
    def risk_level(self):
        """Determine overall risk level based on scores"""
        if not self.overall_risk_score:
            return 'unknown'
        
        if self.overall_risk_score >= 80:
            return 'critical'
        elif self.overall_risk_score >= 60:
            return 'high'
        elif self.overall_risk_score >= 40:
            return 'medium'
        else:
            return 'low'


class RiskAlert(models.Model):
    """
    Stores generated alerts for treatment cases
    """
    ALERT_TYPE_CHOICES = [
        ('preventive', 'Preventiva'),
        ('warning', 'Advertencia'),
        ('critical', 'Crítica'),
        ('informational', 'Informativa'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('acknowledged', 'Reconocida'),
        ('resolved', 'Resuelta'),
        ('dismissed', 'Descartada'),
    ]

    treatment_case = models.ForeignKey(
        TreatmentCase,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    
    alert_rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,
        related_name='generated_alerts'
    )
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    
    # Risk assessment
    risk_score = models.FloatField(null=True, blank=True)
    confidence_level = models.FloatField(null=True, blank=True)
    
    # Recommendations
    recommendations = models.JSONField(
        null=True, blank=True,
        verbose_name="Recomendaciones"
    )
    
    # Alert lifecycle
    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='acknowledged_alerts'
    )
    
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resolved_alerts'
    )

    class Meta:
        verbose_name = "Alerta de Riesgo"
        verbose_name_plural = "Alertas de Riesgo"
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['treatment_case', 'status']),
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['triggered_at']),
        ]

    def __str__(self):
        return f"Alert: {self.title} - {self.treatment_case}"

    def acknowledge(self, user):
        """Mark alert as acknowledged"""
        self.status = 'acknowledged'
        self.acknowledged_by = user
        self.acknowledged_at = django_timezone.now()
        self.save()

    def resolve(self, user):
        """Mark alert as resolved"""
        self.status = 'resolved'
        self.resolved_by = user
        self.resolved_at = django_timezone.now()
        self.save()


class AlertNotification(models.Model):
    """
    Stores notifications sent to users about alerts
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('delivered', 'Entregado'),
        ('failed', 'Falló'),
    ]

    alert = models.ForeignKey(
        RiskAlert,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_notifications'
    )
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación de Alerta"
        verbose_name_plural = "Notificaciones de Alerta"
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification: {self.notification_type} to {self.recipient.username}"


# Signal handlers for automatic risk calculation
@receiver(post_save, sender=PreSurgeryForm)
def calculate_presurgery_risk(sender, instance, created, **kwargs):
    """Calculate risk profile when pre-surgery form is saved"""
    if created:
        from .tasks import calculate_patient_risk_profile
        # Queue background task for risk calculation
        calculate_patient_risk_profile.delay(instance.treatment_case.id)


@receiver(post_save, sender=PostDuringSurgeryForm)
def update_postsurgery_risk(sender, instance, created, **kwargs):
    """Update risk profile when post-surgery form is saved"""
    from .tasks import calculate_patient_risk_profile
    # Queue background task for risk calculation update
    calculate_patient_risk_profile.delay(instance.treatment_case.id)