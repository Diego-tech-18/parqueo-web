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
        """Cuenta cuántos espacios ACTIVOS tiene esta sección.
        Los espacios inactivos (soft-deleted) no se cuentan."""
        return self.espacios.filter(activo=True).count()

    @property
    def espacios_libres(self):
        """Cuenta cuántos espacios activos están libres."""
        return self.espacios.filter(estado='LIBRE', activo=True).count()

    @property
    def espacios_ocupados(self):
        """Cuenta cuántos espacios activos están ocupados."""
        return self.espacios.filter(estado='OCUPADO', activo=True).count()



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



    # ── "Foto" de la tarifa vigente al momento de la ENTRADA ──
    # Se copian aquí para que cambios posteriores en la configuración
    # de tarifas NO afecten a vehículos que ya estaban dentro.
    # (Igual que una factura: conserva el precio del momento de emisión.)
    tarifa_primera_hora_diurno = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    tarifa_hora_adicional_diurno = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    tarifa_primera_hora_nocturno = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    tarifa_hora_adicional_nocturno = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    tarifa_hora_inicio_diurno = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    tarifa_hora_fin_diurno = models.PositiveSmallIntegerField(
        null=True, blank=True
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


class Tarifa(models.Model):
    """
    Configuración global de tarifas del parqueo.

    Patrón Singleton: siempre existe EXACTAMENTE UNA fila (pk=1).
    El administrador edita estos valores desde la web y toman efecto
    inmediatamente, sin necesidad de redesplegar el código.

    Aplica solo a vehículos con cálculo automático (autos) en secciones
    ROTATIVAS. Las motos se cobran de forma manual, por lo que su tarifa
    NO se define aquí. Las secciones ASIGNADOS (abonados) tampoco usan
    esta configuración.

    Se obtiene siempre con Tarifa.obtener(), que garantiza que la fila
    exista (la crea con valores por defecto si es la primera vez).
    """

    # ── Tarifas diurnas ──
    primera_hora_diurno = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=9.00,
        help_text="Bs. por la primera hora en horario diurno",
    )
    hora_adicional_diurno = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=2.00,
        help_text="Bs. por cada hora adicional en horario diurno",
    )

    # ── Tarifas nocturnas ──
    primera_hora_nocturno = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=12.00,
        help_text="Bs. por la primera hora en horario nocturno",
    )
    hora_adicional_nocturno = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=5.00,
        help_text="Bs. por cada hora adicional en horario nocturno",
    )

    # ── Horarios de las franjas (hora del día, 0-23) ──
    hora_inicio_diurno = models.PositiveSmallIntegerField(
        default=6,
        help_text="Hora en que empieza el horario diurno (0-23). Ej: 6 = 6:00 AM",
    )
    hora_fin_diurno = models.PositiveSmallIntegerField(
        default=18,
        help_text="Última hora del horario diurno (0-23). Ej: 18 = válido hasta las 18:59",
    )

    # ── Auditoría básica ──
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tarifa"
        verbose_name_plural = "Tarifas"

    def __str__(self):
        return (
            f"Tarifa: Diurno {self.primera_hora_diurno}/{self.hora_adicional_diurno} | "
            f"Nocturno {self.primera_hora_nocturno}/{self.hora_adicional_nocturno}"
        )

    def save(self, *args, **kwargs):
        """Forzar que siempre sea la fila pk=1 (patrón singleton)."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def obtener(cls):
        """
        Devuelve la única fila de configuración de tarifas.
        Si no existe (primera vez), la crea con los valores por defecto.

        Esto garantiza que el cálculo de tarifa NUNCA falle por
        ausencia de configuración.
        """
        tarifa, _creada = cls.objects.get_or_create(pk=1)
        return tarifa