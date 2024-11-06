# forms.py
from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from .models import ContactMessage
from .models import Patient
from django.utils.translation import gettext_lazy as _
from .models import PreSurgeryForm, PostDuringSurgeryForm
from django.core.exceptions import ValidationError
from .models import PreSurgeryForm as PreSurgeryModel
from django.utils import timezone



class PatientForm(forms.ModelForm):
    """
    Form for patient registration and updates
    """
    class Meta:
        model = Patient
        fields = ['folio_hospitalizacion', 'nombres', 'apellidos', 
                 'fecha_nacimiento', 'codigo_barras']
        widgets = {
            'folio_hospitalizacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Folio de Hospitalización'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres del paciente'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos del paciente'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'codigo_barras': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_folio_hospitalizacion(self):
        folio = self.cleaned_data.get('folio_hospitalizacion')
        if not folio:
            raise forms.ValidationError(_("Este campo es requerido."))
        return folio.upper()




class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono (opcional)',
                'pattern': '^\+?1?\d{9,15}$'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu mensaje aquí...',
                'rows': 5
            })
        }

class MedicRegistrationForm(forms.Form):
    usuario = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'pattern': '^[a-zA-Z0-9._]+$',  # Only allow letters, numbers, dots and underscores
            'title': 'El usuario solo puede contener letras, números, puntos y guiones bajos'
        })
    )
    
    nombre = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombres'
        })
    )
    
    apellidos = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono',
            'pattern': '^\+?1?\d{9,15}$',
            'title': 'Ingrese un número de teléfono válido'
        })
    )
    
    ESPECIALIDADES = [
        ('anestesiologia', 'Anestesiología'),
        ('anestesiologia_pediatrica', 'Anestesiología Pediátrica'),
        ('medicina_critica', 'Medicina Crítica'),
        ('medicina_del_dolor', 'Medicina del Dolor'),
        ('otra', 'Otra Especialidad')
    ]
    
    especialidad = forms.ChoiceField(
        choices=ESPECIALIDADES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar Contraseña'
        })
    )
    
    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if not usuario.isalnum() and not set(usuario) <= set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._'):
            raise forms.ValidationError('El usuario solo puede contener letras, números, puntos y guiones bajos')
        return usuario
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1)
        except forms.ValidationError as error:
            raise forms.ValidationError(error)
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data
    

