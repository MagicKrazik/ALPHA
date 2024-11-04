# forms.py
from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
from .models import ContactMessage

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