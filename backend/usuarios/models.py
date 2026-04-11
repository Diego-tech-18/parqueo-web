from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# ── Manager: controla cómo se crean los usuarios ──
class UsuarioManager(BaseUserManager):

    def create_user(self, email, nombre, apellido, rol, password=None):
        """Crea un usuario normal"""
        if not email:
            raise ValueError('El email es obligatorio')

        # Normaliza el email (todo en minúsculas)
        email = self.normalize_email(email)

        usuario = self.model(
            email    = email,
            nombre   = nombre,
            apellido = apellido,
            rol      = rol,
        )
        # Encripta la contraseña antes de guardar
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nombre, apellido, rol='Administrador', password=None):
        """Crea un superusuario para el panel admin de Django"""
        usuario = self.create_user(email, nombre, apellido, rol, password)
        usuario.is_staff     = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


# ── Modelo principal de Usuario ──
class Usuario(AbstractBaseUser, PermissionsMixin):

    # Opciones de rol disponibles
    ROL_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Empleado', 'Empleado'),
    ]

    # ── Campos de la tabla en la BD ──
    email    = models.EmailField(unique=True)                        # se usa para login
    nombre   = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci       = models.CharField(max_length=20, unique=True)          # carnet de identidad
    rol      = models.CharField(max_length=20, choices=ROL_CHOICES)
    activo   = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)                    # acceso al admin Django

    # Foto de perfil → se guarda en media/usuarios/fotos/
    foto = models.ImageField(
        upload_to='usuarios/fotos/',
        null=True,       # puede estar vacío en la BD
        blank=True       # puede estar vacío en el formulario
    )

    # Se llena automáticamente al crear el usuario
    creado_en = models.DateTimeField(auto_now_add=True)

    # ── Usar email en lugar de username para login ──
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'rol']

    # ── Conectar con el manager de arriba ──
    objects = UsuarioManager()

    class Meta:
        db_table = 'usuarios'  # nombre exacto de la tabla en MySQL

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol})"