"""
════════════════════════════════════════════════════════════════════════
SERVICE: USUARIOS - VORTEX
════════════════════════════════════════════════════════════════════════

Lógica de negocio para gestión de usuarios:
- Listar
- Crear
- Actualizar
- Desactivar (soft delete) con reglas de negocio:
    1. No puedes desactivarte a ti mismo.
    2. Siempre debe quedar al menos un Administrador activo.
"""

from django.db import IntegrityError
from django.db.models import QuerySet

from usuarios.models import Usuario
from core.exceptions import (
    UsuarioNoEncontradoError,
    DatosInvalidosError,
    UltimoAdministradorError,
    AutoDesactivacionError,
)


class UsuarioService:
    """
    Service de gestión de usuarios.

    Encapsula TODA la lógica de negocio relacionada con usuarios.
    Las views solo llaman a estos métodos.
    """

    # ──────────────────────────────────────────────────────────────────
    # LECTURA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def listar_activos() -> QuerySet:
        """Devuelve usuarios activos ordenados por nombre."""
        return Usuario.objects.filter(activo=True).order_by('nombre')

    @staticmethod
    def obtener_por_id(usuario_id: int) -> Usuario:
        """
        Busca un usuario por ID.

        Lanza:
            UsuarioNoEncontradoError: si no existe.
        """
        try:
            return Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            raise UsuarioNoEncontradoError()

    # ──────────────────────────────────────────────────────────────────
    # ESCRITURA
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def crear(datos_validados: dict) -> Usuario:
        """
        Crea un nuevo usuario.

        El serializer ya validó los datos. Aquí solo persistimos
        y manejamos errores de integridad de BD.

        Lanza:
            DatosInvalidosError: si hay conflicto de email o CI duplicados.
        """
        password = datos_validados.pop('password', None)

        if not password:
            raise DatosInvalidosError("La contraseña es obligatoria")

        try:
            usuario = Usuario(**datos_validados)
            usuario.set_password(password)
            usuario.save()
            return usuario
        except IntegrityError as e:
            # Email o CI duplicados → la BD lanza IntegrityError
            raise DatosInvalidosError(f"Datos duplicados: {str(e)}")

    @staticmethod
    def actualizar(usuario_id: int, datos_validados: dict) -> Usuario:
        """
        Actualiza un usuario existente.

        Solo cambia los campos que vinieron en datos_validados.
        Si hay password, la encripta antes de guardar.
        """
        usuario = UsuarioService.obtener_por_id(usuario_id)
        password = datos_validados.pop('password', None)

        for campo, valor in datos_validados.items():
            setattr(usuario, campo, valor)

        if password:
            usuario.set_password(password)

        usuario.save()
        return usuario

    # ──────────────────────────────────────────────────────────────────
    # DESACTIVACIÓN (SOFT DELETE) — aquí está la lógica de negocio fuerte
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def desactivar(usuario_id: int, solicitante: Usuario) -> Usuario:
        """
        Desactiva un usuario (soft delete) aplicando reglas de negocio.

        Reglas:
            1. Un usuario no puede desactivarse a sí mismo.
            2. Si el usuario es Administrador, debe quedar al menos
               un Administrador activo después de desactivarlo.

        Args:
            usuario_id: ID del usuario a desactivar.
            solicitante: usuario autenticado que pide la desactivación.

        Lanza:
            UsuarioNoEncontradoError
            AutoDesactivacionError
            UltimoAdministradorError
        """
        usuario = UsuarioService.obtener_por_id(usuario_id)

        # Regla 1: no auto-desactivación
        if usuario.id == solicitante.id:
            raise AutoDesactivacionError()

        # Regla 2: debe quedar al menos un admin activo
        if usuario.rol == 'Administrador':
            admins_restantes = Usuario.objects.filter(
                rol='Administrador',
                activo=True,
            ).exclude(id=usuario.id).count()

            if admins_restantes == 0:
                raise UltimoAdministradorError()

        # Aplicar el soft delete
        usuario.activo = False
        usuario.save(update_fields=['activo'])
        return usuario