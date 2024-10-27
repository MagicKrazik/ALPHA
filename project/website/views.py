from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MedicRegistrationForm
from django.contrib.auth import get_user_model

# Create your views here.

# Home view
def home(request):
    return render(request, 'home.html')


User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = MedicRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Get cleaned data from form
                cleaned_data = form.cleaned_data
                
                # Create new user instance but don't save yet
                user = User(
                    username=cleaned_data['usuario'],
                    email=cleaned_data['email'],
                    nombre=cleaned_data['nombre'],
                    apellidos=cleaned_data['apellidos'],
                    telefono=cleaned_data['telefono'],
                    especialidad=cleaned_data['especialidad'][:3].upper(),  # Convert to model's format
                )
                
                # Set password
                user.set_password(cleaned_data['password1'])
                
                # Save the user
                user.save()
                
                messages.success(request, 'Registro exitoso. Por favor inicie sesión.')
                return redirect('login')  # Redirect to login page
                
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
        else:
            # If form is not valid, error messages will be shown automatically
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = MedicRegistrationForm()
    
    return render(request, 'register.html', {'form': form})