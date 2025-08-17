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


class Patient(models.Model):
    """
    Patient model for storing patient information
    """
    # Identification and linking fields
    id_paciente = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID Paciente")
    )
    folio_hospitalizacion = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Folio Hospitalización")
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
    
    # Medical relationship
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("Médico Tratante")
    )
    
    # Barcode field
    codigo_barras = models.ImageField(
        upload_to='codigos_barra/%Y/%m/',
        verbose_name=_("Código de Barras")
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

    class Meta:
        verbose_name = _("Paciente")
        verbose_name_plural = _("Pacientes")
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['folio_hospitalizacion']),
            models.Index(fields=['medico', 'fecha_registro'])
        ]

    def __str__(self):
        return f"{self.folio_hospitalizacion} - {self.nombres} {self.apellidos}"

    def get_absolute_url(self):
        return reverse('patient-detail', args=[str(self.id_paciente)])
    
    # Add to Patient model for better folio validation
    def clean(self):
        super().clean()
        if self.folio_hospitalizacion:
            # Ensure folio is uppercase and properly formatted
            self.folio_hospitalizacion = self.folio_hospitalizacion.upper().strip()
            
            # Check for duplicate folios
            existing = Patient.objects.filter(
                folio_hospitalizacion=self.folio_hospitalizacion
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError({'folio_hospitalizacion': 'Este folio ya existe'})



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
    
    def get_especialidad_display(self):
        """Return the display name for the specialty"""
        specialty_dict = {
            'ANE': 'Anestesiología',
            'ANP': 'Anestesiología Pediátrica', 
            'MEC': 'Medicina Crítica',
            'MED': 'Medicina del Dolor',
            'OTR': 'Otra Especialidad'
        }
        return specialty_dict.get(self.especialidad, self.especialidad)

class PreSurgeryForm(models.Model):
    """
    Model for pre-surgery evaluation form containing patient information and initial assessments.
    """
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

    # Primary Key
    folio_hospitalizacion = models.CharField(
        max_length=50, 
        primary_key=True,
        verbose_name="Folio Hospitalización"
    )
    
    # Patient Information
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    medico = models.CharField(max_length=100, verbose_name="Médico")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    codigo_barras = models.ImageField(
        upload_to='codigos_barra/',
        verbose_name="Código de Barras"
    )
    
    # Medical Information
    fecha_reporte = models.DateField(verbose_name="Fecha de Reporte")
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
    imc = models.FloatField(verbose_name="IMC")
    
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
    ayuno_hrs = models.IntegerField(verbose_name="Ayuno (hrs)")
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
    usg_gastrico_ml = models.IntegerField(
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
    ta = models.TextField(verbose_name="TA")
    spo2_aire = models.IntegerField(verbose_name="SpO2 Aire Ambiente")
    spo2_oxigeno = models.IntegerField(verbose_name="SpO2 con Oxígeno")
    glasgow = models.IntegerField(verbose_name="Glasgow")
    
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
    stop_bang = models.IntegerField(verbose_name="Stop Bang")
    desviacion_traquea = models.IntegerField(
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

    def __str__(self):
        return f"{self.folio_hospitalizacion} - {self.nombres} {self.apellidos}"

    class Meta:
        verbose_name = _("Pre-Surgery Form")
        verbose_name_plural = _("Pre-Surgery Forms")


class PostDuringSurgeryForm(models.Model):
    """
    Model for recording information during and after surgery.
    """
    HAN_CHOICES = [(i, str(i)) for i in range(5)]  # 0-4
    CORMACK_CHOICES = [(i, str(i)) for i in range(1, 5)]  # 1-4

    # Foreign Key to PreSurgeryForm
    folio_hospitalizacion = models.OneToOneField(
        PreSurgeryForm,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Folio Hospitalización",
        related_name='post_surgery_form'  # Add this if not present
    )
    
    # Location and Personnel
    lugar_problema = models.CharField( #check
        max_length=200,
        verbose_name="Lugar o Área del Problema"
    )
    presencia_anestesiologo = models.BooleanField( #check
        verbose_name="Presencia de Anestesiólogo"
    )
    
    # Equipment and Techniques
    tecnica_utilizada = models.CharField( #check
        max_length=200,
        verbose_name="Técnica Utilizada"
    )
    carro_via_aerea = models.BooleanField( #check
        verbose_name="Carro de Vía Aérea Difícil Disponible"
    )
    tipo_video_laringoscopia = models.CharField( #check 
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
    clasificacion_han = models.IntegerField( #check
        choices=HAN_CHOICES,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        verbose_name="Clasificación HAN"
    )
    aditamento_via_aerea = models.CharField( #check
        max_length=200,
        verbose_name="Aditamento de Vía Aérea"
    )
    tiempo_preoxigenacion = models.IntegerField( #check
        verbose_name="Tiempo de Pre-oxigenación (minutos)"
    )
    
    # Supraglottic Device
    uso_supraglotico = models.BooleanField( #check
        verbose_name="Uso de Supraglótico"
    )
    tipo_supraglotico = models.CharField( #check
        max_length=100,
        blank=True,
        verbose_name="Tipo de Supraglótico"
    )
    problemas_supragloticos = models.TextField( #check
        blank=True,
        verbose_name="Problemas con Supraglóticos"
    )
    
    # Intubation Details
    tipo_intubacion = models.CharField( #check
        max_length=100,
        verbose_name="Tipo de Intubación"
    )
    numero_intentos = models.IntegerField( #check
        validators=[MinValueValidator(1)],
        verbose_name="Número de Intentos"
    )
    laringoscopia_directa = models.TextField( #check
        verbose_name="Laringoscopía Directa"
    )
    cormack = models.IntegerField( #check
        choices=CORMACK_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name="Cormack"
    )
    pogo = models.FloatField( #check
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="POGO (%)"
    )
    
    # Additional Procedures
    intubacion_tecnica_mixta = models.CharField(  #check
        max_length=200,
        blank=True,
        verbose_name="Intubación Técnica Mixta"
    )
    intubacion_despierto = models.BooleanField( #check
        verbose_name="Intubación Despierto"
    )
    descripcion_intubacion_despierto = models.TextField( #check
        blank=True,
        verbose_name="Descripción Intubación Despierto"
    )
    
    # Anesthesia Details
    tipo_anestesia = models.CharField( #check
        max_length=200,
        verbose_name="Tipo de Anestesia"
    )
    sedacion = models.CharField( #check
        max_length=200,
        verbose_name="Sedación"
    )
    observaciones = models.TextField( # no salio en la pagina
        blank=True,
        verbose_name="Observaciones"
    )
    cooperacion_paciente = models.CharField( #check
        max_length=200,
        verbose_name="Cooperación del Paciente"
    )
    
    # Emergency Procedures
    algoritmo_no_intubacion = models.BooleanField( # no salio en la pagina
        verbose_name="Algoritmo No Intubación"
    )
    crico_tiroidotomia = models.BooleanField( # no salio en la pagina
        verbose_name="Crico-tiroidotomía"
    )
    traqueostomia_percutanea = models.BooleanField( # no salio en la pagina
        verbose_name="Traqueostomía Percutánea"
    )
    
    # Outcomes
    complicaciones = models.TextField( #check
        blank=True,
        verbose_name="Complicaciones"
    )
    resultado_final = models.TextField( #check
        verbose_name="Resultado Final"
    )
    
    # Media
    fotos_videos = models.FileField( # no salio en la pagina
        upload_to='fotos_videos_cirugia/',
        blank=True,
        verbose_name="Fotos o Videos Relacionados"
    )
    
    # Morbidity and Mortality
    morbilidad = models.BooleanField(default=False) 
    descripcion_morbilidad = models.TextField( #check
        blank=True,
        verbose_name="Descripción Morbilidad"
    )
    mortalidad = models.BooleanField(default=False)
    descripcion_mortalidad = models.TextField(
        blank=True,
        verbose_name="Descripción Mortalidad"
    )
    
    # Medical Personnel
    nombre_anestesiologo = models.CharField( #check
        max_length=200,
        verbose_name="Nombre del Anestesiólogo"
    )
    cedula_profesional = models.CharField( #check
        max_length=50,
        verbose_name="Cédula Profesional"
    )
    especialidad = models.CharField( #check
        max_length=100,
        verbose_name="Especialidad"
    )
    nombre_residente = models.CharField( #check
        max_length=200,
        verbose_name="Nombre del Residente"
    )

    def __str__(self):
        return f"Post-Surgery Form - {self.folio_hospitalizacion}"

    class Meta:
        verbose_name = _("Post-During Surgery Form")
        verbose_name_plural = _("Post-During Surgery Forms")
    
    @property
    def patient(self):
        """Get the related patient safely"""
        try:
            return Patient.objects.get(
                folio_hospitalizacion=self.folio_hospitalizacion.folio_hospitalizacion.replace('PRE-', '')
            )
        except Patient.DoesNotExist:
            return None

    def clean(self):
        """Enhanced validation - FIXED VERSION"""
        # Don't call super().clean() with cleaned_data - that's for forms, not models
        super().clean()
        
        # For model validation, we work with the instance fields directly
        # Validate POGO score
        if self.pogo is not None and (self.pogo < 0 or self.pogo > 100):
            raise ValidationError({'pogo': _('El valor POGO debe estar entre 0 y 100')})
        
        # Validate number of attempts
        if self.numero_intentos is not None and self.numero_intentos < 1:
            raise ValidationError({'numero_intentos': _('Debe haber al menos un intento')})
        
        # Validate Cormack score
        if self.cormack is not None and (self.cormack < 1 or self.cormack > 4):
            raise ValidationError({'cormack': _('El valor Cormack debe estar entre 1 y 4')})
        
        # Validate HAN classification
        if self.clasificacion_han is not None and (self.clasificacion_han < 0 or self.clasificacion_han > 4):
            raise ValidationError({'clasificacion_han': _('La clasificación HAN debe estar entre 0 y 4')})
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        return super().save(*args, **kwargs)