class PreSurgeryCreateForm(forms.ModelForm):
    required_fields = [
        'nombres', 'apellidos', 'fecha_nacimiento', 'medico',
        'fecha_reporte', 'medico_tratante', 'diagnostico_preoperatorio',
        'peso', 'talla', 'estado_fisico_asa',
        'evaluacion_preoperatoria', 'fc', 'ta', 'spo2_aire',
        'spo2_oxigeno', 'glasgow', 'mallampati', 'patil_aldrete',
        'desviacion_traquea'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.required_fields:
            self.fields[field_name].required = True

    class Meta:
        model = PreSurgeryForm
        fields = [
            'nombres', 'apellidos', 'fecha_nacimiento', 'medico',
            'fecha_reporte', 'medico_tratante', 'diagnostico_preoperatorio',
            'peso', 'talla', 'imc', 'estado_fisico_asa',
            'comorbilidades', 'medicamentos', 'alergias', 'ayuno_hrs',
            'uso_glp1', 'dosis_glp1', 'tabaquismo',
            'antecedentes_dificultad', 'descripcion_dificultad',
            'evaluacion_preoperatoria', 'estudios_radiologicos_va',
            'uso_usg_gastrico', 'usg_gastrico_ml', 'imagen_usg_gastrico',
            'fc', 'ta', 'spo2_aire', 'spo2_oxigeno', 'glasgow',
            'mallampati', 'patil_aldrete', 'distancia_inter_incisiva',
            'distancia_tiro_mentoniana', 'protrusion_mandibular',
            'macocha', 'stop_bang', 'desviacion_traquea',
            'problemas_deglucion', 'estridor_laringeo', 'observaciones'
        ]
        widgets = {
            # Patient Information
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres del paciente'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos del paciente'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'medico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del médico'
            }),
            'fecha_reporte': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'medico_tratante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Médico tratante'
            }),
            'diagnostico_preoperatorio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnóstico preoperatorio'
            }),

            # Physical Measurements
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Peso en kg',
                'step': 'any',
                'min': '0',
                'inputmode': 'decimal'
            }),
            'talla': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Talla en cm',
                'step': 'any',
                'min': '0',
                'inputmode': 'decimal'
            }),
            'imc': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'step': 'any'
            }),
            'estado_fisico_asa': forms.Select(attrs={
                'class': 'form-control'
            }),

            # Medical History
            'comorbilidades': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enfermedades o condiciones médicas relevantes'
            }),
            'medicamentos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medicamentos actuales'
            }),
            'alergias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Alergias conocidas'
            }),
            'ayuno_hrs': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Horas de ayuno',
                'min': '0',
                'step': '0.5'
            }),

            # GLP1 and Additional Information
            'uso_glp1': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'dosis_glp1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dosis de GLP1'
            }),
            'tabaquismo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'antecedentes_dificultad': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'descripcion_dificultad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción de dificultades previas'
            }),

            # Evaluations
            'evaluacion_preoperatoria': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Evaluación preoperatoria detallada'
            }),
            'estudios_radiologicos_va': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),

            # USG Assessment
            'uso_usg_gastrico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'usg_gastrico_ml': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Volumen en ml',
                'min': '0',
                'step': 'any'
            }),
            'imagen_usg_gastrico': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),

            # Vital Signs
            'fc': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Frecuencia cardíaca',
                'min': '0'
            }),
            'ta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tensión arterial (ej: 120/80)'
            }),
            'spo2_aire': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'SpO2 aire ambiente (%)',
                'min': '0',
                'max': '100'
            }),
            'spo2_oxigeno': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'SpO2 con oxígeno (%)',
                'min': '0',
                'max': '100'
            }),
            'glasgow': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Escala de Glasgow',
                'min': '3',
                'max': '15'
            }),

            # Airway Assessment
            'mallampati': forms.Select(attrs={
                'class': 'form-control'
            }),
            'patil_aldrete': forms.Select(attrs={
                'class': 'form-control'
            }),
            'distancia_inter_incisiva': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distancia en cm',
                'step': '0.1',
                'min': '0'
            }),
            'distancia_tiro_mentoniana': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distancia en cm',
                'step': '0.1',
                'min': '0'
            }),
            'protrusion_mandibular': forms.Select(attrs={
                'class': 'form-control'
            }),

            # Additional Assessments
            'macocha': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Puntaje Macocha',
                'min': '0'
            }),
            'stop_bang': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Puntaje STOP-BANG',
                'min': '0',
                'max': '8'
            }),
            'desviacion_traquea': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Desviación en cm',
                'step': '0.1',
                'min': '0'
            }),
            'problemas_deglucion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'estridor_laringeo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields
        for field_name in self.required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # Set initial date if not provided
        if not self.initial.get('fecha_reporte'):
            self.initial['fecha_reporte'] = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()
        
        # Calculate IMC
        peso = cleaned_data.get('peso')
        talla = cleaned_data.get('talla')
        if peso and talla:
            try:
                talla_metros = float(talla) / 100
                imc = round(float(peso) / (talla_metros * talla_metros), 2)
                cleaned_data['imc'] = imc
            except (ValueError, ZeroDivisionError):
                raise ValidationError(_('Error en el cálculo del IMC. Verifique peso y talla.'))

        # Validate Glasgow score
        glasgow = cleaned_data.get('glasgow')
        if glasgow is not None:
            if glasgow < 3 or glasgow > 15:
                raise ValidationError({
                    'glasgow': _('El valor de Glasgow debe estar entre 3 y 15')
                })

        # Validate SpO2 values
        for field in ['spo2_aire', 'spo2_oxigeno']:
            value = cleaned_data.get(field)
            if value is not None:
                if value < 0 or value > 100:
                    raise ValidationError({
                        field: _('El valor de SpO2 debe estar entre 0 y 100')
                    })

        # Validate GLP1 dose
        if cleaned_data.get('uso_glp1') and not cleaned_data.get('dosis_glp1'):
            raise ValidationError({
                'dosis_glp1': _('La dosis de GLP1 es requerida cuando se marca uso de GLP1')
            })

        # Validate difficulty description
        if cleaned_data.get('antecedentes_dificultad') and not cleaned_data.get('descripcion_dificultad'):
            raise ValidationError({
                'descripcion_dificultad': _('La descripción es requerida cuando hay antecedentes de dificultad')
            })

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.fecha_reporte:
            instance.fecha_reporte = timezone.now().date()
        if commit:
            instance.save()
        return instance


