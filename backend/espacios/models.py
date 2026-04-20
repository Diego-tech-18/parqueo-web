from django.db import models



class Seccion(models.Model):
    """
    Representa una sección del parqueo (A, B, etc.)
    """
    
    # ── Opciones de tipo de sección ──
    TIPO_CHOICES = [
        ('ASIGNADOS', 'Asignados'),    # Para abonados
        ('ROTATIVOS', 'Rotativos'),    # Para ocasionales
    ]
    
    # ── Campos ──
    nombre = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nombre de la sección (ej: A, B, VIP)"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='ROTATIVOS',
        help_text="Tipo de espacios en esta sección"
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción opcional de la sección"
    )
    
    activo = models.BooleanField(
        default=True,
        help_text="Si está desactivada, no se muestra en el mapa"
    )
    
    # ── Auditoría ──
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'secciones'
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
        ordering = ['nombre']
    
    def __str__(self):
        return f"Sección {self.nombre} ({self.get_tipo_display()})"
    
    @property
    def total_espacios(self):
        """Cuenta cuántos espacios tiene esta sección"""
        return self.espacios.count()
    
    @property
    def espacios_libres(self):
        """Cuenta cuántos espacios están libres"""
        return self.espacios.filter(estado='LIBRE').count()
    
    @property
    def espacios_ocupados(self):
        """Cuenta cuántos espacios están ocupados"""
        return self.espacios.filter(estado='OCUPADO').count()



class Espacio(models.Model):
    """
    Representa un espacio individual de estacionamiento
    """
    
    # ── Opciones de estado ──
    ESTADO_CHOICES = [
        ('LIBRE', 'Libre'),                        # Disponible
        ('OCUPADO', 'Ocupado'),                    # En uso
        ('FUERA_SERVICIO', 'Fuera de Servicio'),  # No disponible
    ]
    
    # ── Campos ──
    numero = models.CharField(
        max_length=20,
        unique=True,
        help_text="Número/código del espacio (ej: A1, A2, B1)"
    )
    
    seccion = models.ForeignKey(
        Seccion,
        on_delete=models.CASCADE,
        related_name='espacios',
        help_text="Sección a la que pertenece este espacio"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='LIBRE',
        help_text="Estado actual del espacio"
    )
    
    posicion_fila = models.IntegerField(
        default=0,
        help_text="Fila en el mapa visual (0-indexado)"
    )
    
    posicion_columna = models.IntegerField(
        default=0,
        help_text="Columna en el mapa visual (0-indexado)"
    )
    
    activo = models.BooleanField(
        default=True,
        help_text="Si está desactivado, no se puede usar"
    )
    
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas o comentarios sobre este espacio"
    )
    
    # ── Auditoría ──
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'espacios'
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['seccion', 'numero']
    
    def __str__(self):
        return f"{self.numero} - {self.get_estado_display()}"
    
    def marcar_libre(self):
        """Marca el espacio como libre"""
        self.estado = 'LIBRE'
        self.save()
    
    def marcar_ocupado(self):
        """Marca el espacio como ocupado"""
        self.estado = 'OCUPADO'
        self.save()
    
    def marcar_fuera_servicio(self):
        """Marca el espacio como fuera de servicio"""
        self.estado = 'FUERA_SERVICIO'
        self.save()
    
    @property
    def esta_libre(self):
        """Verifica si el espacio está libre"""
        return self.estado == 'LIBRE' and self.activo
    
    @property
    def esta_ocupado(self):
        """Verifica si el espacio está ocupado"""
        return self.estado == 'OCUPADO'



# ══════════════════════════════════════════════════════════════════════════
# MODELO: REGISTRO (Entradas/Salidas)
# ══════════════════════════════════════════════════════════════════════════

class Registro(models.Model):
    """
    Representa un registro de entrada/salida de un vehículo
    """
    
    # ── Opciones de tipo de vehículo ──
    TIPO_VEHICULO_CHOICES = [
        ('AUTO', 'Auto'),
        ('MOTO', 'Moto'),
        ('CAMIONETA', 'Camioneta'),
    ]
    
    # ── Opciones de estado ──
    ESTADO_CHOICES = [
        ('EN_CURSO', 'En Curso'),      # Vehículo dentro del parqueo
        ('FINALIZADO', 'Finalizado'),  # Vehículo ya salió
    ]
    
    # ── Opciones de horario ──
    HORARIO_CHOICES = [
        ('DIURNO', 'Diurno'),      # 06:00 - 18:00
        ('NOCTURNO', 'Nocturno'),  # 19:00 - 05:59
    ]
    
    # ── Relaciones ──
    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.PROTECT,  # No permitir eliminar espacio si tiene registros
        related_name='registros',
        help_text="Espacio asignado a este vehículo"
    )
    
    # ── Datos del vehículo ──
    placa = models.CharField(
        max_length=20,
        help_text="Placa del vehículo (ej: ABC-123)"
    )
    
    tipo_vehiculo = models.CharField(
        max_length=20,
        choices=TIPO_VEHICULO_CHOICES,
        default='AUTO',
        help_text="Tipo de vehículo"
    )
    
    # ── Fechas y tiempos ──
    fecha_entrada = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de entrada (automática)"
    )
    
    fecha_salida = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de salida"
    )
    
    # ── Cálculos ──
    tiempo_minutos = models.IntegerField(
        null=True,
        blank=True,
        help_text="Tiempo total en minutos"
    )
    
    tarifa = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Tarifa total a pagar en Bs."
    )
    
    horario_entrada = models.CharField(
        max_length=20,
        choices=HORARIO_CHOICES,
        help_text="Horario de entrada (diurno/nocturno)"
    )
    
    # ── Estado ──
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='EN_CURSO',
        help_text="Estado del registro"
    )
    
    # ── Observaciones ──
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas u observaciones adicionales"
    )
    
    # ── Auditoría ──
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'registros'
        verbose_name = 'Registro'
        verbose_name_plural = 'Registros'
        ordering = ['-fecha_entrada']  # Más recientes primero
        indexes = [
            models.Index(fields=['placa']),  # Índice para búsquedas rápidas por placa
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_entrada']),
        ]
    
    def __str__(self):
        return f"{self.placa} - {self.espacio.numero} ({self.get_estado_display()})"
    
    @property
    def esta_activo(self):
        """Verifica si el registro está en curso (vehículo dentro)"""
        return self.estado == 'EN_CURSO'
    
    @property
    def tiempo_transcurrido(self):
        """
        Calcula el tiempo transcurrido desde la entrada
        Retorna en formato legible
        """
        from django.utils import timezone
        
        if self.fecha_salida:
            delta = self.fecha_salida - self.fecha_entrada
        else:
            delta = timezone.now() - self.fecha_entrada
        
        horas = int(delta.total_seconds() // 3600)
        minutos = int((delta.total_seconds() % 3600) // 60)
        
        return f"{horas}h {minutos}min"
    
    def calcular_tiempo_minutos(self):
        """Calcula el tiempo total en minutos"""
        from django.utils import timezone
        
        if self.fecha_salida:
            delta = self.fecha_salida - self.fecha_entrada
        else:
            delta = timezone.now() - self.fecha_entrada
        
        return int(delta.total_seconds() / 60)