from rest_framework import serializers
from .models import Seccion, Espacio, Registro



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


    # ══════════════════════════════════════════════════════════════════════════
# SERIALIZER: REGISTRO
# ══════════════════════════════════════════════════════════════════════════

class RegistroSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el modelo Registro
    """
    
    # ── Campos relacionados (read-only) ──
    espacio_numero = serializers.CharField(
        source='espacio.numero',
        read_only=True
    )
    
    seccion_nombre = serializers.CharField(
        source='espacio.seccion.nombre',
        read_only=True
    )
    
    # ── Campos calculados ──
    tiempo_transcurrido = serializers.CharField(read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Registro
        fields = [
            'id',
            'espacio',
            'espacio_numero',
            'seccion_nombre',
            'placa',
            'tipo_vehiculo',
            'fecha_entrada',
            'fecha_salida',
            'tiempo_minutos',
            'tarifa',
            'horario_entrada',
            'estado',
            'notas',
            'tiempo_transcurrido',
            'esta_activo',
            'creado_en',
            'actualizado_en',
        ]
        read_only_fields = [
            'id', 
            'fecha_entrada', 
            'horario_entrada',
            'creado_en', 
            'actualizado_en'
        ]


# ══════════════════════════════════════════════════════════════════════════
# SERIALIZER: REGISTRAR ENTRADA
# ══════════════════════════════════════════════════════════════════════════

class RegistrarEntradaSerializer(serializers.Serializer):
    """
    Serializer para registrar entrada de vehículo
    Solo necesita: placa, tipo_vehiculo, espacio
    """
    
    placa = serializers.CharField(
        max_length=20,
        required=True,
        help_text="Placa del vehículo (ej: ABC-123)"
    )
    
    tipo_vehiculo = serializers.ChoiceField(
        choices=Registro.TIPO_VEHICULO_CHOICES,
        default='AUTO',
        help_text="Tipo de vehículo"
    )
    
    espacio = serializers.IntegerField(
        required=True,
        help_text="ID del espacio a asignar"
    )
    
    notas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Notas opcionales"
    )
    
    def validate_placa(self, value):
        """Validar formato de placa"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("La placa debe tener al menos 3 caracteres")
        return value.upper().strip()
    
    def validate_espacio(self, value):
        """Validar que el espacio exista y esté disponible"""
        try:
            espacio = Espacio.objects.get(pk=value)
        except Espacio.DoesNotExist:
            raise serializers.ValidationError("El espacio no existe")
        
        # Verificar que esté libre
        if espacio.estado != 'LIBRE':
            raise serializers.ValidationError(
                f"El espacio {espacio.numero} no está disponible"
            )
        
        # Verificar que sea de sección ROTATIVOS
        if espacio.seccion.tipo != 'ROTATIVOS':
            raise serializers.ValidationError(
                "Solo se pueden registrar entradas en espacios rotativos"
            )
        
        # Verificar que no tenga registro activo
        if Registro.objects.filter(espacio=espacio, estado='EN_CURSO').exists():
            raise serializers.ValidationError(
                f"El espacio {espacio.numero} ya tiene un registro activo"
            )
        
        return value


# ══════════════════════════════════════════════════════════════════════════
# SERIALIZER: REGISTRAR SALIDA
# ══════════════════════════════════════════════════════════════════════════

class RegistrarSalidaSerializer(serializers.Serializer):
    """
    Serializer para registrar salida
    Puede buscar por placa o por ID de registro
    """
    
    placa = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Placa del vehículo para buscar"
    )
    
    registro_id = serializers.IntegerField(
        required=False,
        help_text="ID del registro directamente"
    )
    
    notas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Notas de salida"
    )
    
    def validate(self, data):
        """Validar que se proporcione placa o registro_id"""
        if not data.get('placa') and not data.get('registro_id'):
            raise serializers.ValidationError(
                "Debe proporcionar 'placa' o 'registro_id'"
            )
        return data