class PreSurgeryForm(forms.ModelForm):
    class Meta:
        model = PreSurgeryForm
        exclude = ['folio_hospitalizacion']  # Will be set automatically
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'medico': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_reporte': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'medico_tratante': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnostico_preoperatorio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'talla': forms.NumberInput(attrs={'class': 'form-control'}),
            'imc': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado_fisico_asa': forms.Select(attrs={'class': 'form-control'}),
            'comorbilidades': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'medicamentos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'ayuno_hrs': forms.NumberInput(attrs={'class': 'form-control'}),
            'dosis_glp1': forms.TextInput(attrs={'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'descripcion_dificultad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'evaluacion_preoperatoria': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'usg_gastrico_ml': forms.NumberInput(attrs={'class': 'form-control'}),
            'fc': forms.NumberInput(attrs={'class': 'form-control'}),
            'ta': forms.NumberInput(attrs={'class': 'form-control'}),
            'spo2_aire': forms.NumberInput(attrs={'class': 'form-control'}),
            'spo2_oxigeno': forms.NumberInput(attrs={'class': 'form-control'}),
            'glasgow': forms.NumberInput(attrs={'class': 'form-control'}),
            'mallampati': forms.Select(attrs={'class': 'form-control'}),
            'patil_aldrete': forms.Select(attrs={'class': 'form-control'}),
            'distancia_inter_incisiva': forms.NumberInput(attrs={'class': 'form-control'}),
            'distancia_tiro_mentoniana': forms.NumberInput(attrs={'class': 'form-control'}),
            'protrusion_mandibular': forms.Select(attrs={'class': 'form-control'}),
            'macocha': forms.NumberInput(attrs={'class': 'form-control'}),
            'stop_bang': forms.NumberInput(attrs={'class': 'form-control'}),
            'desviacion_traquea': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }



class PostSurgeryCreateForm(forms.ModelForm):
    """
    Form for creating post-surgery records with validation and help text
    """
    required_fields = [
        'lugar_problema', 'tecnica_utilizada', 'clasificacion_han',
        'aditamento_via_aerea', 'tiempo_preoxigenacion', 'tipo_intubacion',
        'numero_intentos', 'cormack', 'pogo', 'tipo_anestesia',
        'resultado_final', 'nombre_anestesiologo', 'cedula_profesional',
        'especialidad'
    ]

    class Meta:
        model = PostDuringSurgeryForm
        exclude = ['folio_hospitalizacion']
        widgets = {
            # Keep all the existing widgets from PostSurgeryForm
            # ... (keep existing widget definitions)
        }
        help_texts = {
            # Location and Personnel
            'lugar_problema': _('Especifique el lugar donde se realizó el procedimiento (ej: Quirófano, Urgencias)'),
            'presencia_anestesiologo': _('Indique si un anestesiólogo estuvo presente durante el procedimiento'),
            
            # Equipment and Techniques
            'tecnica_utilizada': _('Detalle la técnica principal utilizada para el manejo de la vía aérea'),
            'carro_via_aerea': _('¿Se contó con carro de vía aérea difícil?'),
            'tipo_video_laringoscopia': _('Especifique el modelo de videolaringoscopio utilizado'),
            
            # Classifications
            'clasificacion_han': _('Seleccione el grado en la escala HAN (0-4) de dificultad encontrada'),
            'aditamento_via_aerea': _('Indique los dispositivos auxiliares utilizados durante el procedimiento'),
            'tiempo_preoxigenacion': _('Tiempo total en minutos de pre-oxigenación'),
            
            # Supraglottic Device
            'uso_supraglotico': _('¿Se utilizó algún dispositivo supraglótico?'),
            'tipo_supraglotico': _('Indique tipo y tamaño del dispositivo supraglótico utilizado'),
            'problemas_supragloticos': _('Describa cualquier dificultad o complicación con el dispositivo'),
            
            # Intubation Details
            'tipo_intubacion': _('Especifique la vía y técnica de intubación empleada'),
            'numero_intentos': _('Número total de intentos de intubación realizados'),
            'laringoscopia_directa': _('Describa los hallazgos durante la laringoscopía directa'),
            'cormack': _('Indique el grado de visualización según Cormack-Lehane (1-4)'),
            'pogo': _('Porcentaje de visualización de la glotis (0-100%)'),
            
            # Additional Procedures
            'intubacion_tecnica_mixta': _('Si utilizó una combinación de técnicas, especifique cuáles'),
            'intubacion_despierto': _('¿Se realizó intubación con el paciente despierto?'),
            'descripcion_intubacion_despierto': _('Detalle el procedimiento de intubación en paciente despierto'),
            
            # Anesthesia Details
            'tipo_anestesia': _('Especifique el tipo de anestesia administrada'),
            'sedacion': _('Detalle medicamentos y dosis utilizados para sedación'),
            'observaciones': _('Incluya cualquier observación relevante adicional'),
            'cooperacion_paciente': _('Describa el nivel de cooperación del paciente'),
            
            # Emergency Procedures
            'algoritmo_no_intubacion': _('¿Se activó el algoritmo de no intubación?'),
            'crico_tiroidotomia': _('¿Fue necesario realizar cricotiroidotomía?'),
            'traqueostomia_percutanea': _('¿Se realizó traqueostomía percutánea?'),
            
            # Results
            'complicaciones': _('Describa todas las complicaciones presentadas durante el procedimiento'),
            'resultado_final': _('Resuma el resultado final del procedimiento'),
            
            # Morbidity and Mortality
            'morbilidad': _('¿Hubo morbilidad asociada al procedimiento?'),
            'descripcion_morbilidad': _('Detalle la morbilidad presentada y su manejo'),
            'mortalidad': _('¿Hubo mortalidad asociada al procedimiento?'),
            'descripcion_mortalidad': _('Describa las circunstancias y causa de la mortalidad'),
            
            # Personnel
            'nombre_anestesiologo': _('Nombre completo del anestesiólogo responsable'),
            'cedula_profesional': _('Número de cédula profesional del anestesiólogo'),
            'especialidad': _('Especialidad del médico tratante'),
            'nombre_residente': _('Si participó un residente, incluya su nombre'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        for field_name in self.required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

    def clean(self):
        cleaned_data = super().clean()
        
        # Validation for POGO score
        pogo = cleaned_data.get('pogo')
        if pogo is not None and (pogo < 0 or pogo > 100):
            raise ValidationError({'pogo': _('El valor POGO debe estar entre 0 y 100')})
        
        # Validation for number of attempts
        intentos = cleaned_data.get('numero_intentos')
        if intentos is not None and intentos < 1:
            raise ValidationError({'numero_intentos': _('Debe haber al menos un intento')})
        
        # Required descriptions for certain conditions
        if cleaned_data.get('intubacion_despierto') and not cleaned_data.get('descripcion_intubacion_despierto'):
            raise ValidationError({
                'descripcion_intubacion_despierto': _('La descripción es requerida cuando se realiza intubación en paciente despierto')
            })
            
        if cleaned_data.get('morbilidad') and not cleaned_data.get('descripcion_morbilidad'):
            raise ValidationError({
                'descripcion_morbilidad': _('La descripción es requerida cuando se indica morbilidad')
            })
            
        if cleaned_data.get('mortalidad') and not cleaned_data.get('descripcion_mortalidad'):
            raise ValidationError({
                'descripcion_mortalidad': _('La descripción es requerida cuando se indica mortalidad')
            })
            
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance



class PostSurgeryForm(forms.ModelForm):
    """
    Form for creating and updating post-surgery records
    """
    class Meta:
        model = PostDuringSurgeryForm
        exclude = ['folio_hospitalizacion']
        widgets = {
            # Location and Personnel
            'lugar_problema': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar o área del problema'
            }),
            'presencia_anestesiologo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            
            # Equipment and Techniques
            'tecnica_utilizada': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Técnica utilizada'
            }),
            'carro_via_aerea': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tipo_video_laringoscopia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de video-laringoscopía'
            }),
            'video_laringoscopia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
            
            # Classifications
            'clasificacion_han': forms.Select(attrs={
                'class': 'form-control'
            }),
            'aditamento_via_aerea': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Aditamento de vía aérea'
            }),
            'tiempo_preoxigenacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Tiempo en minutos'
            }),
            
            # Supraglottic Device
            'uso_supraglotico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'tipo_supraglotico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de dispositivo supraglótico'
            }),
            'problemas_supragloticos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa problemas con dispositivos supraglóticos'
            }),
            
            # Intubation Details
            'tipo_intubacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de intubación'
            }),
            'numero_intentos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Número de intentos'
            }),
            'laringoscopia_directa': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa la laringoscopía directa'
            }),
            'cormack': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pogo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': 'Porcentaje POGO'
            }),
            
            # Additional Procedures
            'intubacion_tecnica_mixta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Describa la técnica mixta utilizada'
            }),
            'intubacion_despierto': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'descripcion_intubacion_despierto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa el procedimiento de intubación despierto'
            }),
            
            # Anesthesia Details
            'tipo_anestesia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tipo de anestesia'
            }),
            'sedacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sedación utilizada'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales'
            }),
            'cooperacion_paciente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nivel de cooperación del paciente'
            }),
            
            # Emergency Procedures
            'algoritmo_no_intubacion': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'crico_tiroidotomia': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'traqueostomia_percutanea': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            
            # Outcomes
            'complicaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complicaciones presentadas'
            }),
            'resultado_final': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Resultado final del procedimiento'
            }),
            'fotos_videos': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*'
            }),
            
            # Morbidity and Mortality
            'morbilidad': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'descripcion_morbilidad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de morbilidad'
            }),
            'mortalidad': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'descripcion_mortalidad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de mortalidad'
            }),
            
            # Medical Personnel
            'nombre_anestesiologo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del anestesiólogo'
            }),
            'cedula_profesional': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cédula profesional'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especialidad'
            }),
            'nombre_residente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del residente'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        
        # Validation for POGO score
        pogo = cleaned_data.get('pogo')
        if pogo is not None and (pogo < 0 or pogo > 100):
            raise ValidationError({'pogo': 'El valor POGO debe estar entre 0 y 100'})
        
        # Validation for number of attempts
        intentos = cleaned_data.get('numero_intentos')
        if intentos is not None and intentos < 1:
            raise ValidationError({'numero_intentos': 'Debe haber al menos un intento'})
        
        # Required descriptions for certain conditions
        if cleaned_data.get('intubacion_despierto') and not cleaned_data.get('descripcion_intubacion_despierto'):
            raise ValidationError({
                'descripcion_intubacion_despierto': 'La descripción es requerida cuando se realiza intubación en paciente despierto'
            })
            
        if cleaned_data.get('morbilidad') and not cleaned_data.get('descripcion_morbilidad'):
            raise ValidationError({
                'descripcion_morbilidad': 'La descripción es requerida cuando se indica morbilidad'
            })
            
        if cleaned_data.get('mortalidad') and not cleaned_data.get('descripcion_mortalidad'):
            raise ValidationError({
                'descripcion_mortalidad': 'La descripción es requerida cuando se indica mortalidad'
            })
            
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        required_fields = [
            'lugar_problema', 'tecnica_utilizada', 'clasificacion_han',
            'aditamento_via_aerea', 'tiempo_preoxigenacion', 'tipo_intubacion',
            'numero_intentos', 'cormack', 'pogo', 'tipo_anestesia',
            'resultado_final', 'nombre_anestesiologo', 'cedula_profesional',
            'especialidad'
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True