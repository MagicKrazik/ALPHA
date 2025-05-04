from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import MedicRegistrationForm
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .utils import account_activation_token, send_verification_email
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from .forms import PatientForm
from django.utils.translation import gettext_lazy as _
from .forms import PreSurgeryForm, PostSurgeryForm, PreSurgeryCreateForm, PostSurgeryCreateForm
from .models import PostDuringSurgeryForm
from django.db.models import Count, Avg, Q, Sum, StdDev
from django.db.models.functions import TruncMonth, TruncWeek, ExtractHour
import json
from datetime import datetime, timedelta
from django.http import JsonResponse, FileResponse
from .models import Patient, PreSurgeryForm, PostDuringSurgeryForm
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from io import BytesIO
import pandas as pd
from .risk_calculator import RiskCalculator
from django.db.models import Case, When, IntegerField




# Home view
def home(request):
    return render(request, 'home.html')


# Register view to register new users:
User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = MedicRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Check if email already exists
                email = form.cleaned_data['email']
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Este correo electrónico ya está registrado.')
                    return render(request, 'register.html', {'form': form})

                # Create active user directly
                user = User(
                    username=form.cleaned_data['usuario'],
                    email=email,
                    nombre=form.cleaned_data['nombre'],
                    apellidos=form.cleaned_data['apellidos'],
                    telefono=form.cleaned_data['telefono'],
                    especialidad=form.cleaned_data['especialidad'][:3].upper(),
                    is_active=True  # Set user as active immediately
                )
                user.set_password(form.cleaned_data['password1'])
                user.save()
                
                # Log the user in automatically
                login(request, user)
                messages.success(request, '¡Registro exitoso! Bienvenido.')
                return redirect('home')
                
            except IntegrityError as e:
                if 'UNIQUE constraint' in str(e) and 'username' in str(e):
                    messages.error(request, 'Este nombre de usuario ya está en uso.')
                elif 'UNIQUE constraint' in str(e) and 'email' in str(e):
                    messages.error(request, 'Este correo electrónico ya está registrado.')
                else:
                    messages.error(request, 'Error al crear el usuario. Por favor, intente nuevamente.')
            except Exception as e:
                messages.error(request, 'Error al crear el usuario. Por favor, intente nuevamente.')
    else:
        form = MedicRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


# login and logout view:

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso.')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')

