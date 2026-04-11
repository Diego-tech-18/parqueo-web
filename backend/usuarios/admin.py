from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


# ── Registrar el modelo en el panel admin de Django ──
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    # Columnas que se ven en la lista de usuarios
    list_display  = ['email', 'nombre', 'apellido', 'ci', 'rol', 'activo', 'creado_en']

    # Filtros del lado derecho
    list_filter   = ['rol', 'activo']

    # Búsqueda por estos campos
    search_fields = ['email', 'nombre', 'apellido', 'ci']

    # Orden por defecto
    ordering      = ['nombre']

    # Campos al editar un usuario
    fieldsets = (
        ('Información personal', {
            'fields': ('email', 'nombre', 'apellido', 'ci', 'foto')
        }),
        ('Acceso', {
            'fields': ('rol', 'activo', 'is_staff', 'password')
        }),
        ('Fechas', {
            'fields': ('creado_en',)
        }),
    )

    # Campos al crear un usuario nuevo
    add_fieldsets = (
        ('Nuevo usuario', {
            'fields': ('email', 'nombre', 'apellido', 'ci', 'rol', 'foto', 'password1', 'password2')
        }),
    )

    readonly_fields = ['creado_en']