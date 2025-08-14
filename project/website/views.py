from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import MedicRegistrationForm, TreatmentCaseForm, PatientForm
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .utils import account_activation_token, send_verification_email
from django.utils import timezone
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from .forms import PreSurgeryCreateForm, PostSurgeryCreateForm
from .models import PostDuringSurgeryForm, TreatmentCase, PreSurgeryForm
from django.db.models import Count, Avg, Q, Sum
from django.db.models.functions import TruncMonth, TruncWeek, ExtractHour
import json
from datetime import datetime, timedelta
from django.http import JsonResponse, FileResponse, Http404
from .models import Patient, PreSurgeryForm, PostDuringSurgeryForm, RiskAlert
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from io import BytesIO
import pandas as pd


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


## Patient and Treatment Case Views

@login_required
def patient_list(request):
    """
    List view for patients with search and filtering
    """
    search_query = request.GET.get('q', '')
    
    # Get treatment cases the user has access to
    treatment_cases = TreatmentCase.objects.filter(
        Q(medico_responsable=request.user) | Q(medicos_secundarios=request.user),
        activo=True
    ).select_related('patient')
    
    if search_query:
        treatment_cases = treatment_cases.filter(
            Q(folio_hospitalizacion__icontains=search_query) |
            Q(patient__nombres__icontains=search_query) |
            Q(patient__apellidos__icontains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(treatment_cases, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'treatment_cases': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'patient_list.html', context)

@login_required
def patient_create(request):
    """
    Create view for new patient and treatment case
    """
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        case_form = TreatmentCaseForm(request.POST, request.FILES)
        
        if patient_form.is_valid() and case_form.is_valid():
            try:
                with transaction.atomic():
                    # Save patient
                    patient = patient_form.save()
                    
                    # Save treatment case
                    treatment_case = case_form.save(commit=False)
                    treatment_case.patient = patient
                    treatment_case.medico_responsable = request.user
                    treatment_case.save()
                    
                    messages.success(request, _('Paciente y caso registrados exitosamente.'))
                    return redirect('patient-detail', treatment_case.id_case)
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
    else:
        patient_form = PatientForm()
        case_form = TreatmentCaseForm()
    
    return render(request, 'patient_form.html', {
        'patient_form': patient_form,
        'case_form': case_form
    })

@login_required
def patient_detail(request, pk):
    """
    Detail view for treatment case
    """
    treatment_case = get_object_or_404(TreatmentCase, id_case=pk)
    
    # Check access permissions
    if not treatment_case.user_has_access(request.user):
        messages.error(request, _('No tienes permiso para ver esta información.'))
        return redirect('patient-list')
    
    # Get related forms
    try:
        pre_surgery_form = treatment_case.pre_surgery_form
    except PreSurgeryForm.DoesNotExist:
        pre_surgery_form = None
    
    try:
        post_surgery_form = treatment_case.post_surgery_form
    except PostDuringSurgeryForm.DoesNotExist:
        post_surgery_form = None
    
    # Get alerts for this case
    alerts = RiskAlert.objects.filter(
        treatment_case=treatment_case,
        status='active'
    ).order_by('-triggered_at')
    
    context = {
        'treatment_case': treatment_case,
        'patient': treatment_case.patient,
        'pre_surgery_form': pre_surgery_form,
        'post_surgery_form': post_surgery_form,
        'alerts': alerts,
    }
    
    return render(request, 'patient_detail.html', context)

@login_required
def patient_update(request, pk):
    """
    Update view for treatment case and patient
    """
    treatment_case = get_object_or_404(TreatmentCase, id_case=pk)
    
    # Check access permissions
    if not treatment_case.user_has_access(request.user):
        messages.error(request, _('No tienes permiso para editar esta información.'))
        return redirect('patient-list')
    
    if request.method == 'POST':
        patient_form = PatientForm(request.POST, instance=treatment_case.patient)
        case_form = TreatmentCaseForm(request.POST, request.FILES, instance=treatment_case)
        
        if patient_form.is_valid() and case_form.is_valid():
            try:
                with transaction.atomic():
                    patient_form.save()
                    case_form.save()
                    messages.success(request, _('Información actualizada exitosamente.'))
                    return redirect('patient-detail', pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')
    else:
        patient_form = PatientForm(instance=treatment_case.patient)
        case_form = TreatmentCaseForm(instance=treatment_case)
    
    return render(request, 'patient_form.html', {
        'patient_form': patient_form,
        'case_form': case_form,
        'treatment_case': treatment_case
    })

@login_required
def patient_delete(request, pk):
    """
    Delete view for treatment case (soft delete)
    """
    treatment_case = get_object_or_404(TreatmentCase, id_case=pk)
    
    # Check access permissions
    if treatment_case.medico_responsable != request.user and not request.user.is_staff:
        messages.error(request, _('No tienes permiso para eliminar este caso.'))
        return redirect('patient-list')
    
    if request.method == 'POST':
        treatment_case.activo = False
        treatment_case.save()
        messages.success(request, _('Caso eliminado exitosamente.'))
        return redirect('patient-list')
    
    return render(request, 'patient_confirm_delete.html', {
        'treatment_case': treatment_case,
        'patient': treatment_case.patient
    })


## Pre and Post Surgery Forms

@login_required
def presurgery_create(request, case_id):
    """
    Create pre-surgery form for a treatment case
    """
    treatment_case = get_object_or_404(TreatmentCase, id_case=case_id)
    
    # Check access permissions
    if not treatment_case.user_has_access(request.user):
        messages.error(request, _('No tienes permiso para crear este formulario.'))
        return redirect('patient-list')
    
    # Check if pre-surgery form already exists
    if hasattr(treatment_case, 'pre_surgery_form'):
        messages.warning(request, 'Ya existe un formulario pre-quirúrgico para este caso.')
        return redirect('presurgery-detail', treatment_case.pre_surgery_form.id)
    
    if request.method == 'POST':
        form = PreSurgeryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    presurgery = form.save(commit=False)
                    presurgery.treatment_case = treatment_case
                    presurgery.save()
                    
                    messages.success(request, 'Formulario pre-quirúrgico creado exitosamente.')
                    return redirect('patient-detail', case_id)
            except Exception as e:
                messages.error(request, f'Error al guardar el formulario: {str(e)}')
    else:
        # Pre-populate form with patient data
        initial_data = {
            'fecha_reporte': timezone.now().date(),
            'medico_tratante': request.user.get_full_name(),
        }
        form = PreSurgeryCreateForm(initial=initial_data)

    return render(request, 'presurgery_form.html', {
        'form': form,
        'treatment_case': treatment_case,
        'patient': treatment_case.patient
    })

@login_required
def presurgery_detail(request, pk):
    """
    Detail view for pre-surgery form
    """
    presurgery = get_object_or_404(PreSurgeryForm, id=pk)
    
    # Check access permissions
    if not presurgery.treatment_case.user_has_access(request.user):
        messages.error(request, _('No tienes permiso para ver este formulario.'))
        return redirect('patient-list')
    
    return render(request, 'presurgery_detail.html', {
        'form': presurgery,
        'treatment_case': presurgery.treatment_case,
        'patient': presurgery.patient
    })

@login_required
def presurgery_update(request, pk):
    """
    Update view for pre-surgery form
    """
    presurgery = get_object_or_404(PreSurgeryForm, id=pk)
    
    # Check access permissions
    if not presurgery.treatment_case.user_has_access(request.user):
        messages.error(request, _('No tienes permiso para editar este formulario.'))
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
        form = PreSurgeryCreateForm(instance=presurgery)
    
    return render(request, 'presurgery_form.html', {
        'form': form,
        'presurgery': presurgery,
        'treatment_case': presurgery.treatment_case,
        'patient': presurgery.patient
    })

@login_required
def postsurgery_create(request, case_id):
    """
    Create post-surgery form for a treatment case
    """
    treatment_case = get_object_or_404(TreatmentCase, id_case=case_id)
    
    # Check access permissions
    if not treatment_case.user_has_access(request.user):
        messages.error(request, _('No tienes permiso para crear este formulario.'))
        return redirect('patient-list')
    
    # Check if pre-surgery form exists
    if not hasattr(treatment_case, 'pre_surgery_form'):
        messages.error(request, 'Se requiere un formulario pre-quirúrgico antes de crear el post-quirúrgico.')
        return redirect('patient-detail', case_id)
    
    # Check if post-surgery form already exists
    if hasattr(treatment_case, 'post_surgery_form'):
        messages.warning(request, 'Ya existe un formulario post-quirúrgico para este caso.')
        return redirect('postsurgery-detail', treatment_case.post_surgery_form.id)
    
    if request.method == 'POST':
        form = PostSurgeryCreateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    postsurgery = form.save(commit=False)
                    postsurgery.treatment_case = treatment_case
                    postsurgery.pre_surgery_form = treatment_case.pre_surgery_form
                    postsurgery.save()
                    
                    messages.success(request, 'Formulario post-quirúrgico creado exitosamente.')
                    return redirect('patient-detail', case_id)
            except Exception as e:
                messages.error(request, f'Error al guardar el formulario: {str(e)}')
    else:
        # Pre-populate with default values
        initial_data = {
            'nombre_anestesiologo': request.user.get_full_name(),
            'especialidad': request.user.get_especialidad_display(),
        }
        form = PostSurgeryCreateForm(initial=initial_data)

    return render(request, 'postsurgery_form.html', {
        'form': form,
        'treatment_case': treatment_case,
        'patient': treatment_case.patient
    })

@login_required
def postsurgery_detail(request, pk):
    """
    Detail view for post-surgery form
    """
    postsurgery = get_object_or_404(PostDuringSurgeryForm, id=pk)
    
    # Check access permissions
    if not postsurgery.treatment_case.user_has_access(request.user):
        messages.error(request, _('No tienes permiso para ver este formulario.'))
        return redirect('patient-list')
    
    return render(request, 'postsurgery_detail.html', {
        'form': postsurgery,
        'treatment_case': postsurgery.treatment_case,
        'patient': postsurgery.patient
    })

@login_required
def postsurgery_update(request, pk):
    """
    Update view for post-surgery form
    """
    postsurgery = get_object_or_404(PostDuringSurgeryForm, id=pk)
    
    # Check access permissions
    if not postsurgery.treatment_case.user_has_access(request.user):
        messages.error(request, _('No tienes permiso para editar este formulario.'))
        return redirect('patient-list')
    
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
        form = PostSurgeryCreateForm(instance=postsurgery)
    
    return render(request, 'postsurgery_form.html', {
        'form': form,
        'postsurgery': postsurgery,
        'treatment_case': postsurgery.treatment_case,
        'patient': postsurgery.patient
    })


## Dashboard Views

@login_required
def dashboard(request):
    """
    Main dashboard view with statistics and charts
    """
    # Get user's accessible treatment cases
    user_cases = TreatmentCase.objects.filter(
        Q(medico_responsable=request.user) | Q(medicos_secundarios=request.user),
        activo=True
    )
    
    # Basic Statistics
    total_cases = user_cases.count()
    cases_this_month = user_cases.filter(
        fecha_ingreso__month=datetime.now().month
    ).count()
    
    # PreSurgery Statistics
    presurgery_forms = PreSurgeryForm.objects.filter(
        treatment_case__in=user_cases
    )
    
    # ASA Score Distribution
    asa_distribution = (presurgery_forms
        .values('estado_fisico_asa')
        .annotate(count=Count('estado_fisico_asa'))
        .order_by('estado_fisico_asa'))
    
    # Mallampati Distribution
    mallampati_distribution = (presurgery_forms
        .values('mallampati')
        .annotate(count=Count('mallampati'))
        .order_by('mallampati'))
    
    # Airway Risk Factors
    high_risk_airways = presurgery_forms.filter(
        Q(mallampati__gte=3) |
        Q(patil_aldrete__gte=3) |
        Q(distancia_inter_incisiva__lt=3)
    ).count()
    
    # Monthly Cases Trend
    monthly_cases = (user_cases
        .annotate(month=TruncMonth('fecha_ingreso'))
        .values('month')
        .annotate(count=Count('id_case'))
        .order_by('month'))
    
    # BMI Distribution
    bmi_distribution = {
        'underweight': presurgery_forms.filter(imc__lt=18.5).count(),
        'normal': presurgery_forms.filter(imc__range=(18.5, 24.9)).count(),
        'overweight': presurgery_forms.filter(imc__range=(25, 29.9)).count(),
        'obese': presurgery_forms.filter(imc__gte=30).count()
    }
    
    # Age Distribution
    def calculate_age(birth_date):
        return (datetime.now().date() - birth_date).days // 365
    
    age_distribution = {
        '0-18': 0,
        '19-40': 0,
        '41-60': 0,
        '60+': 0
    }
    
    for case in user_cases.select_related('patient'):
        age = calculate_age(case.patient.fecha_nacimiento)
        if age <= 18:
            age_distribution['0-18'] += 1
        elif age <= 40:
            age_distribution['19-40'] += 1
        elif age <= 60:
            age_distribution['41-60'] += 1
        else:
            age_distribution['60+'] += 1
    
    # Complications Analysis
    postsurgery_forms = PostDuringSurgeryForm.objects.filter(
        treatment_case__in=user_cases
    )
    
    complications_data = {
        'total_surgeries': postsurgery_forms.count(),
        'with_complications': postsurgery_forms.filter(
            complicaciones__isnull=False
        ).exclude(complicaciones='').count(),
        'with_morbidity': postsurgery_forms.filter(morbilidad=True).count(),
        'with_mortality': postsurgery_forms.filter(mortalidad=True).count()
    }
    
    # Calculate percentages
    total_surgeries = complications_data['total_surgeries'] or 1
    complications_data.update({
        'complications_percentage': round(
            (complications_data['with_complications'] / total_surgeries) * 100
        ),
        'morbidity_percentage': round(
            (complications_data['with_morbidity'] / total_surgeries) * 100
        ),
        'mortality_percentage': round(
            (complications_data['with_mortality'] / total_surgeries) * 100
        )
    })

    # Intubation Success Analysis
    intubation_data = {
        'total_attempts': postsurgery_forms.count(),
        'first_attempt': postsurgery_forms.filter(numero_intentos=1).count(),
        'multiple_attempts': postsurgery_forms.filter(numero_intentos__gt=1).count(),
    }
    
    # Calculate first attempt success rate
    total_intubations = intubation_data['total_attempts'] or 1
    intubation_data['success_rate'] = round(
        (intubation_data['first_attempt'] / total_intubations) * 100
    )

    # Active alerts count
    active_alerts = RiskAlert.objects.filter(
        treatment_case__in=user_cases,
        status='active'
    ).count()

    context = {
        'total_cases': total_cases,
        'cases_this_month': cases_this_month,
        'high_risk_airways': high_risk_airways,
        'active_alerts': active_alerts,
        'asa_distribution': json.dumps(list(asa_distribution)),
        'mallampati_data': json.dumps(list(mallampati_distribution)),
        'monthly_cases': json.dumps([{
            'month': d['month'].strftime('%Y-%m-%d') if d['month'] else None,
            'count': d['count']
        } for d in monthly_cases]),
        'bmi_distribution': json.dumps(bmi_distribution),
        'age_distribution': json.dumps(age_distribution),
        'complications_data': complications_data,
        'intubation_data': intubation_data,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def get_dashboard_stats(request):
    """API endpoint for real-time dashboard statistics"""
    try:
        date_range = request.GET.get('date_range', '30')
        start_date = datetime.now() - timedelta(days=int(date_range))
        
        # Get user's accessible treatment cases
        user_cases = TreatmentCase.objects.filter(
            Q(medico_responsable=request.user) | Q(medicos_secundarios=request.user),
            activo=True,
            fecha_ingreso__gte=start_date
        )
        
        presurgery_forms = PreSurgeryForm.objects.filter(
            treatment_case__in=user_cases
        )
        postsurgery_forms = PostDuringSurgeryForm.objects.filter(
            treatment_case__in=user_cases
        )

        # Calculate statistics
        stats = {
            'summary': {
                'total_cases': user_cases.count(),
                'active_cases': user_cases.filter(fecha_alta__isnull=True).count(),
                'surgeries_completed': postsurgery_forms.count(),
                'high_risk_cases': presurgery_forms.filter(
                    Q(mallampati__gte=3) | Q(estado_fisico_asa__gte=4)
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
                .annotate(count=Count('id'))
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

        # Export header
        ws.append(["Reporte de Dashboard ALPHA"])
        ws.append(["Fecha de Exportación", datetime.now().strftime("%Y-%m-%d %H:%M")])
        ws.append(["Doctor", request.user.get_full_name()])
        ws.append([])

        # Style headers
        for cell in ws[1:1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border

        # Get user data
        user_cases = TreatmentCase.objects.filter(
            Q(medico_responsable=request.user) | Q(medicos_secundarios=request.user),
            activo=True
        )

        # Add statistics sections
        sections = [
            ("Información General", get_general_stats(request.user, user_cases)),
            ("Estadísticas ASA", get_asa_stats(user_cases)),
            ("Complicaciones", get_complication_stats(user_cases)),
            ("Métricas de Vía Aérea", get_airway_stats(user_cases))
        ]

        row = 5
        for section_title, data in sections:
            ws.append([section_title])
            ws.merge_cells(f'A{row}:C{row}')
            ws[f'A{row}'].font = header_font
            ws[f'A{row}'].fill = header_fill
            
            row += 1
            for key, value in data.items():
                ws.append([key, value])
                row += 1
            
            row += 1

        # Set column widths
        ws.column_dimensions['A'].width = 35
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 20

        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # Return file
        response = FileResponse(
            buffer,
            as_attachment=True,
            filename=f'dashboard_export_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Helper functions for export
def get_general_stats(user, user_cases):
    return {
        "Total Casos": user_cases.count(),
        "Casos Este Mes": user_cases.filter(
            fecha_ingreso__month=datetime.now().month
        ).count(),
        "Casos de Alto Riesgo": PreSurgeryForm.objects.filter(
            treatment_case__in=user_cases,
            estado_fisico_asa__gte=4
        ).count()
    }

def get_asa_stats(user_cases):
    return dict(PreSurgeryForm.objects.filter(
        treatment_case__in=user_cases
    ).values('estado_fisico_asa').annotate(
        count=Count('estado_fisico_asa')
    ).values_list('estado_fisico_asa', 'count'))

def get_complication_stats(user_cases):
    postsurgery_forms = PostDuringSurgeryForm.objects.filter(
        treatment_case__in=user_cases
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

def get_airway_stats(user_cases):
    presurgery_forms = PreSurgeryForm.objects.filter(
        treatment_case__in=user_cases
    )
    return {
        "Vía Aérea Difícil": presurgery_forms.filter(
            Q(mallampati__gte=3) | Q(patil_aldrete__gte=3)
        ).count(),
        "Mallampati Promedio": presurgery_forms.aggregate(
            Avg('mallampati')
        )['mallampati__avg'] or 0
    }


# ===== ALERT SYSTEM VIEWS =====

@login_required
def alerts_list(request):
    """
    List view for risk alerts
    """
    # Get user's accessible treatment cases
    user_cases = TreatmentCase.objects.filter(
        Q(medico_responsable=request.user) | Q(medicos_secundarios=request.user),
        activo=True
    )
    
    # Filter alerts
    status_filter = request.GET.get('status', 'active')
    alerts = RiskAlert.objects.filter(
        treatment_case__in=user_cases
    )
    
    if status_filter != 'all':
        alerts = alerts.filter(status=status_filter)
    
    alerts = alerts.order_by('-triggered_at')
    
    # Add pagination
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'alerts': page_obj,
        'status_filter': status_filter,
    }
    
    return render(request, 'alerts_list.html', context)

@login_required
def alert_detail(request, pk):
    """
    Detail view for a specific alert
    """
    alert = get_object_or_404(RiskAlert, id=pk)
    
    # Check access permissions
    if not alert.treatment_case.user_has_access(request.user):
        raise Http404
    
    return render(request, 'alert_detail.html', {
        'alert': alert,
        'treatment_case': alert.treatment_case,
    })

@login_required
def alert_acknowledge(request, pk):
    """
    Acknowledge an alert
    """
    alert = get_object_or_404(RiskAlert, id=pk)
    
    # Check access permissions
    if not alert.treatment_case.user_has_access(request.user):
        raise Http404
    
    if request.method == 'POST':
        alert.acknowledge(request.user)
        messages.success(request, 'Alerta reconocida exitosamente.')
        return redirect('alert-detail', pk)
    
    return redirect('alert-detail', pk)