# contact form view:

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the message
            contact_message = form.save()
            
            # Send email notification
            subject = f"Nuevo mensaje de contacto - {form.cleaned_data['subject']}"
            message = f"""
            Nuevo mensaje de contacto recibido:
            
            Nombre: {form.cleaned_data['name']}
            Email: {form.cleaned_data['email']}
            Teléfono: {form.cleaned_data['phone']}
            Asunto: {form.cleaned_data['subject']}
            Mensaje: {form.cleaned_data['message']}
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Mensaje enviado correctamente. Nos pondremos en contacto pronto.')
            except Exception as e:
                messages.warning(request, 'El mensaje se ha guardado pero hubo un problema al enviar la notificación.')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'company_email': 'contacto@alphaproject.com',  # Dummy email
        'company_phone': '+52 (555) 123-4567',  # Dummy phone
        'company_address': 'Ciudad de México, México'  # Dummy address
    }
    
    return render(request, 'contact.html', context)


## patient registration views:

@login_required
def patient_list(request):
    """
    List view for patients with search and form type filtering
    """
    search_query = request.GET.get('q', '')
    form_type = request.GET.get('form', '')
    patients = Patient.objects.filter(medico=request.user, activo=True)
    
    if search_query:
        patients = patients.filter(
            Q(folio_hospitalizacion__icontains=search_query) |
            Q(nombres__icontains=search_query) |
            Q(apellidos__icontains=search_query)
        )
    
    context = {
        'patients': patients,
        'search_query': search_query,
        'form_type': form_type  # Pass the form type to the template
    }
    
    # If a specific form type is requested, use the appropriate template
    if form_type == 'pre':
        return render(request, 'presurgery_list.html', context)
    elif form_type == 'post':
        return render(request, 'postsurgery_list.html', context)
    
    return render(request, 'patient_list.html', context)

@login_required
def patient_create(request):
    """
    Create view for new patient registration
    """
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.medico = request.user
            patient.save()
            messages.success(request, _('Paciente registrado exitosamente.'))
            return redirect('patient-detail', patient.id_paciente)
    else:
        form = PatientForm()
    
    return render(request, 'patient_form.html', {'form': form})

@login_required
def patient_update(request, pk):
    """
    Update view for existing patient information
    """
    patient = get_object_or_404(Patient, id_paciente=pk, medico=request.user)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, _('Información del paciente actualizada.'))
            return redirect('patient-detail', pk)
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'patient_form.html', {
        'form': form,
        'patient': patient
    })

@login_required
def patient_detail(request, pk):
    """
    Detail view for patient information
    """
    patient = get_object_or_404(Patient, id_paciente=pk)
    
    # Check if user has permission to view this patient
    if patient.medico != request.user and not request.user.is_staff:
        messages.error(request, _('No tienes permiso para ver esta información.'))
        return redirect('patient-list')
    
    # Get pre-surgery forms for this patient
    presurgery_forms = PreSurgeryForm.objects.filter(
        folio_hospitalizacion__startswith=f"PRE-{patient.folio_hospitalizacion}"
    ).order_by('-fecha_reporte')
    
    # Get post-surgery forms for this patient
    postsurgery_forms = PostDuringSurgeryForm.objects.filter(
        folio_hospitalizacion__folio_hospitalizacion__in=presurgery_forms.values_list('folio_hospitalizacion', flat=True)
    ).order_by('-folio_hospitalizacion__fecha_reporte')
    
    context = {
        'patient': patient,
        'presurgery_forms': presurgery_forms,
        'postsurgery_forms': postsurgery_forms,
    }
    
    return render(request, 'patient_detail.html', context)

@login_required
def patient_delete(request, pk):
    """
    Delete view for patient (soft delete)
    """
    patient = get_object_or_404(Patient, id_paciente=pk, medico=request.user)
    
    if request.method == 'POST':
        patient.activo = False
        patient.save()
        messages.success(request, _('Paciente eliminado exitosamente.'))
        return redirect('patient-list')
    
    return render(request, 'patient_confirm_delete.html', {
        'patient': patient
    })


## pre and post surgery forms:

@login_required
def presurgery_create(request, patient_id):
    patient = get_object_or_404(Patient, id_paciente=patient_id, medico=request.user)
    
    try:
        # Check if a form already exists for this patient
        existing_form = PreSurgeryForm.objects.filter(
            folio_hospitalizacion=f"PRE-{patient.folio_hospitalizacion}"
        ).first()
        
        if existing_form:
            messages.warning(request, 'Ya existe un formulario pre-quirúrgico para este paciente.')
            return redirect('presurgery-detail', pk=existing_form.folio_hospitalizacion)

        if request.method == 'POST':
            form = PreSurgeryCreateForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    presurgery = form.save(commit=False)
                    presurgery.folio_hospitalizacion = f"PRE-{patient.folio_hospitalizacion}"
                    presurgery.fecha_reporte = timezone.now().date()
                    presurgery.medico = request.user.get_full_name()
                    presurgery.save()
                    
                    messages.success(request, 'Formulario pre-quirúrgico creado exitosamente.')
                    return redirect('patient-detail', patient_id)
                except Exception as e:
                    messages.error(request, f'Error al guardar el formulario: {str(e)}')
            else:
                error_messages = []
                for field, errors in form.errors.items():
                    error_messages.append(f"{field}: {', '.join(errors)}")
                messages.error(request, f'Por favor corrija los siguientes errores: {"; ".join(error_messages)}')
        else:
            initial_data = {
                'nombres': patient.nombres,
                'apellidos': patient.apellidos,
                'fecha_nacimiento': patient.fecha_nacimiento,
                'medico': request.user.get_full_name(),
                'fecha_reporte': timezone.now().date(),
                'medico_tratante': request.user.get_full_name(),
            }
            form = PreSurgeryCreateForm(initial=initial_data)

        return render(request, 'presurgery_form.html', {
            'form': form,
            'patient': patient
        })

    except Exception as e:
        messages.error(request, f'Error inesperado: {str(e)}')
        return redirect('patient-list')

@login_required
def presurgery_detail(request, pk):
    presurgery = get_object_or_404(PreSurgeryForm, folio_hospitalizacion=pk)
    patient = get_object_or_404(Patient, folio_hospitalizacion=pk.replace('PRE-', ''))
    
    # Check if user has permission to view this form
    if patient.medico != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver este formulario.')
        return redirect('patient-list')
    
    return render(request, 'presurgery_detail.html', {
        'form': presurgery,
        'patient': patient
    })

@login_required
def presurgery_update(request, pk):
    presurgery = get_object_or_404(PreSurgeryForm, folio_hospitalizacion=pk)
    patient = get_object_or_404(Patient, folio_hospitalizacion=pk.replace('PRE-', ''))
    
    if patient.medico != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para editar este formulario.')
        return redirect('patient-list')
    
    if request.method == 'POST':
        form = PreSurgeryCreateForm(request.POST, request.FILES, instance=presurgery)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Formulario actualizado exitosamente.')
                return redirect('presurgery-detail', pk=pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar el formulario: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = PreSurgeryCreateForm(instance=presurgery)
    
    return render(request, 'presurgery_form.html', {
        'form': form,
        'presurgery': presurgery,
        'patient': patient
    })


@login_required
def postsurgery_create(request, patient_id):
    patient = get_object_or_404(Patient, id_paciente=patient_id, medico=request.user)
    presurgery = get_object_or_404(PreSurgeryForm, folio_hospitalizacion=f"PRE-{patient.folio_hospitalizacion}")
    
    try:
        # Check if a form already exists
        existing_form = PostDuringSurgeryForm.objects.filter(
            folio_hospitalizacion=presurgery
        ).first()
        
        if existing_form:
            messages.warning(request, 'Ya existe un formulario post-quirúrgico para este paciente.')
            return redirect('postsurgery-detail', pk=existing_form.folio_hospitalizacion.folio_hospitalizacion)

        if request.method == 'POST':
            form = PostSurgeryCreateForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    postsurgery = form.save(commit=False)
                    postsurgery.folio_hospitalizacion = presurgery
                    postsurgery.save()
                    
                    messages.success(request, 'Formulario post-quirúrgico creado exitosamente.')
                    return redirect('patient-detail', patient_id)
                except Exception as e:
                    messages.error(request, f'Error al guardar el formulario: {str(e)}')
            else:
                error_messages = []
                for field, errors in form.errors.items():
                    error_messages.append(f"{field}: {', '.join(errors)}")
                messages.error(request, f'Por favor corrija los siguientes errores: {"; ".join(error_messages)}')
        else:
            form = PostSurgeryCreateForm()

        return render(request, 'postsurgery_form.html', {
            'form': form,
            'patient': patient
        })

    except Exception as e:
        messages.error(request, f'Error inesperado: {str(e)}')
        return redirect('patient-list')

@login_required
def postsurgery_detail(request, pk):
    """
    View for displaying post-surgery form details
    """
    postsurgery = get_object_or_404(PostDuringSurgeryForm, folio_hospitalizacion__folio_hospitalizacion=pk)
    # Get the related patient through the pre-surgery form
    patient = Patient.objects.get(folio_hospitalizacion=pk.replace('PRE-', ''))
    
    # Check permissions
    if patient.medico != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver este formulario.')
        return redirect('patient-list')
    
    return render(request, 'postsurgery_detail.html', {
        'form': postsurgery,
        'patient': patient
    })

@login_required
def postsurgery_update(request, pk):
    """
    Update view for post-surgery form
    """
    postsurgery = get_object_or_404(PostDuringSurgeryForm, folio_hospitalizacion__folio_hospitalizacion=pk)
    patient = Patient.objects.get(folio_hospitalizacion=pk.replace('PRE-', ''))
    
    # Check permissions
    if patient.medico != request.user and not request.user.is_staff:
        messages.error(request, _('No tienes permiso para editar este formulario.'))
        return redirect('patient-detail', pk=patient.id_paciente)
    
    if request.method == 'POST':
        form = PostSurgeryCreateForm(request.POST, request.FILES, instance=postsurgery)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Formulario post-quirúrgico actualizado exitosamente.'))
                return redirect('postsurgery-detail', pk=pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar el formulario: {str(e)}')
        else:
            messages.error(request, _('Por favor corrija los errores en el formulario.'))
    else:
        form = PostSurgeryCreateForm(instance=postsurgery)
    
    return render(request, 'postsurgery_form.html', {
        'form': form,
        'patient': patient,
        'postsurgery': postsurgery
    })


@login_required
def get_detailed_stats(request):
    """API endpoint for additional dashboard statistics"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Filter based on date range if provided
    queryset = PreSurgeryForm.objects.filter(medico=request.user.get_full_name())
    if start_date and end_date:
        queryset = queryset.filter(
            fecha_reporte__range=[start_date, end_date]
        )
    
    # Calculate additional statistics
    stats = {
        'mallampati_distribution': queryset.values('mallampati').annotate(
            count=Count('mallampati')
        ).order_by('mallampati'),
        'average_bmi': queryset.aggregate(Avg('imc'))['imc__avg'],
        'comorbidities_count': queryset.exclude(
            comorbilidades=''
        ).count(),
    }
    
    return JsonResponse(stats)


