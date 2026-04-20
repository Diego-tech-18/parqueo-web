
from django.contrib import admin
from .models import Seccion, Espacio , Registro

# ADMIN: SECCIÓN


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    """Configuración del admin para Secciones"""
    
    list_display = ['nombre', 'tipo', 'total_espacios', 'espacios_libres', 'espacios_ocupados', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'descripcion')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

# ADMIN: ESPACIO


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    """Configuración del admin para Espacios"""
    
    list_display = ['numero', 'seccion', 'estado', 'posicion_fila', 'posicion_columna', 'activo']
    list_filter = ['seccion', 'estado', 'activo']
    search_fields = ['numero', 'notas']
    ordering = ['seccion', 'numero']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero', 'seccion', 'estado')
        }),
        ('Posición en el Mapa', {
            'fields': ('posicion_fila', 'posicion_columna')
        }),
        ('Estado y Notas', {
            'fields': ('activo', 'notas')
        }),
    )
    
    # Acciones rápidas
    actions = ['marcar_libre', 'marcar_ocupado', 'marcar_fuera_servicio']
    
    def marcar_libre(self, request, queryset):
        """Marca espacios seleccionados como LIBRE"""
        queryset.update(estado='LIBRE')
        self.message_user(request, f'{queryset.count()} espacios marcados como LIBRE')
    marcar_libre.short_description = "Marcar como LIBRE"
    
    def marcar_ocupado(self, request, queryset):
        """Marca espacios seleccionados como OCUPADO"""
        queryset.update(estado='OCUPADO')
        self.message_user(request, f'{queryset.count()} espacios marcados como OCUPADO')
    marcar_ocupado.short_description = "Marcar como OCUPADO"
    
    def marcar_fuera_servicio(self, request, queryset):
        """Marca espacios seleccionados como FUERA DE SERVICIO"""
        queryset.update(estado='FUERA_SERVICIO')
        self.message_user(request, f'{queryset.count()} espacios marcados como FUERA DE SERVICIO')
    marcar_fuera_servicio.short_description = "Marcar como FUERA DE SERVICIO"

    


# ADMIN: REGISTRO

@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'placa',
        'tipo_vehiculo',
        'espacio',
        'fecha_entrada',
        'fecha_salida',
        'tiempo_minutos',
        'tarifa',
        'horario_entrada',
        'estado',
    ]
    
    list_filter = [
        'estado',
        'horario_entrada',
        'tipo_vehiculo',
        'fecha_entrada',
    ]
    
    search_fields = ['placa', 'espacio__numero']
    
    readonly_fields = [
        'fecha_entrada',
        'horario_entrada',
        'creado_en',
        'actualizado_en',
    ]
    
    ordering = ['-fecha_entrada']