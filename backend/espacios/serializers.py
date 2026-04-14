from rest_framework import serializers
from .models import Seccion, Espacio



class SeccionSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Sección
    Incluye estadísticas calculadas
    """
    
    # ── Campos calculados (read-only) ──
    total_espacios = serializers.IntegerField(read_only=True)
    espacios_libres = serializers.IntegerField(read_only=True)
    espacios_ocupados = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Seccion
        fields = [
            'id',
            'nombre',
            'tipo',
            'descripcion',
            'activo',
            'total_espacios',
            'espacios_libres',
            'espacios_ocupados',
            'creado_en',
            'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']




class EspacioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Espacio
    Incluye información de la sección
    """
    
    # ── Mostrar nombre de la sección (read-only) ──
    seccion_nombre = serializers.CharField(
        source='seccion.nombre',
        read_only=True
    )
    
    # ── Mostrar tipo de la sección (read-only) ──
    seccion_tipo = serializers.CharField(
        source='seccion.tipo',
        read_only=True
    )
    
    # ── Campos calculados ──
    esta_libre = serializers.BooleanField(read_only=True)
    esta_ocupado = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Espacio
        fields = [
            'id',
            'numero',
            'seccion',
            'seccion_nombre',
            'seccion_tipo',
            'estado',
            'posicion_fila',
            'posicion_columna',
            'activo',
            'notas',
            'esta_libre',
            'esta_ocupado',
            'creado_en',
            'actualizado_en',
        ]
        read_only_fields = ['id', 'creado_en', 'actualizado_en']
    
    def validate_numero(self, value):
        """
        Valida que el número del espacio sea único
        """
        # En creación
        if not self.instance:
            if Espacio.objects.filter(numero=value).exists():
                raise serializers.ValidationError(
                    f"Ya existe un espacio con el número '{value}'"
                )
        # En edición
        else:
            if Espacio.objects.filter(numero=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    f"Ya existe un espacio con el número '{value}'"
                )
        
        return value




class CambiarEstadoSerializer(serializers.Serializer):
    """
    Serializer para cambiar el estado de un espacio
    Solo recibe el nuevo estado
    """
    
    estado = serializers.ChoiceField(
        choices=Espacio.ESTADO_CHOICES,
        required=True,
        help_text="Nuevo estado del espacio"
    )
    
    notas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Notas opcionales sobre el cambio"
    )