# In views.py, update the get_dashboard_stats function

@login_required
def get_dashboard_stats(request):
    """API endpoint for real-time dashboard statistics"""
    try:
        date_range = request.GET.get('date_range', '30')  # Default to 30 days
        start_date = datetime.now() - timedelta(days=int(date_range))
        
        # Get user's patients and forms
        user_patients = Patient.objects.filter(medico=request.user, activo=True)
        presurgery_forms = PreSurgeryForm.objects.filter(
            medico=request.user.get_full_name(),
            fecha_reporte__gte=start_date
        )
        postsurgery_forms = PostDuringSurgeryForm.objects.filter(
            folio_hospitalizacion__in=presurgery_forms.values('folio_hospitalizacion')
        )

        # Calculate statistics
        stats = {
            'summary': {
                'total_patients': user_patients.count(),
                'active_patients': user_patients.filter(
                    fecha_registro__gte=start_date
                ).count(),
                'surgeries_completed': postsurgery_forms.count(),
                'high_risk_cases': presurgery_forms.filter(
                    Q(mallampati__gte=3) |
                    Q(estado_fisico_asa__gte=4)
                ).count()
            },
            
            'asa_distribution': [
                {
                    'estado_fisico_asa': item['estado_fisico_asa'],
                    'count': item['count']
                }
                for item in presurgery_forms.values('estado_fisico_asa')
                .annotate(count=Count('estado_fisico_asa'))
                .order_by('estado_fisico_asa')
            ],
            
            'surgery_trends': [
                {
                    'week': item['week'].strftime('%Y-%m-%d') if item['week'] else None,
                    'count': item['count']
                }
                for item in presurgery_forms
                .annotate(week=TruncWeek('fecha_reporte'))
                .values('week')
                .annotate(count=Count('folio_hospitalizacion'))
                .order_by('week')
            ],
            
            'complications': {
                'total': postsurgery_forms.filter(
                    complicaciones__isnull=False
                ).exclude(complicaciones='').count(),
                'by_type': [
                    {
                        'complicacion': item['complicaciones'],
                        'count': item['count']
                    }
                    for item in postsurgery_forms
                    .exclude(complicaciones='')
                    .values('complicaciones')
                    .annotate(count=Count('complicaciones'))
                    .order_by('-count')[:5]
                ]
            },
            
            'airway_metrics': {
                'mallampati_distribution': [
                    {
                        'mallampati': item['mallampati'],
                        'count': item['count']
                    }
                    for item in presurgery_forms
                    .values('mallampati')
                    .annotate(count=Count('mallampati'))
                    .order_by('mallampati')
                ],
                'difficult_intubation': postsurgery_forms.filter(
                    numero_intentos__gt=1
                ).count(),
                'first_attempt_success': postsurgery_forms.filter(
                    numero_intentos=1
                ).count()
            },
            
            'bmi_distribution': {
                'underweight': presurgery_forms.filter(imc__lt=18.5).count(),
                'normal': presurgery_forms.filter(imc__range=(18.5, 24.9)).count(),
                'overweight': presurgery_forms.filter(imc__range=(25, 29.9)).count(),
                'obese': presurgery_forms.filter(imc__gte=30).count()
            },
            
            'performance_metrics': {
                'complication_rate': round(
                    (postsurgery_forms.filter(complicaciones__isnull=False).count() /
                    max(postsurgery_forms.count(), 1)) * 100,
                    1
                ),
                'successful_outcomes': postsurgery_forms.filter(
                    resultado_final__icontains='exitoso'
                ).count()
            }
        }
        
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def export_dashboard(request):
    """Export dashboard data to Excel"""
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Dashboard Export"

        # Styling
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="2B4570", end_color="2B4570", fill_type="solid")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Patient Summary
        ws.append(["Resumen de Pacientes"])
        ws.append(["Fecha de Exportación", datetime.now().strftime("%Y-%m-%d %H:%M")])
        ws.append([])

        # Style headers
        for cell in ws[1:1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border

        # Add statistics sections
        sections = [
            ("Información General", get_general_stats(request.user)),
            ("Estadísticas ASA", get_asa_stats(request.user)),
            ("Complicaciones", get_complication_stats(request.user)),
            ("Métricas de Vía Aérea", get_airway_stats(request.user))
        ]

        row = 4
        for section_title, data in sections:
            ws.append([section_title])
            ws.merge_cells(f'A{row}:C{row}')
            ws[f'A{row}'].font = header_font
            ws[f'A{row}'].fill = header_fill
            
            row += 1
            for key, value in data.items():
                ws.append([key, value])
            
            row += 2

        # Set column widths
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 20

        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # Return file
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f'dashboard_export_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Helper functions for export
def get_general_stats(user):
    return {
        "Total Pacientes": Patient.objects.filter(medico=user, activo=True).count(),
        "Cirugías Este Mes": PreSurgeryForm.objects.filter(
            medico=user.get_full_name(),
            fecha_reporte__month=datetime.now().month
        ).count(),
        "Pacientes de Alto Riesgo": PreSurgeryForm.objects.filter(
            medico=user.get_full_name(),
            estado_fisico_asa__gte=4
        ).count()
    }

def get_asa_stats(user):
    return dict(PreSurgeryForm.objects.filter(
        medico=user.get_full_name()
    ).values('estado_fisico_asa').annotate(
        count=Count('estado_fisico_asa')
    ).values_list('estado_fisico_asa', 'count'))

def get_complication_stats(user):
    postsurgery_forms = PostDuringSurgeryForm.objects.filter(
        nombre_anestesiologo=user.get_full_name()
    )
    total = postsurgery_forms.count() or 1
    complications = postsurgery_forms.filter(
        complicaciones__isnull=False
    ).exclude(complicaciones='').count()
    
    return {
        "Total Cirugías": total,
        "Cirugías con Complicaciones": complications,
        "Tasa de Complicaciones": f"{(complications/total)*100:.2f}%"
    }

def get_airway_stats(user):
    presurgery_forms = PreSurgeryForm.objects.filter(
        medico=user.get_full_name()
    )
    return {
        "Vía Aérea Difícil": presurgery_forms.filter(
            Q(mallampati__gte=3) |
            Q(patil_aldrete__gte=3)
        ).count(),
        "Mallampati Promedio": presurgery_forms.aggregate(
            Avg('mallampati')
        )['mallampati__avg']
    }

def calculate_average_age(patients):
    total_age = 0
    count = 0
    for patient in patients:
        try:
            age = (datetime.now().date() - patient.fecha_nacimiento).days // 365
            total_age += age
            count += 1
        except:
            continue
    return round(total_age / max(count, 1), 1)


@login_required
def presurgery_detail(request, pk):
    # Get the pre-surgery form
    form = get_object_or_404(PreSurgeryForm, folio_hospitalizacion=pk)
    
    # Get the related patient
    patient = get_object_or_404(Patient, folio_hospitalizacion=pk.replace('PRE-', ''))
    
    # Check if user has permission to view this form
    if patient.medico != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver este formulario.')
        return redirect('patient-list')
    
    context = {
        'form': form,
        'patient': patient
    }
    
    return render(request, 'presurgery_detail.html', context)



@login_required
def dashboard(request):
    """
    Enhanced dashboard view with complete patient information
    """
    # Get current user's patients
    user_patients = Patient.objects.filter(medico=request.user, activo=True)
    
    # Get forms data
    presurgery_forms = PreSurgeryForm.objects.filter(
        medico=request.user.get_full_name()
    )
    
    postsurgery_forms = PostDuringSurgeryForm.objects.filter(
        folio_hospitalizacion__in=presurgery_forms.values('folio_hospitalizacion')
    )
    
    # Basic Statistics
    stats = {
        'total_patients': user_patients.count(),
        'active_patients': user_patients.filter(
            fecha_registro__gte=timezone.now() - timedelta(days=30)
        ).count(),
        'total_surgeries': presurgery_forms.count(),
        'completed_surgeries': postsurgery_forms.count()
    }
    
    # ASA Distribution
    asa_distribution = list(presurgery_forms.values('estado_fisico_asa')
        .annotate(count=Count('estado_fisico_asa'))
        .order_by('estado_fisico_asa'))
    
    # Complications Analysis
    complications_data = {
        'total': postsurgery_forms.count(),
        'with_complications': postsurgery_forms.filter(
            complicaciones__isnull=False
        ).exclude(complicaciones='').count(),
        'tipos': list(postsurgery_forms.exclude(
            complicaciones=''
        ).values('complicaciones').annotate(
            count=Count('complicaciones')
        ).order_by('-count')[:5])
    }
    
    # Airway Difficulty Metrics
    airway_metrics = {
        'difficult_airways': presurgery_forms.filter(
            Q(mallampati__gte=3) |
            Q(patil_aldrete__gte=3) |
            Q(distancia_inter_incisiva__lt=3)
        ).count(),
        'mallampati_distribution': list(presurgery_forms.values('mallampati')
            .annotate(count=Count('mallampati'))
            .order_by('mallampati')),
        'successful_intubation': postsurgery_forms.filter(numero_intentos=1).count(),
        'multiple_attempts': postsurgery_forms.filter(numero_intentos__gt=1).count()
    }
    
    # BMI Distribution
    bmi_ranges = {
        'underweight': presurgery_forms.filter(imc__lt=18.5).count(),
        'normal': presurgery_forms.filter(imc__range=(18.5, 24.9)).count(),
        'overweight': presurgery_forms.filter(imc__range=(25, 29.9)).count(),
        'obese': presurgery_forms.filter(imc__gte=30).count()
    }
    
    # Monthly Trends - Fixed Query
    monthly_data = presurgery_forms.annotate(
        month=TruncMonth('fecha_reporte')
    ).values('month').annotate(
        surgeries=Count('folio_hospitalizacion'),
        complications=Sum(
            Case(
                When(post_surgery_form__complicaciones__isnull=False, then=1),
                default=0,
                output_field=IntegerField(),
            )
        )
    ).order_by('month')
    
    # Recent High Risk Cases
    high_risk_cases = []
    for pre_form in presurgery_forms.filter(
        Q(estado_fisico_asa__gte=4) |
        Q(mallampati__gte=3) |
        Q(patil_aldrete__gte=3)
    ).order_by('-fecha_reporte')[:10]:
        risk_factors = []
        if pre_form.estado_fisico_asa >= 4:
            risk_factors.append(f'ASA {pre_form.estado_fisico_asa}')
        if pre_form.mallampati >= 3:
            risk_factors.append(f'Mallampati {pre_form.mallampati}')
        if pre_form.patil_aldrete >= 3:
            risk_factors.append('Patil-Aldrete Elevado')
        if pre_form.imc >= 30:
            risk_factors.append('Obesidad')
            
        high_risk_cases.append({
            'patient_name': f"{pre_form.nombres} {pre_form.apellidos}",
            'folio': pre_form.folio_hospitalizacion,
            'risk_factors': risk_factors,
            'fecha': pre_form.fecha_reporte
        })
    
    context = {
        'stats': stats,
        'asa_distribution': json.dumps(asa_distribution),
        'complications_data': json.dumps(complications_data),
        'airway_metrics': json.dumps(airway_metrics),
        'bmi_distribution': json.dumps(bmi_ranges),
        'monthly_data': json.dumps([{
            'month': data['month'].strftime('%Y-%m-%d'),
            'surgeries': data['surgeries'],
            'complications': data['complications'] or 0  # Handle None values
        } for data in monthly_data]),
        'high_risk_cases': high_risk_cases,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def get_risk_trends(request):
    """API endpoint for risk trend analysis"""
    try:
        date_range = int(request.GET.get('date_range', '30'))
        start_date = datetime.now() - timedelta(days=date_range)
        
        # Get trends data
        presurgery_forms = PreSurgeryForm.objects.filter(
            medico=request.user.get_full_name(),
            fecha_reporte__gte=start_date
        )
        
        # Calculate risk trends
        risk_trends = (presurgery_forms
            .annotate(week=TruncWeek('fecha_reporte'))
            .values('week')
            .annotate(
                high_risk=Count('id', filter=Q(estado_fisico_asa__gte=4)),
                medium_risk=Count('id', filter=Q(estado_fisico_asa=3)),
                low_risk=Count('id', filter=Q(estado_fisico_asa__lte=2))
            )
            .order_by('week')
        )
        
        return JsonResponse({
            'trends': list(risk_trends)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)