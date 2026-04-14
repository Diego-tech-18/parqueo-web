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