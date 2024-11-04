from django.shortcuts import render, redirect
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