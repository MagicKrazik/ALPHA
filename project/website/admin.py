from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import MedicoUser

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
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'date_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'nombre', 'apellidos', 'email')
    ordering = ('username',)