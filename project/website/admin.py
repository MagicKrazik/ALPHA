from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import (
    MedicoUser, ContactMessage, Patient, TreatmentCase,
    PreSurgeryForm, PostDuringSurgeryForm, RiskFactor,
    AlertRule, PatientRiskProfile, RiskAlert, AlertNotification
)


@admin.register(MedicoUser)
class MedicoUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'nombre', 'apellidos', 'especialidad', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'especialidad')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('nombre', 'apellidos', 'email', 'telefono', 'especialidad')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'nombre', 'apellidos', 'email')
    ordering = ('username',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('subject', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    actions = ['mark_as_read']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'fecha_nacimiento', 'edad', 'email', 'activo', 'fecha_registro')
    list_filter = ('activo', 'fecha_registro', 'fecha_nacimiento')
    search_fields = ('nombres', 'apellidos', 'email')
    ordering = ('-fecha_registro',)
    readonly_fields = ('id_paciente', 'fecha_registro', 'ultima_actualizacion', 'edad')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'fecha_nacimiento', 'email', 'telefono')
        }),
        ('Configuración', {
            'fields': ('activo', 'aceptacion_privacidad')
        }),
        ('Información del Sistema', {
            'fields': ('id_paciente', 'fecha_registro', 'ultima_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TreatmentCase)
class TreatmentCaseAdmin(admin.ModelAdmin):
    list_display = ('folio_hospitalizacion', 'patient', 'medico_responsable', 'activo', 'fecha_ingreso')
    list_filter = ('activo', 'fecha_ingreso', 'medico_responsable')
    search_fields = ('folio_hospitalizacion', 'patient__nombres', 'patient__apellidos')
    ordering = ('-fecha_ingreso',)
    readonly_fields = ('id_case', 'fecha_ingreso')
    
    fieldsets = (
        ('Información del Caso', {
            'fields': ('folio_hospitalizacion', 'patient', 'diagnostico_inicial')
        }),
        ('Personal Médico', {
            'fields': ('medico_responsable', 'medicos_secundarios')
        }),
        ('Documentación', {
            'fields': ('codigo_barras',)
        }),
        ('Estado del Caso', {
            'fields': ('activo', 'fecha_alta')
        }),
        ('Información del Sistema', {
            'fields': ('id_case', 'fecha_ingreso'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('medicos_secundarios',)


@admin.register(PreSurgeryForm)
class PreSurgeryFormAdmin(admin.ModelAdmin):
    list_display = ('treatment_case', 'fecha_reporte', 'estado_fisico_asa', 'mallampati', 'imc')
    list_filter = ('estado_fisico_asa', 'mallampati', 'fecha_reporte', 'tabaquismo', 'uso_glp1')
    search_fields = ('treatment_case__folio_hospitalizacion', 'treatment_case__patient__nombres')
    ordering = ('-fecha_reporte',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'patient', 'folio_hospitalizacion')
    
    fieldsets = (
        ('Información del Caso', {
            'fields': ('treatment_case', 'fecha_reporte', 'medico_tratante')
        }),
        ('Diagnóstico', {
            'fields': ('diagnostico_preoperatorio', 'evaluacion_preoperatoria')
        }),
        ('Medidas Físicas', {
            'fields': ('peso', 'talla', 'imc', 'estado_fisico_asa')
        }),
        ('Signos Vitales', {
            'fields': ('fc', 'ta', 'spo2_aire', 'spo2_oxigeno', 'glasgow')
        }),
        ('Evaluación de Vía Aérea', {
            'fields': ('mallampati', 'patil_aldrete', 'distancia_inter_incisiva', 
                      'distancia_tiro_mentoniana', 'protrusion_mandibular',
                      'macocha', 'stop_bang', 'desviacion_traquea')
        }),
        ('Historia Médica', {
            'fields': ('comorbilidades', 'medicamentos', 'alergias', 'ayuno_hrs')
        }),
        ('Factores de Riesgo', {
            'fields': ('tabaquismo', 'uso_glp1', 'dosis_glp1', 'antecedentes_dificultad',
                      'descripcion_dificultad', 'problemas_deglucion', 'estridor_laringeo')
        }),
        ('USG y Estudios', {
            'fields': ('uso_usg_gastrico', 'usg_gastrico_ml', 'imagen_usg_gastrico',
                      'estudios_radiologicos_va')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Información del Sistema', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PostDuringSurgeryForm)
class PostDuringSurgeryFormAdmin(admin.ModelAdmin):
    list_display = ('treatment_case', 'lugar_problema', 'clasificacion_han', 'numero_intentos', 'morbilidad', 'mortalidad')
    list_filter = ('clasificacion_han', 'morbilidad', 'mortalidad', 'presencia_anestesiologo', 'created_at')
    search_fields = ('treatment_case__folio_hospitalizacion', 'nombre_anestesiologo', 'especialidad')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'patient', 'folio_hospitalizacion')
    
    fieldsets = (
        ('Información del Caso', {
            'fields': ('treatment_case', 'pre_surgery_form')
        }),
        ('Ubicación y Personal', {
            'fields': ('lugar_problema', 'presencia_anestesiologo', 'nombre_anestesiologo',
                      'cedula_profesional', 'especialidad', 'nombre_residente')
        }),
        ('Técnica y Equipamiento', {
            'fields': ('tecnica_utilizada', 'carro_via_aerea', 'tipo_video_laringoscopia',
                      'video_laringoscopia')
        }),
        ('Clasificaciones', {
            'fields': ('clasificacion_han', 'aditamento_via_aerea', 'tiempo_preoxigenacion')
        }),
        ('Dispositivo Supraglótico', {
            'fields': ('uso_supraglotico', 'tipo_supraglotico', 'problemas_supragloticos')
        }),
        ('Detalles de Intubación', {
            'fields': ('tipo_intubacion', 'numero_intentos', 'laringoscopia_directa',
                      'cormack', 'pogo', 'intubacion_tecnica_mixta')
        }),
        ('Intubación Despierto', {
            'fields': ('intubacion_despierto', 'descripcion_intubacion_despierto')
        }),
        ('Anestesia', {
            'fields': ('tipo_anestesia', 'sedacion', 'cooperacion_paciente')
        }),
        ('Procedimientos de Emergencia', {
            'fields': ('algoritmo_no_intubacion', 'crico_tiroidotomia', 'traqueostomia_percutanea')
        }),
        ('Resultados', {
            'fields': ('complicaciones', 'resultado_final', 'fotos_videos')
        }),
        ('Morbilidad y Mortalidad', {
            'fields': ('morbilidad', 'descripcion_morbilidad', 'mortalidad', 'descripcion_mortalidad')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Información del Sistema', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ===== ALERT SYSTEM ADMIN =====

@admin.register(RiskFactor)
class RiskFactorAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'severity_level', 'is_active', 'created_at')
    list_filter = ('category', 'severity_level', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('category', 'severity_level', 'name')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'category', 'severity_level')
        }),
        ('Descripción', {
            'fields': ('description',)
        }),
        ('Configuración', {
            'fields': ('is_active',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'priority', 'is_active', 'created_at')
    list_filter = ('rule_type', 'priority', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('priority', 'name')
    filter_horizontal = ('risk_factors',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'rule_type', 'priority')
        }),
        ('Configuración de la Regla', {
            'fields': ('rule_config',)
        }),
        ('Factores de Riesgo Asociados', {
            'fields': ('risk_factors',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PatientRiskProfile)
class PatientRiskProfileAdmin(admin.ModelAdmin):
    list_display = ('treatment_case', 'overall_risk_score', 'airway_risk_score', 
                   'difficult_airway_probability', 'risk_level', 'last_calculated')
    list_filter = ('last_calculated', 'calculation_version')
    search_fields = ('treatment_case__folio_hospitalizacion', 
                    'treatment_case__patient__nombres')
    ordering = ('-overall_risk_score', '-last_calculated')
    readonly_fields = ('created_at', 'last_calculated', 'risk_level')
    
    fieldsets = (
        ('Caso de Tratamiento', {
            'fields': ('treatment_case',)
        }),
        ('Puntuaciones de Riesgo', {
            'fields': ('overall_risk_score', 'airway_risk_score', 
                      'cardiovascular_risk_score', 'respiratory_risk_score')
        }),
        ('Probabilidades', {
            'fields': ('difficult_airway_probability', 'complication_probability')
        }),
        ('Factores de Riesgo Identificados', {
            'fields': ('identified_risk_factors',)
        }),
        ('Metadatos de Cálculo', {
            'fields': ('last_calculated', 'calculation_version')
        }),
        ('Información del Sistema', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ('identified_risk_factors',)
    
    def risk_level(self, obj):
        return obj.risk_level.upper()
    risk_level.short_description = 'Nivel de Riesgo'


@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'treatment_case', 'alert_type', 'status', 
                   'risk_score', 'confidence_level', 'triggered_at')
    list_filter = ('alert_type', 'status', 'triggered_at', 'acknowledged_at')
    search_fields = ('title', 'message', 'treatment_case__folio_hospitalizacion')
    ordering = ('-triggered_at',)
    readonly_fields = ('triggered_at', 'acknowledged_at', 'resolved_at')
    
    fieldsets = (
        ('Información de la Alerta', {
            'fields': ('treatment_case', 'alert_rule', 'alert_type', 'status')
        }),
        ('Contenido', {
            'fields': ('title', 'message')
        }),
        ('Métricas de Riesgo', {
            'fields': ('risk_score', 'confidence_level')
        }),
        ('Recomendaciones', {
            'fields': ('recommendations',)
        }),
        ('Ciclo de Vida', {
            'fields': ('triggered_at', 'acknowledged_at', 'acknowledged_by',
                      'resolved_at', 'resolved_by')
        }),
    )
    
    actions = ['mark_as_acknowledged', 'mark_as_resolved']
    
    def mark_as_acknowledged(self, request, queryset):
        updated = queryset.filter(status='active').update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        self.message_user(request, f'{updated} alertas marcadas como reconocidas.')
    mark_as_acknowledged.short_description = "Marcar como reconocidas"
    
    def mark_as_resolved(self, request, queryset):
        updated = queryset.exclude(status='resolved').update(
            status='resolved',
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} alertas marcadas como resueltas.')
    mark_as_resolved.short_description = "Marcar como resueltas"


@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):
    list_display = ('alert', 'recipient', 'notification_type', 'status', 'sent_at', 'delivered_at')
    list_filter = ('notification_type', 'status', 'sent_at', 'created_at')
    search_fields = ('alert__title', 'recipient__username', 'recipient__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'sent_at', 'delivered_at')
    
    fieldsets = (
        ('Información de la Notificación', {
            'fields': ('alert', 'recipient', 'notification_type')
        }),
        ('Estado', {
            'fields': ('status', 'error_message')
        }),
        ('Fechas', {
            'fields': ('created_at', 'sent_at', 'delivered_at')
        }),
    )


# Custom admin site configuration
admin.site.site_header = "ALPHA Project - Administración"
admin.site.site_title = "ALPHA Admin"
admin.site.index_title = "Panel de Administración"